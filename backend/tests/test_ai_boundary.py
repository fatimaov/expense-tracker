import json
import base64
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import sys
from threading import Barrier
from types import SimpleNamespace

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.engine import make_url

from app.ai.config import AIProvider, AISettings
from app.ai.errors import (
    AIConfigurationError,
    AIProviderResponseError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIUnsupportedSchemaError,
    AIRateLimitExceededError,
)
from app.ai.factory import create_json_generator
from app.ai.providers import GeminiJSONGenerator, LMStudioJSONGenerator
from app.extensions import db
from app.models import AIRequestAttempt, User
from app.services.ai_request_guard import record_provider_request_start
from app import create_app


SCHEMA = {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}


class FakeOpenAI:
    def __init__(self, content='{"answer":"ok"}', error=None):
        self.call = None
        self.calls = 0
        self.content = content
        self.error = error
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls += 1
        self.call = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class FakeGemini:
    def __init__(self, content='{"answer":"ok"}', error=None):
        self.call = None
        self.calls = 0
        self.content = content
        self.error = error
        self.models = SimpleNamespace(generate_content=self.generate_content)

    def generate_content(self, **kwargs):
        self.calls += 1
        self.call = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.content)


def test_ai_config_defaults_to_lm_studio_and_timeout_is_fixed():
    config = AISettings.from_mapping({})
    assert config.provider == AIProvider.LM_STUDIO
    assert config.timeout_seconds == 30
    with pytest.raises(AIConfigurationError):
        AISettings.from_mapping({"AI_REQUEST_TIMEOUT_SECONDS": "12"})
    with pytest.raises(AIConfigurationError):
        AISettings.from_mapping({"AI_PROVIDER": "unknown"})
    with pytest.raises(AIConfigurationError):
        AISettings.from_mapping({"AI_PROVIDER": "gemini"})


def test_provider_factory_selects_by_typed_configuration_and_lm_studio_uses_json_schema():
    settings = AISettings.from_mapping({})
    client = FakeOpenAI()
    adapter = create_json_generator(settings, clients={AIProvider.LM_STUDIO: client})
    assert isinstance(adapter, LMStudioJSONGenerator)
    assert adapter.generate_json("system", "question", {"count": 1}, SCHEMA) == {"answer": "ok"}
    assert client.call["response_format"]["json_schema"]["schema"] == SCHEMA
    assert "\"count\":1" in client.call["messages"][1]["content"]
    assert client.call["timeout"] == 30
    assert client.calls == 1


def test_gemini_adapter_requests_structured_json_and_parses_response():
    settings = AISettings.from_mapping({
        "AI_PROVIDER": "gemini", "GEMINI_API_KEY": "secret", "GEMINI_MODEL": "model-id",
    })
    client = FakeGemini()
    adapter = GeminiJSONGenerator(settings, client=client)
    assert adapter.generate_json("system", "question", {}, SCHEMA) == {"answer": "ok"}
    assert client.call["model"] == "model-id"
    assert client.call["config"]["response_mime_type"] == "application/json"
    assert client.call["config"]["response_json_schema"] == SCHEMA
    assert client.calls == 1


@pytest.mark.parametrize("client_class", [FakeOpenAI, FakeGemini])
def test_adapters_send_image_and_structured_json_without_exposing_sdk_types(client_class):
    settings = AISettings.from_mapping({}) if client_class is FakeOpenAI else AISettings.from_mapping({
        "AI_PROVIDER": "gemini", "GEMINI_API_KEY": "secret", "GEMINI_MODEL": "model-id",
    })
    make_adapter = LMStudioJSONGenerator if client_class is FakeOpenAI else GeminiJSONGenerator
    client = client_class()
    adapter = make_adapter(settings, client=client)
    image = b"private-image-bytes"

    assert adapter.generate_json_from_image(
        "extract receipt", image, "image/png", {"media_type": "image/png"}, SCHEMA
    ) == {"answer": "ok"}
    assert client.calls == 1
    if client_class is FakeOpenAI:
        content = client.call["messages"][1]["content"]
        assert content[0]["type"] == "text"
        assert content[1]["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(image).decode('ascii')}"
        assert client.call["response_format"]["json_schema"]["schema"] == SCHEMA
    else:
        assert client.call["contents"][1] == {"data": image, "mime_type": "image/png"}
        assert client.call["config"]["response_json_schema"] == SCHEMA


def test_sdk_construction_sets_timeout_and_disables_retries(monkeypatch):
    openai_options = {}
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=lambda **kwargs: openai_options.update(kwargs) or FakeOpenAI()))
    LMStudioJSONGenerator(AISettings())
    assert openai_options["timeout"] == 30
    assert openai_options["max_retries"] == 0

    gemini_options = {}
    types = SimpleNamespace(
        HttpOptions=lambda **kwargs: kwargs,
        HttpRetryOptions=lambda **kwargs: kwargs,
    )
    google_genai = SimpleNamespace(Client=lambda **kwargs: gemini_options.update(kwargs) or FakeGemini())
    monkeypatch.setitem(sys.modules, "google", SimpleNamespace(genai=google_genai))
    monkeypatch.setitem(sys.modules, "google.genai", SimpleNamespace(types=types))
    GeminiJSONGenerator(AISettings.from_mapping({
        "AI_PROVIDER": "gemini", "GEMINI_API_KEY": "key", "GEMINI_MODEL": "model",
    }))
    assert gemini_options["http_options"]["timeout"] == 30000
    assert gemini_options["http_options"]["retry_options"] == {"attempts": 1}


