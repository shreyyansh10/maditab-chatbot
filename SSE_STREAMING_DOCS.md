# SSE Streaming Implementation - Documentation

## Overview

Implemented lightweight Server-Sent Events (SSE) streaming for real-time AI response rendering using a **chunk-based approach** (not true token streaming).

### Architecture Choice

**Chunk-Based Streaming:**
- Generate full response using existing LLMManager
- Split response into words/chunks
- Stream chunks progressively to frontend
- Provider-independent and stable

**NOT Implemented:**
- True token-level provider streaming
- WebSocket connections
- Complex queue systems

---

## Backend Implementation

### 1. Stream Schema (`schemas/stream.py`)

**StreamRequest:**
```python
{
  "message": "Tell me about Python",
  "conversation_id": "optional-uuid"
}
```

**StreamChunk:**
```python
{
  "type": "conversation_id" | "token" | "done" | "error",
  "content": "optional content",
  "conversation_id": "uuid",
  "message_id": "msg-uuid"
}
```

### 2. Stream Router (`routers/stream.py`)

**Endpoint:** `POST /api/chat/stream`

**Flow:**
1. Create conversation if missing
2. Save user message
3. Send `conversation_id` event
4. Generate full response using LLMManager
5. Split into words
6. Stream chunks with 30ms delay
7. Save assistant message
8. Send `done` event

**SSE Format:**
```
data: {"type":"token","content":"Hello"}\n\n
data: {"type":"done","conversation_id":"..."}\n\n
```

**Headers:**
```python
{
  "Cache-Control": "no-cache",
  "Connection": "keep-alive",
  "X-Accel-Buffering": "no"
}
```

### 3. LLM Manager Update (`services/llm_manager.py`)

**Added Method:**
```python
async def generate_stream(prompt: str) -> AsyncGenerator[str, None]:
    full_response = await self.generate(prompt)
    words = full_response.split()
    for i, word in enumerate(words):
        yield word if i == 0 else f" {word}"
```

**Note:** Currently not used in router (router splits directly), but available for future use.

---

## Frontend Implementation

### 1. API Streaming (`services/api.js`)

**Function:** `sendMessageStream(message, conversationId, callbacks)`

**Callbacks:**
- `onConversationId(convId)` - New conversation created
- `onToken(content)` - Chunk received
- `onDone(data)` - Stream complete
- `onError(error)` - Stream error

**Implementation:**
- Uses native `fetch()` API
- Manual SSE parsing
- Handles `data: ` prefix
- Parses JSON events

**Example:**
```javascript
await sendMessageStream(message, conversationId, {
  onToken: (token) => console.log(token),
  onDone: (data) => console.log('Done:', data),
  onError: (error) => console.error(error)
});
```

### 2. Chat Interface (`components/ChatInterface.jsx`)

**New State:**
```javascript
const [isStreaming, setIsStreaming] = useState(false);
const streamingMessageIdRef = useRef(null);
```

**Flow:**
1. Add user message (optimistic)
2. Add temporary streaming assistant message
3. Start SSE stream
4. Update streaming message with chunks
5. Finalize message on completion
6. Load suggestions
7. **Fallback to normal API on error**

**Streaming Message:**
```javascript
{
  role: 'assistant',
  content: '', // Updated progressively
  id: 'streaming-123',
  isStreaming: true
}
```

**Fallback Logic:**
```javascript
try {
  await sendMessageStream(...);
} catch (error) {
  // Remove streaming message
  // Use normal sendMessage() API
}
```

### 3. Message List (`components/MessageList.jsx`)

**Streaming Cursor:**
```jsx
{msg.isStreaming && (
  <span className="inline-block w-2 h-4 ml-1 bg-brown-600 animate-pulse"></span>
)}
```

**Features:**
- Blinking cursor during streaming
- Smooth content updates
- Error message styling
- Proper key management

---

## Event Flow

### Normal Streaming Flow

