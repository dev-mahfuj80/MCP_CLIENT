from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import random

mcp = FastMCP("Python360")

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m ** 2)

@mcp.tool()
async def fetch_weather(latitude: float, longitude: float) -> str:
    """Fetch current weather for a location using latitude and longitude"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&current_weather=true&"
        f"hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

@mcp.tool()
def calculate_subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b

@mcp.tool()
def calculate_sum(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def generate_random_number(min_value: int = 1, max_value: int = 100) -> int:
    """Generate a random number between min_value and max_value"""
    return random.randint(min_value, max_value)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start background async tasks (if needed)
    loop.run_until_complete(asyncio.sleep(0))  # Ensures an event loop is available

    # Now run FastMCP (blocking)
    mcp.run()

    """Since mcp.run() is blocking, but we also have async functions (like fetch_weather), 
        the best solution is to run the  async tasks in a background event loop before calling mcp.run().
    """
