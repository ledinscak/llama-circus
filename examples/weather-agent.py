import sys
import requests
from ollama import chat


def get_weather(city: str) -> str:
    """Get the current weather for a city including temperature, conditions, humidity and wind

    Args:
      city: The name of the city

    Returns:
      The current weather information for the city
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=%l:+%C,+%t,+humidity:+%h,+wind:+%w")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"


def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city for the next days

    Args:
      city: The name of the city
      days: Number of days to forecast (1-3), defaults to 3

    Returns:
      Weather forecast for the specified number of days
    """
    try:
        days = min(max(1, days), 3)
        response = requests.get(f"https://wttr.in/{city}?format=j1")
        response.raise_for_status()
        data = response.json()

        forecast_lines = [f"Weather forecast for {city}:"]
        for i, day in enumerate(data.get("weather", [])[:days]):
            date = day.get("date", "Unknown")
            max_temp = day.get("maxtempC", "?")
            min_temp = day.get("mintempC", "?")
            hourly = day.get("hourly", [{}])
            condition = hourly[len(hourly)//2].get("weatherDesc", [{}])[0].get("value", "Unknown") if hourly else "Unknown"
            forecast_lines.append(f"  {date}: {condition}, {min_temp}°C - {max_temp}°C")

        return "\n".join(forecast_lines)
    except requests.RequestException as e:
        return f"Error fetching forecast: {e}"


if len(sys.argv) < 2:
    print("Usage: python weather-agent.py <user query>")
    print('Example: python weather-agent.py "What\'s the weather like in Paris?"')
    sys.exit(1)

user_input = sys.argv[1]

tools = [get_weather, get_weather_forecast]
available_functions = {
    "get_weather": get_weather,
    "get_weather_forecast": get_weather_forecast,
}

messages = [{"role": "user", "content": user_input}]

response = chat(
    model="qwen3:8b", messages=messages, tools=tools, think=True
)

messages.append(response.message)
if response.message.tool_calls:
    call = response.message.tool_calls[0]
    func = available_functions.get(call.function.name)
    if func:
        result = func(**call.function.arguments)
    else:
        result = f"Unknown function: {call.function.name}"
    messages.append(
        {"role": "tool", "tool_name": call.function.name, "content": str(result)}
    )

    final_response = chat(
        model="qwen3:8b", messages=messages, tools=tools, think=True
    )
    print(final_response.message.content)
else:
    print(response.message.content)
