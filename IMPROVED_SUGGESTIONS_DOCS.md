# Improved AI Suggestion Service - Technical Documentation

## Overview

The suggestion service has been significantly improved to generate **context-aware, topic-specific** follow-up questions instead of generic suggestions.

## Key Improvements

### 1. Enhanced Prompt Engineering

**Before:**
```
"Based on this conversation, generate 3-4 short follow-up questions..."
```

**After:**
```
"You are helping generate specific follow-up questions for an ongoing conversation.

Generate 4 follow-up questions that:
1. Directly reference the specific topic being discussed
2. Are natural questions the user would realistically ask next
3. Build on what was just said in the conversation
4. Are specific, not generic
5. Are between 15-60 characters each

Examples of GOOD questions:
- "What's the syntax for list comprehensions?"
- "How do I handle authentication errors?"

Examples of BAD questions (too generic):
- "Can you explain more?"
- "What are the benefits?"
```

### 2. Better Context Handling

**Changes:**
- Increased from 6 to **8 messages** for better context
- Extended content preview from 200 to **250 characters**
- Clear role labeling: `User:` and `Assistant:`
- Prioritizes latest user messages and last assistant response

### 3. Anti-Generic Filtering

**Filters out suggestions containing:**
- "can you explain more"
- "what are the benefits"
- "how does this work"
- "tell me more"
- "explain further"

**Result:** Only topic-specific suggestions pass through.

### 4. Improved Parsing

**New Features:**
- **Duplicate detection** (case-insensitive)
- **Minimum length:** 15 characters (was 5)
- **Maximum length:** 60 characters
- **Auto question marks** if missing
- **Empty line removal**

### 5. Relevance Validation

**Process:**
1. Extract topic keywords from conversation
2. Check if suggestions contain related keywords
3. If not relevant → **retry once**
4. If still not relevant → fallback to defaults

**Example:**
```
Conversation about "Python lists"
Keywords: ["python", "lists", "create", "mutable"]

✓ Valid: "How do I append items to a list?"
✗ Invalid: "What are the main features?"
```

### 6. Smart Fallback Logic

**Defaults used ONLY for:**
- Empty conversations
- LLM failures
- Parsing failures
- Relevance validation failures (after retry)

**Not used for:** Normal operation with valid context

### 7. Enhanced Logging

**Logs include:**
- Topic keywords detected
- Fallback usage reasons
- Duplicate removal count
- Retry attempts

**Does NOT log:**
- Full prompts
- Full message contents
- Sensitive data

## Code Structure

### Main Methods

#### `generate_suggestions(history)`
Main entry point. Orchestrates the entire suggestion generation flow.

#### `_format_history(history)`
Formats conversation with clear User/Assistant labels.

#### `_extract_topic_keywords(history)`
Extracts meaningful keywords (5+ chars) from user messages and last assistant response.

#### `_parse_suggestions(response)`
Parses LLM output with duplicate detection and length validation.

#### `_filter_generic(suggestions)`
Removes generic phrases that don't reference specific topics.

#### `_is_relevant(suggestions, keywords)`
Validates that suggestions contain topic-related keywords.

## Example Outputs

### Python Conversation
**Input:**
```
User: What is Python?
Assistant: Python is a high-level programming language...
User: How do I create a list?
Assistant: You can create a list using square brackets...
```

**Output:**
```
1. What's the syntax for list comprehensions?
2. How do I add items to a list?
3. Can lists contain different data types?
4. What's the difference between lists and tuples?
```

### FastAPI Conversation
**Input:**
```
User: What is FastAPI?
Assistant: FastAPI is a modern web framework...
User: How do I create a POST endpoint?
Assistant: You use the @app.post() decorator...
```

**Output:**
```
1. How do I validate request body data?
2. What's the syntax for path parameters?
3. Can I use async functions with FastAPI?
4. How do I handle authentication in FastAPI?
```

## Performance Characteristics

- **Lightweight:** No embeddings, vector search, or ML models
- **Fast:** Single LLM call (or 2 if retry needed)
- **Stable:** Comprehensive error handling with fallbacks
- **Production-ready:** Logging and monitoring built-in

## Testing

Run the improved test suite:

```bash
cd maditab-chatbot/backend
python test_suggestions_improved.py
```

This will test:
- Python programming conversation
- FastAPI web development conversation
- Machine learning conversation
- Empty history fallback
- Short conversation handling

## Monitoring

Check logs for:

```
INFO - Topic detected: python, lists, create
INFO - Removed 2 generic/duplicate suggestions
WARNING - Generated suggestions not relevant - retrying once
INFO - Using fallback suggestions due to error
```

## Configuration

### Adjustable Parameters

In `suggestion_service.py`:

```python
# History window
recent_history = history[-8:]  # Change 8 to adjust

# Content preview length
content = msg['content'][:250]  # Change 250 to adjust

# Minimum suggestion length
if len(cleaned) < 15:  # Change 15 to adjust

# Maximum suggestions returned
return filtered[:4]  # Change 4 to adjust
```

### Generic Phrases List

Add more phrases to filter:

```python
GENERIC_PHRASES = [
    "can you explain more",
    "what are the benefits",
    "how does this work",
    "tell me more",
    "explain further",
    # Add more here
]
```

## Troubleshooting

### Still getting generic suggestions?

1. Check if LLM is responding properly
2. Verify conversation has enough context (2+ exchanges)
3. Check logs for "using fallback" messages
4. Ensure topic keywords are being extracted

### Suggestions not relevant?

1. Increase history window (8 → 10 messages)
2. Adjust keyword extraction (5+ chars → 4+ chars)
3. Check if retry logic is working
4. Review LLM prompt effectiveness

### Too few suggestions?

1. Lower minimum length (15 → 10 chars)
2. Reduce generic phrase filtering
3. Check duplicate detection logic
4. Review parsing regex patterns

## Future Enhancements (Optional)

If needed later:
- Add caching for repeated conversations
- Implement suggestion ranking
- Add user feedback loop
- Track suggestion click rates
- A/B test different prompts

## Summary

The improved suggestion service now generates **context-aware, topic-specific** questions that feel unique to each conversation, while maintaining lightweight, production-stable implementation.
