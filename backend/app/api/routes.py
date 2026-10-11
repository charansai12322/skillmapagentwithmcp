"""FastAPI route definitions for SkillMap AI.

Provides GET /api/health and POST /api/query endpoints with structured
response schemas and centralized error translation.
"""

import datetime
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.schemas import (
    SkillQueryRequest,
    SkillQueryResponse,
    HealthResponse,
    ErrorResponse,
)
from app.config import get_settings
from app.services.skillmap_service import SkillMapService
from app.utils.errors import SkillMapError

router = APIRouter(prefix="/api", tags=["SkillMap Intelligence"])
service = SkillMapService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns service vitality without triggering external API calls or exposing secrets."
)
async def health_check():
    settings = get_settings()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=now_iso,
        services={
            "gemini": "configured" if settings.has_gemini_key else "missing",
            "rapidapi": "configured" if settings.has_rapidapi_key else "missing",
            "composio": "configured" if settings.has_composio_key else "missing",
            "tavily": "configured" if settings.has_tavily_key else "not_configured",
        }
    )


@router.post(
    "/query",
    response_model=SkillQueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        502: {"model": ErrorResponse, "description": "Upstream service error"},
    },
    summary="Submit natural language skill & job inquiry",
    description="Analyzes skill demand, retrieves live verified job openings, and synthesizes salary benchmarks."
)
async def query_skill_intelligence(request: SkillQueryRequest):
    try:
        response = await service.process_query(request)
        return response
    except SkillMapError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(
                error=True,
                code=e.code,
                message=e.message,
                details=e.details,
            ).model_dump()
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=True,
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred while processing the request.",
            ).model_dump()
        )
