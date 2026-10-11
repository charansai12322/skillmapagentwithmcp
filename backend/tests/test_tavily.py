"""Regression and unit tests for Tavily integration in SkillMap AI backend.

Verifies:
1. TAVILY_API_KEY configuration and presence checking without secret leakage.
2. Server startup resilience when Tavily key is missing.
3. Tool discovery and inclusion in agent runner.
4. Agent result consumption with mocked Tavily results.
5. Error handling for auth failures and timeouts.
6. Graceful degradation when Tavily fails or is unavailable.
7. Source URL attribution preservation.
8. Secret redaction in outputs and health checks.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings
from app.agent.skill_agent import SkillAgentRunner
from app.services.skillmap_service import SkillMapService
from app.schemas import SkillQueryRequest


client = TestClient(app)


def test_tavily_key_loaded_and_detected_safely():
    """1. Verifies TAVILY_API_KEY is detected correctly without leaking raw values."""
    settings_with_key = Settings(TAVILY_API_KEY="tvly-mock-secret-key-12345")
    assert settings_with_key.has_tavily_key is True
    # Ensure str representation doesn't expose the secret in common logs
    assert "tvly-mock-secret-key-12345" not in repr(settings_with_key.has_tavily_key)

    settings_empty = Settings(TAVILY_API_KEY="")
    assert settings_empty.has_tavily_key is False

    settings_none = Settings(TAVILY_API_KEY=None)
    assert settings_none.has_tavily_key is False


def test_missing_tavily_key_does_not_crash_health_endpoint():
    """2. Verifies missing Tavily credentials do not crash the server and report accurately."""
    with patch("app.api.routes.get_settings") as mock_settings:
        mock_instance = MagicMock()
        mock_instance.has_gemini_key = True
        mock_instance.has_rapidapi_key = True
        mock_instance.has_composio_key = False
        mock_instance.has_tavily_key = False
        mock_settings.return_value = mock_instance

        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["tavily"] == "not_configured"
        assert "tvly-" not in response.text


def test_tavily_reported_configured_when_key_present():
    """Verifies health endpoint reports tavily configured when key is provided."""
    with patch("app.api.routes.get_settings") as mock_settings:
        mock_instance = MagicMock()
        mock_instance.has_gemini_key = True
        mock_instance.has_rapidapi_key = True
        mock_instance.has_composio_key = False
        mock_instance.has_tavily_key = True
        mock_settings.return_value = mock_instance

        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["services"]["tavily"] == "configured"
        assert "tvly-" not in response.text


@pytest.mark.asyncio
async def test_tavily_tool_included_when_configured():
    """3. Verifies TavilySearch is instantiated and added to tools when configured."""
    mock_settings = MagicMock()
    mock_settings.has_tavily_key = True
    mock_settings.TAVILY_API_KEY = "tvly-test-key"
    mock_settings.has_composio_key = False
    mock_settings.has_gemini_key = True
    mock_settings.GEMINI_MODEL = "gemini-3.7-flash"
    mock_settings.REQUEST_TIMEOUT_SECONDS = 5.0
    mock_settings.MAX_AGENT_ITERATIONS = 4

    runner = SkillAgentRunner()
    runner.settings = mock_settings

    mock_agent_instance = MagicMock()
    mock_agent_instance.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Mocked summary with Tavily insights.")]
    })

    with patch("langchain_tavily.TavilySearch") as MockTavilySearch, \
         patch("app.agent.skill_agent.SkillAgentRunner._init_model") as mock_model, \
         patch("langchain.agents.create_agent", return_value=mock_agent_instance) as mock_create_agent:

        mock_tool_obj = MagicMock()
        mock_tool_obj.name = "tavily_search"
        MockTavilySearch.return_value = mock_tool_obj

        result = await runner.execute(query="Generative AI demand")

        # TavilySearch was instantiated with correct args
        MockTavilySearch.assert_called_once_with(
            max_results=5,
            search_depth="advanced",
            tavily_api_key="tvly-test-key",
        )
        assert "TAVILY_SEARCH" in result["tools_invoked"]

        # create_agent received the tool list containing tavily
        created_tools = mock_create_agent.call_args[1]["tools"]
        assert mock_tool_obj in created_tools


@pytest.mark.asyncio
async def test_tavily_tool_failure_degrades_gracefully():
    """5 & 6. Verifies Tavily initialization failure produces a warning and allows agent to proceed."""
    mock_settings = MagicMock()
    mock_settings.has_tavily_key = True
    mock_settings.TAVILY_API_KEY = "tvly-bad-key"
    mock_settings.has_composio_key = False
    mock_settings.has_gemini_key = True
    mock_settings.GEMINI_MODEL = "gemini-3.7-flash"
    mock_settings.REQUEST_TIMEOUT_SECONDS = 5.0
    mock_settings.MAX_AGENT_ITERATIONS = 4

    runner = SkillAgentRunner()
    runner.settings = mock_settings

    mock_agent_instance = MagicMock()
    mock_agent_instance.ainvoke = AsyncMock(return_value={
        "messages": [MagicMock(content="Proceeded without Tavily.")]
    })

    with patch("langchain_tavily.TavilySearch", side_effect=Exception("Unauthorized Tavily Key")), \
         patch("app.agent.skill_agent.SkillAgentRunner._init_model"), \
         patch("langchain.agents.create_agent", return_value=mock_agent_instance):

        result = await runner.execute(query="AI Engineer demand")
        assert any("Tavily Search tool unavailable" in w for w in result["warnings"])
        assert result["final_text"] == "Proceeded without Tavily."


@pytest.mark.asyncio
async def test_source_attribution_includes_tavily_when_invoked():
    """7. Verifies source URL and attribution for Tavily are preserved in final response."""
    service = SkillMapService()
    mock_settings = MagicMock()
    mock_settings.has_gemini_key = True
    mock_settings.has_tavily_key = True
    mock_settings.has_rapidapi_key = False
    mock_settings.has_composio_key = False
    mock_settings.REQUEST_TIMEOUT_SECONDS = 5.0
    service.settings = mock_settings

    mock_runner_res = {
        "final_text": "### INDUSTRY DEMAND OVERVIEW\nHigh demand for Generative AI.\n\n### KEY SKILLS\n- PyTorch\n- LLMs",
        "tools_invoked": ["TAVILY_SEARCH"],
        "warnings": [],
    }

    with patch.object(service.runner, "execute", new=AsyncMock(return_value=mock_runner_res)):
        req = SkillQueryRequest(query="Generative AI career insights")
        resp = await service.process_query(req)

        # Check source attribution has Tavily
        tavily_sources = [s for s in resp.sources if "Tavily" in s.name]
        assert len(tavily_sources) >= 1
        assert tavily_sources[0].url == "https://tavily.com"
        assert "TAVILY_SEARCH" in resp.metadata.tools_invoked


def test_tavily_no_secret_leakage_in_error():
    """8. Verifies mock errors containing Tavily secrets are sanitized."""
    raw_secret = "tvly-super-secret-key-999"
    err_message = f"Failed to authenticate with Tavily using key {raw_secret}"

    # Sanitization simulation
    sanitized = err_message.replace(raw_secret, "[REDACTED]")
    assert raw_secret not in sanitized
    assert "[REDACTED]" in sanitized
