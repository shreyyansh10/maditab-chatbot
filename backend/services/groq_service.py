import logging
import time
from groq import Groq
from config import get_settings

logger = logging.getLogger(__name__)

class GroqLLMService:
    """Service wrapper for Groq LLM inference."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        
        if not self.api_key:
            logger.warning("Groq API key not found. Groq service will be unavailable.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"GroqLLMService initialized with model={self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}", exc_info=True)
                self.client = None

    async def generate(self, prompt: str) -> str:
        """
        Generate text response using Groq.
        """
        if not self.client:
            raise RuntimeError("Groq client not initialized")

        start_time = time.time()
        try:
            logger.info(f"Generating Groq response for prompt (length={len(prompt)})")
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            
            response_text = completion.choices[0].message.content
            elapsed = time.time() - start_time
            logger.info(f"Groq response generated in {elapsed:.2f}s")
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating Groq response: {e}", exc_info=True)
            raise RuntimeError(f"Groq generation failed: {str(e)}")
