# 🌤️ Weather MCP Server

A Python [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that integrates with the [OpenWeatherMap API](https://openweathermap.org/api) to give Claude real-time weather data.

## Tools Exposed

| Tool | Description |
|---|---|
| `get_current_weather` | Current conditions for any city |
| `get_forecast` | 5-day / 3-hour forecast for any city |
| `get_weather_by_coordinates` | Current weather by lat/lon |
| `geocode_city` | Convert city name → coordinates |

## Prerequisites

- Python 3.10+
- A free [OpenWeatherMap API key](https://openweathermap.org/api)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/weather-mcp-server.git
cd weather-mcp-server
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

```bash
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

### 4. Run the server

```bash
OPENWEATHER_API_KEY=your_key_here python -m src.server
```

## Connect to Claude Desktop

Add this block to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/weather-mcp-server",
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Restart Claude Desktop — you should now see the weather tools available.

## Example Usage in Claude

> "What's the weather like in Tokyo right now?"  
> "Give me a 3-day forecast for London in Fahrenheit."  
> "What are the coordinates for Sydney, Australia?"

## Project Structure

```
weather-mcp-server/
├── src/
│   └── server.py        # MCP server + all tool handlers
├── .env.example         # Template for your API key
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

MIT
