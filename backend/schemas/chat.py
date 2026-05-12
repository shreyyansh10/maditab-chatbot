from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue a thread")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "conversation_id": "uuid-v4-string"
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI generated response")
    conversation_id: str = Field(..., description="The conversation ID")
    user_message_id: str = Field(..., description="ID of the saved user message")
    assistant_message_id: str = Field(..., description="ID of the saved assistant message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I'm doing well, thank you!",
                "conversation_id": "uuid-v4-string",
                "user_message_id": "msg-uuid-1",
                "assistant_message_id": "msg-uuid-2"
            }
        }
