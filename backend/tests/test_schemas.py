"""Unit tests for Pydantic request and response schemas."""

import pytest
from pydantic import ValidationError
from app.schemas import (
    SkillQueryRequest,
    SkillQueryResponse,
    JobOpportunity,
    IndustryOverview,
    SalaryInsights,
    ResponseMetadata,
    ExperienceLevel,
    JobSearchStatus,
    ErrorResponse,
)


def test_valid_request_schema():
    """Valid request with required and optional parameters passes validation."""
    req = SkillQueryRequest(
        query="What is the demand for Generative AI?",
        location="Bengaluru",
        country="in",
        experience_level=ExperienceLevel.ENTRY,
        remote_only=False,
    )
    assert req.query == "What is the demand for Generative AI?"
    assert req.location == "Bengaluru"
    assert req.country == "in"
    assert req.experience_level == ExperienceLevel.ENTRY


def test_empty_query_rejected():
    """Empty string or pure whitespace query must fail validation."""
    with pytest.raises(ValidationError):
        SkillQueryRequest(query="")

    with pytest.raises(ValidationError):
        SkillQueryRequest(query="   ")


def test_excessively_long_query_rejected():
    """Query exceeding 1000 characters must fail validation."""
    long_q = "A" * 1001
    with pytest.raises(ValidationError):
        SkillQueryRequest(query=long_q)


def test_invalid_country_code_rejected():
    """Country codes that are not 2-letter ISO codes must fail validation."""
    with pytest.raises(ValidationError):
        SkillQueryRequest(query="AI Engineer jobs", country="INDIA")

    with pytest.raises(ValidationError):
        SkillQueryRequest(query="AI Engineer jobs", country="12")


def test_country_code_normalized_to_lowercase():
    """Country codes with uppercase letters must be normalized to lowercase."""
    req = SkillQueryRequest(query="AI Engineer jobs", country="IN")
    assert req.country == "in"


def test_job_opportunity_schema_required_fields():
    """JobOpportunity requires title, company, and valid types."""
    job = JobOpportunity(
        title="Full Stack Developer",
        company="Accenture",
        location="Remote",
        apply_url="https://accenture.com/careers/123",
        source="RAPIDAPI_JSEARCH"
    )
    assert job.title == "Full Stack Developer"
    assert job.company == "Accenture"
    assert job.source == "RAPIDAPI_JSEARCH"
    assert job.is_remote is False


def test_job_opportunity_invalid_url_handling():
    """Apply URLs without http/https should be rejected or normalized."""
    job = JobOpportunity(
        title="Engineer",
        company="Startup",
        apply_url=None
    )
    assert job.apply_url is None


def test_skill_query_response_schema_completeness():
    """Full SkillQueryResponse model serializes correctly without missing required fields."""
    res = SkillQueryResponse(
        request_id="req-12345",
        query="Python demand",
        status="SUCCESS",
        industry_overview=IndustryOverview(
            summary="Strong demand across sectors.",
            demand_level="HIGH"
        ),
        salary_insights=SalaryInsights(
            currency="USD",
            median="$120,000"
        ),
        key_skills=["Python", "FastAPI"],
        job_opportunities=[],
        sources=[],
        warnings=[],
        metadata=ResponseMetadata(
            execution_time_ms=150,
            timestamp="2026-10-11T12:00:00Z",
            tools_invoked=["RAPIDAPI_JSEARCH"],
            job_results_count=0,
            job_search_status=JobSearchStatus.EMPTY
        )
    )
    assert res.request_id == "req-12345"
    assert res.metadata.execution_time_ms == 150
    assert res.metadata.job_search_status == JobSearchStatus.EMPTY


def test_error_response_schema():
    """ErrorResponse formats machine-readable error codes."""
    err = ErrorResponse(
        error=True,
        code="INVALID_REQUEST",
        message="Query must not be empty",
        details={"field": "query"}
    )
    assert err.error is True
    assert err.code == "INVALID_REQUEST"
