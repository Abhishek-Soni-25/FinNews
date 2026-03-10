from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a financial assistant analyzing SEC filings. Use ONLY the provided context to answer.
        Rules:
        - If the answer is not present, say: "The data is not available in the provided filings."
        - Do not invent information.
        - Answer in ONE concise paragraph."""
    ),
    (
        "human",
        """Context: {context}
        Question: {user_query}"""
    )
])

def chatbot(query: str, context: str):

    formatted_prompt = prompt.format_messages(
        user_query=query,
        context=context
    )

    response = model.invoke(formatted_prompt)

    return response.content