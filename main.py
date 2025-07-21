from flask import Flask, request, jsonify
import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return 'App running', 200

@app.route('/startup-probe')
def startup_probe():
    return 'OK', 200

@app.route('/get-access-token', methods=['GET'])
def get_access_token():
    try:
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
        credentials.refresh(Request())
        access_token = credentials.token
        return jsonify({'access_token': access_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/call-agent', methods=['POST'])
def call_agent():
    try:
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
        credentials.refresh(Request())
        access_token = credentials.token

        project_id = os.environ.get("PROJECT_ID")
        agent_id = os.environ.get("AGENT_ID")
        url_base = os.environ.get("VERTEX_AGENT_URL")

        endpoint = f"{url_base}/v1/projects/{project_id}/locations/us-central1/agents/{agent_id}:detectIntent"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = request.get_json()
        response = requests.post(endpoint, headers=headers, json=payload)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
