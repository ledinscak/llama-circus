# Utilities

Helper scripts for testing and debugging.

## test-tool-support.py

Test if Ollama models support tool/function calling.

```bash
# Test single model
python utils/test-tool-support.py llama3.1:8b

# Test multiple models
python utils/test-tool-support.py llama3.1:8b qwen3:8b mistral:7b gemma2:9b
```

**Example Output:**

```
✓ llama3.1:8b: Supports tools
✓ qwen3:8b: Supports tools
✗ gemma:7b: No tool support (...)

--- Summary ---
Supported: llama3.1:8b, qwen3:8b
Unsupported: gemma:7b
```

## test-image.py

Debug script to test the image search and display pipeline. Run this if images aren't showing in search-agent.py.

```bash
# Search with default term (llama)
python utils/test-image.py

# Search for a single term
python utils/test-image.py cat

# Search for multiple terms (each searched separately)
python utils/test-image.py llama cat dog
```

This tests:

1. chafa installation
2. DuckDuckGo image search (3 results per term)
3. Image download and terminal display for all results
