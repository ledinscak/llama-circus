# Ollama Agent Tools

A collection of Python scripts that use Ollama's tool/function calling capabilities to create intelligent agents for web search, weather lookup, and more.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.8 or higher** installed

   ```bash
   python3 --version
   ```

2. **Ollama** installed and running
   - Install from [ollama.ai](https://ollama.ai/)
   - Start Ollama service:

     ```bash
     ollama serve
     ```

   - Pull a model with tool support:

     ```bash
     ollama pull llama3.1:8b
     ```

3. **chafa** (optional, for displaying images in terminal)

   ```bash
   sudo apt install chafa
   ```

## Installation

### Step 1: Clone or download this repository

```bash
git clone https://github.com/ledinscak/llama-circus.git
cd llama-circus
```

### Step 2: Create a Python virtual environment

A virtual environment keeps dependencies isolated from your system Python.

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

Your terminal prompt should now show `(venv)` at the beginning.

### Step 3: Install Python dependencies

```bash
pip install ollama requests ddgs
```

This installs:

- `ollama` - Python client for Ollama API
- `requests` - HTTP library for web requests
- `ddgs` - DuckDuckGo search library

### Step 4: Verify installation

```bash
# Check that Ollama is running and model is available
ollama list

# Test if your model supports tools
python utils/test-tool-support.py llama3.1:8b
```

## Project Structure

```
├── search-agent.py      # Web search agent (DuckDuckGo)
├── hn-agent.py          # Hacker News agent
├── examples/
│   ├── single-tool.py   # Basic tool calling example
│   ├── weather-tool.py  # Simple weather tool
│   └── weather-agent.py # Weather agent with forecast
├── utils/
│   ├── test-tool-support.py  # Test model tool support
│   └── test-image.py         # Debug image display
├── README.md
└── LICENSE
```

## Scripts

### search-agent.py (Main)

A powerful web search agent that searches DuckDuckGo, summarizes results using AI, and can display images in terminal.

**Features:**

- Web search, news search, and image search
- Multiple output formats (brief, bullets, detailed, all)
- Configurable model and result count
- Colorful ANSI terminal output
- Image display via chafa

**Basic Examples:**

```bash
# Simple search (uses default settings)
python search-agent.py "What is Python programming language?"

# Search with verbose output (shows what's happening)
python search-agent.py -v "What is machine learning?"

# Search for news
python search-agent.py "Latest technology news 2025"

# Get a brief answer
python search-agent.py -f brief "Who is the CEO of Tesla?"

# Get detailed research report with images
python search-agent.py -v -f all "History of artificial intelligence"
```

**Advanced Examples:**

```bash
# Use a different model
python search-agent.py -m qwen3:8b "Explain quantum computing"

# Get more search results for thorough research
python search-agent.py -n 20 -f detailed "Climate change solutions"

# Combine all options
python search-agent.py -v -m llama3.1:8b -f all -n 15 "SpaceX Starship progress"
```

**Command-Line Options:**

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-v` | `--verbose` | Show intermediate results and tool calls | off |
| `-m` | `--model` | Ollama model to use | llama3.1:8b |
| `-f` | `--format` | Output format (see below) | bullets |
| `-n` | `--num-results` | Number of search results to fetch | 10 |

**Output Formats:**

| Format | Description | Best For |
|--------|-------------|----------|
| `brief` | 2-3 sentences + one source URL | Quick answers |
| `bullets` | Summary + bullet points | General use |
| `detailed` | Comprehensive with context | In-depth answers |
| `all` | Full research report with analysis, recommendations, images | Research tasks |

---

### hn-agent.py

A Hacker News research assistant that helps developers discover and understand trending tech content using the official HN API.

**Features:**

- Access to all HN content types (top, new, best, ask, show, jobs)
- Story details with top comments
- Keyword search across stories
- Developer-focused analysis with project ideas
- Colorful ANSI terminal output

**Available Tools:**

| Tool | Description |
|------|-------------|
| `get_top_stories(limit)` | Current trending stories |
| `get_new_stories(limit)` | Latest submissions |
| `get_best_stories(limit)` | Highest rated stories |
| `get_ask_hn(limit)` | Community questions and discussions |
| `get_show_hn(limit)` | Project showcases and demos |
| `get_jobs(limit)` | Job postings |
| `get_story_details(story_id)` | Full story with top comments |
| `search_stories(query, limit)` | Search stories by keyword |

**Basic Examples:**

```bash
# Get top stories with analysis
python hn-agent.py "What's trending on Hacker News today?"

# Explore specific topics
python hn-agent.py "Find stories about Rust programming"

# Check job postings
python hn-agent.py "Show me the latest job postings"

# See Show HN projects
python hn-agent.py "What interesting projects are people showing?"

# Verbose mode to see tool calls
python hn-agent.py -v "What are the best stories this week?"
```

**Advanced Examples:**

```bash
# Use a different model
python hn-agent.py -m qwen3:8b "AI and machine learning discussions"

# Get more results
python hn-agent.py -n 20 "Latest news about startups"

# Combine options
python hn-agent.py -v -m llama3.1:8b -n 15 "Find discussions about Python"
```

**Command-Line Options:**

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-v` | `--verbose` | Show tool calls and intermediate results | off |
| `-m` | `--model` | Ollama model to use | llama3.1:8b |
| `-n` | `--num-results` | Number of stories to fetch | 10 |

**Output Format:**

The agent provides structured analysis including:

- **Overview**: Brief summary of findings
- **Key Stories**: Detailed breakdown with relevance and applications
- **Insights**: Common themes and trending topics
- **Project Ideas**: Hobby project suggestions inspired by the stories
- **Sources**: Links to HN discussions

---

### examples/weather-agent.py

Weather agent using wttr.in API. Understands natural language questions about weather.

**Examples:**

```bash
# Current weather
python examples/weather-agent.py "What's the weather like in London?"

# Weather forecast
python examples/weather-agent.py "Will it rain in Paris tomorrow?"

# Multi-day forecast
python examples/weather-agent.py "Give me a 3-day forecast for Tokyo"

# Temperature query
python examples/weather-agent.py "How cold is it in Oslo right now?"
```

---

### examples/weather-tool.py

Simple weather tool demonstrating basic Ollama tool calling. Takes city as command-line argument.

**Examples:**

```bash
python examples/weather-tool.py London
python examples/weather-tool.py "New York"
python examples/weather-tool.py Tokyo
```

---

### utils/test-tool-support.py

Utility to test if Ollama models support tool/function calling.

**Examples:**

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

---

### utils/test-image.py

Debug script to test the image search and display pipeline. Run this if images aren't showing.

```bash
python utils/test-image.py
```

This tests:

1. chafa installation
2. DuckDuckGo image search
3. Image download
4. Terminal display

## Supported Ollama Models

Models known to support tool calling:

| Model | Size | Notes |
|-------|------|-------|
| `llama3.1:8b` | 8B | Recommended default |
| `llama3.1:70b` | 70B | Better quality, slower |
| `llama3.2:3b` | 3B | Lightweight |
| `qwen2.5:7b` | 7B | Good alternative |
| `qwen2.5:14b` | 14B | Higher quality |
| `qwen3:8b` | 8B | Supports thinking mode |
| `mistral:7b` | 7B | Fast |
| `mixtral:8x7b` | 8x7B | MoE model |
| `command-r` | - | Cohere model |

Use `test-tool-support.py` to verify support for other models.

## Troubleshooting

### "No module named 'ollama'"

Make sure you activated the virtual environment:

```bash
source venv/bin/activate
```

### "Connection refused" or Ollama errors

Make sure Ollama is running:

```bash
ollama serve
```

### Images not displaying

1. Install chafa: `sudo apt install chafa`
2. Run `python utils/test-image.py` to diagnose
3. Some images may fail due to website restrictions (403 errors)

### Model doesn't support tools

Try a different model:

```bash
python search-agent.py -m llama3.1:8b "your query"
```

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## License

MIT License - see [LICENSE](LICENSE) file.

Free to use, modify, and distribute.
