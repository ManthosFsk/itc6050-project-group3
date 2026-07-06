import os
import time
from datetime import datetime, timezone

import dlt
import requests
from dotenv import load_dotenv

# ------------------------------------------------------------
# HTTP session
# ------------------------------------------------------------

session = requests.Session()

load_dotenv()

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "itc6050-project-group3",
    "x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")
}

MARKETS_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd"
    "&order=market_cap_desc"
    "&per_page=50"
    "&page=1"
)


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
# Fetch the top-50 markets ONCE and reuse across resources
# ------------------------------------------------------------

def get_markets():

    print("Fetching top 50 markets...")

    return get_json(MARKETS_URL)


markets_data = get_markets()


# ------------------------------------------------------------
# Resource: coins  (snapshot -> replace)
# ------------------------------------------------------------

@dlt.resource(
    name="coins",
    write_disposition="replace",
    columns={
        "current_price": {"data_type": "double"}
    }
)
def coins():

    print(f"Loaded {len(markets_data)} coins")

    yield markets_data


# ------------------------------------------------------------
# Resource: coin_history  (historical -> merge on coin_id + date)
# ------------------------------------------------------------

@dlt.resource(
    name="coin_history",
    write_disposition="merge",
    primary_key=["coin_id", "date"],
    columns={
        "price": {"data_type": "double"},
        "market_cap": {"data_type": "double"},
        "total_volume": {"data_type": "double"}
    }
)
def coin_history():

    print(f"Downloading history for {len(markets_data)} coins...")

    for index, coin in enumerate(markets_data, start=1):

        coin_id = coin["id"]

        print(f"[{index}/{len(markets_data)}] {coin_id}")

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
                "date": datetime.fromtimestamp(
                    timestamp / 1000, tz=timezone.utc
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

coins_info = pipeline.run(coins())

print(coins_info)

print("\n==============================")
print("Loading coin history...")
print("==============================")

history_info = pipeline.run(coin_history())

print(history_info)

print("\nPipeline completed successfully!")