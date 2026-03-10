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
        url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break
        annual_earnings = data["annualEarnings"]

        for annual_earning in annual_earnings[:10]:
            eps = annual_earning["reportedEPS"]
            eps = float(eps) if eps != "None" else None
            year = datetime.strptime(annual_earning["fiscalDateEnding"], "%Y-%m-%d")
            cur.execute("""
                INSERT INTO earnings
                (symbol, eps, year) VALUES (%s, %s, %s)
            """, (symbol, eps, year))

        time.sleep(0.5)

    conn.commit()
    print("Earnings inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()