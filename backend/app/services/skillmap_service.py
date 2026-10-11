"""Service layer coordinating input validation, agent execution,
and structured output normalization.
"""

import time
import uuid
import re
import datetime
from typing import List, Optional, Tuple, Dict, Any

from app.schemas import (
    SkillQueryRequest,
    SkillQueryResponse,
    IndustryOverview,
    SalaryInsights,
    JobOpportunity,
    SourceAttribution,
    ResponseMetadata,
    JobSearchStatus,
)
from app.config import get_settings
from app.agent.skill_agent import SkillAgentRunner
from app.tools.job_search import execute_job_search, deduplicate_jobs
from app.utils.errors import ConfigurationError


def extract_skill_keyword(query: str) -> str:
    """Heuristic extraction of the core technology or skill from a natural query."""
    # Common tech patterns
    patterns = [
        r"(?:demand for|skills? in|jobs? in|careers? in|openings? for|learning)\s+([A-Za-z0-9\s\+\#\.\-]+?)(?:\s+(?:in|for|and|at|with|\?|$))",
        r"(Generative AI|GenAI|Machine Learning|Deep Learning|Data Science|Python|React|Java|DevOps|Cloud|Full Stack|Kubernetes)",
    ]
    for p in patterns:
        m = re.search(p, query, re.IGNORECASE)
        if m:
            extracted = m.group(1).strip()
            if len(extracted) > 1:
                return extracted
    # Fallback: clean words
    cleaned = re.sub(r"[^\w\s]", "", query)
    words = [w for w in cleaned.split() if len(w) > 2 and w.lower() not in {"what", "the", "for", "and", "are", "which", "available"}]
    return " ".join(words[:3]) if words else query.strip()


