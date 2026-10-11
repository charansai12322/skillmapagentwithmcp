"""Integration tests for POST /api/query and service normalization."""

import pytest
from unittest.mock import patch, AsyncMock
from app.services.skillmap_service import parse_agent_text_response, extract_skill_keyword
from app.schemas import JobOpportunity


SAMPLE_AGENT_OUTPUT_TEXT = """
SKILL DEMAND ANALYSIS: GENERATIVE AI

INDUSTRY DEMAND OVERVIEW
Generative AI is currently experiencing massive growth across tech, finance, and healthcare. Roles centered around AI development now account for over 25% of tech hiring demand.

SALARY INSIGHTS
Median Compensation: The median total compensation in the US ranges from $143,000 to $212,000 per year.
Senior & Lead Positions: Staff-level engineers regularly earn between $300,000 and $500,000+ per year.
Entry-Level: Base salaries start around $110,000 per year.

KEY SKILLS
1. Retrieval-Augmented Generation (RAG)
2. Vector Databases
3. LangChain & LangGraph
4. Agentic AI Workflows

ACTIVE JOB OPPORTUNITIES
1. Generative AI Applications Engineer
Company: Accenture Federal Services
Location: United States
Apply Link: https://boards.greenhouse.io/accenture/1

2. Helix AI Engineer
Company: Figure AI
Location: United States
Apply Link: https://job-boards.greenhouse.io/figureai/2
"""


def test_extract_skill_keyword():
    """Extracts target skill from natural language queries."""
    assert "Generative AI" in extract_skill_keyword("What is the demand for Generative AI in the industry?")
    assert "Python" in extract_skill_keyword("Show me open jobs in Python in Bengaluru")
    assert "Kubernetes" in extract_skill_keyword("Careers in Kubernetes")


def test_parse_agent_text_response():
    """Accurately extracts structured sections from free-form agent output text."""
    overview, salaries, skills, jobs = parse_agent_text_response(SAMPLE_AGENT_OUTPUT_TEXT)

    assert overview is not None
    assert "massive growth" in overview.summary
    assert overview.demand_level == "HIGH"

    assert salaries is not None
    assert salaries.currency == "USD"
    assert "$143,000 to $212,000" in salaries.median
    assert "$300,000 and $500,000+" in salaries.senior
    assert "$110,000" in salaries.entry_level

    assert len(skills) >= 4
    assert any("RAG" in s or "Retrieval" in s for s in skills)

    assert len(jobs) == 2
    assert jobs[0].title == "Generative AI Applications Engineer"
    assert jobs[0].company == "Accenture Federal Services"
    assert jobs[0].apply_url == "https://boards.greenhouse.io/accenture/1"
    assert jobs[0].source == "COMPOSIO_WEB_SEARCH"


def test_api_query_empty_body_rejected(client):
    """POST /api/query with missing body returns 422 Unprocessable Entity."""
    response = client.post("/api/query", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["error"] is True
    assert data["code"] == "VALIDATION_ERROR"


def test_api_query_invalid_country_rejected(client):
    """POST /api/query with invalid country code returns 422."""
    response = client.post(
        "/api/query",
        json={"query": "AI Engineer in India", "country": "INDIA_INVALID"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] is True


@patch("app.tools.job_search.execute_job_search")
@patch("app.agent.skill_agent.SkillAgentRunner.execute")
def test_api_query_success_mocked(mock_agent_exec, mock_search, client):
    """POST /api/query successfully returns normalized response contract."""
    mock_agent_exec.return_value = {
        "final_text": SAMPLE_AGENT_OUTPUT_TEXT,
        "tools_invoked": ["COMPOSIO_MCP", "RAPIDAPI_JSEARCH"],
        "warnings": []
    }
    mock_search.return_value = (
        [
            JobOpportunity(
                title="Generative AI Developer",
                company="Wipro",
                location="Bengaluru",
                apply_url="https://wipro.com/jobs/1",
                source="RAPIDAPI_JSEARCH"
            )
        ],
        "success",
        None
    )

    response = client.post(
        "/api/query",
        json={
            "query": "What is the demand for Generative AI in the industry?",
            "location": "Bengaluru",
            "country": "in"
        }
    )
    assert response.status_code == 200
    data = response.json()

    assert "request_id" in data
    assert data["query"] == "What is the demand for Generative AI in the industry?"
    assert data["status"] in ("SUCCESS", "PARTIAL_SUCCESS")
    assert data["industry_overview"] is not None
    assert data["salary_insights"] is not None
    assert len(data["key_skills"]) > 0
    assert len(data["job_opportunities"]) > 0
    assert data["metadata"]["job_results_count"] > 0
    assert data["metadata"]["execution_time_ms"] >= 0


@patch("app.services.skillmap_service.SkillMapService.process_query")
def test_api_query_handles_unexpected_exception(mock_process, client):
    """Unexpected exception in service returns safe 500 without leaking stack trace."""
    mock_process.side_effect = RuntimeError("Sensitive DB Connection String: secret123")

    response = client.post(
        "/api/query",
        json={"query": "AI jobs in Pune"}
    )
    assert response.status_code == 500
    data = response.json()
    assert data["error"] is True
    assert data["code"] == "INTERNAL_SERVER_ERROR"
    # Never leaks sensitive internal exception details
    assert "secret123" not in response.text
