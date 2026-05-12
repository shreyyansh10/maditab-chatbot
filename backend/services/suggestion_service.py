import logging
import re
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

DEFAULT_SUGGESTIONS = [
    "Can you explain more?",
    "Give me an example",
    "What are the benefits?",
    "How does this work?"
]

GENERIC_PHRASES = [
    "can you explain more",
    "what are the benefits",
    "how does this work",
    "tell me more",
    "explain further"
]

SUGGESTION_PROMPT = """You are helping generate specific follow-up questions for an ongoing conversation.

Conversation context:
{history}

Generate 4 follow-up questions that:
1. Directly reference the specific topic being discussed
2. Are natural questions the user would realistically ask next
3. Build on what was just said in the conversation
4. Are specific, not generic (avoid "explain more", "what are benefits", etc.)
5. Are between 15-60 characters each

Examples of GOOD questions:
- "What's the syntax for list comprehensions?"
- "How do I handle authentication errors?"
- "Can FastAPI work with PostgreSQL?"

Examples of BAD questions (too generic):
- "Can you explain more?"
- "What are the benefits?"
- "How does this work?"

Return ONLY the 4 questions, one per line, no numbering or bullets:"""


class SuggestionService:
    """Generate contextual follow-up question suggestions."""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
    
    async def generate_suggestions(self, history: List[Dict[str, Any]]) -> List[str]:
        """
        Generate contextual follow-up questions based on conversation history.
        
        Args:
            history: List of conversation messages with 'role' and 'content'
            
        Returns:
            List of 3-4 follow-up question strings
        """
        try:
            # Use only last 8 messages for context
            recent_history = history[-8:] if len(history) > 8 else history
            
            if not recent_history:
                logger.info("Empty conversation - using default suggestions")
                return DEFAULT_SUGGESTIONS
            
            # Extract topic keywords for validation
            topic_keywords = self._extract_topic_keywords(recent_history)
            logger.info(f"Topic detected: {', '.join(list(topic_keywords)[:3])}")
            
            # Format history for prompt (prioritize latest messages)
            formatted_history = self._format_history(recent_history)
            
            # Build prompt
            prompt = SUGGESTION_PROMPT.format(history=formatted_history)
            
            # Generate suggestions
            logger.info("Generating context-aware follow-up suggestions")
            response = await self.llm_manager.generate(prompt)
            
            if not response:
                logger.warning("Empty LLM response - using fallback")
                return DEFAULT_SUGGESTIONS
            
            # Parse and filter suggestions
            suggestions = self._parse_suggestions(response)
            
            # Remove generic suggestions
            filtered = self._filter_generic(suggestions)
            duplicates_removed = len(suggestions) - len(filtered)
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} generic/duplicate suggestions")
            
            # Validate relevance
            if filtered and not self._is_relevant(filtered, topic_keywords):
                logger.warning("Generated suggestions not relevant - retrying once")
                # Retry once
                response = await self.llm_manager.generate(prompt)
                if response:
                    suggestions = self._parse_suggestions(response)
                    filtered = self._filter_generic(suggestions)
                    
                    if not self._is_relevant(filtered, topic_keywords):
                        logger.warning("Retry failed - using fallback")
                        return DEFAULT_SUGGESTIONS
            
            if not filtered:
                logger.warning("No valid suggestions after filtering - using fallback")
                return DEFAULT_SUGGESTIONS
            
            return filtered[:4]  # Return max 4 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}", exc_info=True)
            logger.info("Using fallback suggestions due to error")
            return DEFAULT_SUGGESTIONS
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Format conversation history with clear labels.
        Prioritize latest messages.
        """
        formatted_lines = []
        for msg in history:
            role = msg['role'].capitalize()
            content = msg['content'][:250]  # Slightly longer context
            formatted_lines.append(f"{role}: {content}")
        
        return "\n".join(formatted_lines)
    
    def _extract_topic_keywords(self, history: List[Dict[str, Any]]) -> Set[str]:
        """
        Extract key topic words from conversation for relevance checking.
        """
        keywords = set()
        
        # Focus on user messages and last assistant message
        relevant_messages = [msg for msg in history if msg['role'] == 'user']
        if history and history[-1]['role'] == 'assistant':
            relevant_messages.append(history[-1])
        
        for msg in relevant_messages:
            content = msg['content'].lower()
            # Extract words longer than 4 characters (likely meaningful)
            words = re.findall(r'\b[a-z]{5,}\b', content)
            keywords.update(words[:10])  # Limit to avoid bloat
        
        return keywords
    
    def _parse_suggestions(self, response: str) -> List[str]:
        """
        Parse LLM response into clean suggestion list.
        
        Args:
            response: Raw LLM output
            
        Returns:
            List of cleaned suggestion strings
        """
        suggestions = []
        seen = set()  # Track duplicates
        
        # Split by newlines
        lines = response.strip().split('\n')
        
        for line in lines:
            # Clean the line
            cleaned = line.strip()
            
            # Remove numbering (1., 2), 1:, etc.)
            cleaned = re.sub(r'^\d+[\.\):\-]\s*', '', cleaned)
            
            # Remove bullets (-, *, •)
            cleaned = re.sub(r'^[\-\*•]\s*', '', cleaned)
            
            # Remove markdown (**, __, etc.)
            cleaned = re.sub(r'[\*_`]', '', cleaned)
            
            # Remove quotes
            cleaned = cleaned.strip('"\'')
            
            # Skip empty or very short lines (minimum 15 chars)
            if len(cleaned) < 15:
                continue
            
            # Truncate to 60 chars
            if len(cleaned) > 60:
                cleaned = cleaned[:57] + "..."
            
            # Add question mark if missing
            if cleaned and not cleaned.endswith('?'):
                cleaned += '?'
            
            # Check for duplicates (case-insensitive)
            normalized = cleaned.lower()
            if normalized in seen:
                continue
            
            seen.add(normalized)
            suggestions.append(cleaned)
        
        return suggestions
    
    def _filter_generic(self, suggestions: List[str]) -> List[str]:
        """
        Remove generic suggestions that don't reference specific topics.
        """
        filtered = []
        
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            
            # Check if it contains generic phrases
            is_generic = any(
                generic in suggestion_lower 
                for generic in GENERIC_PHRASES
            )
            
            if not is_generic:
                filtered.append(suggestion)
        
        return filtered
    
    def _is_relevant(self, suggestions: List[str], topic_keywords: Set[str]) -> bool:
        """
        Check if suggestions contain keywords related to conversation topic.
        """
        if not topic_keywords:
            return True  # Can't validate without keywords
        
        # Check if at least one suggestion contains a topic keyword
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            suggestion_words = set(re.findall(r'\b[a-z]{5,}\b', suggestion_lower))
            
            # Check for overlap with topic keywords
            if suggestion_words & topic_keywords:
                return True
        
        return False
