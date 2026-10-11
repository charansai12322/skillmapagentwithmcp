"""Centralized exception definitions and error codes for SkillMap AI.

Ensures that errors are consistently classified, machine-readable,
and never leak secrets, API keys, or raw system paths.
"""

from typing import Optional, Dict, Any


class SkillMapError(Exception):
    """Base exception for all SkillMap AI application errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class RequestValidationError(SkillMapError):
    """Raised when client input fails validation rules."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_REQUEST",
            status_code=400,
            details=details,
        )


class ConfigurationError(SkillMapError):
    """Raised when required server-side credentials or configuration are absent."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )


class ProviderAuthError(SkillMapError):
    """Raised when upstream API (RapidAPI, Gemini, Composio) returns 401/403."""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Authentication or subscription failure with upstream provider: {provider}",
            code="UPSTREAM_AUTH_ERROR",
            status_code=502,
            details=details,
        )


class ProviderQuotaError(SkillMapError):
    """Raised when upstream API quota or rate limits are exhausted (HTTP 429)."""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Rate limit or quota exhausted for upstream provider: {provider}",
            code="UPSTREAM_QUOTA_ERROR",
            status_code=429,
            details=details,
        )


class ProviderTimeoutError(SkillMapError):
    """Raised when an upstream request times out."""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Upstream provider request timed out: {provider}",
            code="UPSTREAM_TIMEOUT",
            status_code=504,
            details=details,
        )


class ProviderUnavailableError(SkillMapError):
    """Raised when an upstream service returns 5xx or fails connection."""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Upstream provider is temporarily unavailable: {provider}",
            code="UPSTREAM_UNAVAILABLE",
            status_code=503,
            details=details,
        )


class ProviderResponseError(SkillMapError):
    """Raised when upstream returns unexpected schema or invalid JSON."""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Invalid or unexpected response structure received from: {provider}",
            code="UPSTREAM_RESPONSE_ERROR",
            status_code=502,
            details=details,
        )


class AgentExecutionError(SkillMapError):
    """Raised when LangGraph or the LLM agent encounters an unrecoverable runtime error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            status_code=500,
            details=details,
        )
