from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

prompt = PromptTemplate(
    template="""
        You are a helpful financial assistant.
        Answer the user query in plain text only.
        Rules:
        - The response must be a single paragraph.
        - Do NOT use markdown.
        - Do NOT use symbols like: \\n, -, /, \\, *, #, or bullet points.
        User Query: {query}
    """,
    input_variables=["query"]
)

def generate_default_response(query: str):
    formatted_prompt = prompt.format(query=query)
    response = model.invoke(formatted_prompt)
    return response.content