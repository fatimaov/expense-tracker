from .config import AIProvider, AISettings
from .errors import AIConfigurationError
from .providers import GeminiJSONGenerator, JSONGenerator, LMStudioJSONGenerator


def create_json_generator(settings: AISettings, *, clients: dict | None = None) -> JSONGenerator:
    clients = clients or {}
    if settings.provider == AIProvider.LM_STUDIO:
        return LMStudioJSONGenerator(settings, client=clients.get(AIProvider.LM_STUDIO))
    if settings.provider == AIProvider.GEMINI:
        return GeminiJSONGenerator(settings, client=clients.get(AIProvider.GEMINI))
    raise AIConfigurationError("The selected AI provider is not supported.")
