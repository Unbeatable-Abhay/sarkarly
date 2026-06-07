import requests

response = requests.post(
    "http://localhost:5000/home",
    json={"query": "I am a farmer with 5 acres in UP, which schemes can I get?"}
)

print(response.json())