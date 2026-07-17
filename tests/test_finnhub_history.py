import time
import requests

# Replace with your API key
API_KEY = "d9c1299r01qiem1ut26gd9c1299r01qiem1ut270"

# Last 5 days
to_time = int(time.time())
from_time = to_time - (5 * 24 * 60 * 60)

url = "https://finnhub.io/api/v1/stock/candle"

params = {
    "symbol": "^NSEI",
    "resolution": "3",
    "from": from_time,
    "to": to_time,
    "token": API_KEY,
}

response = requests.get(url, params=params)

print("Status Code:", response.status_code)
print(response.json())