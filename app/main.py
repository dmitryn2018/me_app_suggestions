# app/main.py
from fastapi import FastAPI
from app.services.router import router_service
from app.routers import suggestions

app = FastAPI(
    title="ME App Suggestions API",
    description="API for personalized suggestions based on user memory and conversations",
    version="1.0.0"
)

# Register routers
router_service.register_router(
    suggestions.router,
    prefix="/api/v1",
    tags=["suggestions"]
)

# Include the main router
app.include_router(router_service.router)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "app": "ME App Suggestions API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
