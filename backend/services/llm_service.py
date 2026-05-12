import logging
import time

from langchain_community.llms import Ollama

from config import get_settings

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when connection to Ollama fails."""
    pass


class OllamaLLMService:
    """Simple LangChain wrapper around Ollama for text generation."""

    def __init__(self):
        settings = get_settings()

        self.model_name = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_history = []

        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.7,
                num_ctx=2048,
                timeout=120,
            )

            logger.info(
                f"OllamaLLMService initialized "
                f"with model={self.model_name}, "
                f"base_url={self.base_url}"
            )

        except Exception as e:
            logger.error(
                f"Failed to initialize Ollama: {e}",
                exc_info=True
            )

            raise OllamaConnectionError(
                f"Could not connect to Ollama at {self.base_url}"
            )
            
    async def clear_memory(self):
        """Clear temporary conversation memory."""
        self.chat_history = []

    async def generate(self, prompt: str) -> str:
        """
        Generate text response from Ollama.

        Args:
            prompt: Input text prompt

        Returns:
            Generated text response
        """

        start_time = time.time()
        
        # Build prompt manually using recent history
        context = ""
        for msg in self.chat_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
            
        full_prompt = f"Context:\n{context}\nUser: {prompt}\nAssistant:" if context else prompt

        try:
            logger.info(
                f"Generating response "
                f"(length={len(full_prompt)}, model={self.model_name})"
            )

            response = await self.llm.ainvoke(full_prompt)

            if not response or not response.strip():
                raise OllamaConnectionError(
                    "Empty response from Ollama"
                )

            elapsed = time.time() - start_time

            logger.info(
                f"Response generated successfully in {elapsed:.2f}s"
            )
            
            response_text = response.strip()
            
            self.chat_history.append({"role": "user", "content": prompt})
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 messages (5 pairs)
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]

            return response_text

        except Exception as e:
            logger.error(
                f"Error generating response: {e}",
                exc_info=True
            )

            raise OllamaConnectionError(
                "Failed to generate response"
            )