from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from llm import llm

import os
import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


class CohereEmbeddings(Embeddings):
    def embed_documents(self, texts):
        response = co.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings.float

    def embed_query(self, text):
        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        return response.embeddings.float[0]


embedding_model = CohereEmbeddings()


def create_chunks(text):
    return text_splitter.create_documents([text])


def create_vectorstore(chunks):
    return FAISS.from_documents(chunks, embedding_model)


def ask_question(vectorstore, question):
    docs = vectorstore.similarity_search(question, k=4)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a helpful assistant.

Answer ONLY using the context below.

If the answer is not present, reply exactly:
"I couldn't find that information in the uploaded PDF."

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    if hasattr(response, "text"):
        return response.text()

    if isinstance(response.content, list):
        return response.content[0]["text"]

    return str(response.content)