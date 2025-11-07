"""
Performance-optimized main FastAPI application.
Includes caching, compression, rate limiting, and database pooling.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from core.config import settings
from api import (
    auth, manuscripts, users, reviews, themes, copyediting,
    production, issues, discussions, export, crossref,
    ai_features, metrics, datacite, websocket, ab_testing,
    personalization, analytics
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG
)

# Add limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# GZip compression middleware (responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
)

# Performance monitoring middleware
@app.middleware("http")
async def add_performance_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Cache control middleware for static responses
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)

    # Cache public endpoints
    if request.url.path.startswith(f"{settings.API_V1_PREFIX}/themes"):
        response.headers["Cache-Control"] = "public, max-age=3600"  # 1 hour
    elif request.url.path.startswith(f"{settings.API_V1_PREFIX}/articles"):
        response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
    elif request.url.path.startswith(f"{settings.API_V1_PREFIX}/issues"):
        response.headers["Cache-Control"] = "public, max-age=600"  # 10 minutes

    return response

# Include routers with rate limiting
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"]
)
app.include_router(
    manuscripts.router,
    prefix=f"{settings.API_V1_PREFIX}/manuscripts",
    tags=["Manuscripts"]
)
app.include_router(
    reviews.router,
    prefix=f"{settings.API_V1_PREFIX}/reviews",
    tags=["Reviews"]
)
app.include_router(
    themes.router,
    prefix=f"{settings.API_V1_PREFIX}/themes",
    tags=["Themes"]
)
app.include_router(
    copyediting.router,
    prefix=f"{settings.API_V1_PREFIX}/copyediting",
    tags=["Copyediting"]
)
app.include_router(
    production.router,
    prefix=f"{settings.API_V1_PREFIX}/production",
    tags=["Production"]
)
app.include_router(
    issues.router,
    prefix=f"{settings.API_V1_PREFIX}/issues",
    tags=["Issues"]
)
app.include_router(
    discussions.router,
    prefix=f"{settings.API_V1_PREFIX}/discussions",
    tags=["Discussions"]
)
app.include_router(
    export.router,
    prefix=f"{settings.API_V1_PREFIX}/export",
    tags=["Export"]
)
app.include_router(
    crossref.router,
    prefix=f"{settings.API_V1_PREFIX}/crossref",
    tags=["Crossref"]
)
app.include_router(
    datacite.router,
    prefix=f"{settings.API_V1_PREFIX}/datacite",
    tags=["DataCite"]
)
app.include_router(
    ai_features.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["AI Features"]
)
app.include_router(
    metrics.router,
    prefix=f"{settings.API_V1_PREFIX}/metrics",
    tags=["Metrics"]
)
app.include_router(
    websocket.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["WebSocket"]
)
app.include_router(
    ab_testing.router,
    prefix=f"{settings.API_V1_PREFIX}/ab-testing",
    tags=["A/B Testing"]
)
app.include_router(
    personalization.router,
    prefix=f"{settings.API_V1_PREFIX}/personalization",
    tags=["Personalization"]
)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Diamond OA Journal Management System API",
        "docs": "/docs",
        "version": "1.0.0",
        "performance": "optimized"
    }


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint with rate limiting."""
    return {"status": "healthy", "performance": "optimized"}
