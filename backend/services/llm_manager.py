import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from services.groq_service import GroqLLMService
from services.gemini_service import GeminiLLMService
from services.llm_service import OllamaLLMService
from services.prompt_service import PromptService

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Orchestrates multiple LLM providers with automatic fallback logic.
    Priority: Groq -> Gemini -> Ollama
    """

    def __init__(self):
        self.groq_service = GroqLLMService()
        self.gemini_service = GeminiLLMService()
        self.ollama_service = OllamaLLMService()
        self.prompt_service = PromptService()

    async def generate(self, prompt: str) -> str:
        """
        Generate response with automatic fallback.
        """
        # 1. Try Groq
        try:
            logger.info("Attempting generation with Groq (Primary)")
            return await self.groq_service.generate(prompt)
        except Exception as e:
            logger.warning(f"Groq failure: {e}. Falling back to Gemini.")

        # 2. Try Gemini
        try:
            logger.info("Attempting generation with Gemini (Secondary Fallback)")
            return await self.gemini_service.generate(prompt)
        except Exception as e:
            logger.warning(f"Gemini failure: {e}. Falling back to Ollama.")

        # 3. Try Ollama
        try:
            logger.info("Attempting generation with Ollama (Local Fallback)")
            return await self.ollama_service.generate(prompt)
        except Exception as e:
            logger.error(f"All LLM providers failed. Final error: {e}")
            raise RuntimeError("All LLM providers failed to generate a response.")

    async def generate_with_context(self, message: str, history: List[Dict[str, Any]]) -> str:
        """
        Format prompt with history and generate response with fallback.
        """
        full_prompt = self.prompt_service.build_prompt_with_history(message, history)
        return await self.generate(full_prompt)
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate response and yield chunks progressively.
        This is a lightweight chunk-based streaming (not true token streaming).
        """
        # Generate full response using existing method
        full_response = await self.generate(prompt)
        
        # Split into words and yield progressively
        words = full_response.split()
        for i, word in enumerate(words):
            # Add space before word (except first)
            yield word if i == 0 else f" {word}"
