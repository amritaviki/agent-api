import json
import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.auth import jwt
from google.auth.transport.requests import Request as GoogleRequest

class TextInput(BaseModel):
    text: str

app = FastAPI()

def get_access_token():
    sa_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    credentials = jwt.Credentials.from_service_account_info(
        sa_info, audience="https://dialogflow.googleapis.com/"
    )
    credentials.refresh(GoogleRequest())
    return credentials.token

@app.post("/detect-intent")
def detect_intent(input_data: TextInput):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    session_id = "session-001"
    url = f"https://us-central1-dialogflow.googleapis.com/v3/projects/{os.environ['PROJECT_ID']}/locations/us-central1/agents/{os.environ['AGENT_ID']}/sessions/{session_id}:detectIntent"
    payload = {
        "queryInput": {
            "text": {
                "text": input_data.text,
                "languageCode": "en"
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
