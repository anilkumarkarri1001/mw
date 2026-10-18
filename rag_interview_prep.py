Folder Structure
text
fastapi-rag-gemini/
├── .env
├── main.py
├── requirements.txt
└── routers/
    ├── __init__.py
    ├── upload.py
    └── ask.py
1. requirements.txt
Create this file to install the necessary libraries. Note that we are using google-generativeai instead of openai.

text
fastapi
uvicorn
python-dotenv
pydantic
chromadb
pypdf
python-multipart
google-generativeai
2. .env
Create this file and paste your Gemini API key. You can get one for free at Google AI Studio.

env
GEMINI_API_KEY=your_actual_gemini_api_key_here
3. main.py
This is the entry point of your application.

python
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Import routers
from routers import upload, ask

# Include routers
app.include_router(upload.router)
app.include_router(ask.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG API with Gemini"}
4. routers/__init__.py
Leave this file empty. It just tells Python that routers is a package.

5. routers/upload.py
This file handles PDF uploading, text extraction, chunking, and storing embeddings in ChromaDB using Gemini's embedding model.

python
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
import chromadb
from pypdf import PdfReader
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text(file_path: str):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def text_embedding(text: str):
    # Using Gemini's text embedding model
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text
    )
    return response['embedding']

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the file
    content = file.file.read()
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Extract text
    text = extract_text(file_path)
    chunks = chunk_text(text)
    
    # Process and store chunks
    for chunk in chunks:
        embedding = text_embedding(chunk)
        collection.add(
            ids=[str(uuid.uuid4())],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{"filename": file.filename}]
        )
        
    return {
        "message": "Upload Successfully",
        "chunks": len(chunks)
    }
6. routers/ask.py
This file handles the question-answering endpoint. It searches ChromaDB for relevant context and uses the Gemini LLM (gemini-1.5-flash) to generate an answer.

python
from fastapi import APIRouter
from pydantic import BaseModel
import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize ChromaDB (make sure it points to the same path as upload.py)
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

class QuestionRequest(BaseModel):
    question: str

def text_embedding(text: str):
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text
    )
    return response['embedding']

@router.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question
    
    # Get embedding for the question
    question_embedding = text_embedding(question)
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )
    
    # Combine retrieved chunks into a single context string
    documents = results['documents'][0]
    context = "\n\n".join(documents)
    
    # Construct the prompt for Gemini
    prompt = f"""
    You are a helpful PDF assistant.
    
    Answer the user's question using only the information provided in the context below.
    If the answer is not available in the context, say that the information is not available in the document.
    
    Context:
    {context}
    
    Question: {question}
    """
    
    # Call Gemini LLM
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    return {
        "question": question,
        "answer": response.text
    }
How to run this project:
Open your terminal in the fastapi-rag-gemini folder.

Create a virtual environment: python -m venv venv

Activate it:

Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Install dependencies: pip install -r requirements.txt

Run the server: uvicorn main:app --reload

Go to http://127.0.0.1:8000/docs in your browser to test the endpoints.