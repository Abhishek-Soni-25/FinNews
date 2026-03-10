from db.database import get_connection
from dotenv import load_dotenv
from datetime import datetime
import requests
import time
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

symbols = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA"]

def safe_int(value):
    return int(value) if value != "None" else None

try:
    conn = get_connection()
    cur = conn.cursor()

    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break
        report = data["annualReports"][0]

        date = datetime.strptime(report["fiscalDateEnding"], "%Y-%m-%d")
        operating_cashflow = safe_int(report["operatingCashflow"])
        capital_expenditures = safe_int(report["capitalExpenditures"])
        cashflow_investing = safe_int(report["cashflowFromInvestment"])
        cashflow_financing = safe_int(report["cashflowFromFinancing"])
        dividend_payout = safe_int(report["dividendPayout"])
        stock_based_compensation = safe_int(report["stockBasedCompensation"])
        net_income = safe_int(report["netIncome"])
        cur.execute("""
            INSERT INTO cashflow
            (symbol, date, operating_cashflow, capital_expenditures, cashflow_investing, cashflow_financing, dividend_payout, stock_based_compensation, net_income)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (symbol, date, operating_cashflow, capital_expenditures, cashflow_investing, cashflow_financing, dividend_payout, stock_based_compensation, net_income))

        time.sleep(1)

    conn.commit()
    print("CashFlow inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()