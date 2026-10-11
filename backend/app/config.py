"""Configuration management for SkillMap AI Backend.

Loads environment variables safely with redaction helpers and defaults.
Never prints or logs raw secrets.
"""

import os
from typing import List, Optional
from pathlib import Path

# Look for .env file in backend/ or root
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"
if not ENV_PATH.exists() and (ROOT_DIR / ".env").exists():
    ENV_PATH = ROOT_DIR / ".env"

try:
    from dotenv import load_dotenv
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        load_dotenv()
except ImportError:
    pass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        # AI & LLM Services
        GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")
        GEMINI_MODEL: str = Field(default="gemini-3.7-flash", description="Gemini model identifier")

        # RapidAPI JSearch
        RAPIDAPI_KEY: Optional[str] = Field(default=None, description="RapidAPI Key for JSearch")
        RAPIDAPI_HOST: str = Field(default="jsearch.p.rapidapi.com")
        RAPIDAPI_URL: str = Field(default="https://jsearch.p.rapidapi.com/search-v2")

        # Composio MCP Remote Server
        COMPOSIO_API_KEY: Optional[str] = Field(default=None, description="Composio Consumer API Key")
        COMPOSIO_MCP_URL: str = Field(default="https://connect.composio.dev/mcp")

        # Tavily Search Tool
        TAVILY_API_KEY: Optional[str] = Field(default=None, description="Tavily API Key")

        # Server Settings
        HOST: str = Field(default="0.0.0.0")
        PORT: int = Field(default=8000)
        LOG_LEVEL: str = Field(default="INFO")
        REQUEST_TIMEOUT_SECONDS: float = Field(default=15.0)
        MAX_AGENT_ITERATIONS: int = Field(default=8)
        DEFAULT_COUNTRY: str = Field(default="in")

        # CORS
        FRONTEND_ORIGINS: str = Field(
            default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
        )

        model_config = {
            "env_file": str(ENV_PATH) if ENV_PATH.exists() else None,
            "env_file_encoding": "utf-8",
            "extra": "ignore",
        }

        @property
        def allowed_origins(self) -> List[str]:
            return [o.strip() for o in self.FRONTEND_ORIGINS.split(",") if o.strip()]

        @property
        def has_gemini_key(self) -> bool:
            return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())

        @property
        def has_rapidapi_key(self) -> bool:
            return bool(self.RAPIDAPI_KEY and self.RAPIDAPI_KEY.strip())

        @property
        def has_composio_key(self) -> bool:
            return bool(self.COMPOSIO_API_KEY and self.COMPOSIO_API_KEY.strip())

        @property
        def has_tavily_key(self) -> bool:
            return bool(self.TAVILY_API_KEY and self.TAVILY_API_KEY.strip())

    settings = Settings()

except (ImportError, Exception):
    # Standalone fallback when pydantic-settings is not yet installed
    class FallbackSettings:
        def __init__(self):
            self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
            self.RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
            self.RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
            self.RAPIDAPI_URL = os.getenv("RAPIDAPI_URL", "https://jsearch.p.rapidapi.com/search-v2")
            self.COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
            self.COMPOSIO_MCP_URL = os.getenv("COMPOSIO_MCP_URL", "https://connect.composio.dev/mcp")
            self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
            self.HOST = os.getenv("HOST", "0.0.0.0")
            self.PORT = int(os.getenv("PORT", "8000"))
            self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
            self.REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "15.0"))
            self.MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "8"))
            self.DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "in")
            self.FRONTEND_ORIGINS = os.getenv(
                "FRONTEND_ORIGINS",
                "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
            )

        @property
        def allowed_origins(self) -> List[str]:
            return [o.strip() for o in self.FRONTEND_ORIGINS.split(",") if o.strip()]

        @property
        def has_gemini_key(self) -> bool:
            return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())

        @property
        def has_rapidapi_key(self) -> bool:
            return bool(self.RAPIDAPI_KEY and self.RAPIDAPI_KEY.strip())

        @property
        def has_composio_key(self) -> bool:
            return bool(self.COMPOSIO_API_KEY and self.COMPOSIO_API_KEY.strip())

        @property
        def has_tavily_key(self) -> bool:
            return bool(self.TAVILY_API_KEY and self.TAVILY_API_KEY.strip())


    settings = FallbackSettings()


def get_settings():
    return settings
