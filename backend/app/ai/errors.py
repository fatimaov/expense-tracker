class AIError(RuntimeError):
    """Base safe error raised by the AI integration boundary."""


class AIConfigurationError(AIError):
    pass


class AIProviderUnavailableError(AIError):
    pass


class AIProviderTimeoutError(AIError):
    pass


class AIProviderResponseError(AIError):
    pass


class AIUnsupportedSchemaError(AIError):
    pass


class AIRateLimitExceededError(AIError):
    pass
