"""
Weather MCP Server
Integrates with OpenWeatherMap API to expose weather tools via MCP protocol.
"""

import asyncio
import os
import httpx
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# --- Config ---
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "http://api.openweathermap.org/geo/1.0"

app = Server("weather-mcp-server")


def _check_api_key() -> None:
    if not API_KEY:
        raise ValueError(
            "OPENWEATHER_API_KEY environment variable is not set. "
            "Get a free key at https://openweathermap.org/api"
        )


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_current_weather",
            description=(
                "Fetch current weather conditions for a city. "
                "Returns temperature, humidity, wind speed, and a description."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'London' or 'New York,US'",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "standard"],
                        "default": "metric",
                        "description": "Temperature units: metric (°C), imperial (°F), standard (K)",
                    },
                },
                "required": ["city"],
            },
        ),
        types.Tool(
            name="get_forecast",
            description=(
                "Fetch a 5-day / 3-hour weather forecast for a city. "
                "Returns a list of forecast entries with timestamps."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Tokyo' or 'Paris,FR'",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "standard"],
                        "default": "metric",
                        "description": "Temperature units",
                    },
                    "count": {
                        "type": "integer",
                        "default": 8,
                        "description": "Number of forecast entries to return (max 40, each ~3 hours apart)",
                    },
                },
                "required": ["city"],
            },
        ),
        types.Tool(
            name="get_weather_by_coordinates",
            description=(
                "Fetch current weather using latitude and longitude. "
                "Useful when you have precise coordinates instead of a city name."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "standard"],
                        "default": "metric",
                    },
                },
                "required": ["lat", "lon"],
            },
        ),
        types.Tool(
            name="geocode_city",
            description="Convert a city name to latitude/longitude coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name to geocode"},
                    "limit": {
                        "type": "integer",
                        "default": 3,
                        "description": "Max number of results to return",
                    },
                },
                "required": ["city"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    _check_api_key()

    async with httpx.AsyncClient(timeout=10.0) as client:
        if name == "get_current_weather":
            return await _get_current_weather(client, arguments)
        elif name == "get_forecast":
            return await _get_forecast(client, arguments)
        elif name == "get_weather_by_coordinates":
            return await _get_weather_by_coordinates(client, arguments)
        elif name == "geocode_city":
            return await _geocode_city(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


async def _get_current_weather(
    client: httpx.AsyncClient, args: dict
) -> list[types.TextContent]:
    params = {
        "q": args["city"],
        "appid": API_KEY,
        "units": args.get("units", "metric"),
    }
    resp = await client.get(f"{BASE_URL}/weather", params=params)
    resp.raise_for_status()
    data = resp.json()

    unit_symbol = _unit_symbol(args.get("units", "metric"))
    result = (
        f"Current weather in {data['name']}, {data['sys']['country']}:\n"
        f"  Description : {data['weather'][0]['description'].capitalize()}\n"
        f"  Temperature : {data['main']['temp']}{unit_symbol} "
        f"(feels like {data['main']['feels_like']}{unit_symbol})\n"
        f"  Humidity    : {data['main']['humidity']}%\n"
        f"  Wind speed  : {data['wind']['speed']} m/s\n"
        f"  Visibility  : {data.get('visibility', 'N/A')} m\n"
    )
    return [types.TextContent(type="text", text=result)]


async def _get_forecast(
    client: httpx.AsyncClient, args: dict
) -> list[types.TextContent]:
    count = min(args.get("count", 8), 40)
    params = {
        "q": args["city"],
        "appid": API_KEY,
        "units": args.get("units", "metric"),
        "cnt": count,
    }
    resp = await client.get(f"{BASE_URL}/forecast", params=params)
    resp.raise_for_status()
    data = resp.json()

    unit_symbol = _unit_symbol(args.get("units", "metric"))
    lines = [f"5-day forecast for {data['city']['name']}, {data['city']['country']}:\n"]
    for entry in data["list"]:
        lines.append(
            f"  {entry['dt_txt']}  |  "
            f"{entry['weather'][0]['description'].capitalize():25s}  |  "
            f"{entry['main']['temp']}{unit_symbol}  |  "
            f"Humidity {entry['main']['humidity']}%"
        )
    return [types.TextContent(type="text", text="\n".join(lines))]


async def _get_weather_by_coordinates(
    client: httpx.AsyncClient, args: dict
) -> list[types.TextContent]:
    params = {
        "lat": args["lat"],
        "lon": args["lon"],
        "appid": API_KEY,
        "units": args.get("units", "metric"),
    }
    resp = await client.get(f"{BASE_URL}/weather", params=params)
    resp.raise_for_status()
    data = resp.json()

    unit_symbol = _unit_symbol(args.get("units", "metric"))
    result = (
        f"Weather at ({args['lat']}, {args['lon']}) — {data['name']}:\n"
        f"  Description : {data['weather'][0]['description'].capitalize()}\n"
        f"  Temperature : {data['main']['temp']}{unit_symbol}\n"
        f"  Humidity    : {data['main']['humidity']}%\n"
        f"  Wind speed  : {data['wind']['speed']} m/s\n"
    )
    return [types.TextContent(type="text", text=result)]


async def _geocode_city(
    client: httpx.AsyncClient, args: dict
) -> list[types.TextContent]:
    params = {
        "q": args["city"],
        "limit": args.get("limit", 3),
        "appid": API_KEY,
    }
    resp = await client.get(f"{GEO_URL}/direct", params=params)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        return [types.TextContent(type="text", text=f"No results found for '{args['city']}'.")]

    lines = [f"Geocoding results for '{args['city']}':"]
    for place in data:
        lines.append(
            f"  {place['name']}, {place.get('state', '')}, {place['country']} "
            f"→ lat={place['lat']}, lon={place['lon']}"
        )
    return [types.TextContent(type="text", text="\n".join(lines))]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unit_symbol(units: str) -> str:
    return {"metric": "°C", "imperial": "°F", "standard": "K"}.get(units, "°C")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
