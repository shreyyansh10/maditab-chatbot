import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PromptService:
    """Service for advanced prompt engineering and context formatting."""

    SYSTEM_PROMPT = (
        "You are a helpful, professional, and concise AI assistant. "
        "Your goal is to provide clear explanations and assist the user with their queries. "
        "Maintain a professional tone and use the provided conversational memory to stay context-aware. "
        "Keep your responses focused and avoid unnecessary fluff."
    )

    @staticmethod
    def detect_intent(message: str) -> str:
        """
        Simple rule-based intent detection.
        """
        msg_lower = message.lower().strip()
        
        greetings = {'hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening'}
        if any(word in msg_lower.split() for word in greetings) or msg_lower in greetings:
            return "greeting"
            
        if '?' in msg_lower or any(word in msg_lower for word in ['how', 'what', 'why', 'where', 'when', 'who', 'can you']):
            return "question"
            
        return "general"

    @staticmethod
    def format_history_for_context(history: List[Dict[str, Any]], limit: int = 10) -> str:
        """
        Format the message history into a clean string for context.
        Uses only the last 'limit' messages.
        """
        try:
            # Use only last N messages
            recent_history = history[-limit:] if history else []
            
            formatted_lines = []
            for msg in recent_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg["content"].strip()
                formatted_lines.append(f"{role}: {content}")
                
            return "\n".join(formatted_lines)
        except Exception as e:
            logger.error(f"Error formatting history: {str(e)}")
            return ""

    @classmethod
    def build_prompt_with_history(cls, message: str, history: List[Dict[str, Any]]) -> str:
        """
        Construct the full prompt including system instructions, history, and the current message.
        """
        try:
            intent = cls.detect_intent(message)
            logger.info(f"Detected intent: {intent} | History size: {len(history)}")
            
            history_context = cls.format_history_for_context(history)
            
            prompt_parts = [
                f"System: {cls.SYSTEM_PROMPT}",
            ]
            
            if history_context:
                prompt_parts.append(f"Recent Conversation:\n{history_context}")
            
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            
            return "\n\n".join(prompt_parts)
        except Exception as e:
            logger.error(f"Failed to build prompt with history: {str(e)}")
            # Fallback to simple prompt
            return f"User: {message}\nAssistant:"

    @staticmethod
    def format_chat_prompt(message: str, history: List[Dict[str, Any]]) -> str:
        """
        Compatibility method for existing calls.
        """
        return PromptService.build_prompt_with_history(message, history)
