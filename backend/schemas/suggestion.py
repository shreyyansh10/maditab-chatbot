from pydantic import BaseModel, Field
from typing import List

class SuggestionsResponse(BaseModel):
    conversation_id: str = Field(..., description="The conversation ID")
    suggestions: List[str] = Field(..., description="List of follow-up question suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "uuid-v4-string",
                "suggestions": [
                    "Can you explain more?",
                    "Give me an example",
                    "What are the benefits?"
                ]
            }
        }
