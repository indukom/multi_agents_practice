import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Get the bearer token
bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

if not bearer_token:
    print("ERROR: AWS_BEARER_TOKEN_BEDROCK not found in .env")
    exit(1)

# Bedrock API endpoint
url = "https://bedrock.us-east-1.amazonaws.com/foundation-models"

headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/x-amz-json-1.1"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        for model in data.get('modelSummaries', []):
            if 'claude' in model.get('modelId', '').lower():
                print(f"{model['modelId']} - {model.get('modelName', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
