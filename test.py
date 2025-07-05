import os

endpoint = os.environ["AZURE_AI_ENDPOINT"]
token = os.environ["AZURE_AI_SECRET"]

print("Endpoint:", endpoint)
print("Token:", token)
