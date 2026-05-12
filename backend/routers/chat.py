import logging
import time
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from schemas.chat import ChatRequest, ChatResponse
from schemas.suggestion import SuggestionsResponse
from services import LLMManager, ConversationService, SuggestionService

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Instantiate LLMManager globally to manage providers and fallback
llm_manager = LLMManager()
suggestion_service = SuggestionService(llm_manager)

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest, session: AsyncSession = Depends(get_db)):
    """
    Process a chat message with persistence and context awareness.
    """
    conversation_id = request.conversation_id
    
    try:
        # 1. Ensure conversation exists or create new one
        if not conversation_id:
            logger.info("No conversation_id provided, creating new conversation")
            conv = await ConversationService.create_conversation(session)
            conversation_id = conv["id"]
        
        # 2. Save user message
        logger.info(f"Saving user message to conversation {conversation_id}")
        user_msg = await ConversationService.save_message(
            session, 
            conversation_id=conversation_id, 
            role="user", 
            content=request.message
        )
        user_message_id = user_msg["id"]
        
        # 3. Load history (last 10 messages excluding current)
        history_data = await ConversationService.get_conversation_with_messages(session, conversation_id)
        # Filter messages to only include previous ones (excluding the one we just saved)
        # Actually, get_conversation_with_messages returns all messages.
        # We need to pass history to LLMManager.
        full_history = history_data.get("messages", [])
        # Last 10 messages excluding the very last one (which is the current user message)
        history_for_llm = full_history[:-1][-10:] if len(full_history) > 1 else []
        
        # Convert history to format expected by LLMManager: List[Dict[str, Any]] with 'role' and 'content'
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in history_for_llm
        ]
        
        # 4. Generate AI response with context
        start_time = time.time()
        try:
            response_text = await llm_manager.generate_with_context(request.message, formatted_history)
            
            if not response_text:
                raise ValueError("LLM returned empty response")
                
            logger.info(f"LLM response generated in {time.time() - start_time:.2f}s")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            # Rollback since we saved the user message but failed to get a response
            await session.rollback()
            raise HTTPException(status_code=500, detail="Failed to generate AI response.")

        # 5. Save assistant response
        assistant_msg = await ConversationService.save_message(
            session,
            conversation_id=conversation_id,
            role="assistant",
            content=response_text
        )
        assistant_message_id = assistant_msg["id"]
        
        # 6. Commit transaction
        await session.commit()
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id
        )
        
    except HTTPException:
        await session.rollback()
        raise
    except ValueError as e:
        await session.rollback()
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred.")


@router.get("/suggestions/{conversation_id}", response_model=SuggestionsResponse)
async def get_suggestions(conversation_id: str, session: AsyncSession = Depends(get_db)):
    """
    Generate contextual follow-up question suggestions for a conversation.
    """
    try:
        # Load conversation history
        history_data = await ConversationService.get_conversation_with_messages(session, conversation_id)
        
        if not history_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages = history_data.get("messages", [])
        
        # Format history for suggestion service
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        # Generate suggestions
        suggestions = await suggestion_service.generate_suggestions(formatted_history)
        
        return SuggestionsResponse(
            conversation_id=conversation_id,
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}", exc_info=True)
        # Return default suggestions on error instead of failing
        from services.suggestion_service import DEFAULT_SUGGESTIONS
        return SuggestionsResponse(
            conversation_id=conversation_id,
            suggestions=DEFAULT_SUGGESTIONS
        )
