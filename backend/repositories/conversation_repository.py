from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.conversation import Conversation
from typing import List, Optional
from datetime import datetime

class ConversationRepository:
    
    @staticmethod
    async def create(session: AsyncSession, title: str = "New Conversation") -> Conversation:
        conversation = Conversation(title=title)
        session.add(conversation)
        await session.flush()  # Get ID without committing
        return conversation
    
    @staticmethod
    async def get_by_id(session: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(session: AsyncSession, limit: int = 50) -> List[Conversation]:
        result = await session.execute(
            select(Conversation)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_timestamp(session: AsyncSession, conversation_id: str) -> None:
        conversation = await ConversationRepository.get_by_id(session, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
    
    @staticmethod
    async def delete(session: AsyncSession, conversation_id: str) -> bool:
        conversation = await ConversationRepository.get_by_id(session, conversation_id)
        if conversation:
            await session.delete(conversation)
            return True
        return False
