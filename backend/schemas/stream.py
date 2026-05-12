from pydantic import BaseModel, Field
from typing import Optional, Literal

class StreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue a thread")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Tell me about Python",
                "conversation_id": "uuid-v4-string"
            }
        }

class StreamChunk(BaseModel):
    type: Literal["conversation_id", "token", "done", "error"] = Field(..., description="Event type")
    content: Optional[str] = Field(None, description="Content of the chunk")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    message_id: Optional[str] = Field(None, description="Message ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "token",
                "content": "Hello",
                "conversation_id": "uuid-v4-string",
                "message_id": "msg-uuid"
            }
        }
