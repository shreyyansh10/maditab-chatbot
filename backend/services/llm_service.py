import logging
import time
from typing import Optional
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
        
        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.7,
                num_ctx=500,
                timeout=30
            )
            logger.info(f"OllamaLLMService initialized with model={self.model_name}, base_url={self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}", exc_info=True)
            raise OllamaConnectionError(f"Could not connect to Ollama at {self.base_url}: {str(e)}")
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text response from Ollama.
        
        Args:
            prompt: Input text prompt
            
        Returns:
            Generated text response or empty string on failure
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating response for prompt (length={len(prompt)}, model={self.model_name})")
            
            # LangChain's Ollama doesn't have native async, so we use invoke
            response = self.llm.invoke(prompt)
            
            elapsed = time.time() - start_time
            logger.info(f"Response generated in {elapsed:.2f}s")
            
            return response
            
        except ConnectionError as e:
            logger.error(f"Connection error to Ollama: {e}", exc_info=True)
            return ""
        except TimeoutError as e:
            logger.error(f"Timeout error from Ollama: {e}", exc_info=True)
            return ""
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "model" in error_msg:
                logger.error(f"Model not found: {self.model_name}", exc_info=True)
            else:
                logger.error(f"Error generating response: {e}", exc_info=True)
            return ""