```
Client                          Server
  |                               |
  |-- POST /api/chat/stream ----->|
  |                               |
  |<-- conversation_id event -----|
  |<-- token: "Hello" ------------|
  |<-- token: " world" -----------|
  |<-- token: "!" ----------------|
  |<-- done event ----------------|
  |                               |
```

### Error Flow with Fallback

```
Client                          Server
  |                               |
  |-- POST /api/chat/stream ----->|
  |<-- error event ----------------|
  |                               |
  |-- POST /api/chat/message ----->|
  |<-- full response --------------|
  |                               |
```

---

## Key Features

### ✅ Streaming
- Progressive response rendering
- 30ms delay between chunks
- Blinking cursor animation
- Smooth updates

### ✅ Fallback
- Automatic fallback to normal API
- No UI crashes
- Seamless user experience
- Error logging

### ✅ State Management
- Temporary streaming messages
- Proper message finalization
- Conversation ID tracking
- Duplicate prevention

### ✅ Error Handling
- Stream disconnects
- Backend errors
- Network failures
- Graceful degradation

---

## Configuration

### Chunk Delay (Backend)
```python
# routers/stream.py
await asyncio.sleep(0.03)  # 30ms between chunks
```

### Streaming Toggle (Frontend)
```javascript
// To disable streaming, comment out:
await sendMessageStream(...)
// And use:
await sendMessage(...)
```

---

## Testing

### Test Streaming
1. Send a message
2. Watch response appear word-by-word
3. See blinking cursor during streaming
4. Verify cursor disappears when done

### Test Fallback
1. Stop backend
2. Send a message
3. Verify error is caught
4. Restart backend
5. Send message again
6. Verify fallback to normal API works

### Test Conversation Creation
1. Start new chat
2. Send first message
3. Verify `conversation_id` event received
4. Verify conversation appears in sidebar

---

## Performance

### Metrics
- **Chunk delay:** 30ms
- **Network overhead:** Minimal (SSE is efficient)
- **Memory:** Temporary streaming message
- **Rendering:** Smooth (React updates)

### Optimization
- Small chunk size (words, not characters)
- Efficient SSE parsing
- Minimal state updates
- Proper cleanup

---

## Logging

### Backend
```
INFO - Generating full response
INFO - Streaming response in chunks
INFO - Saving assistant message
ERROR - Error in stream generation: ...
```

### Frontend
```
Starting SSE stream: /api/chat/stream
Received conversation_id: abc-123
Stream complete
Stream error, falling back to normal API
```

---

## Architecture Principles

✅ **Lightweight** - No heavy dependencies
✅ **Provider-independent** - Works with any LLM
✅ **Stable** - Comprehensive fallback
✅ **Hackathon-friendly** - Simple implementation
✅ **Production-ready** - Error handling

---

## What Was NOT Implemented

❌ True token-level streaming
❌ WebSocket connections
❌ Stream cancellation
❌ Retry systems
❌ Typing speed controls
❌ Analytics
❌ Caching

---

## Future Enhancements (Optional)

If needed later:
- Add stream cancellation (AbortController)
- Add typing speed configuration
- Add character-level streaming
- Add stream progress indicator
- Add retry logic

---

## Troubleshooting

### Streaming not working?
1. Check backend logs for errors
2. Verify `/api/chat/stream` endpoint exists
3. Check browser console for SSE errors
4. Verify CORS headers allow streaming

### Fallback always triggered?
1. Check backend is running
2. Verify stream endpoint returns SSE format
3. Check for network issues
4. Review backend error logs

### Cursor not showing?
1. Verify `isStreaming` state is true
2. Check message has `isStreaming: true`
3. Verify Tailwind `animate-pulse` works

---

## Summary

Implemented lightweight SSE streaming with:
- ✅ Chunk-based streaming (not token-level)
- ✅ Progressive response rendering
- ✅ Blinking cursor animation
- ✅ Automatic fallback to normal API
- ✅ Comprehensive error handling
- ✅ Provider-independent architecture

**Result:** Real-time streaming chat UX with stable fallback behavior! 🚀
