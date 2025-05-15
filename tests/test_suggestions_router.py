import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.models import Suggestion, ModelType
from app.main import app
from app.services.memory import MemoryService
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

@pytest.fixture
def mock_memory_service():
    with patch('app.routers.suggestions.memory_service') as mock:
        mock.get_recent_conversations = AsyncMock(return_value=[
            {
                "memory": "User discussed Python algorithm optimization techniques",
                "timestamp": "2024-03-20T10:00:00Z"
            },
            {
                "memory": "User requested help with designing a logo",
                "timestamp": "2024-03-20T10:05:00Z"
            },
            {
                "memory": "User needed assistance with technical documentation",
                "timestamp": "2024-03-20T10:10:00Z"
            }
        ])
        yield mock

@pytest.fixture
def mock_suggestion_generator():
    with patch('app.routers.suggestions.suggestion_generator') as mock:
        mock.generate_from_conversations = AsyncMock(return_value=[
            Suggestion(
                title="Optimize your algorithm",
                description="Improve the time complexity of your graph traversal algorithm",
                model_type=ModelType.CODE,
                selected_model="anthropic/claude-3.7-sonnet"
            ),
            Suggestion(
                title="Create a modern logo",
                description="Design a minimalist tech startup logo",
                model_type=ModelType.IMAGE,
                selected_model="openai/gpt-image-1"
            ),
            Suggestion(
                title="Write API documentation",
                description="Document your API endpoints using OpenAPI standards",
                model_type=ModelType.TEXT,
                selected_model="gpt-4.1"
            )
        ])
        yield mock

@pytest.mark.asyncio
async def test_get_suggestions_endpoint(mock_memory_service, mock_suggestion_generator):
    """Test the GET /suggestions endpoint"""
    
    # Test with default parameters
    response = client.get("/api/v1/suggestions?user_id=test_user_123")
    assert response.status_code == 200
    suggestions = response.json()
    
    # Verify response structure
    assert isinstance(suggestions, list)
    assert len(suggestions) == 3  # Default n=3
    
    # Verify each suggestion
    for suggestion in suggestions:
        assert "title" in suggestion
        assert "description" in suggestion
        assert "model_type" in suggestion
        assert "selected_model" in suggestion
        
        # Verify model types are valid
        assert suggestion["model_type"].lower() in ["text", "code", "image"]
        
        # Verify model selection
        if suggestion["model_type"] == "code":
            assert suggestion["selected_model"] == "anthropic/claude-3.7-sonnet"
        elif suggestion["model_type"] == "image":
            assert suggestion["selected_model"] == "openai/gpt-image-1"
        elif suggestion["model_type"] == "text":
            assert suggestion["selected_model"] == "gpt-4.1"
    
    # Test with custom number of suggestions
    response = client.get("/api/v1/suggestions?user_id=test_user_123&n=2")
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 2
    
    # Test with invalid n
    response = client.get("/api/v1/suggestions?user_id=test_user_123&n=11")
    assert response.status_code == 422  # Validation error
    
    # Test with missing user_id
    response = client.get("/api/v1/suggestions")
    assert response.status_code == 422  # Validation error
    
    # Verify service calls
    mock_memory_service.get_recent_conversations.assert_called_with("test_user_123")
    mock_suggestion_generator.generate_from_conversations.assert_called()

