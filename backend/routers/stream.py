import logging
import asyncio
import json
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas.stream import StreamRequest, StreamChunk
from services import LLMManager, ConversationService

router = APIRouter(prefix="/api/chat", tags=["stream"])
logger = logging.getLogger(__name__)

# Instantiate LLMManager
llm_manager = LLMManager()


async def generate_sse_stream(request: StreamRequest, session: AsyncSession):
    """
    Generate SSE stream for chat response.
    """
    conversation_id = request.conversation_id
    
    try:
        # 1. Ensure conversation exists or create new one
        if not conversation_id:
            logger.info("No conversation_id provided, creating new conversation")
            conv = await ConversationService.create_conversation(session)
            conversation_id = conv["id"]
            
            # Send conversation_id event first
            chunk = StreamChunk(
                type="conversation_id",
                conversation_id=conversation_id
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
        
        # 2. Save user message
        logger.info(f"Saving user message to conversation {conversation_id}")
        user_msg = await ConversationService.save_message(
            session,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        await session.commit()
        
        # 3. Load history
        history_data = await ConversationService.get_conversation_with_messages(session, conversation_id)
        full_history = history_data.get("messages", [])
        history_for_llm = full_history[:-1][-10:] if len(full_history) > 1 else []
        
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history_for_llm
        ]
        
        # 4. Generate full response using existing LLMManager
        logger.info("Generating full response")
        full_response = await llm_manager.generate_with_context(request.message, formatted_history)
        
        if not full_response:
            raise ValueError("LLM returned empty response")
        
        # 5. Stream response in chunks
        logger.info("Streaming response in chunks")
        words = full_response.split()
        
        for i, word in enumerate(words):
            # Add space before word (except first)
            content = word if i == 0 else f" {word}"
            
            chunk = StreamChunk(
                type="token",
                content=content,
                conversation_id=conversation_id
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            
            # Small delay between chunks (30ms)
            await asyncio.sleep(0.03)
        
        # 6. Save assistant message after streaming completes
        logger.info("Saving assistant message")
        assistant_msg = await ConversationService.save_message(
            session,
            conversation_id=conversation_id,
            role="assistant",
            content=full_response
        )
        await session.commit()
        
        # 7. Send done event
        chunk = StreamChunk(
            type="done",
            conversation_id=conversation_id,
            message_id=assistant_msg["id"]
        )
        yield f"data: {chunk.model_dump_json()}\n\n"
        
    except Exception as e:
        logger.error(f"Error in stream generation: {e}", exc_info=True)
        
        # Send error event
        chunk = StreamChunk(
            type="error",
            content=str(e),
            conversation_id=conversation_id
        )
        yield f"data: {chunk.model_dump_json()}\n\n"


@router.post("/stream")
async def stream_chat(request: StreamRequest, session: AsyncSession = Depends(get_db)):
    """
    Stream chat response using Server-Sent Events (SSE).
    """
    return StreamingResponse(
        generate_sse_stream(request, session),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
