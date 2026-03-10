from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from db.database import get_connection
from dotenv import load_dotenv
import toons

load_dotenv()

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

schemas = {
    "earnings": ["symbol","eps","year"],
    "shares": ["symbol","diluted","basic","date"],
    "cashflow": ["symbol","date","operating_cashflow","capital_expenditures","cashflow_investing","cashflow_financing","dividend_payout","stock_based_compensation","net_income"],
    "income_statement": ["symbol","date","gross_profit","total_revenue","cost_of_revenue","operating_income","research_and_development","operating_expenses","income_before_tax","income_tax_expense","ebit","ebitda","net_income"],
    "balance_sheet": ["symbol","date","total_assets","total_current_assets","cash_equivalents","inventory","net_receivables","property_plant_equipment","intangible_assets","goodwill","total_liabilities","total_current_liabilities","long_term_debt","short_term_debt","shareholder_equity","retained_earnings","shares_outstanding"],
    "crypto": ["symbol","market","date","open_price","high_price","low_price","close_price","volume"]
}

schema_tokens = toons.dumps(schemas)

class SQLResponse(BaseModel):
    answer_prefix: str = Field(description="Sentence prefix for the answer")
    sql: str = Field(description="PostgreSQL SQL query")

parser = PydanticOutputParser(pydantic_object=SQLResponse)

prompt = PromptTemplate(
    template=""" Generate SQL and answer prefix. Database schema: {schema}
        Rules:
        - Stock symbols: AAPL, MSFT, GOOG, TSLA, NVDA
        - Crypto symbols: BTC, ETH
        - Do NOT generate actual numbers
        - Answer prefix should end with a colon (:)
        {format_instructions}
        User Question: {query}
    """,
    input_variables=["query"],
    partial_variables={
        "schema": schema_tokens,
        "format_instructions": parser.get_format_instructions()
    }
)

def generate_sql_response(query: str):

    chain = prompt | model | parser

    response = chain.invoke({"query": query})

    return response

def formatted_response(query: str):
    result = generate_sql_response(query)

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(result.sql)

        rows = cur.fetchall()
        if len(rows) == 1:
            ans = rows[0][0]
        else:
            ans = rows

        return f"{result.answer_prefix} {ans}"
        
    except Exception as e:
        print(f"Error: {e}")

    finally:
        cur.close()
        conn.close()