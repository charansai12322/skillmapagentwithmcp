"""Shared pytest configuration, fixtures, and mocks."""

import sys
import os
from pathlib import Path
import pytest

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Set test environment variables
os.environ["RAPIDAPI_KEY"] = "mock_test_rapidapi_key"
os.environ["GEMINI_API_KEY"] = "mock_test_gemini_key"
os.environ["COMPOSIO_API_KEY"] = "mock_test_composio_key"
os.environ["DEFAULT_COUNTRY"] = "in"

from app.main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def mock_jsearch_success_response():
    """Sample realistic JSearch API response with multiple listings."""
    return {
        "status": "OK",
        "request_id": "test-req-123",
        "parameters": {"query": "python developer in in", "page": 1, "num_pages": 1},
        "data": [
            {
                "job_id": "job_1",
                "job_title": "AI Engineer",
                "employer_name": "Infosys",
                "job_city": "Bengaluru",
                "job_state": "Karnataka",
                "job_country": "India",
                "job_description": "We are looking for an AI Engineer experienced in LLMs and Python.",
                "job_employment_type": "FULLTIME",
                "job_is_remote": False,
                "job_apply_link": "https://careers.infosys.com/job/1",
                "job_min_salary": 800000,
                "job_max_salary": 1200000,
                "job_salary_currency": "INR",
                "job_salary_period": "YEAR",
                "job_posted_at_timestamp": 1712000000,
                "job_required_skills": ["Python", "PyTorch", "Generative AI"]
            },
            {
                "job_id": "job_2",
                "job_title": "Generative AI Researcher",
                "employer_name": "TCS",
                "job_city": "Hyderabad",
                "job_state": "Telangana",
                "job_country": "India",
                "job_description": "Research generative models and computer vision pipelines.",
                "job_employment_type": "FULLTIME",
                "job_is_remote": True,
                "job_apply_link": "https://tcs.com/jobs/genai",
                "job_min_salary": None,
                "job_max_salary": None,
                "job_salary_currency": None,
                "job_salary_period": None,
                "job_posted_at_timestamp": 1712050000,
                "job_required_skills": ["RAG", "LangChain"]
            },
            # Duplicate item to test deduplication
            {
                "job_id": "job_1_dup",
                "job_title": "AI Engineer",
                "employer_name": "Infosys",
                "job_city": "Bengaluru",
                "job_state": "Karnataka",
                "job_country": "India",
                "job_description": "Duplicate listing.",
                "job_employment_type": "FULLTIME",
                "job_is_remote": False,
                "job_apply_link": "https://careers.infosys.com/job/1?ref=linkedin",
                "job_min_salary": 800000,
                "job_max_salary": 1200000,
                "job_salary_currency": "INR",
                "job_salary_period": "YEAR",
                "job_posted_at_timestamp": 1712000000,
                "job_required_skills": ["Python"]
            }
        ]
    }
