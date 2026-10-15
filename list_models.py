import boto3

bedrock_client = boto3.client('bedrock', region_name='us-east-1')
response = bedrock_client.list_foundation_models()
for model in response['modelSummaries']:
    if 'claude' in model['modelId'].lower():
        print(f"{model['modelId']} - {model.get('modelName', 'N/A')}")
