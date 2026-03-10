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
        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        if "Information" in data:
            print(f"API limit reached or invalid request: {data}")
            break

        report = data["annualReports"][0]

        date = datetime.strptime(report["fiscalDateEnding"], "%Y-%m-%d")
        gross_profit = safe_int(report["grossProfit"])
        total_revenue = safe_int(report["totalRevenue"])
        cost_of_revenue = safe_int(report["costOfRevenue"])
        operating_income = safe_int(report["operatingIncome"])
        research_and_development = safe_int(report["researchAndDevelopment"])
        operating_expenses = safe_int(report["operatingExpenses"])
        income_before_tax = safe_int(report["incomeBeforeTax"])
        income_tax_expense = safe_int(report["incomeTaxExpense"])
        ebit = safe_int(report["ebit"])
        ebitda = safe_int(report["ebitda"])
        net_income = safe_int(report["netIncome"])

        cur.execute("""
            INSERT INTO income_statement
            (symbol, date, gross_profit, total_revenue, cost_of_revenue, operating_income,
            research_and_development, operating_expenses, income_before_tax, income_tax_expense,
            ebit, ebitda, net_income)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            symbol,
            date,
            gross_profit,
            total_revenue,
            cost_of_revenue,
            operating_income,
            research_and_development,
            operating_expenses,
            income_before_tax,
            income_tax_expense,
            ebit,
            ebitda,
            net_income
        ))

        time.sleep(1)

    conn.commit()
    print("Income statements inserted successfully")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()