@pytest.mark.parametrize("client_class", [FakeOpenAI, FakeGemini])
def test_adapters_raise_safe_typed_errors_for_timeout_and_invalid_json(client_class):
    settings = AISettings.from_mapping({}) if client_class is FakeOpenAI else AISettings.from_mapping({
        "AI_PROVIDER": "gemini", "GEMINI_API_KEY": "secret", "GEMINI_MODEL": "model-id",
    })
    make_adapter = LMStudioJSONGenerator if client_class is FakeOpenAI else GeminiJSONGenerator
    timed_out = make_adapter(settings, client=client_class(error=TimeoutError("sentinel-private")))
    with pytest.raises(AIProviderTimeoutError) as error:
        timed_out.generate_json("prompt-sentinel", "input", {}, SCHEMA)
    assert "sentinel-private" not in str(error.value)
    malformed = make_adapter(settings, client=client_class(content="not-json"))
    with pytest.raises(AIProviderResponseError):
        malformed.generate_json("system", "input", {}, SCHEMA)
    unavailable = make_adapter(settings, client=client_class(error=RuntimeError("response-secret")))
    with pytest.raises(AIProviderUnavailableError) as error:
        unavailable.generate_json("prompt-sentinel", "input", {"record": "financial-sentinel"}, SCHEMA)
    assert "response-secret" not in str(error.value)
    assert "financial-sentinel" not in str(error.value)


def test_unsupported_schema_is_rejected_without_calling_provider():
    client = FakeOpenAI()
    adapter = LMStudioJSONGenerator(AISettings(), client=client)
    with pytest.raises(AIUnsupportedSchemaError):
        adapter.generate_json("system", "user", {}, {"type": "array"})
    assert client.call is None


def test_rate_guard_allows_ten_rejects_eleven_and_prunes_expired_attempts(app):
    now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    with app.app_context():
        record_provider_request_start(app.config["TEST_USER_ID"], now)
        failed_provider = LMStudioJSONGenerator(AISettings(), client=FakeOpenAI(error=RuntimeError("provider unavailable")))
        with pytest.raises(AIProviderUnavailableError):
            failed_provider.generate_json("private prompt", "input", {"record": "private"}, SCHEMA)
        assert db.session.query(AIRequestAttempt).count() == 1
        for offset in range(1, 10):
            record_provider_request_start(app.config["TEST_USER_ID"], now + timedelta(seconds=offset))
        with pytest.raises(AIRateLimitExceededError):
            record_provider_request_start(app.config["TEST_USER_ID"], now + timedelta(seconds=11))
        assert db.session.query(AIRequestAttempt).count() == 10
        record_provider_request_start(app.config["TEST_USER_ID"], now + timedelta(minutes=15, seconds=11))
        attempts = db.session.query(AIRequestAttempt).all()
        assert len(attempts) == 1
        assert {column.name for column in AIRequestAttempt.__table__.columns} == {"id", "user_id", "started_at"}


def test_rate_guard_uses_a_database_row_lock_for_same_user():
    from sqlalchemy.dialects import postgresql

    statement = select(User.id).where(User.id == 1).with_for_update()
    assert "FOR UPDATE" in str(statement.compile(dialect=postgresql.dialect()))


def test_rate_guard_concurrent_starts_do_not_exceed_the_limit_on_postgresql():
    database_url = os.getenv("AI_RATE_GUARD_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set AI_RATE_GUARD_TEST_DATABASE_URL to a fresh disposable PostgreSQL database.")
    url = make_url(database_url)
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg2")
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": url.render_as_string(hide_password=False),
        "JWT_SECRET_KEY": "rate-guard-test-secret-that-is-long-enough",
    })
    with app.app_context():
        assert not inspect(db.engine).get_table_names(), "Concurrency test requires a fresh disposable PostgreSQL database."
        db.create_all()
        user = User(email="rate-guard@example.com", password_hash="unused")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    try:
        with app.app_context():
            for _ in range(9):
                record_provider_request_start(user_id, now)
        barrier = Barrier(2)

        def concurrent_start():
            with app.app_context():
                barrier.wait()
                try:
                    record_provider_request_start(user_id, now)
                    return "allowed"
                except AIRateLimitExceededError:
                    return "limited"
                finally:
                    db.session.remove()

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _index: concurrent_start(), range(2)))
        assert sorted(outcomes) == ["allowed", "limited"]
        with app.app_context():
            assert db.session.query(AIRequestAttempt).count() == 10
    finally:
        with app.app_context():
            db.session.remove()
            db.drop_all()
