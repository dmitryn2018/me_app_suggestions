from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
import os
from dotenv import load_dotenv

from app.models import Suggestion
from app.services.memory import MemoryService
from app.services.generator import SuggestionGenerator

load_dotenv()

router = APIRouter()
memory_service = MemoryService()
suggestion_generator = SuggestionGenerator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    mem0_api_key=os.getenv("MEM0_API_KEY"),
    proxy_url=os.getenv("OPENAI_PROXY")
)

@router.get("/suggestions", response_model=List[Suggestion])
async def get_suggestions(
    user_id: str,
    n: int = Query(default=3, description="Number of suggestions to return", ge=1, le=20)
):
    """
    Get personalized suggestions for the user based on their memory and conversations.
    
    This endpoint analyzes the user's recent conversations and returns personalized suggestions 
    with appropriate AI models. The suggestions will include a mix of coding, writing, and image
    suggestions based on the user's recent activities.
    
    Args:
        user_id: The ID of the user to get suggestions for
        n: Number of suggestions to return (1-20, default 3)
        
    Returns:
        List[Suggestion]: A list of personalized suggestions
        
    Raises:
        HTTPException: If there's an error retrieving memories or generating suggestions
        HTTPException: If n is not between 1 and 10
    """
    try:
        # Validate n parameter
        if n < 1 or n > 20:
            raise HTTPException(
                status_code=422,
                detail="Number of suggestions (n) must be between 1 and 10"
            )
        
        # Get user data from memory service
        conversations = await memory_service.get_recent_conversations(user_id)
        
        # Generate suggestions
        suggestions = await suggestion_generator.generate_from_conversations(
            conversations=[],  # Empty list since we're using memories
            user_id=user_id,
            memories=conversations
        )
        
        # Ensure we have at least one suggestion
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any suggestions"
            )
        
        # Return top N suggestions
        return suggestions[:n]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating suggestions: {str(e)}"
        )

__all__ = ["router"]