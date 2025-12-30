import sys
import requests
from ollama import chat


def get_temperature(city: str) -> str:
    """Get the current temperature for a city

    Args:
      city: The name of the city

    Returns:
      The current temperature for the city
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=%t")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error fetching temperature: {e}"


if len(sys.argv) < 2:
    print("Usage: python weather-tool.py <city>")
    sys.exit(1)

city = sys.argv[1]

messages = [{"role": "user", "content": f"What is the temperature in {city}?"}]

response = chat(
    model="qwen3:8b", messages=messages, tools=[get_temperature], think=True
)

messages.append(response.message)
if response.message.tool_calls:
    call = response.message.tool_calls[0]
    result = get_temperature(**call.function.arguments)
    messages.append(
        {"role": "tool", "tool_name": call.function.name, "content": str(result)}
    )

    final_response = chat(
        model="qwen3:8b", messages=messages, tools=[get_temperature], think=True
    )
    print(final_response.message.content)
