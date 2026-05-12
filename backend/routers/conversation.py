import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse
)
from services import ConversationService

router = APIRouter(prefix="/api/conversations", tags=["conversations"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    session: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    try:
        result = await ConversationService.create_conversation(session, title=conversation.title)
        await session.commit()
        return result
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    """List all conversations sorted by most recent."""
    try:
        return await ConversationService.get_all_conversations(session, limit=limit)
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get a conversation with its messages by ID."""
    try:
        conversation = await ConversationService.get_conversation_with_messages(session, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    try:
        success = await ConversationService.delete_conversation(session, conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        await session.commit()
        return None
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
