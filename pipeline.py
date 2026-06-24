import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Connect to PostgreSQL
connection = psycopg2.connect(
    host=os.getenv("DESTINATION__POSTGRES__CREDENTIALS__HOST"),
    port=os.getenv("DESTINATION__POSTGRES__CREDENTIALS__PORT"),
    database=os.getenv("DESTINATION__POSTGRES__CREDENTIALS__DATABASE"),
    user=os.getenv("DESTINATION__POSTGRES__CREDENTIALS__USERNAME"),
    password=os.getenv("DESTINATION__POSTGRES__CREDENTIALS__PASSWORD"),
)

print("✅ Connected successfully!")

connection.close()
print("Connection closed.")