# SSE Streaming - Quick Test Guide

## 🎯 What to Test

1. **Streaming Response** - Words appear progressively
2. **Blinking Cursor** - Cursor shows during streaming
3. **Fallback** - Normal API works if streaming fails
4. **Conversation Creation** - New chats work with streaming
5. **Suggestions** - Load after streaming completes

---

## 🧪 Test Scenarios

### Test 1: Basic Streaming
```
1. Open the chat
2. Send message: "Tell me about Python"
3. ✅ Watch response appear word-by-word
4. ✅ See blinking cursor during streaming
5. ✅ Cursor disappears when done
6. ✅ Suggestions appear after completion
```

### Test 2: New Conversation
```
1. Click "New Chat"
2. Send first message
3. ✅ Streaming works
4. ✅ Conversation appears in sidebar
5. ✅ Suggestions load
```

### Test 3: Long Response
```
1. Ask: "Explain machine learning in detail"
2. ✅ Response streams smoothly
3. ✅ No lag or freezing
4. ✅ Auto-scrolls to bottom
5. ✅ Cursor visible throughout
```

### Test 4: Rapid Messages
```
1. Send message
2. Wait for streaming to start
3. ✅ Cannot send another message during streaming
4. Wait for completion
5. Send another message
6. ✅ Second message streams correctly
```

### Test 5: Fallback (Backend Down)
```
1. Stop backend server
2. Send a message
3. ✅ Error is caught
4. ✅ UI doesn't crash
5. Restart backend
6. Send message
7. ✅ Works normally
```

### Test 6: Conversation Switch During Stream
```
1. Send message in Chat A
2. While streaming, switch to Chat B
3. ✅ Streaming stops/completes in Chat A
4. ✅ Chat B loads correctly
5. ✅ No mixed content
```

---

## 📊 Visual Checks

### Streaming Cursor
- [ ] Cursor is visible during streaming
- [ ] Cursor blinks (animate-pulse)
- [ ] Cursor is brown color
- [ ] Cursor disappears when done

### Response Rendering
- [ ] Words appear progressively
- [ ] No flickering
- [ ] Smooth updates
- [ ] Auto-scrolls to bottom

### Loading States
- [ ] "Assistant is thinking..." shows before stream
- [ ] Disappears when streaming starts
- [ ] Suggestions load after completion

---

## 🔍 Console Logs to Watch

### ✅ Good Patterns

**Streaming Start:**
```
Clearing suggestions before sending message
Starting SSE stream: /api/chat/stream
```

**Streaming Progress:**
```
Received conversation_id: abc-123
Stream: New conversation created: abc-123
```

**Streaming Complete:**
```
Stream complete: {conversation_id: "...", message_id: "..."}
Loading suggestions for: abc-123
```

**Fallback:**
```
Stream error, falling back to normal API: ...
Streaming failed, using fallback: ...
```

### ❌ Bad Patterns (Should NOT See)

```
// Uncaught errors
Uncaught Error: ...

// No fallback
Stream error: ... (and then UI crashes)

// Duplicate messages
// Same message appearing twice
```

---

## 🐛 Debugging

### Streaming not working?

**Check Backend:**
```bash
# Verify endpoint exists
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

**Check Browser Console:**
```
Look for: "Starting SSE stream"
Look for: SSE events being received
Look for: Error messages
```

**Check Network Tab:**
```
Filter: "stream"
Verify: Request is sent
Verify: Response is text/event-stream
Verify: Events are received
```

### Cursor not showing?

**Check Message State:**
```javascript
// In React DevTools, check message object:
{
  role: 'assistant',
  content: '...',
  isStreaming: true  // Should be true during streaming
}
```

**Check CSS:**
```
Verify: animate-pulse class exists
Verify: Tailwind is loaded
Verify: No CSS conflicts
```

### Fallback not working?

**Check Error Handling:**
```
Look for: "Stream error, falling back"
Look for: Normal API call after error
Verify: Message still appears
```

---

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

[ ] Test 1: Basic Streaming - PASS/FAIL
[ ] Test 2: New Conversation - PASS/FAIL
[ ] Test 3: Long Response - PASS/FAIL
[ ] Test 4: Rapid Messages - PASS/FAIL
[ ] Test 5: Fallback - PASS/FAIL
[ ] Test 6: Conversation Switch - PASS/FAIL

Visual Checks:
[ ] Streaming cursor - PASS/FAIL
[ ] Progressive rendering - PASS/FAIL
[ ] Auto-scroll - PASS/FAIL

Console Logs: CLEAN / ERRORS FOUND
Network: STREAMING / FALLBACK / ERRORS
Overall: PASS / FAIL

Notes:
_________________________________
_________________________________
```

---

## 🎬 Demo Script

**30-Second Demo:**
```
1. "Watch the AI response stream in real-time"
2. Send: "Explain Python in 3 sentences"
3. Point out: "See the blinking cursor?"
4. Point out: "Words appear progressively"
5. Point out: "Suggestions load after completion"
```

**2-Minute Demo:**
```
1. Show basic streaming
2. Show new conversation creation
3. Show long response streaming
4. Show fallback (stop backend)
5. Show recovery (restart backend)
```

---

## ✅ Success Criteria

After testing, you should see:

1. ✅ Responses stream word-by-word
2. ✅ Blinking cursor during streaming
3. ✅ Smooth, no lag
4. ✅ Auto-scrolls to bottom
5. ✅ Suggestions load after completion
6. ✅ Fallback works on errors
7. ✅ No UI crashes
8. ✅ Console logs are clean

---

## 🚀 Quick Verification

**10-Second Test:**
```
1. Send message
2. Watch for streaming cursor
3. See words appear progressively
4. Verify cursor disappears when done
```

**If all 4 steps work, streaming is working! ✅**

---

## 🎉 Expected Result

**Before Streaming:**
- Response appears all at once
- No visual feedback during generation
- Feels slow

**After Streaming:**
- Response appears progressively ✅
- Blinking cursor shows activity ✅
- Feels fast and responsive ✅
- Real-time chat experience ✅
