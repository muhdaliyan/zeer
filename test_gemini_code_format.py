"""
Test script to simulate Gemini's actual code response format.
This tests the code display with Gemini's weird format:
- Fake ANSI codes like [35m instead of \x1b[35m
- Line numbers embedded in the code
"""

from src.cli_interface import display_assistant_message

# Simulate Gemini's actual response format
gemini_response = """Here is the palindrome code from palindrome.py:

python
1 [35mdef[37m [33mis_palindrome[37m(text):
2     processed_text [31m=[37m [32m""[37m.[33mjoin[37m(char.[33mlower[37m() [35mfor[37m char [35min[37m text [35mif[37m char.[33misalnum[37m())
3     [35mreturn[37m processed_text [31m==[37m processed_text[::[31m-[37m[36m1[37m]
4
5 [35mif[37m __name__ [31m==[37m [32m"__main__"[37m:
6     test_strings [31m=[37m [
7         [32m"madam"[37m,
8         [32m"A man, a plan, a canal: Panama"[37m,
9         [32m"racecar"[37m,
10         [32m"hello"[37m,
11     ]
12
13     [35mfor[37m s [35min[37m test_strings:
14         [35mif[37m [33mis_palindrome[37m(s):
15             [33mprint[37m(f"[32m'{s}'[37m [35mis[37m a palindrome.")
16         [35melse[37m:
17             [33mprint[37m(f"[32m'{s}'[37m [35mis[37m [35mnot[37m a palindrome.")

This code checks if strings are palindromes by removing non-alphanumeric characters."""

print("=" * 80)
print("Testing Gemini Code Format Display")
print("=" * 80)
print("\nGemini's raw response (with fake ANSI codes and line numbers):")
print("-" * 80)
print(gemini_response[:200] + "...")
print("-" * 80)
print("\nProcessed output:")
print("=" * 80)

# Display using the actual function
display_assistant_message(
    message=gemini_response,
    model="gemini-2.5-flash",
    tokens={"completionTokens": 150, "promptTokens": 50},
    elapsed_time=2.5,
    context_window=1000000
)

print("=" * 80)
print("✓ Test complete - code should be displayed with:")
print("  • Language label with white background")
print("  • Line numbers with gray background")
print("  • Code with black background")
print("  • Full syntax highlighting (all elements colored)")
print("=" * 80)
