---
category: Python
tags: ["python", "loops", "input"]
---
# Name_Loop_Example

### Python Loop that Repeats Until User Types 'stop'

This simple program repeatedly asks the user for their name and prints it back. It terminates automatically when the user types **'stop'** (case‑insensitive).

```python
# Simple name-loop program
while True:                     # keep looping forever
    name = input("Enter your name (or type 'stop' to quit): ")

    if name.lower() == "stop":   # case-insensitive check for quit command
        print("Goodbye!")
        break                   # exit the loop

    print(f"Hello, {name}")         # greet the user with their entered name
```

**How it works**
1. **`while True:`** – creates an infinite loop; the body runs repeatedly until we explicitly `break`.
2. **`input(...)`** – prompts the user for a line of text and stores it in the variable `name`.
3. **`if name.lower() == "stop":`** – converts the entered string to lowercase so “STOP”, “Stop”, or “stop” all trigger the same action.
4. If the condition is true, we print a farewell message and call `break`, which ends the loop.
5. Otherwise, we simply greet the user with their name.

You can run this script in any Python environment (IDLE, VS Code, Jupyter, etc.). Just type names one after another; when you’re done typing “stop”, the program will exit cleanly.

```

<parameter=filename>
name_loop_example.md
