import os
from typing import List, Dict, Any
from mem0 import AsyncMemoryClient
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CATEGORIES = [
    {"personal_information": "Basic information about the user including name, preferences, and personality traits"},
    {"communicational_style": "Tracks the user's communication preferences including tone, length, formality, slang usage, and preferred response format"},
    {"lifestyle_management_concerns": "Tracks daily routines, habits, hobbies and interests including cooking, time management and work-life balance"},
    {"working_projects": "Information about the user's active and past projects including project goals, status, technologies, and relevant details"},
    {"family": "Information related to the user's family members including names, ages, birthdays, and significant family events"},
    {"connections": "Details about people the user interacts with regularly, including their names, personal traits, and preferences"},
    {"entertainment": "User's preferences in leisure activities, entertainment choices, hobbies, and recreational interests"},
    {"health": "Tracks health-related details, medical conditions, treatments, wellness routines, and other relevant health information"},
    {"milestones_and_goals": "Records short-term and long-term personal and professional goals, achievements, and significant milestones"},
    {"sports": "Tracks user's interests and involvement in sports, favorite teams, athletic activities, and sports-related preferences"},
    {"music": "Captures user's musical preferences, favorite genres, artists, playlists, and listening habits"},
    {"food": "Tracks user's dietary preferences, favorite cuisines, restaurants, cooking habits, and food-related interests"},
    {"fashion": "Information regarding user's fashion preferences, style choices, favorite brands, and shopping habits"},
    {"technology_and_tools": "Details about tools, software, platforms, and technologies the user regularly utilizes or prefers"},
    {"ai_model_preferences": "Information about user's preferences for specific AI models, including model types, versions, and use cases"},
    {"image_generation_preferences": "Details about user's preferences for image generation, including styles, themes, contexts, and specific requirements"}
]

class MemoryService:
    def __init__(self):
        self.client = AsyncMemoryClient()
        
    async def initialize_categories(self, user_id: str) -> List[Dict[str, str]]:
        """Initialize default categories for a new user."""
        # First, set the categories at the project level
        response = await self.client.update_project(custom_categories=DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES

    async def get_user_categories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user's custom categories from mem0."""
        # Get project settings to check categories
        project = await self.client.get_project(fields=["custom_categories"])
        categories = project.get("custom_categories", [])
        
        if not categories:
            # If no categories set, initialize them
            await self.initialize_categories(user_id)
            project = await self.client.get_project(fields=["custom_categories"])
            categories = project.get("custom_categories", [])
            
        # Transform categories into the expected format
        formatted_categories = []
        for category in categories:
            name = list(category.keys())[0]
            description = list(category.values())[0]
            formatted_categories.append({
                "name": name,
                "description": description,
                "keywords": [],
                "goal": ""
            })
            
        return formatted_categories
    
    async def get_user_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user's goals from mem0."""
        # Get all memories with milestones_and_goals category
        filters = {
            "AND": [
                {"user_id": user_id},
                {"categories": {"contains": "milestones_and_goals"}}
            ]
        }
        response = await self.client.get_all(version="v2", filters=filters)
        memories = response.get("results", []) if isinstance(response, dict) else response
        goals = []
        
        # Extract goals from memories
        for memory in memories:
            if isinstance(memory, dict):
                # Get the memory content
                content = memory.get("memory", "")
                if content:
                    goals.append({
                        "content": content,
                        "timestamp": memory.get("created_at"),
                        "categories": memory.get("categories", [])
                    })
        
        # Sort goals by timestamp if available
        goals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return goals
    
    async def add_memory(self, user_id: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self.client.add(messages=messages, user_id=user_id, output_format="v1.1")
    
    async def get_recent_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user's recent conversations."""
        # Get all memories for the user, sorted by timestamp
        filters = {
            "AND": [
                {"user_id": user_id}
            ]
        }
        response = await self.client.get_all(version="v2", filters=filters)
        memories = response.get("results", []) if isinstance(response, dict) else response
        
        # Sort memories by timestamp and return the most recent ones
        memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return memories  # Return the 10 most recent conversations
