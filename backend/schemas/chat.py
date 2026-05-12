from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    
    class Config:
        json_schema_extra = {"example": {"message": "Hello, how are you?"}}

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI generated response")
    
    class Config:
        json_schema_extra = {"example": {"response": "I'm doing well, thank you!"}}
