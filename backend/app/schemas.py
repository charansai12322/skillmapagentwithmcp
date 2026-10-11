"""Pydantic request and response schemas for SkillMap AI.

Provides strict data validation, predictable JSON serialization,
and explicit source attribution without inventing unavailable data.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"


class JobSearchStatus(str, Enum):
    SUCCESS = "success"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class SkillQueryRequest(BaseModel):
    """User query request payload."""
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language question regarding skills, demand, or jobs.",
        examples=["What is the demand for Generative AI in the industry, and what jobs are open in India?"]
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional city, state, or regional preference (e.g., 'Bengaluru', 'San Francisco', 'Remote')."
    )
    country: Optional[str] = Field(
        default=None,
        max_length=5,
        description="Optional 2-letter ISO country code (e.g., 'in', 'us', 'gb', 'ca')."
    )
    experience_level: Optional[ExperienceLevel] = Field(
        default=None,
        description="Optional filter for candidate experience level ('entry', 'mid', 'senior')."
    )
    remote_only: Optional[bool] = Field(
        default=False,
        description="Whether to restrict search strictly to remote opportunities."
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty or whitespace only.")
        return cleaned

    @field_validator("country")
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip().lower()
        if not re.match(r"^[a-z]{2}$", cleaned):
            raise ValueError("Country must be a 2-letter ISO country code (e.g., 'in', 'us').")
        return cleaned


class JobOpportunity(BaseModel):
    """Normalized, deduplicated job listing schema."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Employer name")
    location: Optional[str] = Field(default=None, description="City, region, or 'Remote'")
    description: Optional[str] = Field(default=None, description="Brief description or preview snippet")
    employment_type: Optional[str] = Field(default=None, description="e.g. FULLTIME, CONTRACTOR, INTERN")
    experience_level: Optional[str] = Field(default=None, description="e.g. Entry-level, Senior, Not Specified")
    is_remote: Optional[bool] = Field(default=False, description="Whether position is flagged as remote")
    salary: Optional[str] = Field(default=None, description="Reported salary range if available from provider")
    posted_at: Optional[str] = Field(default=None, description="Date/timestamp listing was published")
    apply_url: Optional[str] = Field(default=None, description="Direct application link verified as http/https")
    skills: List[str] = Field(default_factory=list, description="Explicit skills mentioned in listing")
    source: str = Field(
        default="RAPIDAPI_JSEARCH",
        description="Identifies retrieval origin: RAPIDAPI_JSEARCH | COMPOSIO_WEB_SEARCH | SYNTHESIZED"
    )


class IndustryOverview(BaseModel):
    """Industry demand assessment and growth summary."""
    summary: str = Field(..., description="Concise assessment of industry demand")
    demand_level: Optional[str] = Field(
        default="HIGH",
        description="Demand ranking: HIGH | MODERATE | LOW | EMERGING"
    )
    growth_metrics: Optional[str] = Field(
        default=None,
        description="Verifiable growth statistics or citation notes"
    )


class SalaryInsights(BaseModel):
    """Verified market compensation figures."""
    currency: str = Field(default="USD", description="Currency code (USD, INR, EUR, etc.)")
    entry_level: Optional[str] = Field(default=None, description="Entry level base or total compensation")
    median: Optional[str] = Field(default=None, description="Median salary range")
    senior: Optional[str] = Field(default=None, description="Senior / staff compensation")
    notes: Optional[str] = Field(default=None, description="Contextual compensation notes or source")


class SourceAttribution(BaseModel):
    """Attribution details for retrieved facts."""
    name: str = Field(..., description="Provider or site name (e.g. RapidAPI JSearch, Greenhouse, Lever)")
    url: Optional[str] = Field(default=None, description="Origin URL where factual claim was retrieved")
    retrieved_at: Optional[str] = Field(default=None, description="ISO timestamp of data retrieval")


class ResponseMetadata(BaseModel):
    """Diagnostics and performance tracking metadata."""
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    timestamp: str = Field(..., description="ISO 8601 response timestamp")
    tools_invoked: List[str] = Field(default_factory=list, description="Names of tools called during reasoning")
    job_results_count: int = Field(default=0, description="Number of job opportunities returned")
    job_search_status: JobSearchStatus = Field(
        default=JobSearchStatus.SUCCESS,
        description="Retrieval status: success | empty | unavailable | error"
    )


class SkillQueryResponse(BaseModel):
    """Main API response contract for SkillMap AI frontend."""
    request_id: str = Field(..., description="Unique UUID for request tracing")
    query: str = Field(..., description="Original user query")
    status: str = Field(default="SUCCESS", description="SUCCESS | PARTIAL_SUCCESS | ERROR")
    industry_overview: Optional[IndustryOverview] = Field(default=None)
    salary_insights: Optional[SalaryInsights] = Field(default=None)
    key_skills: List[str] = Field(default_factory=list, description="Key skills identified by intelligence")
    job_opportunities: List[JobOpportunity] = Field(default_factory=list, description="List of matching jobs")
    sources: List[SourceAttribution] = Field(default_factory=list, description="Attributed citations & data sources")
    warnings: List[str] = Field(default_factory=list, description="Notices about partial or degraded data sources")
    metadata: ResponseMetadata = Field(..., description="Diagnostic metadata")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    timestamp: str = Field(...)
    services: Dict[str, str] = Field(
        ...,
        description="Configuration status of external dependencies ('configured' | 'missing')"
    )


class ErrorResponse(BaseModel):
    """Centralized machine-readable error response schema."""
    error: bool = Field(default=True)
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Safe human-readable explanation")
    request_id: Optional[str] = Field(default=None)
    details: Optional[Dict[str, Any]] = Field(default=None)
