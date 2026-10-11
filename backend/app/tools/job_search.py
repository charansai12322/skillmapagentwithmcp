"""Repaired and production-ready RapidAPI JSearch integration.

Removes hardcoded country/experience contradictions, validates request
construction, gracefully handles network failures, normalizes schema fields,
and deduplicates job listings.
"""

import re
import datetime
import requests
from typing import List, Optional, Dict, Any, Tuple
from app.schemas import JobOpportunity, JobSearchStatus
from app.config import get_settings


# RapidAPI JSearch Service Constants
JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com"
JSEARCH_ENDPOINT = "https://jsearch.p.rapidapi.com/search-v2"
JSEARCH_HOST = "jsearch.p.rapidapi.com"


INDIA_LOCATION_KEYWORDS = {
    "india", "in", "bengaluru", "bangalore", "hyderabad", "delhi", "new delhi",
    "mumbai", "pune", "chennai", "gurgaon", "gurugram", "noida", "kolkata", "ahmedabad"
}

US_LOCATION_KEYWORDS = {
    "united states", "us", "usa", "san francisco", "new york", "nyc", "seattle",
    "austin", "california", "texas", "boston", "chicago", "los angeles", "ny", "ca", "wa"
}


def resolve_country_code(
    location: Optional[str] = None,
    explicit_country: Optional[str] = None,
    default_country: str = "in"
) -> Optional[str]:
    """Resolves the appropriate 2-letter country code without contradiction.

    1. If explicit_country is provided, normalizes and respects it.
    2. If location contains clear geographic signals (India or US keywords), resolves accordingly.
    3. If location explicitly indicates 'remote' without a country, returns None (global/remote).
    4. If no location or country is specified, defaults to default_country.
    """
    if explicit_country:
        cleaned = explicit_country.strip().lower()
        if re.match(r"^[a-z]{2}$", cleaned):
            return cleaned

    if not location:
        return default_country

    loc_lower = location.strip().lower()

    # Check for pure remote indicator
    if loc_lower == "remote":
        return None

    # Check India keywords
    for kw in INDIA_LOCATION_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", loc_lower):
            return "in"

    # Check US keywords
    for kw in US_LOCATION_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", loc_lower):
            return "us"

    # If location is given but doesn't match known presets, don't force India
    return None


def build_jsearch_query(
    skill: str,
    location: Optional[str] = None,
    country: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_only: Optional[bool] = False,
    page: int = 1,
    default_country: str = "in"
) -> Tuple[str, Dict[str, str]]:
    """Builds an accurate, non-contradictory querystring for JSearch API.

    Returns:
        Tuple of (formatted_query_text, querystring_params_dict)
    """
    cleaned_skill = skill.strip()
    resolved_country = resolve_country_code(location, country, default_country)

    # Build natural query string
    if location and location.strip().lower() != "remote":
        # Avoid duplicate "in <location>" if already present in skill
        if location.lower() in cleaned_skill.lower():
            query_text = cleaned_skill
        else:
            query_text = f"{cleaned_skill} in {location.strip()}"
    elif remote_only or (location and location.strip().lower() == "remote"):
        if "remote" not in cleaned_skill.lower():
            query_text = f"{cleaned_skill} remote"
        else:
            query_text = cleaned_skill
    else:
        query_text = cleaned_skill

    params: Dict[str, str] = {
        "query": query_text,
        "page": str(max(1, page)),
        "num_pages": "1",
        "date_posted": "all",
    }

    if resolved_country:
        params["country"] = resolved_country

    if remote_only or (location and location.strip().lower() == "remote"):
        params["remote_jobs_only"] = "true"

    # Apply experience filters only when explicitly requested
    if experience_level:
        exp_clean = experience_level.lower().strip()
        if exp_clean in ("entry", "no_experience", "entry_level"):
            params["job_requirements"] = "no_experience,under_3_years_experience"
        elif exp_clean in ("senior", "lead", "principal"):
            params["job_requirements"] = "more_than_3_years_experience"

    return query_text, params


