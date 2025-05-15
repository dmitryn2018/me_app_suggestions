import pytest
import os
from dotenv import load_dotenv
from app.services.memory import MemoryService

load_dotenv()

@pytest.fixture
def test_conversation():
    return [
        {
            "role": "user",
            "content": "Hi there! I'm working on a graph project—could you write a Python function that optimizes a depth-first search with memoization for a weighted graph and explain its time and space complexity?"
        },
        {
            "role": "assistant",
            "content": "Absolutely. Here's a function using DFS with memoization to cache intermediate results and avoid redundant work..."
        },
        {
            "role": "user",
            "content": "Great, thanks! Next, I need to draft a blog post outline about remote work best practices. Could you suggest headings and bullet points?"
        },
        {
            "role": "assistant",
            "content": "**Blog Post Outline: \"Mastering Remote Work: Best Practices for Productivity and Well-Being\"**..."
        },
        {
            "role": "user",
            "content": "Perfect. Now, could you write a short fantasy story about a traveling musician who discovers magic through song?"
        },
        {
            "role": "assistant",
            "content": "Elara strummed her weathered lute beneath the shadow of the Moonspire cliffs..."
        }
    ]

@pytest.fixture
def memory_service():
    assert os.getenv("MEM0_API_KEY"), "MEM0_API_KEY must be set"
    return MemoryService()

@pytest.mark.asyncio
async def test_add_and_retrieve_memory(memory_service, test_conversation):
    """Test adding and retrieving memories."""
    test_user_id = "test_user_123"
    
    # Add memory
    add_response = await memory_service.add_memory(test_user_id, test_conversation)
    assert add_response, "Should get response from add_memory"
    
    # Retrieve recent conversations
    memories = await memory_service.get_recent_conversations(test_user_id)
    assert len(memories) > 0, "Should retrieve at least one memory"
    
    # Verify memory content
    found_dfs_content = False
    found_remote_work_content = False
    found_fantasy_story_content = False
    
    for memory in memories:
        content = memory.get("memory", "")
        if "depth-first search" in content:
            found_dfs_content = True
        if "remote work" in content.lower():
            found_remote_work_content = True
        if "fantasy story" in content:
            found_fantasy_story_content = True
    
    assert found_dfs_content, "Should find DFS-related content in memories"
    assert found_remote_work_content, "Should find remote work-related content in memories"
    assert found_fantasy_story_content, "Should find fantasy story content in memories"

@pytest.mark.asyncio
async def test_get_user_categories(memory_service):
    """Test retrieving and initializing user categories."""
    test_user_id = "test_user_456"
    
    # Get categories
    categories = await memory_service.get_user_categories(test_user_id)
    assert len(categories) > 0, "Should have default categories"
    
    # Verify category structure
    for category in categories:
        assert "name" in category, "Category should have a name"
        assert "description" in category, "Category should have a description"
        assert "keywords" in category, "Category should have keywords field"
        assert "goal" in category, "Category should have goal field"

@pytest.mark.asyncio
async def test_get_user_goals(memory_service):
    """Test retrieving user goals."""
    test_user_id = "test_user_789"
    
    # Add a test goal
    goal_message = [
        {
            "role": "user",
            "content": "My goal is to master Python programming by the end of the year"
        }
    ]
    await memory_service.add_memory(test_user_id, goal_message)
    
    # Get goals
    goals = await memory_service.get_user_goals(test_user_id)
    
    # Verify goals
    assert isinstance(goals, list), "Should return a list of goals"
    if goals:  # If any goals were found
        goal = goals[0]
        assert "content" in goal, "Goal should have content"
        assert "timestamp" in goal, "Goal should have timestamp"
        assert "categories" in goal, "Goal should have categories" 