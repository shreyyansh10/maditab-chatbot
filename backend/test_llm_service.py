import asyncio
import logging
import sys
from services.llm_service import OllamaLLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test():
    print("Testing OllamaLLMService...")
    
    try:
        service = OllamaLLMService()
        print("[OK] Service initialized successfully")
        
        response = await service.generate('Say hello in one sentence')
        print(f"[OK] Response received: {response}")
        
        if response:
            print("[OK] Test passed!")
        else:
            print("[FAIL] Test failed: Empty response")
            
    except Exception as e:
        print(f"[FAIL] Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
