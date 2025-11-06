"""
Main FastAPI application for Diamond OA Journal Management System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import auth, manuscripts, users, reviews, themes, copyediting, production, issues, discussions

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(manuscripts.router, prefix=f"{settings.API_V1_PREFIX}/manuscripts", tags=["Manuscripts"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_PREFIX}/reviews", tags=["Reviews"])
app.include_router(themes.router, prefix=f"{settings.API_V1_PREFIX}/themes", tags=["Themes"])
app.include_router(copyediting.router, prefix=f"{settings.API_V1_PREFIX}/copyediting", tags=["Copyediting"])
app.include_router(production.router, prefix=f"{settings.API_V1_PREFIX}/production", tags=["Production"])
app.include_router(issues.router, prefix=f"{settings.API_V1_PREFIX}/issues", tags=["Issues"])
app.include_router(discussions.router, prefix=f"{settings.API_V1_PREFIX}/discussions", tags=["Discussions"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Diamond OA Journal Management System API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
