import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.llm_manager import LLMManager
from services.suggestion_service import SuggestionService

async def test_suggestions():
    print("Testing SuggestionService...")
    
    # Initialize services
    llm_manager = LLMManager()
    suggestion_service = SuggestionService(llm_manager)
    
    # Test with sample conversation history
    sample_history = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language known for its simplicity and readability."},
        {"role": "user", "content": "What are its main features?"},
        {"role": "assistant", "content": "Python's main features include dynamic typing, automatic memory management, extensive standard library, and support for multiple programming paradigms."}
    ]
    
    print("\nGenerating suggestions for sample conversation...")
    suggestions = await suggestion_service.generate_suggestions(sample_history)
    
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    # Test with empty history
    print("\n\nTesting with empty history (should return defaults)...")
    default_suggestions = await suggestion_service.generate_suggestions([])
    print(f"Default suggestions: {default_suggestions}")
    
    print("\n✓ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_suggestions())
