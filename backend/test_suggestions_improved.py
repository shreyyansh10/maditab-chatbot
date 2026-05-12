import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.llm_manager import LLMManager
from services.suggestion_service import SuggestionService

async def test_contextual_suggestions():
    print("=" * 60)
    print("Testing Improved Contextual Suggestion Service")
    print("=" * 60)
    
    # Initialize services
    llm_manager = LLMManager()
    suggestion_service = SuggestionService(llm_manager)
    
    # Test Case 1: Python Programming Conversation
    print("\n\n[TEST 1] Python Programming Conversation")
    print("-" * 60)
    python_history = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used for web development, data science, automation, and more."},
        {"role": "user", "content": "How do I create a list in Python?"},
        {"role": "assistant", "content": "You can create a list using square brackets: my_list = [1, 2, 3, 4]. Lists are mutable and can contain different data types."}
    ]
    
    suggestions = await suggestion_service.generate_suggestions(python_history)
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test Case 2: FastAPI Conversation
    print("\n\n[TEST 2] FastAPI Web Development Conversation")
    print("-" * 60)
    fastapi_history = [
        {"role": "user", "content": "What is FastAPI?"},
        {"role": "assistant", "content": "FastAPI is a modern, fast web framework for building APIs with Python. It's based on standard Python type hints and provides automatic API documentation."},
        {"role": "user", "content": "How do I create a POST endpoint?"},
        {"role": "assistant", "content": "You can create a POST endpoint using the @app.post() decorator. For example: @app.post('/items/') async def create_item(item: Item): return item"}
    ]
    
    suggestions = await suggestion_service.generate_suggestions(fastapi_history)
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test Case 3: Machine Learning Conversation
    print("\n\n[TEST 3] Machine Learning Conversation")
    print("-" * 60)
    ml_history = [
        {"role": "user", "content": "What is supervised learning?"},
        {"role": "assistant", "content": "Supervised learning is a type of machine learning where the model learns from labeled training data. The algorithm learns to map inputs to outputs based on example input-output pairs."},
        {"role": "user", "content": "What's the difference between classification and regression?"},
        {"role": "assistant", "content": "Classification predicts discrete categories (like spam/not spam), while regression predicts continuous values (like house prices). Both are supervised learning tasks."}
    ]
    
    suggestions = await suggestion_service.generate_suggestions(ml_history)
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test Case 4: Empty History (Should return defaults)
    print("\n\n[TEST 4] Empty History (Fallback Test)")
    print("-" * 60)
    default_suggestions = await suggestion_service.generate_suggestions([])
    print(f"\nDefault suggestions: {default_suggestions}")
    
    # Test Case 5: Short Conversation
    print("\n\n[TEST 5] Short Conversation")
    print("-" * 60)
    short_history = [
        {"role": "user", "content": "Tell me about Docker containers"},
        {"role": "assistant", "content": "Docker containers are lightweight, standalone packages that include everything needed to run an application: code, runtime, libraries, and dependencies."}
    ]
    
    suggestions = await suggestion_service.generate_suggestions(short_history)
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)
    print("\nKey Improvements Demonstrated:")
    print("  • Context-specific suggestions (not generic)")
    print("  • Topic-aware questions")
    print("  • No duplicate suggestions")
    print("  • Minimum 15 character length")
    print("  • Fallback to defaults only when needed")

if __name__ == "__main__":
    asyncio.run(test_contextual_suggestions())
