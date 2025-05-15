from fastapi import APIRouter
from typing import List

class RouterService:
    """Service for managing FastAPI routers and their configuration."""
    
    def __init__(self):
        self._router = APIRouter()
        self._registered_routers: List[APIRouter] = []
    
    def register_router(self, router: APIRouter, prefix: str = "", tags: List[str] = None):
        """
        Register a new router with optional prefix and tags.
        
        Args:
            router: The FastAPI router to register
            prefix: URL prefix for all routes in this router
            tags: OpenAPI tags for documentation
        """
        if tags is None:
            # Extract tag from prefix if not provided
            tags = [prefix.strip("/") or "default"]
            
        self._router.include_router(
            router,
            prefix=prefix,
            tags=tags
        )
        self._registered_routers.append(router)
    
    @property
    def router(self) -> APIRouter:
        """Get the main router with all registered sub-routers."""
        return self._router
    
    def get_registered_routers(self) -> List[APIRouter]:
        """Get list of all registered routers."""
        return self._registered_routers.copy()

# Create singleton instance
router_service = RouterService()

def get_router_service() -> RouterService:
    """Dependency injection for router service."""
    return router_service
