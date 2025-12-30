# Examples

Learning examples demonstrating Ollama tool calling basics. Start here to understand how tool calling works before diving into the main agents.

## weather-agent.py

Weather agent using wttr.in API. Understands natural language questions about weather.

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

## weather-tool.py

Simple weather tool demonstrating basic Ollama tool calling. Takes city as command-line argument.

```bash
python examples/weather-tool.py London
python examples/weather-tool.py "New York"
python examples/weather-tool.py Tokyo
```

## single-tool.py

Minimal example showing the basic structure of an Ollama tool call. Good starting point for understanding the API.

```bash
python examples/single-tool.py
```
