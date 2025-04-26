# Background
![image](https://github.com/user-attachments/assets/ea67fb7e-f4d5-4db2-aa2b-6e94a1e5b0fd)


This is a Google Agent Development Kit (ADK) example which can control a Roborock device
- https://github.com/google/adk-samples/tree/main

This is a personal development project and is not related to Google or Roborock professionally or at a partnership level.  Gemini Code Assist was also extremely valuable with this effort and saved many hours in related to trying different structures and especially woth debugging errors. 

(will add useage examples) This agent allows for natural language interaction with your Roborock device. The Agent translates your natural language chat inputs into valid commanda by making ise of the functions (tools) defined in the agent.py file

It makes use of the python-roborock library:
- https://github.com/Python-roborock/python-roborock/tree/main/docs

# Install Steps
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
# Running locally
From the directory above roborock-s8-agent,
```
adk web
```
then browse to http://localhost:8000 to begin testing

# Limitations and issues
Due to issues I encountered with passing parameters (work in progress), all functions that would have had parameters (such as the ones for selective room cleaning) have to be added as separate, hard-coded functions

In addition, due to a limitation with room names (segments) not being listed by the Roborock, you must add a mapping manually in the agent.py root_agent instruction sections to let the agent know which room name corresponds to which segment name.  You can ask the agent to "get the room mappings".  Then you will need to copy the "app_segment_clean_XX" function for each segment returned (the first of the 3 values in each line item).  Run each separately, check the App for which room lights up (stop the cleaning if you want to).  Then you can update the instructions section with the mapping.  You can see the section created in the instructions section to see how this works.  This allows for selective cleaning by room name.

For future functionality, you will see a full listing of all commands in the commands.txt file.  If you add your own functionality, ensure you add the functions in the code, add the name of the function to the tools section, and add the details to the instructions section.
