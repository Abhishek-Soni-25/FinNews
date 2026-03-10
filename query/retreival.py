from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

from db.vector_db import get_index
from chat.query_llm import chatbot

load_dotenv()


def retrieve_chunks(user_query: str, k: int = 3):
    """
    1. Embed the user query
    2. Retrieve top-k chunks from Pinecone
    3. Build context
    4. Send query + context to chatbot()
    """

    # Initialize embedding model
    embeddings = MistralAIEmbeddings(
        model="mistral-embed",
        api_key=os.getenv("MISTRAL_API_KEY")
    )

    # Connect to Pinecone index
    index = get_index()

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    # Retrieve top-k similar chunks
    docs = vector_store.similarity_search(user_query, k=k)

    # Build context string
    context_parts = []

    for d in docs:

        metadata = d.metadata

        part = metadata.get("part", "")
        item = metadata.get("item", "")
        section = metadata.get("section", "")
        subsection = metadata.get("subsection", "")
        source = metadata.get("source", "")

        header = f"{part} | {item} | {section} | {subsection} | {source}"

        context_parts.append(
            f"{header}\n{d.page_content}"
        )

    context = "\n\n".join(context_parts)

    # Send to chatbot
    response = chatbot(user_query, context)

    return response