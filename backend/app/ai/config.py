from dataclasses import dataclass
from enum import Enum

from .errors import AIConfigurationError


class AIProvider(str, Enum):
    LM_STUDIO = "lm_studio"
    GEMINI = "gemini"


@dataclass(frozen=True)
class AISettings:
    provider: AIProvider = AIProvider.LM_STUDIO
    timeout_seconds: int = 30
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "local-model"
    gemini_api_key: str | None = None
    gemini_model: str | None = None

    @classmethod
    def from_mapping(cls, values: dict) -> "AISettings":
        provider_value = values.get("AI_PROVIDER", AIProvider.LM_STUDIO.value)
        try:
            provider = AIProvider(provider_value)
        except (TypeError, ValueError) as error:
            raise AIConfigurationError("AI_PROVIDER must be lm_studio or gemini.") from error
        try:
            timeout = int(values.get("AI_REQUEST_TIMEOUT_SECONDS", 30))
        except (TypeError, ValueError) as error:
            raise AIConfigurationError("AI_REQUEST_TIMEOUT_SECONDS must be 30.") from error
        if timeout != 30:
            raise AIConfigurationError("AI_REQUEST_TIMEOUT_SECONDS is fixed at 30 seconds.")
        settings = cls(
            provider=provider,
            timeout_seconds=timeout,
            lm_studio_base_url=str(values.get("LM_STUDIO_BASE_URL") or "http://localhost:1234/v1"),
            lm_studio_model=str(values.get("LM_STUDIO_MODEL") or "local-model"),
            gemini_api_key=values.get("GEMINI_API_KEY"),
            gemini_model=values.get("GEMINI_MODEL"),
        )
        if provider == AIProvider.GEMINI and not (settings.gemini_api_key and settings.gemini_model):
            raise AIConfigurationError("Gemini requires GEMINI_API_KEY and GEMINI_MODEL.")
        if provider == AIProvider.LM_STUDIO and not (settings.lm_studio_base_url and settings.lm_studio_model):
            raise AIConfigurationError("LM Studio requires LM_STUDIO_BASE_URL and LM_STUDIO_MODEL.")
        return settings
