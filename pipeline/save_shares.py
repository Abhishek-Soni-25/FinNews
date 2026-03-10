from db.database import get_connection
from dotenv import load_dotenv
from datetime import datetime
import requests
import time
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

symbols = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA"]

try:
    conn = get_connection()
    cur = conn.cursor()

    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function=SHARES_OUTSTANDING&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break
        shares = data["data"]

        for share in shares[:4]:
            date = datetime.strptime(share["date"], "%Y-%m-%d")
            cur.execute("""
                INSERT INTO shares
                (symbol, diluted, basic, date) VALUES (%s, %s, %s, %s)
            """, (symbol, int(share["shares_outstanding_diluted"]), int(share["shares_outstanding_basic"]), date))

        time.sleep(1)

    conn.commit()
    print("Shares inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()