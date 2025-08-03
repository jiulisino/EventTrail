import requests
import json

url = "http://localhost:5000/api/events/search"
headers = {"Content-Type": "application/json"}
data = {"input": "北京暴雨"}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")