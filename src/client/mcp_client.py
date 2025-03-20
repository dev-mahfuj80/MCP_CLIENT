from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import logging
import json
import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
import httpx
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Enable logging but set to INFO to reduce noise
logging.basicConfig(level=logging.INFO)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["src/server/example_server.py"],  # relative path to the server script
    env=None  # Optional environment variables
)

# Create a custom HTTP client without proxies
custom_http_client = httpx.AsyncClient(
    timeout=60.0,
    follow_redirects=True
)

# Initialize OpenAI client with API key from environment variable and custom HTTP client
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=custom_http_client
)

async def run():
    print("\n===== MCP CLIENT WITH OPENAI INTEGRATION =====")
    print("This client connects to a local MCP server and OpenAI's API")
    
    # Initialize conversation history at the function level
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant. The user has access to MCP tools including calculate_bmi and fetch_weather."}
    ]
    
    async with stdio_client(server_params) as (read, write):
        print("\nConnected to server via stdio")
        
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            print("Checking available tools...")
            tools_response = await session.list_tools()
            
            # Print tools information
            if hasattr(tools_response, 'tools') and tools_response.tools:
                tool_names = [getattr(tool, 'name', str(tool)) for tool in tools_response.tools]
                print(f"Found {len(tools_response.tools)} tools: {', '.join(tool_names)}")
            else:
                print("No tools found or unexpected response format")
            
            # Main interactive loop
            print("\n===== INTERACTIVE CHAT =====")
            print("Type 'exit' to quit, or ask any question")
            
            while True:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Exiting program...")
                    break
                
                # Handle tool-related queries directly
                if any(phrase in user_input.lower() for phrase in [
                    "how many tools", "what tools", "mcp tools", "available tools", 
                    "how many", "how many mcp", "tools do you have", "sure", "tools available",
                    "what mcp", "which tools"
                ]):
                    try:
                        # Always query the server for the latest tools
                        tools_response = await session.list_tools()
                        if hasattr(tools_response, 'tools') and tools_response.tools:
                            tool_names = [getattr(tool, 'name', str(tool)) for tool in tools_response.tools]
                            print(f"\nThere are {len(tools_response.tools)} MCP tools available:")
                            for tool in tool_names:
                                print(f"- {tool}")
                        else:
                            print("No tools found or unexpected response format")
                    except Exception as e:
                        print(f"Error listing tools: {e}")
                
                # Check if this is a BMI calculation request
                elif "bmi" in user_input.lower() or "body mass index" in user_input.lower():
                    try:
                        print("\nCalculating BMI using MCP server tool...")
                        weight = float(input("Enter weight in kg: "))
                        height = float(input("Enter height in meters: "))
                        
                        # Call the BMI tool on the server
                        bmi_result = await session.call_tool("calculate_bmi", {"weight_kg": weight, "height_m": height})
                        
                        if hasattr(bmi_result, 'result'):
                            bmi_value = float(bmi_result.result)
                            print(f"Your BMI is: {bmi_value:.2f}")
                            
                            # Provide BMI category
                            if bmi_value < 18.5:
                                category = "Underweight"
                            elif bmi_value < 25:
                                category = "Normal weight"
                            elif bmi_value < 30:
                                category = "Overweight"
                            else:
                                category = "Obese"
                                
                            print(f"BMI Category: {category}")
                        else:
                            print(f"Unexpected result format from MCP server: {bmi_result}")
                    except ValueError:
                        print("Error: Please enter valid numbers for weight and height")
                    except Exception as e:
                        print(f"Error calling BMI calculator on MCP server: {e}")
                
                # Check for calculator operations
                elif any(word in user_input.lower() for word in ["add", "sum", "plus", "+"]):
                    try:
                        print("\nCalculating sum using MCP server tool...")
                        a = float(input("Enter first number: "))
                        b = float(input("Enter second number: "))
                        
                        # Call the sum tool on the server
                        result = await session.call_tool("calculate_sum", {"a": a, "b": b})
                        
                        if hasattr(result, 'result'):
                            print(f"Result: {a} + {b} = {result.result}")
                        elif hasattr(result, 'content') and result.content:
                            # Extract the text content from the response
                            text_content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            print(f"Result: {a} + {b} = {text_content}")
                        else:
                            print(f"Unexpected result format from MCP server: {result}")
                    except ValueError:
                        print("Error: Please enter valid numbers")
                    except Exception as e:
                        print(f"Error calling calculator on MCP server: {e}")
                
                # Check for subtraction operations
                elif any(word in user_input.lower() for word in ["subtract", "minus", "difference", "-"]):
                    try:
                        print("\nCalculating subtraction using MCP server tool...")
                        a = float(input("Enter first number: "))
                        b = float(input("Enter second number: "))
                        
                        # Call the subtract tool on the server
                        result = await session.call_tool("calculate_subtract", {"a": a, "b": b})
                        
                        if hasattr(result, 'result'):
                            print(f"Result: {a} - {b} = {result.result}")
                        elif hasattr(result, 'content') and result.content:
                            # Extract the text content from the response
                            text_content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            print(f"Result: {a} - {b} = {text_content}")
                        else:
                            print(f"Unexpected result format from MCP server: {result}")
                    except ValueError:
                        print("Error: Please enter valid numbers")
                    except Exception as e:
                        print(f"Error calling calculator on MCP server: {e}")
                
                # Check for random number generation
                elif any(phrase in user_input.lower() for phrase in ["random", "random number", "generate number"]):
                    try:
                        print("\nGenerating random number using MCP server tool...")
                        min_value = int(input("Enter minimum value (default 1): ") or "1")
                        max_value = int(input("Enter maximum value (default 100): ") or "100")
                        
                        # Call the random number tool on the server
                        result = await session.call_tool("generate_random_number", {"min_value": min_value, "max_value": max_value})
                        
                        if hasattr(result, 'result'):
                            print(f"Random number between {min_value} and {max_value}: {result.result}")
                        elif hasattr(result, 'content') and result.content:
                            # Extract the text content from the response
                            text_content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            print(f"Random number between {min_value} and {max_value}: {text_content}")
                        else:
                            print(f"Unexpected result format from MCP server: {result}")
                    except ValueError:
                        print("Error: Please enter valid numbers")
                    except Exception as e:
                        print(f"Error generating random number from MCP server: {e}")
                
                # Check if this is a weather request
                elif any(kw in user_input.lower() for kw in [
                    "weather", "temperature", "forecast", "rain", "sunny", "cold", "hot", "climate",
                    "wether", "wetehr", "weathr", "weater", "wheather", "weathe", "wwetehr"
                ]):
                    try:
                        print("\nFetching weather using MCP server tool...")
                        # Check if location is mentioned
                        locations = {
                            "london": (51.5, -0.12),
                            "new york": (40.71, -74.0),
                            "tokyo": (35.68, 139.76),
                            "paris": (48.85, 2.35)
                        }
                        
                        location = None
                        for loc in locations:
                            if loc in user_input.lower():
                                location = loc
                                break
                        
                        if location:
                            latitude, longitude = locations[location]
                            print(f"Using coordinates for {location.title()}: {latitude}, {longitude}")
                        else:
                            print("Enter location coordinates:")
                            latitude = float(input("Latitude: "))
                            longitude = float(input("Longitude: "))
                        
                        print(f"Fetching weather for coordinates: {latitude}, {longitude}...")
                        
                        # Call the weather tool on the server
                        weather_result = await session.call_tool("fetch_weather", {"latitude": latitude, "longitude": longitude})
                        
                        if hasattr(weather_result, 'result'):
                            # Parse the JSON response
                            try:
                                weather_data = json.loads(weather_result.result)
                                
                                # Extract and display current weather
                                if 'current_weather' in weather_data:
                                    current = weather_data['current_weather']
                                    print("\nCurrent Weather:")
                                    print(f"Temperature: {current.get('temperature', 'N/A')}°C")
                                    print(f"Wind Speed: {current.get('windspeed', 'N/A')} km/h")
                                    print(f"Wind Direction: {current.get('winddirection', 'N/A')}°")
                                    
                                    # Weather code interpretation
                                    weather_code = current.get('weathercode', 0)
                                    weather_descriptions = {
                                        0: "Clear sky",
                                        1: "Mainly clear",
                                        2: "Partly cloudy",
                                        3: "Overcast",
                                        45: "Fog",
                                        48: "Depositing rime fog",
                                        51: "Light drizzle",
                                        53: "Moderate drizzle",
                                        55: "Dense drizzle",
                                        61: "Slight rain",
                                        63: "Moderate rain",
                                        65: "Heavy rain",
                                        71: "Slight snow fall",
                                        73: "Moderate snow fall",
                                        75: "Heavy snow fall",
                                        95: "Thunderstorm"
                                    }
                                    
                                    weather_desc = weather_descriptions.get(weather_code, f"Unknown ({weather_code})")
                                    print(f"Conditions: {weather_desc}")
                                else:
                                    print("Weather data received from MCP server but current weather not available")
                            except json.JSONDecodeError:
                                print("Weather data received from MCP server but not in valid JSON format")
                                print(f"Raw response: {weather_result.result[:200]}...")
                        else:
                            print(f"Unexpected result format from MCP server: {weather_result}")
                    except ValueError:
                        print("Error: Please enter valid numbers for coordinates")
                    except Exception as e:
                        print(f"Error fetching weather from MCP server: {e}")
                
                # For all other queries, use OpenAI
                else:
                    # Send to OpenAI for general conversation
                    try:
                        # Add user message to conversation history
                        conversation_history.append({"role": "user", "content": user_input})
                        
                        # Call OpenAI API
                        response = await openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=conversation_history
                        )
                        
                        # Get and display the response
                        assistant_response = response.choices[0].message.content
                        print(f"\nAssistant: {assistant_response}")
                        
                        # Add assistant response to conversation history
                        conversation_history.append({"role": "assistant", "content": assistant_response})
                    except Exception as e:
                        print(f"Error with OpenAI: {e}")

if __name__ == "__main__":
    asyncio.run(run())
