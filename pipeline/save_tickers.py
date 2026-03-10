import requests
import time
from db.database import get_connection

urls = [
    'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo',
    'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tencent&apikey=demo',
    'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=BA&apikey=demo',
    'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=SAIC&apikey=demo'
]

try:
    conn = get_connection()
    cur = conn.cursor()

    for url in urls:
        r = requests.get(url)
        data = r.json()
        bestMatches = data['bestMatches']
        for bestMatch in bestMatches:
            cur.execute(
                "INSERT INTO tickers (symbol, name) VALUES (%s, %s) ON CONFLICT (symbol) DO NOTHING",
                (bestMatch["1. symbol"], bestMatch["2. name"])
            )
        print(f"{url}: DONE")
        time.sleep(0.5)

    conn.commit()
    print("Tickers inserted successfully")

except Exception as e:
    print(f"Error: {e}")

finally:
    cur.close()
    conn.close()