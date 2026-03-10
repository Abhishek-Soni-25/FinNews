from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

class QueryRoute(BaseModel):
    route: Literal['sql_data', 'cmpy_data'] = Field(description="Route the query to the correct datasource")

parser = PydanticOutputParser(pydantic_object=QueryRoute)

prompt = PromptTemplate(
    template="""
        Classify the user query into one datasource.

        sql_data:
        - questions about financial numbers
        - revenue, profit, EPS, balance sheet
        - cashflow, debt, assets
        - stock or crypto prices
        - anything that requires database numeric values

        cmpy_data:
        - qualitative information from SEC filings
        - company risks
        - supply chain issues
        - management discussion
        - strategy, products, operations
        - regulatory issues

        User Query:
        {query}
        {format_instruction}
""",
    input_variables=['query'],
    partial_variables={'format_instruction': parser.get_format_instructions()}
)

def route_query(query: str) -> str:
    chain = prompt | model | parser

    result = chain.invoke({'query': query})

    return result.route