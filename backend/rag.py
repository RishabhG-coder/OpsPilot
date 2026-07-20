from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from llm import llm

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

import os
from dotenv import load_dotenv

load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(
    model="text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def get_embedding_model():
    return embedding_model

def create_chunks(text):
    return text_splitter.create_documents([text])


def create_vectorstore(chunks):
    return FAISS.from_documents(
        chunks,
        get_embedding_model()
    )


def ask_question(vectorstore, question):
    docs = vectorstore.similarity_search(question, k=4)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.

If the answer is not present, reply:
"I couldn't find that information in the uploaded PDF."

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    # Handle latest LangChain response format
    if hasattr(response, "text"):
        return response.text()

    if isinstance(response.content, list):
        return response.content[0]["text"]

    return str(response.content)