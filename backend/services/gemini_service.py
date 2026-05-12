import logging
import time
import google.generativeai as genai
from config import get_settings

logger = logging.getLogger(__name__)

class GeminiLLMService:
    """Service wrapper for Google Gemini LLM inference."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        
        if not self.api_key:
            logger.warning("Gemini API key not found. Gemini service will be unavailable.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"GeminiLLMService initialized with model={self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}", exc_info=True)
                self.model = None

    async def generate(self, prompt: str) -> str:
        """
        Generate text response using Gemini.
        """
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        start_time = time.time()
        try:
            logger.info(f"Generating Gemini response for prompt (length={len(prompt)})")
            
            # Gemini's generate_content is synchronous in the basic SDK, 
            # but for a hackathon-friendly implementation we'll keep it simple.
            # In a production app, we might use the async SDK or run in a thread.
            response = self.model.generate_content(prompt)
            
            response_text = response.text
            elapsed = time.time() - start_time
            logger.info(f"Gemini response generated in {elapsed:.2f}s")
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            raise RuntimeError(f"Gemini generation failed: {str(e)}")
