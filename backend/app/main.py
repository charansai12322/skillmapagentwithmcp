"""Main FastAPI application entry point for SkillMap AI.

Configures application lifecycle, CORS middleware, centralized exception
handling, and OpenAPI documentation routes.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.api.routes import router as api_router
from app.schemas import ErrorResponse
from app.utils.errors import SkillMapError

settings = get_settings()

app = FastAPI(
    title="SkillMap AI Backend API",
    description="Intelligence engine for technology skill demand, salary benchmarks, and verified job discovery.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors into standardized machine-readable responses."""
    errors = exc.errors()
    clean_errors = []
    for err in errors:
        clean_errors.append({
            "loc": [str(loc) for loc in err.get("loc", [])],
            "msg": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=True,
            code="VALIDATION_ERROR",
            message="Request parameters failed validation.",
            details={"errors": clean_errors},
        ).model_dump()
    )


@app.exception_handler(SkillMapError)
async def custom_skillmap_exception_handler(request: Request, exc: SkillMapError):
    """Centralized handler for typed domain errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=True,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ).model_dump()
    )


@app.get("/", tags=["Root"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": "SkillMap AI Backend API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