def parse_agent_text_response(text: str) -> Tuple[Optional[IndustryOverview], Optional[SalaryInsights], List[str], List[JobOpportunity]]:
    """Normalizes the agent's free-form output into structured models without fragile breakage."""
    overview: Optional[IndustryOverview] = None
    salaries: Optional[SalaryInsights] = None
    skills: List[str] = []
    scraped_jobs: List[JobOpportunity] = []

    # Section extraction using regex boundaries
    sec_overview = re.search(
        r"(?:INDUSTRY DEMAND OVERVIEW|DEMAND OVERVIEW|INDUSTRY OVERVIEW)[:\n]+(.*?)(?=(?:SALARY INSIGHTS|CAREER TRENDS|KEY SKILLS|ACTIVE JOB|JOB OPPORTUNITIES|\Z))",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if sec_overview:
        content = sec_overview.group(1).strip()
        if content:
            demand_level = "HIGH"
            if re.search(r"\b(growing|high|massive|rapid|strong)\b", content, re.IGNORECASE):
                demand_level = "HIGH"
            elif re.search(r"\b(moderate|steady)\b", content, re.IGNORECASE):
                demand_level = "MODERATE"
            overview = IndustryOverview(summary=content[:600], demand_level=demand_level)

    sec_salaries = re.search(
        r"(?:SALARY INSIGHTS|COMPENSATION|SALARY)[:\n]+(.*?)(?=(?:CAREER TRENDS|KEY SKILLS|ACTIVE JOB|JOB OPPORTUNITIES|\Z))",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if sec_salaries:
        sal_content = sec_salaries.group(1).strip()
        median_match = re.search(r"(?:median|average|typical)[^\n\:]*?[:\-]\s*([^\n\.]+)", sal_content, re.IGNORECASE)
        senior_match = re.search(r"(?:senior|lead|architect)[^\n\:]*?[:\-]\s*([^\n\.]+)", sal_content, re.IGNORECASE)
        entry_match = re.search(r"(?:entry|junior)[^\n\:]*?[:\-]\s*([^\n\.]+)", sal_content, re.IGNORECASE)

        salaries = SalaryInsights(
            currency="USD" if "$" in sal_content else "INR" if ("₹" in sal_content or "INR" in sal_content or "LPA" in sal_content) else "USD",
            entry_level=entry_match.group(1).strip() if entry_match else None,
            median=median_match.group(1).strip() if median_match else (sal_content[:150] if not senior_match else None),
            senior=senior_match.group(1).strip() if senior_match else None,
            notes=sal_content[:300] if not (median_match or senior_match) else None
        )

    sec_skills = re.search(
        r"(?:KEY SKILLS|CAREER TRENDS & KEY SKILLS|SKILLS)[:\n]+(.*?)(?=(?:ACTIVE JOB|JOB OPPORTUNITIES|\Z))",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if sec_skills:
        skill_content = sec_skills.group(1).strip()
        # Look for numbered items or bullet points
        items = re.findall(r"(?:^|\n)\s*(?:[0-9]+[\.\)]|[\-\*\•])\s*([^\n]+)", skill_content)
        if items:
            skills = [re.sub(r"^[:\s]+", "", i).strip() for i in items if len(i.strip()) > 2][:10]

    # Look for fallback job listings in text
    job_blocks = re.findall(
        r"(?:^|\n)(?:[0-9]+\.|\*)\s*([^\n]+)\nCompany:\s*([^\n]+)\nLocation:\s*([^\n]+)(?:.*?(?:Apply Link|Apply|Link):\s*(https?://[^\s\)]+))?",
        text,
        re.DOTALL | re.IGNORECASE
    )
    for title, company, loc, apply_url in job_blocks:
        scraped_jobs.append(
            JobOpportunity(
                title=title.strip(),
                company=company.strip(),
                location=loc.strip(),
                apply_url=apply_url.strip() if apply_url else None,
                source="COMPOSIO_WEB_SEARCH"
            )
        )

    # Fallback if overview wasn't parsed into a structured section
    if not overview and text:
        first_para = text.split("\n\n")[0].strip()
        overview = IndustryOverview(summary=first_para[:600] if first_para else "Market demand analysis synthesized.", demand_level="HIGH")

    return overview, salaries, skills, scraped_jobs


class SkillMapService:
    """Coordinates query orchestration, execution timing, and response construction."""

    def __init__(self):
        self.settings = get_settings()
        self.runner = SkillAgentRunner()

    async def process_query(self, request: SkillQueryRequest) -> SkillQueryResponse:
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        warnings: List[str] = []
        tools_invoked: List[str] = []
        sources: List[SourceAttribution] = []

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        skill_keyword = extract_skill_keyword(request.query)

        agent_text = ""
        # 1. Attempt agent execution if Gemini key is present
        if self.settings.has_gemini_key:
            try:
                agent_res = await self.runner.execute(
                    query=request.query,
                    location=request.location,
                    country=request.country,
                    experience_level=request.experience_level.value if request.experience_level else None,
                    remote_only=request.remote_only,
                )
                agent_text = agent_res.get("final_text", "")
                tools_invoked.extend(agent_res.get("tools_invoked", []))
                warnings.extend(agent_res.get("warnings", []))
            except Exception as e:
                warnings.append(f"AI Agent reasoning degraded ({str(e)}); falling back to direct job intelligence retrieval.")
        else:
            warnings.append("GEMINI_API_KEY is not configured on the server. AI reasoning synthesis was skipped.")

        # 2. Parse model generated sections
        overview, salaries, key_skills, scraped_jobs = parse_agent_text_response(agent_text)

        # 3. Direct verified RapidAPI JSearch call to guarantee structured job cards
        rapid_jobs: List[JobOpportunity] = []
        job_search_status = JobSearchStatus.EMPTY
        if self.settings.has_rapidapi_key:
            rapid_jobs, job_search_status, search_err = execute_job_search(
                skill=skill_keyword,
                location=request.location,
                country=request.country,
                experience_level=request.experience_level.value if request.experience_level else None,
                remote_only=request.remote_only,
                api_key=self.settings.RAPIDAPI_KEY,
                timeout=self.settings.REQUEST_TIMEOUT_SECONDS
            )
            if rapid_jobs:
                tools_invoked.append("RAPIDAPI_JSEARCH")
                sources.append(SourceAttribution(name="RapidAPI JSearch", url=self.settings.RAPIDAPI_URL, retrieved_at=now_iso))
            if search_err:
                warnings.append(f"RapidAPI Notice: {search_err}")
        else:
            warnings.append("RAPIDAPI_KEY is not configured on the server. Live job retrieval was skipped.")
            job_search_status = JobSearchStatus.UNAVAILABLE

        # Combine and deduplicate job opportunities (RapidAPI preferred, fallback to web-scraped)
        all_jobs = deduplicate_jobs(rapid_jobs + scraped_jobs)

        # Add Composio source attribution if scraped jobs exist or tool was invoked
        if scraped_jobs or "COMPOSIO_MCP" in tools_invoked:
            sources.append(SourceAttribution(name="Web Search via Composio", url="https://connect.composio.dev/mcp", retrieved_at=now_iso))

        # Add Tavily source attribution if invoked
        if "TAVILY_SEARCH" in tools_invoked:
            sources.append(SourceAttribution(name="Tavily AI Search", url="https://tavily.com", retrieved_at=now_iso))


        # Build fallback overview if still empty
        if not overview:
            overview = IndustryOverview(
                summary=f"Demand research for '{skill_keyword}'. High interest across technology and industry roles.",
                demand_level="HIGH"
            )

        if not key_skills and skill_keyword:
            key_skills = [skill_keyword, "Problem Solving", "System Architecture"]

        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        metadata = ResponseMetadata(
            execution_time_ms=execution_time_ms,
            timestamp=now_iso,
            tools_invoked=list(set(tools_invoked)),
            job_results_count=len(all_jobs),
            job_search_status=job_search_status,
        )

        return SkillQueryResponse(
            request_id=request_id,
            query=request.query,
            status="SUCCESS" if not warnings else "PARTIAL_SUCCESS",
            industry_overview=overview,
            salary_insights=salaries,
            key_skills=key_skills,
            job_opportunities=all_jobs,
            sources=sources,
            warnings=warnings,
            metadata=metadata,
        )
