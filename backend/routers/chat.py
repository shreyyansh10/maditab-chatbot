import logging
import time
from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from services.llm_service import OllamaLLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Instantiate service globally to preserve temporary memory
llm_service_instance = OllamaLLMService()

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Process a chat message and return an AI response.
    """
    logger.info(f"Received chat message: length={len(request.message)}")
    start_time = time.time()
    
    try:
        response_text = await llm_service_instance.generate(request.message)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate AI response.")
            
        logger.info(f"LLM response generated in {time.time() - start_time:.2f}s")
        return ChatResponse(response=response_text)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while generating the response.")
