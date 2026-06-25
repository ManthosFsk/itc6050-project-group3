import time
from datetime import datetime

import dlt
import requests


# ------------------------------------------------------------
# HTTP session
# ------------------------------------------------------------

session = requests.Session()

import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "itc6050-project-group3",
    "x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")
}


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def get_json(url):

    while True:

        response = session.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:

            retry_after = response.headers.get("Retry-After")

            if retry_after is not None:
                wait = int(retry_after)
            else:
                wait = 20

            print(f"Rate limit reached. Waiting {wait} seconds...")

            time.sleep(wait)

            continue

        response.raise_for_status()


# ------------------------------------------------------------
# Resource: coins
# ------------------------------------------------------------

@dlt.resource(
    name="coins",
    columns={
        "current_price": {"data_type": "double"}
    }
)
def coins():

    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd"
        "&order=market_cap_desc"
        "&per_page=50"
        "&page=1"
    )

    data = get_json(url)

    print(f"Loaded {len(data)} coins")

    yield data

   # ------------------------------------------------------------
# Resource: coin_history
# ------------------------------------------------------------

@dlt.resource(
    name="coin_history",
    columns={
        "price": {"data_type": "double"},
        "market_cap": {"data_type": "double"},
        "total_volume": {"data_type": "double"}
    }
)
def coin_history():

    markets_url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd"
        "&order=market_cap_desc"
        "&per_page=50"
        "&page=1"
    )

    coins = get_json(markets_url)

    print(f"Downloading history for {len(coins)} coins...")

    for index, coin in enumerate(coins, start=1):

        coin_id = coin["id"]

        print(f"[{index}/50] {coin_id}")

        history_url = (
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            "?vs_currency=usd"
            "&days=90"
            "&interval=daily"
        )

        history = get_json(history_url)

        prices = history.get("prices", [])
        market_caps = history.get("market_caps", [])
        total_volumes = history.get("total_volumes", [])

        rows = min(
            len(prices),
            len(market_caps),
            len(total_volumes)
        )

        for i in range(rows):

            timestamp = prices[i][0]

            yield {
                "coin_id": coin_id,
                "date": datetime.utcfromtimestamp(
                    timestamp / 1000
                ).date(),
                "price": prices[i][1],
                "market_cap": market_caps[i][1],
                "total_volume": total_volumes[i][1]
            }

# ------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------

pipeline = dlt.pipeline(
    pipeline_name="crypto_market_pipeline",
    destination="postgres",
    dataset_name="raw"
)

print("\n==============================")
print("Loading coins...")
print("==============================")

coins_info = pipeline.run(
    coins(),
    table_name="coins",
    write_disposition="replace"
)

print(coins_info)

print("\n==============================")
print("Loading coin history...")
print("==============================")

history_info = pipeline.run(
    coin_history(),
    table_name="coin_history",
    write_disposition="replace"
)

print(history_info)

print("\nPipeline completed successfully!")
 