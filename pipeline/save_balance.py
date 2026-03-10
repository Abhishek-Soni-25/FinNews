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
        url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break

        report = data["annualReports"][0]

        date = datetime.strptime(report["fiscalDateEnding"], "%Y-%m-%d")

        total_assets = safe_int(report["totalAssets"])
        total_current_assets = safe_int(report["totalCurrentAssets"])
        cash_equivalents = safe_int(report["cashAndCashEquivalentsAtCarryingValue"])
        inventory = safe_int(report["inventory"])
        net_receivables = safe_int(report["currentNetReceivables"])
        property_plant_equipment = safe_int(report["propertyPlantEquipment"])
        intangible_assets = safe_int(report["intangibleAssets"])
        goodwill = safe_int(report["goodwill"])
        total_liabilities = safe_int(report["totalLiabilities"])
        total_current_liabilities = safe_int(report["totalCurrentLiabilities"])
        long_term_debt = safe_int(report["longTermDebt"])
        short_term_debt = safe_int(report["shortTermDebt"])
        shareholder_equity = safe_int(report["totalShareholderEquity"])
        retained_earnings = safe_int(report["retainedEarnings"])
        shares_outstanding = safe_int(report["commonStockSharesOutstanding"])

        cur.execute("""
            INSERT INTO balance_sheet
            (symbol, date, total_assets, total_current_assets, cash_equivalents, inventory,
            net_receivables, property_plant_equipment, intangible_assets, goodwill,
            total_liabilities, total_current_liabilities, long_term_debt, short_term_debt,
            shareholder_equity, retained_earnings, shares_outstanding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            symbol,
            date,
            total_assets,
            total_current_assets,
            cash_equivalents,
            inventory,
            net_receivables,
            property_plant_equipment,
            intangible_assets,
            goodwill,
            total_liabilities,
            total_current_liabilities,
            long_term_debt,
            short_term_debt,
            shareholder_equity,
            retained_earnings,
            shares_outstanding
        ))

        time.sleep(1)

    conn.commit()
    print("Balance sheet inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()