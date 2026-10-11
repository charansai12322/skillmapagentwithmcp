"""Unit and mock tests for RapidAPI JSearch query construction,
response normalization, deduplication, and error classification.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from app.tools.job_search import (
    build_jsearch_query,
    resolve_country_code,
    normalize_jsearch_job,
    deduplicate_jobs,
    execute_job_search,
)
from app.schemas import JobSearchStatus, JobOpportunity


# =====================================================================
# C. RAPIDAPI REQUEST-CONSTRUCTION TESTS (10 REQUIRED SCENARIOS)
# =====================================================================

def test_query_construction_generative_ai_india():
    """1. Generative AI jobs in India."""
    q_text, params = build_jsearch_query(skill="Generative AI", country="in")
    assert "Generative AI" in q_text
    assert params["country"] == "in"
    assert "job_requirements" not in params  # Unconditional filter removed


def test_query_construction_hyderabad_india():
    """2. AI engineer jobs in Hyderabad, India resolves country to 'in'."""
    q_text, params = build_jsearch_query(skill="AI Engineer", location="Hyderabad")
    assert "Hyderabad" in q_text
    assert params["country"] == "in"


def test_query_construction_explicit_us():
    """3. Explicit US job search must resolve country to 'us' and never force 'in'."""
    q_text, params = build_jsearch_query(skill="Generative AI", location="United States")
    assert params["country"] == "us"
    assert params["country"] != "in"

    q_text_sf, params_sf = build_jsearch_query(skill="Prompt Engineer", location="San Francisco")
    assert params_sf["country"] == "us"


def test_query_construction_remote_jobs():
    """4. Remote jobs sets remote_jobs_only and does not force country='in'."""
    q_text, params = build_jsearch_query(skill="Python", location="Remote", remote_only=True)
    assert params.get("remote_jobs_only") == "true"
    assert "country" not in params  # Does not force India for global remote


def test_query_construction_entry_level():
    """5. Entry-level filter applies under_3_years_experience only when requested."""
    q_text, params = build_jsearch_query(skill="Data Science", experience_level="entry")
    assert "no_experience,under_3_years_experience" in params.get("job_requirements", "")


def test_query_construction_senior_roles():
    """6. Senior roles apply more_than_3_years_experience."""
    q_text, params = build_jsearch_query(skill="Machine Learning", experience_level="senior")
    assert params.get("job_requirements") == "more_than_3_years_experience"


def test_query_construction_no_explicit_location():
    """7. Requests with no explicit location default to documented default_country."""
    q_text, params = build_jsearch_query(skill="Full Stack", location=None, default_country="in")
    assert params["country"] == "in"


def test_query_construction_unrecognized_location():
    """8. Unrecognized regional location does not force invalid country code."""
    resolved = resolve_country_code(location="Zurich", explicit_country=None, default_country="in")
    assert resolved is None


def test_query_execution_missing_credentials():
    """9. Missing RapidAPI credentials handled gracefully without raising unhandled exception."""
    jobs, status, msg = execute_job_search(skill="Python", api_key="")
    assert jobs == []
    assert status == JobSearchStatus.UNAVAILABLE
    assert "not configured" in msg


def test_query_construction_contradictory_location_and_country():
    """10. Contradictory query and filter: explicit country overrides inferred location keyword."""
    # When user explicitly specifies country="gb", it must take precedence over US in text
    q_text, params = build_jsearch_query(
        skill="Cloud Architect",
        location="Austin",
        country="gb"
    )
    assert params["country"] == "gb"


# =====================================================================
# D. RAPIDAPI RESPONSE & ERROR TESTS (MOCKED)
# =====================================================================

def test_normalize_valid_job_listing():
    """Valid raw JSearch job dictionary normalizes into structured JobOpportunity."""
    raw = {
        "job_title": "Senior AI Architect",
        "employer_name": "Google",
        "job_city": "Bengaluru",
        "job_state": "Karnataka",
        "job_country": "India",
        "job_description": "Lead design and deployment of large language models.",
        "job_employment_type": "FULLTIME",
        "job_is_remote": False,
        "job_apply_link": "https://careers.google.com/jobs/123",
        "job_min_salary": 2500000,
        "job_max_salary": 4500000,
        "job_salary_currency": "INR",
        "job_salary_period": "YEAR",
        "job_posted_at_timestamp": 1712000000,
        "job_required_skills": ["Python", "TensorFlow", "Kubernetes"]
    }
    job = normalize_jsearch_job(raw)
    assert job is not None
    assert job.title == "Senior AI Architect"
    assert job.company == "Google"
    assert "Bengaluru" in job.location
    assert job.is_remote is False
    assert "2,500,000" in job.salary
    assert job.apply_url == "https://careers.google.com/jobs/123"
    assert len(job.skills) == 3


def test_normalize_missing_optional_fields():
    """Job listing with minimal fields normalizes safely without inventing data."""
    raw = {
        "job_title": "Software Engineer",
        "employer_name": "Startup"
    }
    job = normalize_jsearch_job(raw)
    assert job is not None
    assert job.title == "Software Engineer"
    assert job.location is None
    assert job.salary is None  # Does not invent salary
    assert job.apply_url is None
    assert job.skills == []


def test_normalize_invalid_apply_url():
    """Non-HTTP/HTTPS URLs are stripped to None."""
    raw = {
        "job_title": "Engineer",
        "employer_name": "Corp",
        "job_apply_link": "javascript:alert(1)"
    }
    job = normalize_jsearch_job(raw)
    assert job.apply_url is None


def test_deduplication_removes_identical_urls_and_titles():
    """Deduplication removes duplicate listings with identical URLs or (title, company)."""
    jobs = [
        JobOpportunity(title="DevOps", company="Amazon", apply_url="https://amazon.jobs/1"),
        JobOpportunity(title="DevOps", company="Amazon", apply_url="https://amazon.jobs/1?source=indeed"),  # Canonical url matches
        JobOpportunity(title="DevOps", company="Amazon", apply_url=None),  # Title + company matches
        JobOpportunity(title="SRE", company="Amazon", apply_url="https://amazon.jobs/2"),
    ]
    deduped = deduplicate_jobs(jobs)
    assert len(deduped) == 2
    assert deduped[0].title == "DevOps"
    assert deduped[1].title == "SRE"


@patch("requests.get")
def test_mock_jsearch_success(mock_get, mock_jsearch_success_response):
    """Mock HTTP 200 response returns normalized deduplicated jobs."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_jsearch_success_response
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="AI Engineer", api_key="valid_key")
    assert status == JobSearchStatus.SUCCESS
    assert err is None
    assert len(jobs) == 2  # 3 items in fixture, 1 duplicate removed
    assert jobs[0].company == "Infosys"
    assert jobs[1].company == "TCS"


