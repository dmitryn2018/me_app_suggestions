from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ModelType(str, Enum):
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"

class Suggestion(BaseModel):
    """A suggestion for the user based on their memories and conversations."""
    title: str
    description: str
    model_type: str  # code, text, image
    selected_model: str  # The model to use for this suggestion

class Memory(BaseModel):
    """A memory from the user's conversation history."""
    content: str
    timestamp: Optional[str] = None
    type: Optional[str] = None  # code, text, image
    metadata: Optional[dict] = None
