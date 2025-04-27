# Background
![image](https://github.com/user-attachments/assets/ea67fb7e-f4d5-4db2-aa2b-6e94a1e5b0fd)


This is a Google Agent Development Kit (ADK) example which can control a Roborock device. The ADK can be downloaded from here:
- https://github.com/google/adk-samples/tree/main

This is a personal development project and is not related to Google or Roborock professionally or at a partnership level.  

Gemini Code Assist was extremely valuable with this effort and saved many hours in related to trying different structures and especially with debugging errors. 

This agent allows for natural language interaction with your Roborock device. The Agent translates your natural language chat inputs into valid commanda by making use of the functions (tools) defined in the agent.py file

It makes use of the python-roborock library:
- https://github.com/Python-roborock/python-roborock/tree/main/docs

# Current Features
The current features are also listed in the agent.py root_agent instructions
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
- app_segment_clean (starts cleaning rooms or segments)

# Installation Steps
Create a python virtual environment
```
python -m venv .venv
```

Install all pre-requisites using. I ran a pip freeze command which output all requirements. You will likely already have most of them satisfied. 
```
pip install -r requirements.txt
```

Then create a .env file at the root of the directory with the following information:

```
# set variables for credentials
GOOGLE_GENAI_USE_VERTEXAI="false" # assumes you will use AI Studio
GOOGLE_API_KEY="your AI Studio Key" # check https://aistudio-preprod.corp.google.com/apikey

ROBOROCK_USERNAME = "your Roborock Username"
ROBOROCK_PASSWORD = "your Roborock Password"

```
# Agent Configuration
After the above installation, you will need to update the room mapping in your instructions.  You can do this using the output of the get_room_mappings function from the agent after you run locally below.  You can see from the output here, they are only returned as identifiers and not your actually room names.
![image](https://github.com/user-attachments/assets/440a02d4-66fd-446b-bd2b-8f71b83c8715)
And on the left side, you can see and scroll to get all of your room indexes (in this case starting at 16)
![image](https://github.com/user-attachments/assets/f55ee86d-9587-4520-93cf-c86018f88fbd)
Next, add your indexes to the instructions section of your root_agent
```
Segment mapping:
16 = Bedroom4
17 = Balcony
18 = Bedroom3
...
```
Next using the placeholders I have here, ask the agent to clean Bedroom 4.
![image](https://github.com/user-attachments/assets/76092257-9ed2-4010-8fcd-178f0248a5b6)
Now in the Roborock App, you can see which room actually will be cleaned.
![image](https://github.com/user-attachments/assets/851bfff1-1104-4f11-9093-bd83c2cca364)
Now update the instructions line for 16 with your actual room name. You can type stop immediately and keep iterating until complete without having to return to the dock.

# Running locally
From the directory above roborock-s8-agent,
```
adk web
```
then browse to http://localhost:8000 to begin configuration and testing
# Agent Configuration
After the above installation, you will need to update the room mapping in your instructions.  You can do this using the output of the get_room_mappings function from the agent after you run locally below.  You can see from the output here, they are only returned as identifiers and not your actually room names.
![image](https://github.com/user-attachments/assets/440a02d4-66fd-446b-bd2b-8f71b83c8715)
And on the left side, you can see and scroll to get all of your room indexes (in this case starting at 16)
![image](https://github.com/user-attachments/assets/f55ee86d-9587-4520-93cf-c86018f88fbd)
Next, add your indexes to the instructions section of your root_agent
```
Segment mapping:
16 = Bedroom4
17 = Balcony
18 = Bedroom3
...
```
Next using the placeholders I have here, ask the agent to clean Bedroom 4.
![image](https://github.com/user-attachments/assets/76092257-9ed2-4010-8fcd-178f0248a5b6)
Now in the Roborock App, you can see which room actually will be cleaned.
![image](https://github.com/user-attachments/assets/851bfff1-1104-4f11-9093-bd83c2cca364)
Now update the instructions line for 16 with your actual room name. You can type stop immediately and keep iterating until complete without having to return to the dock.
# Limitations and Issues
You must add a mapping manually in the agent.py root_agent instruction sections to let the agent know which room name corresponds to which segment name.  See above for how to do this.

For future functionality, you will see a full listing of all commands in the commands.txt file.  If you add your own functionality, ensure you add the functions in the code, add the name of the function to the tools section, and add the details to the instructions section.
