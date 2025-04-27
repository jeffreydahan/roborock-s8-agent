# Import ADK Agent and other libraries
from google.adk.agents import Agent
import os  # Import the os module for environment variables
import asyncio
from dotenv import load_dotenv

# Import Roborock libraries
from roborock import HomeDataProduct, DeviceData, RoborockCommand
from roborock.version_1_apis import RoborockMqttClientV1, RoborockLocalClientV1
from roborock.web_api import RoborockApiClient


load_dotenv()  # Load environment variables from .env file

# Global variables to hold the MQTT client and device
mqtt_client = None
device = None

# Helper function to get environment variables
def get_env_var(key):
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' not found.")
    return value

# Login to Roborock (will only run if mqtt_client is None)
async def ensure_login():
    global mqtt_client
    global device
    if mqtt_client is None:
        try:
            web_api = RoborockApiClient(username=get_env_var('ROBOROCK_USERNAME'))
            user_data = await web_api.pass_login(password=get_env_var('ROBOROCK_PASSWORD'))
            home_data = await web_api.get_home_data_v2(user_data)
            device_data = home_data.devices[0]
            product_info: dict[str, HomeDataProduct] = {
                product.id: product for product in home_data.products
            }
            device = DeviceData(device_data, product_info[device_data.product_id].model)
            mqtt_client = RoborockMqttClientV1(user_data, device)
            await mqtt_client.async_connect()
            print("Roborock login successful.")
            return True
        except Exception as e:
            print(f"Roborock login failed: {e}")
            mqtt_client = None
            device = None
            return False
    return True

# Resets Roborock login and session
async def reset_connection():
    global mqtt_client
    global device
    if mqtt_client:
        try:
            await mqtt_client.async_disconnect()
            print("MQTT client disconnected.")
        except Exception as e:
            print(f"Error disconnecting MQTT client: {e}")
        finally:
            mqtt_client = None
            device = None
            print("Roborock connection reset.")

# Get Roborock status
async def get_status():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    try:
        status = await mqtt_client.get_status()
        print("Current Status:")
        print(status)
        return {
            "state": status.state_name,
            "battery": status.battery,
            "clean_time": status.clean_time,
            "clean_area": status.square_meter_clean_area,
            "error": status.error_code_name,
            "fan_speed": status.fan_power_name,
            "mop_mode": status.mop_mode_name,
            "docked": status.state_name == "charging"
        }
    except Exception as e:
        print(f"Error getting status: {e}")
        await reset_connection()
        return {"error": f"Error getting status: {e}. Connection reset."}

# Return Roborock to dock and ends job
async def app_charge():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_charge"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Start washing the mop while docked
async def app_start_wash():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_start_wash"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Stops washing the mop while docked
async def app_stop_wash():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_stop_wash"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Start general cleaning of all areas
async def app_start():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_start"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Stops cleaning
async def app_stop():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_stop"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Pauses cleaning
async def app_pause():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_pause"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Starts collecting dust
async def app_start_collect_dust():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_start_collect_dust"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# Stops collecting dust
async def app_stop_collect_dust():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_stop_collect_dust"
    try:
        await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# generate mapping of rooms. This returns a tuple of room indexes and IDs aso known as segments
async def get_room_mapping():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "get_room_mapping"
    try:
        mapping = await mqtt_client.send_command(command, None)
        print(f"Command sent: {command}")
        return mapping
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# cleans a specific room also known as segment. To Do is to make this dynamic based upon desired segment from instructions mapping in thr Agent definition below. 
async def app_segment_clean(segment_number: dict) -> str:
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_segment_clean"
    try:
        segment = await mqtt_client.send_command(command, [{"segments": segment_number, "repeat": 1}])
        print(f"Command sent: {command}")
        return segment
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# root agent definition
root_agent = Agent(
    name="Roborock_Agent", # ensure no spaces here
    model="gemini-2.0-flash",
    description="Agent to control and get status of your Roborock vacuum",
    # natural language i struction set which explains to the agent its capabilities and how to operate
    instruction="""I can control and get the status of your Roborock vacuum.
        I can handle the following commands
        - get_status (this command gets the current status of the Roborock)
        - app_charge (this command sends the Roborock back to the dock)
        - app_start_wash (this command starts the washing of the mop while docked)
        - app_stop_wash (this command stops the washing of the mop while docked)
        - app_start (this command starts vacuuming and mopping job)
        - app_stop (this command stops the vacuuming and mopping job)
        - app_pause (this command pauses the vacuuming and mopping job)
        - app_start_collect_dust (this command starts emptying the dust bin)
        - app_stop_collect_dust (this command stops emptying the dust bin)
        - get_room_mapping (gets a list of the rooms in a map)
        - app_segment_clean (starts cleaning rooms or segments) - when using this command, you must pass
        a segment number from the mapping below.  For example, for a request to clean Bedroom4, you would call
        app_segment_clean([16]) where you would send the number 16 as an integer.  if multiple rooms are specified,
        send both integers comma-separated such as app_segment_clean([16,17])

        Segment mapping:
        16 = Bedroom4
        17 = Balcony
        18 = Bedroom3
        19 = Bathroom
        20 = Hallway
        21 = Kitchen
        22 = Dining Room
        23 = Entryway
        24 = Bedroom1
        25 = Bedroom2
        26 = Living Room
        """,
    # tells the agent what tools (function names from above) it has access to. The agent uses the instructions above to understand how and when to use these tools. 
    tools=[
        get_status,
        app_charge,
        app_start_wash,
        app_stop_wash,
        app_start,
        app_stop,
        app_pause,
        app_start_collect_dust,
        app_stop_collect_dust,
        get_room_mapping,
        app_segment_clean,
    ],
)
