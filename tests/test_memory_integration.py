import pytest
import os
import time
import asyncio
from dotenv import load_dotenv
from pytest_asyncio import fixture
from app.services.memory import MemoryService, DEFAULT_CATEGORIES

# Load environment variables before importing Memory
load_dotenv()

# Ensure required environment variables are set
required_env_vars = ["MEM0_API_KEY", "OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}", allow_module_level=True)

@fixture(scope="function")
async def memory_service():
    """Fixture that provides a MemoryService instance."""
    service = MemoryService()
    return service

@pytest.mark.asyncio
async def test_add_and_verify_categories(memory_service):
    """Integration test: Add memories and verify their assigned categories."""
    # Use a test user ID with timestamp to avoid conflicts
    test_user_id = f"test_user_{int(time.time())}"
    print(f"\nTesting with user ID: {test_user_id}")
    
    try:
        # First, set up the custom categories at project level
        response = await memory_service.client.update_project(custom_categories=DEFAULT_CATEGORIES)
        print("Categories set at project level")

        # Add test conversation
        test_messages = [
            {
                "role": "user",
                "content": "My name is Alice. I need help organizing my daily schedule better. I feel overwhelmed trying to balance work, exercise, and social life."
            },
            {
                "role": "assistant",
                "content": "I understand how overwhelming that can feel. Let's break this down together. What specific areas of your schedule feel most challenging to manage?"
            },
            {
                "role": "user",
                "content": "I want to be more productive at work, maintain a consistent workout routine, and still have energy for friends and hobbies."
            },
            {
                "role": "assistant",
                "content": "Those are great goals for better time management. What's one small change you could make to start improving your daily routine?"
            }
        ]
        
        # Add the conversation with categories
        await memory_service.add_memory(test_user_id, test_messages)
        print("Test conversation added")
        
        # Wait for memory processing
        await asyncio.sleep(2)
        
        # Get all memories for the user with specific categories
        filters = {
            "AND": [
                {"user_id": test_user_id},
                {
                    "OR": [
                        {"categories": {"contains": "lifestyle_management_concerns"}},
                        {"categories": {"contains": "personal_information"}}
                    ]
                }
            ]
        }
        response = await memory_service.client.get_all(version="v2", filters=filters)
        memories = response.get("results", []) if isinstance(response, dict) else response
        print(f"Retrieved {len(memories)} memories")
        
        # Verify the memories have been assigned the expected categories
        expected_categories = ["lifestyle_management_concerns", "personal_information"]
        found_categories = set()
        
        for memory in memories:
            if isinstance(memory, dict):
                categories = memory.get("categories", [])
                found_categories.update(categories)
                # Print memory details for debugging
                print(f"\nMemory details:")
                print(f"ID: {memory.get('id')}")
                print(f"Memory: {memory.get('memory')}")
                print(f"Categories: {categories}")
                print(f"Created at: {memory.get('created_at')}")
        
        print(f"Found categories: {found_categories}")
        
        # Verify each expected category is present
        for category in expected_categories:
            assert category in found_categories, f"Expected category {category} not found in memories"
        
        print("Category verification complete")
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {str(e)}")

@pytest.mark.asyncio
async def test_get_user_goals(memory_service):
    """Integration test: Add memories with goals and verify their retrieval."""
    test_user_id = f"test_user_{int(time.time())}"
    print(f"\nTesting with user ID: {test_user_id}")
    
    try:
        # Set up categories
        response = await memory_service.client.update_project(custom_categories=DEFAULT_CATEGORIES)
        print("Categories set at project level")
        
        # Add test goals conversation
        test_messages = [
            {
                "role": "user",
                "content": "My goals for this year are: 1) Learn Python and FastAPI for backend development, 2) Run a half marathon, 3) Read 24 books"
            },
            {
                "role": "assistant",
                "content": "Those are great goals! Let's break them down into manageable steps. Which one would you like to start with?"
            },
            {
                "role": "user",
                "content": "Let's start with the Python and FastAPI goal. I want to build a complete web application by the end of Q2."
            }
        ]
        
        # Add the conversation with categories
        await memory_service.add_memory(test_user_id, test_messages)
        print("Goals conversation added")
        
        # Wait for memory processing
        await asyncio.sleep(2)
        
        # Get user goals
        goals = await memory_service.get_user_goals(test_user_id)
        print(f"\nRetrieved {len(goals)} goals")
        
        # Verify goals were retrieved
        assert len(goals) > 0, "Should have retrieved at least one goal"
        
        # Verify goal structure
        for goal in goals:
            assert "content" in goal, "Goal should have content"
            assert "timestamp" in goal, "Goal should have timestamp"
            assert "categories" in goal, "Goal should have categories"
            assert "milestones_and_goals" in goal["categories"], "Goal should be in milestones_and_goals category"
            
        # Verify specific goal content is present
        goal_contents = [goal["content"] for goal in goals]
        assert any("Python and FastAPI" in content for content in goal_contents), "Should find the Python learning goal"
        assert any("half marathon" in content for content in goal_contents), "Should find the running goal"
        assert any("24 books" in content for content in goal_contents), "Should find the reading goal"
        
        print("Goals verification complete")
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {str(e)}")
