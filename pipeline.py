import requests
import dlt


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
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    print(data[0]["current_price"])
    print(data[1]["current_price"])

    yield data


pipeline = dlt.pipeline(
    pipeline_name="crypto_market_pipeline",
    destination="postgres",
    dataset_name="raw"
)

load_info = pipeline.run(
    coins(),
    table_name="coins",
    write_disposition="replace"
)

print(load_info)