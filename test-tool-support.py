#!/usr/bin/env python3
"""Test if an Ollama model supports tool/function calling."""

import sys
from ollama import chat


def test_fn(x: str) -> str:
    """Test function for tool support detection."""
    return x


def test_model(model_name: str) -> bool:
    """Test if a model supports tool calling."""
    try:
        response = chat(
            model=model_name,
            messages=[{"role": "user", "content": "Say hi"}],
            tools=[test_fn]
        )
        print(f"✓ {model_name}: Supports tools")
        return True
    except Exception as e:
        print(f"✗ {model_name}: No tool support ({e})")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test-tool-support.py <model_name> [model_name2 ...]")
        print("Example: python test-tool-support.py llama3.1:8b qwen3:8b mistral:7b")
        sys.exit(1)

    models = sys.argv[1:]
    results = {model: test_model(model) for model in models}

    print("\n--- Summary ---")
    supported = [m for m, ok in results.items() if ok]
    unsupported = [m for m, ok in results.items() if not ok]

    if supported:
        print(f"Supported: {', '.join(supported)}")
    if unsupported:
        print(f"Unsupported: {', '.join(unsupported)}")