def normalize_jsearch_job(raw_job: Dict[str, Any]) -> Optional[JobOpportunity]:
    """Extracts, validates, and normalizes a single JSearch job item."""
    if not isinstance(raw_job, dict):
        return None

    title = raw_job.get("job_title")
    company = raw_job.get("employer_name")
    if not title or not company:
        return None

    # Construct clean location
    loc_parts = []
    if raw_job.get("job_city"):
        loc_parts.append(raw_job.get("job_city"))
    if raw_job.get("job_state"):
        loc_parts.append(raw_job.get("job_state"))
    if raw_job.get("job_country"):
        loc_parts.append(raw_job.get("job_country"))

    location_str = ", ".join(loc_parts) if loc_parts else None
    if raw_job.get("job_is_remote") and not location_str:
        location_str = "Remote"

    # Validate apply URL
    apply_link = raw_job.get("job_apply_link")
    if apply_link and not (apply_link.startswith("http://") or apply_link.startswith("https://")):
        apply_link = None

    # Salary formatting
    salary_str = None
    min_sal = raw_job.get("job_min_salary")
    max_sal = raw_job.get("job_max_salary")
    currency = raw_job.get("job_salary_currency") or "USD"
    salary_period = raw_job.get("job_salary_period") or "YEAR"
    if min_sal and max_sal:
        salary_str = f"{min_sal:,.0f} - {max_sal:,.0f} {currency}/{salary_period.lower()}"
    elif min_sal:
        salary_str = f"From {min_sal:,.0f} {currency}/{salary_period.lower()}"
    elif max_sal:
        salary_str = f"Up to {max_sal:,.0f} {currency}/{salary_period.lower()}"

    # Posting timestamp
    posted_at = None
    posted_ts = raw_job.get("job_posted_at_timestamp")
    if posted_ts and isinstance(posted_ts, (int, float)):
        try:
            posted_at = datetime.datetime.fromtimestamp(posted_ts, tz=datetime.timezone.utc).isoformat()
        except Exception:
            posted_at = None

    # Description snippet
    desc = raw_job.get("job_description")
    desc_snippet = None
    if desc and isinstance(desc, str):
        clean_desc = re.sub(r"\s+", " ", desc).strip()
        desc_snippet = clean_desc[:300] + ("..." if len(clean_desc) > 300 else "")

    # Required skills
    skills_raw = raw_job.get("job_required_skills")
    skills = []
    if isinstance(skills_raw, list):
        skills = [str(s).strip() for s in skills_raw if s and str(s).strip()]

    return JobOpportunity(
        title=str(title).strip(),
        company=str(company).strip(),
        location=location_str,
        description=desc_snippet,
        employment_type=raw_job.get("job_employment_type"),
        is_remote=bool(raw_job.get("job_is_remote")),
        salary=salary_str,
        posted_at=posted_at,
        apply_url=apply_link,
        skills=skills,
        source="RAPIDAPI_JSEARCH",
    )


def deduplicate_jobs(jobs: List[JobOpportunity]) -> List[JobOpportunity]:
    """Deduplicates job listings using canonical application URL, with title+company fallback."""
    seen_urls = set()
    seen_tuples = set()
    deduped = []

    for job in jobs:
        # Check URL key
        if job.apply_url:
            canonical_url = job.apply_url.split("?")[0].rstrip("/").lower()
            if canonical_url in seen_urls:
                continue
            seen_urls.add(canonical_url)

        # Check title + company key
        tuple_key = (job.title.lower().strip(), job.company.lower().strip())
        if tuple_key in seen_tuples:
            continue
        seen_tuples.add(tuple_key)

        deduped.append(job)

    return deduped


