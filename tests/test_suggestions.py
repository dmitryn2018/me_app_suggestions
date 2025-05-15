import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.services.memory import MemoryService
from app.routers import suggestions

client = TestClient(app)

@pytest.fixture
def mock_categories():
    return [
        {
            "category_name": "learning",
            "keywords": ["typescript", "reading"],
            "goal": "Master TypeScript"
        },
        {
            "category_name": "content_to_create",
            "keywords": ["image", "blog"]
        }
    ]

@pytest.fixture
def mock_conversations():
    return [
        {
            "memory": "Working on a Python code for graph optimization",
            "timestamp": "2024-03-20T10:00:00Z"
        },
        {
            "memory": "Writing a blog post about TypeScript best practices",
            "timestamp": "2024-03-20T11:00:00Z"
        },
        {
            "memory": "Designing a logo for the new app",
            "timestamp": "2024-03-20T12:00:00Z"
        }
    ]

@pytest.fixture
def mock_memory_service(mock_categories, mock_conversations):
    with patch('app.routers.suggestions.memory_service') as mock_service:
        # Mock the methods
        mock_service.get_user_categories = AsyncMock(return_value=mock_categories)
        mock_service.get_user_goals = AsyncMock(return_value=[])
        mock_service.get_recent_conversations = AsyncMock(return_value=mock_conversations)
        yield mock_service

@pytest.mark.asyncio
async def test_get_suggestions(mock_memory_service):
    """Test that suggestions endpoint returns expected suggestions."""
    response = client.get("/api/v1/suggestions?user_id=test_user")
    
    assert response.status_code == 200
    suggestions = response.json()
    
    # Check we got suggestions
    assert len(suggestions) > 0
    
    # Verify suggestion structure
    for suggestion in suggestions:
        assert "title" in suggestion
        assert "description" in suggestion
        assert "model_type" in suggestion
        assert "selected_model" in suggestion
        assert suggestion["model_type"].lower() in ["text", "code", "image"]
    
    # Verify we have suggestions of different types
    model_types = {s["model_type"].lower() for s in suggestions}
    # assert "code" in model_types, "Should have at least one coding suggestion"
    assert "text" in model_types, "Should have at least one text suggestion"
    assert "image" in model_types, "Should have at least one image suggestion"
    
    # Verify we have appropriate suggestions based on mock data
    titles = [s["title"].lower() for s in suggestions]
    descriptions = [s["description"].lower() for s in suggestions]
    all_text = " ".join(titles + descriptions)
    
    assert any("python" in text or "algorithm" in text for text in titles + descriptions), "Should have coding-related suggestion"
    assert any("typescript" in text or "blog" in text for text in titles + descriptions), "Should have writing-related suggestion"
    assert any("logo" in text or "design" in text for text in titles + descriptions), "Should have design-related suggestion"

@pytest.mark.asyncio
async def test_get_suggestions_custom_count(mock_memory_service):
    """Test that suggestions endpoint respects custom count parameter."""
    response = client.get("/api/v1/suggestions?user_id=test_user&n=2")
    
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 2
    
    # Verify suggestion structure
    for suggestion in suggestions:
        assert "title" in suggestion
        assert "description" in suggestion
        assert "model_type" in suggestion
        assert "selected_model" in suggestion

@pytest.mark.asyncio
async def test_get_suggestions_invalid_count(mock_memory_service):
    """Test that suggestions endpoint validates count parameter."""
    # Test too high count
    response = client.get("/api/v1/suggestions?user_id=test_user&n=21")
    assert response.status_code == 422
    
    # Test too low count
    response = client.get("/api/v1/suggestions?user_id=test_user&n=0")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_suggestions_missing_user_id(mock_memory_service):
    """Test that suggestions endpoint requires user_id."""
    response = client.get("/api/v1/suggestions")
    assert response.status_code == 422
