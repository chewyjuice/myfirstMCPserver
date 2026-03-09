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
git clone https://github.com/chewyjuice/myfirstMCPserver.git
cd myfirstmcpserver
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

Copy `.env.example` to `.env` and fill in your OpenWeatherMap API key:

```
OPENWEATHER_API_KEY=your_api_key_here
```

## Connect to Claude Desktop

Open the config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

First, find your exact Python path:
```powershell
(Get-Command python).Source
# e.g. C:\Python313\python.exe
```

Then add this to your config (replace paths accordingly):
```json
{
  "mcpServers": {
    "weather": {
      "command": "C:\\Python313\\python.exe",
      "args": ["C:\\Users\\YOUR_USERNAME\\Code\\myfirstmcpserver\\src\\server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### macOS / Linux

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/absolute/path/to/weather-mcp-server/src/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Fully quit Claude Desktop from the system tray and reopen it. The weather tools will now be available.

### Verify it's working

Check the logs to confirm a successful connection:

```powershell
# Windows
Get-Content "$env:APPDATA\Claude\logs\mcp-server-weather.log" -Tail 20
```

You should see `Server started and connected successfully` with no disconnect errors after it.

### Troubleshooting

- **`ENOENT` error** — the Python path in your config is wrong. Use the full absolute path from `(Get-Command python).Source`
- **`No module named 'src'`** — you're using `-m src.server` in args; switch to the full file path instead
- **Server disconnects immediately** — you have multiple Python versions installed and `mcp` is only on one of them. Use the full path to the correct Python executable
- **No hammer icon** — this is normal in some Claude Desktop versions. Just ask Claude a weather question directly and it will use the tools automatically

## Example Usage in Claude

> "What's the weather like in Tokyo right now?"
> "Give me a 3-day forecast for London in Fahrenheit."
> "What are the coordinates for Sydney, Australia?"

## Project Structure

```
weather-mcp-server/
├── src/
│   ├── __init__.py
│   └── server.py        # MCP server + all tool handlers
├── .env.example         # Template for your API key
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

MIT
