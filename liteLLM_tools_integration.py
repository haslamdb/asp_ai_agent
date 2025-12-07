from litellm import completion

response = completion(
    model="anthropic/claude-sonnet-4-5-20250514",  # or ollama/qwen2.5:72b
    messages=messages,
    tools=TOOLS
)