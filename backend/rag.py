from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from llm import llm

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


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