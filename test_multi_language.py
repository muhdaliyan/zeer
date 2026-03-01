"""Test multiple programming languages"""

from src.cli_interface import display_assistant_message

# Multiple languages
multi_lang_response = """Here are examples in different languages:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

```javascript
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

```java
public class Factorial {
    public static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
}
```

All three implement the same factorial function."""

print("=" * 80)
print("Testing Multiple Languages")
print("=" * 80)

display_assistant_message(
    message=multi_lang_response,
    model="gemini-2.5-flash",
    tokens={"completionTokens": 120, "promptTokens": 30},
    elapsed_time=2.0,
    context_window=1000000
)

print("=" * 80)
print("✓ Multiple languages should all be syntax highlighted")
print("=" * 80)
