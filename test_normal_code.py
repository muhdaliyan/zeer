"""Test normal markdown code blocks (not Gemini's weird format)"""

from src.cli_interface import display_assistant_message

# Normal markdown code block
normal_response = """Here's a simple Python function:

```python
def greet(name):
    message = f"Hello, {name}!"
    print(message)
    return message

if __name__ == "__main__":
    greet("World")
```

This function prints a greeting message."""

print("=" * 80)
print("Testing Normal Markdown Code Blocks")
print("=" * 80)

display_assistant_message(
    message=normal_response,
    model="gemini-2.5-flash",
    tokens={"completionTokens": 50, "promptTokens": 20},
    elapsed_time=1.2,
    context_window=1000000
)

print("=" * 80)
print("✓ Normal markdown code blocks should also work")
print("=" * 80)
