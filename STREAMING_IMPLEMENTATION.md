# Streaming with Tool Calling Implementation

## Overview
Implemented streaming responses with tool calling support for all AI providers in the zeer CLI application.

## Changes Made

### 1. Base Provider Class (`src/provider_base.py`)
- Added `send_message_stream()` method to the `AIProvider` base class
- Default implementation falls back to non-streaming for backward compatibility
- All providers now support streaming as an async generator

### 2. Provider Implementations

#### Ollama Provider (`src/providers/ollama_provider.py`)
- ✅ Implemented `send_message_stream()` with native Ollama streaming
- Uses `stream=True` parameter in `client.chat()`
- Yields text chunks as they arrive
- Accumulates tool calls and yields complete response when done
- Handles thought_signature for models that require it

#### OpenAI Provider (`src/providers/openai_provider.py`)
- ✅ Implemented `send_message_stream()` with SSE parsing
- Parses Server-Sent Events (SSE) format: `data: {json}`
- Accumulates tool call chunks by index
- Handles partial function arguments streaming
- Yields complete tool calls when stream ends

#### Gemini Provider (`src/providers/gemini_provider.py`)
- ✅ Implemented `send_message_stream()` with Gemini streaming API
- Uses `streamGenerateContent` endpoint with `alt=sse` parameter
- Parses SSE format for function calls and text
- Supports image generation in streaming mode
- Handles thought_signature for Gemini 3+ models

#### Claude Provider (`src/providers/claude_provider.py`)
- ✅ Implemented `send_message_stream()` with Claude streaming
- Parses SSE events: `content_block_start`, `content_block_delta`, `content_block_stop`
- Supports fine-grained tool streaming
- Accumulates tool call arguments incrementally
- Handles usage metadata from stream

#### OpenRouter Provider (`src/providers/openrouter_provider.py`)
- ✅ Implemented `send_message_stream()` with OpenAI-compatible streaming
- Uses same SSE format as OpenAI
- Validates tool call JSON before yielding
- Filters out malformed tool calls with warnings
- Full compatibility with underlying provider models

### 3. Chat Session (`src/chat_session.py`)
- Updated `send_message()` to use streaming by default
- Streams text content to console in real-time
- Accumulates content while streaming
- Falls back to non-streaming if streaming fails
- Maintains all existing tool calling logic

## Streaming Format

All providers yield chunks in a consistent format:

```python
# Text content chunk
{
    "type": "content",
    "content": "text chunk"
}

# Tool calls detected
{
    "type": "tool_calls",
    "response": Response(
        content="accumulated text",
        model="model-name",
        usage={...},
        tool_calls=[...]
    )
}

# Stream complete (no tool calls)
{
    "type": "done",
    "response": Response(
        content="accumulated text",
        model="model-name",
        usage={...}
    )
}
```

## Usage Example

```python
# Streaming is now automatic in chat_session
async for chunk in provider.send_message_stream(message, context):
    if chunk["type"] == "content":
        print(chunk["content"], end="", flush=True)
    elif chunk["type"] == "tool_calls":
        response = chunk["response"]
        # Handle tool calls
    elif chunk["type"] == "done":
        response = chunk["response"]
        # Final response
```

## Benefits

1. **Real-time feedback**: Users see responses as they're generated
2. **Better UX**: No waiting for complete response before seeing output
3. **Tool calling preserved**: All tool calling functionality works with streaming
4. **Backward compatible**: Non-streaming methods still available
5. **Consistent interface**: All providers use same streaming format

## Testing

To test streaming:
1. Run any command that generates text responses
2. Observe text appearing character-by-character or word-by-word
3. Tool calls still work normally (displayed after streaming completes)
4. All providers (OpenAI, Gemini, Claude, Ollama, OpenRouter) support streaming

## Notes

- Streaming is enabled by default in `chat_session.py`
- Tool calls are accumulated during streaming and executed after stream completes
- Error handling maintains same behavior as non-streaming
- Usage/token information is collected from final stream chunks
- Telegram bot still uses non-streaming (can be updated separately if needed)
