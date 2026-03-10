from db.database import get_connection
from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import time

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

symbols = ["BTC", "ETH"]

try:
    conn = get_connection()
    cur = conn.cursor()

    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market=EUR&apikey={ALPHA_VANTAGE_API_KEY}"
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break

        market = data["Meta Data"]["4. Market Code"]
        series = data["Time Series (Digital Currency Daily)"]

        for date_str, values in list(series.items())[:10]:
            date = datetime.strptime(date_str, "%Y-%m-%d")

            open_price = float(values["1. open"])
            high_price = float(values["2. high"])
            low_price = float(values["3. low"])
            close_price = float(values["4. close"])
            volume = float(values["5. volume"])

            cur.execute("""
                INSERT INTO crypto
                (symbol, market, date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                symbol,
                market,
                date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume
            ))

        time.sleep(1)

    conn.commit()
    print("Crypto prices inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()