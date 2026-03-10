import os
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from rag.chunk import chunk_document
from db.vector_db import get_index

load_dotenv()


def convert_chunks_to_documents(chunks):
    """
    Convert chunk dictionary output to LangChain Documents
    """

    documents = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata=chunk["metadata"]
        )
        documents.append(doc)

    return documents


def store_embeddings(file_path):
    """
    Main pipeline:
    1. Chunk SEC filing
    2. Create embeddings
    3. Store vectors in Pinecone
    """

    print("Chunking document...")

    chunks = chunk_document(file_path)

    print(f"Total chunks created: {len(chunks)}")

    documents = convert_chunks_to_documents(chunks)

    print("Initializing Mistral embeddings...")

    embeddings = MistralAIEmbeddings(
        model="mistral-embed",
        api_key=os.getenv("MISTRAL_API_KEY")
    )

    print("Connecting to Pinecone index...")

    index = get_index()

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    print("Storing embeddings in Pinecone...")

    vector_store.add_documents(documents)

    print("Embeddings stored successfully!")


if __name__ == "__main__":

    file_paths = [
        "data/markdown/aapl_10k.md",
        "data/markdown/goog_10k.md",
        "data/markdown/msft_10k.md",
        "data/markdown/nvda_10k.md",
        "data/markdown/tsla_10k.md",
    ]

    for file_path in file_paths:
        store_embeddings(file_path)