import os
import json
import requests
from flask import Flask, request, jsonify
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = Flask(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
AGENT_ID = os.environ["AGENT_ID"]
LOCATION = os.environ["LOCATION"]

def get_credentials():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/agent-creds/versions/latest"
    response = client.access_secret_version(name=name)
    secret_payload = response.payload.data.decode("UTF-8")
    credentials_info = json.loads(secret_payload)
    return service_account.Credentials.from_service_account_info(credentials_info)

def get_access_token():
    credentials = get_credentials()
    credentials.refresh(Request())
    return credentials.token

@app.route('/call-agent', methods=['POST'])
def call_agent():
    access_token = get_access_token()
    user_input = request.json.get("query", "")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "query": user_input
    }

    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}:chat"

    response = requests.post(url, headers=headers, json=body)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run()
