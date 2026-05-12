from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    role: str = Field(..., description="Role of the sender (user or assistant)")
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str = Field(default="New Conversation", max_length=200)

class CreateConversationRequest(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []

class CreateConversationResponse(ConversationResponse):
    pass
