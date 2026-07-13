import os
import json

GEMINI_MODEL = "gemini-3.1-flash-lite"

def generate_refactor_snippet(filename: str, file_path: str, api_key: str) -> str:
    if not api_key:
        return "⚠️ *Error:* `GEMINI_API_KEY` is required for the AI Architect to generate code."
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        prompt = (
            f"You are a Staff Software Engineer. The file `{filename}` is a structural bottleneck "
            "because it tightly couples internal systems to the external payment SDK (Stripe).\n\n"
            "Here is the current code:\n"
            f"```python\n{code}\n```\n\n"
            "Task 1: Write an 'Executive Translation' (2-3 sentences max). Explain what this refactor "
            "does for a non-technical CEO using a simple real-world analogy (e.g., 'Instead of hardwiring "
            "the lamp to the house, we installed a universal wall outlet'). Explain that this makes switching "
            "billing providers cheap and easy.\n\n"
            "Task 2: Write a complete, drop-in replacement for this file using the Adapter or Facade pattern. "
            "Return the code inside a markdown block.\n\n"
            "Format your response exactly like this:\n"
            "**👔 Executive Translation:**\n[Your analogy here]\n\n"
            "**💻 Engineering Implementation:**\n```python\n[Your code here]\n```"
        )
        
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={"temperature": 0.2}
        )
        return response.text
        
    except Exception as e:
        return f"⚠️ *Error generating refactor:* {str(e)}"
