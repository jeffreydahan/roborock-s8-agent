
from agent import *
import vertexai


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