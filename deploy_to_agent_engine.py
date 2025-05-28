
from google.adk.agents import Agent
import vertexai

from dotenv import load_dotenv
import os
load_dotenv()


# Import Roborock libraries
from roborock import HomeDataProduct, DeviceData, RoborockCommand
from roborock.version_1_apis import RoborockMqttClientV1, RoborockLocalClientV1
from roborock.web_api import RoborockApiClient

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

# Send basic Roborock commands that don't have parameters
async def send_basic_command(command: str) -> str:
    if not await ensure_login():
        return {"error": "Not logged in to Roborock."}
    try:
        await mqtt_client.send_command(command)
        print(f"Command sent: {command}")
        return {"result": f"Command {command} sent successfully."}
    except Exception as e:
        print(f"Error sending {command}: {e}")
        await reset_connection()
        return {"error": f"Error sending {command}: {e}. Connection reset."}

# cleans a specific room also known as segment. To Do is to make this dynamic based upon desired segment from instructions mapping in the Agent definition below.
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
root_agent =  Agent(
    name="Roborock_Agent", # ensure no spaces here
    # model="gemini-2.0-flash-exp", # for live api
    model="gemini-2.0-flash",
    description="Agent to control and get status of your Roborock vacuum",
    # natural language instruction set which explains to the agent its capabilities and how to operate
    instruction="""I can control and get the status of your Roborock vacuum.
        I can handle the following commands:
        - get_status (this command gets the current status of the Roborock)
        when the above command is needed, call the get_status function

        Additional commands.  Use the send_basic_command function for these commands
        - app_charge (this command sends the Roborock back to the dock)
        - app_start_wash (this command starts the washing of the mop while docked)
        - app_stop_wash (this command stops the washing of the mop while docked)
        - app_start (this command starts vacuuming and mopping job)
        - app_stop (this command stops the vacuuming and mopping job)
        - app_pause (this command pauses the vacuuming and mopping job)
        - app_start_collect_dust (this command starts emptying the dust bin)
        - app_stop_collect_dust (this command stops emptying the dust bin)
        - get_room_mapping (gets a list of the rooms in a map)

        when the above commands are needed, call send_basic_command(command).  Examples:
        - for app_start_wash call send_basic_command("app_start_wash")
        - for app_stop_wash call send_bacic_command("app_stop_wash")

        Additional commands:
        - app_segment_clean (this command starts cleaning rooms or segments)
        - for this command, use the function app_segment_clean function
        - when using this command, you must pass a segment number from the mapping below as a list of integers.
        - For example, for a request to clean Bedroom4, you would call:
        app_segment_clean([16])
        - if multiple rooms are specified,
        app_segment_clean([16,18])


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

        ***Finally, format the status as a nice table***

        """,
    # tells the agent what tools (function names from above) it has access to. The agent uses the instructions above to understand how and when to use these tools.
    tools=[
        get_status,
        send_basic_command,
        app_segment_clean,
    ],
)


project_id=get_env_var("GOOGLE_CLOUD_PROJECT")
staging_bucket=get_env_var("GOOGLE_CLOUD_STORAGE_BUCKET")
location=get_env_var("GOOGLE_CLOUD_LOCATION")

# initialitze vertexai
vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=staging_bucket,
)


from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

requirements_path = "requirements.txt"
with open(requirements_path, "r") as f:
    requirements_list = [line.strip() for line in f if line.strip() and not line.startswith("#")]

print(requirements_list)



env_vars = {
    "ROBOROCK_USERNAME": get_env_var('ROBOROCK_USERNAME'),
    "ROBOROCK_PASSWORD": get_env_var('ROBOROCK_PASSWORD'),
}

from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=requirements_list,
    display_name=get_env_var("APP_NAME"),
    description="The Roborock Agent can control and get the status for the Roborock Vacuum",
    env_vars=env_vars
)

print(remote_app.resource_name)

from dotenv import set_key, find_dotenv
# Find the .env file (usually in the current directory or project root)
dotenv_path = find_dotenv(usecwd=True)
if not dotenv_path: # If .env is not found, default to creating one in the current directory
    dotenv_path = ".env"
set_key(dotenv_path, "AGENT_ENGINE_APP_RESOURCE_ID", remote_app.resource_name)
print(f"AGENT_ENGINE_APP_RESOURCE_ID='{remote_app.resource_name}' has been set in {dotenv_path}")

# Verify the key can be loaded
print(f"Verifying AGENT_ENGINE_APP_RESOURCE_ID from {dotenv_path}...")
# Clear the variable from os.environ if it was set by a previous load_dotenv in this same script run
if "AGENT_ENGINE_APP_RESOURCE_ID" in os.environ:
    del os.environ["AGENT_ENGINE_APP_RESOURCE_ID"]
load_dotenv(dotenv_path=dotenv_path, override=True) # Force reload from the .env file
loaded_app_resource_id = os.getenv("AGENT_ENGINE_APP_RESOURCE_ID")
if loaded_app_resource_id == remote_app.resource_name:
    print(f"Successfully loaded AGENT_ENGINE_APP_RESOURCE_ID: {loaded_app_resource_id}")
else:
    print(f"Error: AGENT_ENGINE_APP_RESOURCE_ID could not be verified. Expected '{remote_app.resource_name}', got '{loaded_app_resource_id}'")