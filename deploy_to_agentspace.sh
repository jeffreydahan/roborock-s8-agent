#!/bin/bash

# Source environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Variables
ACCESS_TOKEN=$(gcloud auth print-access-token)


# Use the following from the .env file, or a default if not set
PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
LOCATION="${GOOGLE_CLOUD_LOCATION}"
COLLECTION_ID="default_collection"
ENGINE_ID="${AGENTSPACE_ENGINE_ID}"
ASSISTANT_ID="default_assistant"
REASONING_ENGINE_ID="${AGENT_ENGINE_APP_RESOURCE_ID}"

API_ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/${COLLECTION_ID}/engines/${ENGINE_ID}/assistants/${ASSISTANT_ID}/agents"

JSON_PAYLOAD=$(cat <<EOF
{
    "displayName": "Roborock Agent",
    "description": "This agent can control and get the status of a Roborock Vacuum",
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "This agent can control and get the status of a Roborock Vacuum"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": "${REASONING_ENGINE_ID}"
        }
    }
}
EOF
)

curl -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "${API_ENDPOINT}" \
    -d "${JSON_PAYLOAD}"