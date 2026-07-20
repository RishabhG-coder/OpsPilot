from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from pdf_loader import load_pdf
from rag import create_chunks, create_vectorstore, ask_question

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

# This will hold our FAISS index
vectorstore = None

@app.get("/")
def home():
    return {"message": "OpsPilot Backend Running 🚀"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore

    # Create uploads folder if it doesn't exist
    os.makedirs("../uploads", exist_ok=True)

    file_path = f"../uploads/{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    text = load_pdf(file_path)

    # Create chunks
    chunks = create_chunks(text)

    # Create FAISS vector database
    vectorstore = create_vectorstore(chunks)

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "chunks": len(chunks)
    }

@app.post("/ask")
def ask(data: QuestionRequest):
    global vectorstore

    if vectorstore is None:
        return {
            "error": "Please upload a PDF first."
        }

    try:
        answer = ask_question(vectorstore, data.question)
        return {
            "answer": answer
        }

    except Exception as e:
        print("ERROR:", repr(e))
        return {
            "error": "Gemini API quota exceeded. Please try again later."
        }