def execute_job_search(
    skill: str,
    location: Optional[str] = None,
    country: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_only: Optional[bool] = False,
    page: int = 1,
    api_key: Optional[str] = None,
    timeout: Optional[float] = None
) -> Tuple[List[JobOpportunity], JobSearchStatus, Optional[str]]:
    """Executes a validated search against RapidAPI JSearch.

    Returns:
        Tuple of (List[JobOpportunity], JobSearchStatus, Optional[error_or_warning_message])
    """
    settings = get_settings()
    key = settings.RAPIDAPI_KEY if api_key is None else api_key
    if not key or not key.strip():
        return [], JobSearchStatus.UNAVAILABLE, "RapidAPI key is not configured on the server."

    request_timeout = timeout or settings.REQUEST_TIMEOUT_SECONDS
    query_text, params = build_jsearch_query(
        skill=skill,
        location=location,
        country=country,
        experience_level=experience_level,
        remote_only=remote_only,
        page=page,
        default_country=settings.DEFAULT_COUNTRY
    )

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }

    endpoint = settings.RAPIDAPI_URL or JSEARCH_ENDPOINT

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=request_timeout
        )

        if response.status_code in (401, 403):
            return [], JobSearchStatus.ERROR, f"RapidAPI authentication failed ({response.status_code}). Check subscription."
        elif response.status_code == 429:
            return [], JobSearchStatus.ERROR, "RapidAPI rate limit or quota exceeded (429)."
        elif response.status_code >= 500:
            return [], JobSearchStatus.UNAVAILABLE, f"RapidAPI upstream service unavailable ({response.status_code})."
        elif response.status_code == 404:
            return [], JobSearchStatus.UNAVAILABLE, "RapidAPI JSearch endpoint returned 404 (verify endpoint permissions on RapidAPI)."
        elif response.status_code != 200:
            return [], JobSearchStatus.ERROR, f"RapidAPI returned unexpected status code {response.status_code}."

        try:
            data = response.json()
        except Exception:
            return [], JobSearchStatus.ERROR, "Failed to parse RapidAPI JSON response."

        # Extract jobs supporting /search-v2 ({data: {jobs: [...]}}) and legacy ({data: [...]})
        data_field = data.get("data") if isinstance(data, dict) else None
        if isinstance(data_field, dict):
            raw_jobs = data_field.get("jobs", [])
        elif isinstance(data_field, list):
            raw_jobs = data_field
        elif "jobs" in data and isinstance(data.get("jobs"), list):
            raw_jobs = data["jobs"]
        else:
            raw_jobs = []

        if not raw_jobs:
            return [], JobSearchStatus.EMPTY, None

        normalized_jobs = []
        for rj in raw_jobs:
            job_obj = normalize_jsearch_job(rj)
            if job_obj:
                normalized_jobs.append(job_obj)

        deduped = deduplicate_jobs(normalized_jobs)
        if not deduped:
            return [], JobSearchStatus.EMPTY, None

        return deduped, JobSearchStatus.SUCCESS, None

    except requests.exceptions.Timeout:
        return [], JobSearchStatus.UNAVAILABLE, f"RapidAPI request timed out after {request_timeout}s."
    except requests.exceptions.ConnectionError:
        return [], JobSearchStatus.UNAVAILABLE, "Failed to connect to RapidAPI host."
    except Exception as e:
        return [], JobSearchStatus.ERROR, f"Unexpected error during RapidAPI request: {str(e)}"


def get_langchain_job_search_tool():
    """Builds a LangChain tool wrapper preserving the notebook's tool signature.

    Returns the @tool callable suitable for create_agent.
    """
    try:
        from langchain.tools import tool

        @tool
        def search_jobs(skill: str, location: str = "") -> list:
            """Search for jobs requiring a specific skill using JSearch API from RapidAPI.

            Args:
                skill: The technology, role, or programming skill.
                location: City, country, or 'Remote'.
            """
            jobs, status, err = execute_job_search(skill=skill, location=location)
            result = []
            for j in jobs:
                result.append({
                    "title": j.title,
                    "company": j.company,
                    "location": j.location or "Not specified",
                    "apply_link": j.apply_url or "Not available",
                    "salary": j.salary or "Not disclosed",
                    "employment_type": j.employment_type or "Full-time"
                })
            return result

        return search_jobs
    except ImportError:
        # Fallback if langchain is not present
        def search_jobs(skill: str, location: str = "") -> list:
            jobs, status, err = execute_job_search(skill=skill, location=location)
            return [j.model_dump() for j in jobs]
        return search_jobs
