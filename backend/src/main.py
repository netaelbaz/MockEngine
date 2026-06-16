"""Main FastAPI application for MockEngine backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import api_keys, rules, sdk, analytics


# Initialize FastAPI app
app = FastAPI(
    title="MockEngine API",
    description="Backend API for MockEngine mobile SDK - HTTP request mocking for development and testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_keys.router)
app.include_router(rules.router)
app.include_router(sdk.router)
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "MockEngine API",
        "version": "1.0.0",
        "description": "Backend for mobile SDK mock engine",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "api_keys": "/api/v1/api-keys",
            "rules": "/api/v1/rules",
            "sdk": "/api/sdk",
            "analytics": "/api/v1/analytics"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mockengine-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
