import requests
import json

url = "http://127.0.0.1:8000/analyze"
file_path = "sample_contract.pdf"

print(f"Uploading {file_path} to {url}...")
try:
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"file": f})
    
    if response.status_code == 200:
        print("Success! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
