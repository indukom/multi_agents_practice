import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get AWS credentials from environment variables
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
session_token = os.getenv("AWS_SESSION_TOKEN")

print("AWS Credentials loaded:")
print(f"  Access Key: {access_key_id[:20] if access_key_id else 'Not found'}...")
print(f"  Secret Key: {secret_access_key[:20] if secret_access_key else 'Not found'}...")
print(f"  Session Token: {session_token[:20] if session_token else 'Not found'}...")

# Set environment variables for boto3
os.environ["AWS_ACCESS_KEY_ID"] = access_key_id or ""
os.environ["AWS_SECRET_ACCESS_KEY"] = secret_access_key or ""
os.environ["AWS_SESSION_TOKEN"] = session_token or ""

# Now try to connect to Bedrock
import boto3

try:
    bedrock = boto3.client("bedrock", region_name="us-east-1")
    response = bedrock.list_foundation_models()
    
    print("\nAvailable Claude models in us-east-1:")
    models = []
    for model in response['modelSummaries']:
        model_id = model['modelId']
        if 'claude' in model_id.lower():
            models.append(model_id)
            print(f"  ✓ {model_id}")
    
    if models:
        print(f"\nRecommended model: {models[0]}")
    else:
        print("\nNo Claude models found in us-east-1")
        
except Exception as e:
    print(f"\nError connecting to Bedrock: {e}")
    print("\nTrying us-west-2 for inference profiles...")
    
    try:
        bedrock = boto3.client("bedrock", region_name="us-west-2")
        response = bedrock.list_foundation_models()
        
        print("\nAvailable models in us-west-2:")
        models = []
        for model in response['modelSummaries']:
            model_id = model['modelId']
            if 'claude' in model_id.lower():
                models.append(model_id)
                print(f"  ✓ {model_id}")
                
        if models:
            print(f"\nRecommended model: {models[0]}")
            print("Region: us-west-2")
            
    except Exception as e2:
        print(f"Error in us-west-2: {e2}")
