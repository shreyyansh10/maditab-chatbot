from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.message import Message
from typing import List, Optional

class MessageRepository:
    
    @staticmethod
    async def create(
        session: AsyncSession,
        conversation_id: str,
        role: str,
        content: str
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        session.add(message)
        await session.flush()
        return message
    
    @staticmethod
    async def get_by_conversation(
        session: AsyncSession,
        conversation_id: str,
        limit: int = 100
    ) -> List[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(session: AsyncSession, message_id: str) -> Optional[Message]:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_by_conversation(session: AsyncSession, conversation_id: str) -> int:
        messages = await MessageRepository.get_by_conversation(session, conversation_id)
        count = len(messages)
        for message in messages:
            await session.delete(message)
        return count
