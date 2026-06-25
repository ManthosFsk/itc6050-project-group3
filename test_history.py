import requests
import json

url = (
    "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    "?vs_currency=usd&days=90"
)

response = requests.get(url)
response.raise_for_status()

data = response.json()

print(json.dumps(data, indent=2)[:3000])