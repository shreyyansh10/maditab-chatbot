# Quick Start - Testing AI Suggestions

## Backend Setup

1. **Start the backend server:**
```bash
cd maditab-chatbot/backend
python main.py
```

2. **Test suggestion service (optional):**
```bash
python test_suggestions.py
```

## Frontend Setup

1. **Start the frontend:**
```bash
cd maditab-chatbot/frontend
npm run dev
```

## How It Works

### User Flow:
1. User sends a message
2. AI responds
3. **Suggestion pills appear** above the input box
4. User clicks a suggestion → it sends as a new message
5. New suggestions appear after the next AI response

### Visual Example:

```
┌─────────────────────────────────────────────┐
│  User: What is Python?                      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  AI: Python is a programming language...    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  [Can you explain more?] [Give me an        │
│   example] [What are the benefits?]         │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │ Type your message...               │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

## API Testing

### Test the endpoint directly:

```bash
# Get suggestions for a conversation
curl http://localhost:8000/api/chat/suggestions/{conversation_id}
```

### Expected Response:
```json
{
  "conversation_id": "abc-123",
  "suggestions": [
    "Can you explain more?",
    "Give me an example",
    "What are the benefits?",
    "How does this work?"
  ]
}
```

## Features to Test

✅ **Contextual Suggestions**
- Have a conversation about a topic
- Check if suggestions are relevant to the topic

✅ **Clickable Pills**
- Click a suggestion
- Verify it sends as a user message

✅ **Loading States**
- Watch for skeleton loading while fetching suggestions
- Verify smooth transitions

✅ **Error Handling**
- Stop backend → suggestions should show defaults
- No UI crashes

✅ **Visual Design**
- Brown theme matching
- Hover effects
- Responsive wrapping

## Troubleshooting

### No suggestions appearing?
- Check browser console for errors
- Verify backend is running
- Check conversation_id is valid

### Default suggestions only?
- LLM might be unavailable
- Check backend logs
- This is expected behavior (graceful fallback)

### Styling issues?
- Verify Tailwind CSS is configured
- Check brown color classes exist in theme

## Next Steps

Once tested, you can:
- Adjust suggestion prompt in `suggestion_service.py`
- Modify default suggestions
- Customize styling in `SuggestionBar.jsx`
- Add more sophisticated parsing logic