@patch("requests.get")
def test_mock_jsearch_zero_jobs(mock_get):
    """Mock HTTP 200 with empty data array returns JobSearchStatus.EMPTY."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "OK", "data": []}
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="ObscureSkill999", api_key="valid_key")
    assert status == JobSearchStatus.EMPTY
    assert jobs == []
    assert err is None


@patch("requests.get")
def test_mock_jsearch_auth_failure_401(mock_get):
    """Mock HTTP 401 returns JobSearchStatus.ERROR with auth explanation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="Python", api_key="invalid_key")
    assert status == JobSearchStatus.ERROR
    assert "authentication failed" in err.lower()


@patch("requests.get")
def test_mock_jsearch_rate_limit_429(mock_get):
    """Mock HTTP 429 returns JobSearchStatus.ERROR with rate limit explanation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.ERROR
    assert "rate limit" in err.lower()


@patch("requests.get")
def test_mock_jsearch_server_error_500(mock_get):
    """Mock HTTP 500 returns JobSearchStatus.UNAVAILABLE."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.UNAVAILABLE
    assert "unavailable" in err.lower()


@patch("requests.get")
def test_mock_jsearch_timeout(mock_get):
    """Mock requests.exceptions.Timeout returns JobSearchStatus.UNAVAILABLE."""
    mock_get.side_effect = requests.exceptions.Timeout()

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.UNAVAILABLE
    assert "timed out" in err.lower()


@patch("requests.get")
def test_mock_jsearch_connection_error(mock_get):
    """Mock requests.exceptions.ConnectionError returns JobSearchStatus.UNAVAILABLE."""
    mock_get.side_effect = requests.exceptions.ConnectionError()

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.UNAVAILABLE
    assert "failed to connect" in err.lower()


@patch("requests.get")
def test_mock_jsearch_invalid_json(mock_get):
    """Mock malformed non-JSON payload returns JobSearchStatus.ERROR."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.ERROR
    assert "failed to parse" in err.lower()


def test_jsearch_v2_constants():
    """Verify required JSearch v2 constants."""
    from app.tools.job_search import JSEARCH_BASE_URL, JSEARCH_ENDPOINT, JSEARCH_HOST
    assert JSEARCH_BASE_URL == "https://jsearch.p.rapidapi.com"
    assert JSEARCH_ENDPOINT == "https://jsearch.p.rapidapi.com/search-v2"
    assert JSEARCH_HOST == "jsearch.p.rapidapi.com"


@patch("requests.get")
def test_execute_job_search_calls_v2_endpoint_and_headers(mock_get):
    """Verify execute_job_search calls /search-v2 with X-RapidAPI-Host and X-RapidAPI-Key."""
    from app.tools.job_search import JSEARCH_ENDPOINT, JSEARCH_HOST

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "OK",
        "data": {
            "jobs": [
                {
                    "job_title": "Full Stack Engineer",
                    "employer_name": "Acme Corp",
                    "job_city": "Chicago",
                    "job_country": "US",
                    "job_apply_link": "https://example.com/apply",
                }
            ]
        }
    }
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(
        skill="developer jobs",
        location="Chicago",
        country="us",
        api_key="mock_secret_key"
    )

    assert status == JobSearchStatus.SUCCESS
    assert len(jobs) == 1
    assert jobs[0].title == "Full Stack Engineer"
    assert jobs[0].company == "Acme Corp"
    assert jobs[0].apply_url == "https://example.com/apply"

    # Verify request call args
    call_args = mock_get.call_args
    assert call_args[0][0] == JSEARCH_ENDPOINT
    headers = call_args[1]["headers"]
    assert headers["X-RapidAPI-Host"] == JSEARCH_HOST
    assert headers["X-RapidAPI-Key"] == "mock_secret_key"
    params = call_args[1]["params"]
    assert "developer jobs" in params["query"]
    assert params["num_pages"] == "1"
    assert params["date_posted"] == "all"
    assert params["country"] == "us"


@patch("requests.get")
def test_mock_jsearch_v2_nested_data_jobs_empty(mock_get):
    """Verify /search-v2 nested schema with empty jobs list returns JobSearchStatus.EMPTY."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "OK",
        "data": {"jobs": []}
    }
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="UnknownRole", api_key="valid_key")
    assert status == JobSearchStatus.EMPTY
    assert jobs == []
    assert err is None


@patch("requests.get")
def test_mock_jsearch_404_handling(mock_get):
    """Verify HTTP 404 returns JobSearchStatus.UNAVAILABLE."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    jobs, status, err = execute_job_search(skill="Python", api_key="valid_key")
    assert status == JobSearchStatus.UNAVAILABLE
    assert "404" in err

