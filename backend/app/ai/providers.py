import json
from typing import Protocol

from .config import AIProvider, AISettings
from .errors import (
    AIConfigurationError,
    AIProviderResponseError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIUnsupportedSchemaError,
)


class JSONGenerator(Protocol):
    def generate_json(self, system_instructions: str, user_content: str,
                      evidence: dict, response_schema: dict) -> dict: ...


def _validate_schema(schema: object) -> dict:
    if not isinstance(schema, dict) or schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
        raise AIUnsupportedSchemaError("The requested response schema is not supported.")
    if "required" in schema and (not isinstance(schema["required"], list) or
                                  any(key not in schema["properties"] for key in schema["required"])):
        raise AIUnsupportedSchemaError("The requested response schema is not supported.")
    return schema


def _json_response(content: str | None) -> dict:
    if not content:
        raise AIProviderResponseError("The AI provider returned no JSON response.")
    try:
        parsed = json.loads(content)
    except (TypeError, json.JSONDecodeError) as error:
        raise AIProviderResponseError("The AI provider returned malformed JSON.") from error
    if not isinstance(parsed, dict):
        raise AIProviderResponseError("The AI provider response must be a JSON object.")
    return parsed


def _is_timeout(error: Exception) -> bool:
    return isinstance(error, TimeoutError) or "timeout" in type(error).__name__.lower()


class LMStudioJSONGenerator:
    def __init__(self, settings: AISettings, client=None):
        if settings.provider != AIProvider.LM_STUDIO:
            raise AIConfigurationError("LM Studio adapter configuration does not match the selected provider.")
        if client is None:
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key="lm-studio",
                    base_url=settings.lm_studio_base_url,
                    timeout=settings.timeout_seconds,
                    max_retries=0,
                )
            except Exception as error:
                raise AIConfigurationError("The OpenAI client is unavailable for LM Studio.") from error
        self._client = client
        self._model = settings.lm_studio_model

    def generate_json(self, system_instructions: str, user_content: str, evidence: dict,
                      response_schema: dict) -> dict:
        schema = _validate_schema(response_schema)
        content = f"{user_content}\n\nApplication evidence (JSON):\n{json.dumps(evidence, ensure_ascii=False, separators=(',', ':'))}"
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "system", "content": system_instructions},
                          {"role": "user", "content": content}],
                response_format={"type": "json_schema", "json_schema": {
                    "name": "application_response", "strict": True, "schema": schema,
                }},
                timeout=30,
            )
        except Exception as error:
            if _is_timeout(error):
                raise AIProviderTimeoutError("The AI provider request timed out.") from error
            raise AIProviderUnavailableError("The configured AI provider could not complete the request.") from error
        try:
            return _json_response(response.choices[0].message.content)
        except AIProviderResponseError:
            raise
        except Exception as error:
            raise AIProviderResponseError("The AI provider response could not be read.") from error


class GeminiJSONGenerator:
    def __init__(self, settings: AISettings, client=None):
        if settings.provider != AIProvider.GEMINI:
            raise AIConfigurationError("Gemini adapter configuration does not match the selected provider.")
        self._types = None
        if client is None:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(
                    api_key=settings.gemini_api_key,
                    http_options=types.HttpOptions(
                        timeout=settings.timeout_seconds * 1000,
                        retry_options=types.HttpRetryOptions(attempts=1),
                    ),
                )
                self._types = types
            except Exception as error:
                raise AIConfigurationError("The Gemini client is unavailable or misconfigured.") from error
        else:
            from types import SimpleNamespace
            self._types = SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs)
        self._client = client
        self._model = settings.gemini_model

    def generate_json(self, system_instructions: str, user_content: str, evidence: dict,
                      response_schema: dict) -> dict:
        schema = _validate_schema(response_schema)
        content = f"{user_content}\n\nApplication evidence (JSON):\n{json.dumps(evidence, ensure_ascii=False, separators=(',', ':'))}"
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=content,
                config=self._types.GenerateContentConfig(
                    system_instruction=system_instructions,
                    response_mime_type="application/json",
                    response_json_schema=schema,
                ),
            )
        except Exception as error:
            if _is_timeout(error):
                raise AIProviderTimeoutError("The AI provider request timed out.") from error
            raise AIProviderUnavailableError("The configured AI provider could not complete the request.") from error
        try:
            return _json_response(response.text)
        except AIProviderResponseError:
            raise
        except Exception as error:
            raise AIProviderResponseError("The AI provider response could not be read.") from error