@pytest.mark.asyncio
async def test_suggestions_error_handling(mock_memory_service, mock_suggestion_generator):
    """Test error handling in the suggestions endpoint"""
    
    # Test memory service error
    mock_memory_service.get_recent_conversations.side_effect = Exception("Memory service error")
    response = client.get("/api/v1/suggestions?user_id=test_user_123")
    assert response.status_code == 500
    
    # Test suggestion generator error
    mock_memory_service.get_recent_conversations.side_effect = None
    mock_suggestion_generator.generate_from_conversations.side_effect = Exception("Generator error")
    response = client.get("/api/v1/suggestions?user_id=test_user_123")
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_suggestions_with_real_memory():
    """Integration test for suggestions endpoint with real memory service."""
    # Initialize real services
    memory_service = MemoryService()
    test_user_id = "test_integration_user"
    
    # Test conversations to add to memory
    test_conversations = [
        {
            "role": "user",
            "content": "I need help optimizing this Python function that implements a graph traversal algorithm."
        },
        {
            "role": "assistant",
            "content": "I'll help you optimize the algorithm. Let's analyze the time complexity first..."
        },
        {
            "role": "user",
            "content": "Could you also help me create a logo for my tech startup? Something modern and minimalist."
        },
        {
            "role": "assistant",
            "content": "I'll help you design a logo that represents your startup's vision..."
        }
    ]
    
    try:
        print("\n=== Starting integration test with real memory service ===")
        
        # Add test conversations to memory
        print("\nAdding test conversations to memory...")
        for conversation in test_conversations:
            await memory_service.add_memory(test_user_id, [conversation])
        
        # Make request to suggestions endpoint
        print("\nRequesting suggestions...")
        response = client.get(f"/api/v1/suggestions?user_id={test_user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        suggestions = response.json()
        print(f"\nReceived {len(suggestions)} suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion['title']} ({suggestion['model_type']}) - {suggestion['selected_model']}")
        
        # Verify basic response structure
        assert isinstance(suggestions, list), "Response should be a list"
        assert len(suggestions) > 0, "Should receive at least one suggestion"
        
        # Verify suggestion content types based on conversations
        content_types = {suggestion["model_type"] for suggestion in suggestions}
        print(f"\nContent types in suggestions: {content_types}")
        
        # Verify we have suggestions for both coding and design content
        has_coding_suggestion = any(
            term in suggestion["title"].lower() or term in suggestion["description"].lower()
            for suggestion in suggestions
            for term in ["algorithm", "code", "python", "function", "graph", "traversal", "optimize"]
        )
        has_design_suggestion = any(
            term in suggestion["title"].lower() or term in suggestion["description"].lower()
            for suggestion in suggestions
            for term in ["logo", "design", "visual", "minimalist"]
        )
        
        assert has_coding_suggestion, "Should include coding-related suggestions"
        assert has_design_suggestion, "Should include design-related suggestions"
        
        # Verify each suggestion's structure and content
        for suggestion in suggestions:
            # Check required fields
            assert suggestion["title"], "Suggestion should have a title"
            assert suggestion["description"], "Suggestion should have a description"
            assert suggestion["model_type"].lower() in ["text", "code", "image"], \
                f"Invalid model type: {suggestion['model_type']}"
            assert suggestion["selected_model"], "Suggestion should have a selected model"
            
            # Verify model selection based on content
            if any(term in suggestion["title"].lower() for term in ["algorithm", "code", "python"]):
                assert suggestion["selected_model"] == "anthropic/claude-3.7-sonnet", \
                    "Coding suggestions should use Claude 3.7"
            elif any(term in suggestion["title"].lower() for term in ["logo", "design", "visual"]):
                assert suggestion["selected_model"] in [
                    "openai/gpt-image-1",
                    "recraft-ai/recraft-v3",
                    "recraft-ai/recraft-v3-svg",
                    "black-forest-labs/flux-1.1-pro-ultra",
                    "google/gemini-2.0-flash-exp-image-generation"
                ], "Image suggestions should use appropriate image models"
        
        print("\n=== Integration test completed successfully ===")
        
    except Exception as e:
        print(f"\nIntegration test failed: {str(e)}")
        raise
    
    finally:
        # Clean up test data
        print("\nCleaning up test data...")
        try:
            # Here you might want to add cleanup logic if your memory service has such functionality
            pass
        except Exception as e:
            print(f"Warning: Cleanup failed: {str(e)}") 