# Import ADK Agent
from google.adk.agents import Agent
import os  # Import the os module for environment variables
import asyncio

from roborock import HomeDataProduct, DeviceData, RoborockCommand
from roborock.version_1_apis import RoborockMqttClientV1, RoborockLocalClientV1
from roborock.web_api import RoborockApiClient
from dotenv import load_dotenv

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

async def app_segment_clean_16():
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    command = "app_segment_clean"
    try:
        segment = await mqtt_client.send_command(command, [{"segments": [16], "repeat": 1}])
        print(f"Command sent: {command}")
        return segment
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

root_agent = Agent(
    name="Roborock_Agent",
    model="gemini-2.0-flash-001",
    description="Agent to control and get status of your Roborock vacuum",
    instruction="""I can control and get the status of your Roborock vacuum.
        I can handle the following commands
        - get_status (this command gets the current status of the Roborock)
        - app_charge (this command sends the Roborock back to the dock)
        - app_start_wash (this command starts the washing of the mop while docked)
        - app_stop_wash (this command stops the washing of the mop while docked)
        - app_start (this command starts vacuuming and mopping job)
        - app_stop (this command stops the vacuuming and mopping job)
        - app_pause (this command pauses the vacuuming and mopping job)
        - get_room_mapping (gets a list of the rooms in a map)
        - app_segment_clean_16 (starts cleaning Abby's Room)

        for segments, here is the mapping of segment_number to the room name
        16 = Abby's Room
        """,
    tools=[
        get_status,
        app_charge,
        app_start_wash,
        app_stop_wash,
        app_start,
        app_stop,
        app_pause,
        get_room_mapping,
        app_segment_clean_16,
    ],
)