import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import ConversationRepository, MessageRepository

logger = logging.getLogger(__name__)

class ConversationService:
    
    @staticmethod
    async def create_conversation(session: AsyncSession, title: str = "New Conversation") -> Dict[str, Any]:
        """Create a new conversation."""
        try:
            conversation = await ConversationRepository.create(session, title=title)
            logger.info(f"Created conversation with ID: {conversation.id}")
            return {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at
            }
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
            raise ValueError("Failed to create conversation")
            
    @staticmethod
    async def get_all_conversations(session: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conversations."""
        try:
            conversations = await ConversationRepository.get_all(session, limit)
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at
                }
                for conv in conversations
            ]
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}", exc_info=True)
            raise ValueError("Failed to retrieve conversations")

    @staticmethod
    async def get_conversation_with_messages(session: AsyncSession, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID with its messages."""
        try:
            conversation = await ConversationRepository.get_by_id(session, conversation_id)
            if not conversation:
                return None
                
            messages = await MessageRepository.get_by_conversation(session, conversation_id)
            
            return {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "messages": [
                    {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at
                    }
                    for msg in messages
                ]
            }
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}", exc_info=True)
            raise ValueError("Failed to retrieve conversation details")

    @staticmethod
    async def save_message(session: AsyncSession, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        """Save a new message to a conversation."""
        # Validation
        if role not in ("user", "assistant"):
            raise ValueError("Role must be 'user' or 'assistant'")
        
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")
            
        try:
            # Check if conversation exists
            conversation = await ConversationRepository.get_by_id(session, conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
                
            # Business logic: Auto-generate title from first user message
            if role == "user" and conversation.title == "New Conversation":
                # Check if this is the first message
                existing_messages = await MessageRepository.get_by_conversation(session, conversation_id, limit=1)
                if not existing_messages:
                    # Normalize whitespace
                    clean_content = re.sub(r'\s+', ' ', content.strip())
                    new_title = clean_content[:50] + ("..." if len(clean_content) > 50 else "")
                    conversation.title = new_title
                    
            # Save message
            message = await MessageRepository.create(
                session, 
                conversation_id=conversation_id, 
                role=role, 
                content=content
            )
            
            # Auto-update conversation timestamp
            await ConversationRepository.update_timestamp(session, conversation_id)
            
            logger.info(f"Saved {role} message to conversation {conversation_id}")
            
            return {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}", exc_info=True)
            raise ValueError("Failed to save message")

    @staticmethod
    async def delete_conversation(session: AsyncSession, conversation_id: str) -> bool:
        """Delete a conversation and its messages."""
        try:
            success = await ConversationRepository.delete(session, conversation_id)
            if success:
                logger.info(f"Deleted conversation {conversation_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}", exc_info=True)
            raise ValueError("Failed to delete conversation")
