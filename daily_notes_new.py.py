1. Proxy = An intermediary that acts on behalf of someone or something. 
1. roxy = బదులుగా పనిచేసే మధ్యవర్తి
2. Proxy number = మధ్యలో ఉపయోగించే ఫోన్ నంబర్
3. Proxy system = ఇద్దరి మధ్య కమ్యూనికేషన్‌ను నిర్వహించే వ్యవస్థ meanign in enligh


==========================================================================>

Step 1: Check ngrok installation
In the same PowerShell window, run:
ngrok version
Expected output will look similar to:
ngrok version 3.x.x
If PowerShell says ngrok is not recognized, close PowerShell, open a new window, and try again.
Step 2: Configure your ngrok token
If the version command works, open the ngrok dashboard, copy your authentication token, and run:
ngrok config add-authtoken "YOUR_ACTUAL_TOKEN"
Replace the placeholder with your token. Do not share the token publicly.
Step 3: Start your FastAPI server
Open a separate PowerShell terminal and run:
cd C:\Users\DELL\Downloads\whatsapp_meta\whatsapp_meta
Activate your environment:
.\meta_env\Scripts\Activate.ps1
Then start the application using the correct module name. For example, if your FastAPI instance is in main.py:
python -m uvicorn main:app --host 127.0.0.1 --port 8001
Keep this terminal running.
Step 4: Generate the public URL
Open another PowerShell window and run:
ngrok http 8001
You should see a forwarding address similar to:
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8001
Your webhook URL will use this public domain plus your actual webhook route, for example:
https://abc123.ngrok-free.app/webhook
The /webhook path is only correct if your application defines that route.
First, run ngrok version and send me the output. We'll confirm the installation before moving to the webhook configuration.








=====================================================================>


=====================================================================>

 What is a WebSocket in FastAPI?
A WebSocket provides a persistent, bidirectional communication channel between a client and a server. 
In this code, FastAPI accepts a WebSocket connection, registers it with a connection manager, 
continuously listens for incoming text messages, and removes the connection when the client disconnects.
 Other backend code can use the connection manager to send real-time notifications to connected 
dashboard clients. 

=====================================================================>


    upload_media_to_meta,
    download_whatsapp_media_bytes,
    generate_gemini_reply,
    build_substituted_template_data
)
from db import update_or_create_conversation, save_message_record, get_conversations, get_chat_history, save_ocr_result, update_message_ocr, update_message_status, save_flow_submission, get_api_delivery_logs, get_message_status_by_id, get_batch_message_statuses, INDEX_FLOW_SUBMISSIONS
from datetime import datetime, timezone
from config import APPS_CONFIG, OCR_SERVICE_URL
from logging_config import logger

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "your_verify_token")
PLAYSTORE_URL = os.getenv("PLAYSTORE_URL", "https://play.google.com/store/apps/details?id=com.markwave.animalcart")
APPSTORE_URL = os.getenv("APPSTORE_URL", "https://apps.apple.com/in/app/animal-kart/id6758013353")

router = APIRouter()
security = HTTPBearer()




# ---------------------------------------------------------------------------
# WebSocket Manager for Dashboard
# ---------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total active connections: {len(self.active_connections)}", flush=True)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS] Client disconnected. Total active connections: {len(self.active_connections)}", flush=True)

    async def broadcast(self, message: dict):
        print(f"[WS] Broadcasting event='{message.get('event')}' app='{message.get('app_name')}' to {len(self.active_connections)} active client(s)", flush=True)
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending message to client: {e}", flush=True)
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

ws_manager = ConnectionManager()

=====================================================================>

Semantic Search అంటే తెలుగులో “అర్థం ఆధారంగా వెతకడం” (Searching based on meaning).
అంటే, మనం ఏ పదాలతో search చేసినా, ఆ పదాల వెనుక ఉన్న అర్థాన్ని అర్థం చేసుకుని సంబంధిత సమాచారాన్ని వెతకడం.
Simple example
మీ company documents లో ఈ sentence ఉందనుకుందాం:
"Employees can take 12 casual leaves per year."
ఇప్పుడు మీరు ఈ ప్రశ్న అడిగారు:
"How many days can I take off from work?"
Keyword Search: days off అనే పదాల కోసం వెతికితే, document లో ఆ exact words లేవు కాబట్టి result దొరకకపోవచ్చు.
Semantic Search: మీరు అడిగిన ప్రశ్న అర్థాన్ని అర్థం చేసుకుని, casual leaves గురించి ఉన్న document ను గుర్తించగలదు.
Illustrative numbers only అంటే తెలుగులో “ఉదాహరణ కోసం మాత్రమే ఇచ్చిన సంఖ్యలు” లేదా “కేవలం వివరణ కోసం ఉపయోగించిన సంఖ్యలు” అని అర్థం.
1. What is a Vector Database?
A Vector Database is a database designed to store numerical representations of data called vectors and efficiently find data that is similar in meaning to a search query.
To understand why we need one, let's start with a real-world problem.
Example 1: Searching in a normal database
Imagine you are building a company chatbot. Your company has these documents:
Document 1
"Employees can take 12 casual leaves per year."
Document 2
"The office working hours are 9 AM to 6 PM."
Document 3
"Employees receive health insurance benefits."
Now a user asks:
"How many days can I take off from work?"
A traditional database query that searches for the exact words days off might fail to find Document 1 because it contains the words casual leaves, not days off.
A traditional database is not inherently limited to exact matching—it can also use full-text search, synonyms, and other techniques—but ordinary keyword searches may miss relevant information when the wording differs.
This is one of the problems vector search helps solve.
4. What happens if we don't use a vector database?
Let's compare the alternatives.
Approach	What can happen?
Exact keyword matching	May miss information expressed using different words
Traditional SQL queries	Great for structured data, but semantic search requires additional capabilities
Full-text search	Good for words and phrases; semantic similarity may need additional techniques
Store vectors in a simple file or list	Can work for small datasets, but indexing, filtering, persistence, and scaling become your responsibility
Vector database	Provides specialized storage and similarity-search capabilities
Computers don't naturally understand the meaning of sentences as humans do. An embedding model converts text into a list of numbers called a vector embedding.
For example, imagine an embedding model converts these sentences into vectors:
Sentence A
"How many days off can I take?"
Example vector (simplified)
[0.82, 0.21, 0.67, 0.14]
Sentence B
"How many casual leaves are available?"
Example vector (simplified)
[0.80, 0.24, 0.65, 0.17]
Sentence C
"What time does the office open?"
Example vector (simplified)
[0.12, 0.91, 0.18, 0.73]
Illustrative numbers only. Real embeddings usually have many more dimensions, and their values depend on the model.
Sentences A and B have similar meanings, so a suitable embedding model will often represent them as vectors that are close under an appropriate similarity measure.
3. Why were vector databases introduced?
As AI applications began working with large amounts of text, images, audio, and other data, developers needed efficient ways to search by semantic similarity rather than relying only on exact words.
Vector databases and vector search systems address several challenges:
Problem 1: Different words, same meaning
A user searches for "forgot my password," but the document says "account recovery instructions."
Vector search can find the related document even when the wording differs.
Problem 2: Too much data to search inefficiently
Imagine millions of document chunks. Comparing every query against every stored vector can become expensive and slow.
Vector databases can use indexing techniques to find similar vectors efficiently, often without comparing every vector individually.
Vector databases are not the only way to solve these problems. Some relational databases, search engines, and specialized libraries also support vector search.
RAG solves this by retrieving information from the company's documents and supplying it to the model.
Here is the complete workflow.
1. Company documents
PDFs, Word files, FAQs, policies
2. Split into chunks
Divide long documents into smaller pieces
3. Embedding model
Convert each chunk into a vector
4. Vector database
Store vectors and associated document information
When a user asks a question
5. Embed the question and retrieve similar chunks
6. Send retrieved context + question to the LLM
7. Generate the answer
Based on the retrieved information
6. Real-world use cases
Use case 1: Customer support chatbot
User: "My payment went through, but my order isn't showing."
The system retrieves relevant payment and order troubleshooting articles, then gives the user an appropriate response.
Use case 2: Company HR assistant
User: "Can I take a day off for a personal reason?"
The system searches HR policies for the relevant leave rules and provides those rules to the LLM.
Use case 3: E-commerce search
User: "Comfortable shoes for walking all day."
Vector search can retrieve products described as cushioned, lightweight, or suitable for extended walking, even if the exact query words aren't in the product description.
Use case 4: Coding assistant
Developer: "Where do we handle reconnection when the WebSocket disconnects?"
The system retrieves relevant code snippets or documentation to provide context for the answer.
Q2. Why do we use a vector database in RAG?
We use it to retrieve relevant document chunks based on the semantic similarity between the user's query and the stored document embeddings. The retrieved context is then supplied to the LLM to generate an informed answer.
Q3. What is an embedding?
An embedding is a numerical representation of data, such as text, that captures useful semantic or other learned features.
Q4. Can we implement RAG without a vector database?
Yes. We can use keyword search, a relational database with vector support, or an in-memory similarity-search implementation. A dedicated vector database is one possible solution, not a mandatory requirement.
Q5. Name some vector databases.
Pinecone, Chroma, Qdrant, Weaviate, and Milvus are examples. FAISS is a popular vector similarity-search library, and PostgreSQL can support vector search using pgvector.

=====================================================================>
Semantic Search అంటే తెలుగులో “అర్థం ఆధారంగా వెతకడం” (Searching based on meaning).
అంటే, మనం ఏ పదాలతో search చేసినా, ఆ పదాల వెనుక ఉన్న అర్థాన్ని అర్థం చేసుకుని సంబంధిత సమాచారాన్ని వెతకడం.
Simple example
మీ company documents లో ఈ sentence ఉందనుకుందాం:
"Employees can take 12 casual leaves per year."
ఇప్పుడు మీరు ఈ ప్రశ్న అడిగారు:
"How many days can I take off from work?"
Keyword Search: days off అనే పదాల కోసం వెతికితే, document లో ఆ exact words లేవు కాబట్టి result దొరకకపోవచ్చు.
Semantic Search: మీరు అడిగిన ప్రశ్న అర్థాన్ని అర్థం చేసుకుని, casual leaves గురించి ఉన్న document ను గుర్తించగలదు.
Illustrative numbers only అంటే తెలుగులో “ఉదాహరణ కోసం మాత్రమే ఇచ్చిన సంఖ్యలు” లేదా “కేవలం వివరణ కోసం ఉపయోగించిన సంఖ్యలు” అని అర్థం.
1. What is a Vector Database?
A Vector Database is a database designed to store numerical representations of data called vectors and efficiently find data that is similar in meaning to a search query.
To understand why we need one, let's start with a real-world problem.
Example 1: Searching in a normal database
Imagine you are building a company chatbot. Your company has these documents:
Document 1
"Employees can take 12 casual leaves per year."
Document 2
"The office working hours are 9 AM to 6 PM."
Document 3
"Employees receive health insurance benefits."
Now a user asks:
"How many days can I take off from work?"
A traditional database query that searches for the exact words days off might fail to find Document 1 because it contains the words casual leaves, not days off.
A traditional database is not inherently limited to exact matching—it can also use full-text search, synonyms, and other techniques—but ordinary keyword searches may miss relevant information when the wording differs.
This is one of the problems vector search helps solve.
4. What happens if we don't use a vector database?
Let's compare the alternatives.
Approach	What can happen?
Exact keyword matching	May miss information expressed using different words
Traditional SQL queries	Great for structured data, but semantic search requires additional capabilities
Full-text search	Good for words and phrases; semantic similarity may need additional techniques
Store vectors in a simple file or list	Can work for small datasets, but indexing, filtering, persistence, and scaling become your responsibility
Vector database	Provides specialized storage and similarity-search capabilities
Computers don't naturally understand the meaning of sentences as humans do. An embedding model converts text into a list of numbers called a vector embedding.
For example, imagine an embedding model converts these sentences into vectors:
Sentence A
"How many days off can I take?"
Example vector (simplified)
[0.82, 0.21, 0.67, 0.14]
Sentence B
"How many casual leaves are available?"
Example vector (simplified)
[0.80, 0.24, 0.65, 0.17]
Sentence C
"What time does the office open?"
Example vector (simplified)
[0.12, 0.91, 0.18, 0.73]
Illustrative numbers only. Real embeddings usually have many more dimensions, and their values depend on the model.
Sentences A and B have similar meanings, so a suitable embedding model will often represent them as vectors that are close under an appropriate similarity measure.
3. Why were vector databases introduced?
As AI applications began working with large amounts of text, images, audio, and other data, developers needed efficient ways to search by semantic similarity rather than relying only on exact words.
Vector databases and vector search systems address several challenges:
Problem 1: Different words, same meaning
A user searches for "forgot my password," but the document says "account recovery instructions."
Vector search can find the related document even when the wording differs.
Problem 2: Too much data to search inefficiently
Imagine millions of document chunks. Comparing every query against every stored vector can become expensive and slow.
Vector databases can use indexing techniques to find similar vectors efficiently, often without comparing every vector individually.
Vector databases are not the only way to solve these problems. Some relational databases, search engines, and specialized libraries also support vector search.
RAG solves this by retrieving information from the company's documents and supplying it to the model.
Here is the complete workflow.
1. Company documents
PDFs, Word files, FAQs, policies
2. Split into chunks
Divide long documents into smaller pieces
3. Embedding model
Convert each chunk into a vector
4. Vector database
Store vectors and associated document information
When a user asks a question
5. Embed the question and retrieve similar chunks
6. Send retrieved context + question to the LLM
7. Generate the answer
Based on the retrieved information
6. Real-world use cases
Use case 1: Customer support chatbot
User: "My payment went through, but my order isn't showing."
The system retrieves relevant payment and order troubleshooting articles, then gives the user an appropriate response.
Use case 2: Company HR assistant
User: "Can I take a day off for a personal reason?"
The system searches HR policies for the relevant leave rules and provides those rules to the LLM.
Use case 3: E-commerce search
User: "Comfortable shoes for walking all day."
Vector search can retrieve products described as cushioned, lightweight, or suitable for extended walking, even if the exact query words aren't in the product description.
Use case 4: Coding assistant
Developer: "Where do we handle reconnection when the WebSocket disconnects?"
The system retrieves relevant code snippets or documentation to provide context for the answer.
Q2. Why do we use a vector database in RAG?
We use it to retrieve relevant document chunks based on the semantic similarity between the user's query and the stored document embeddings. The retrieved context is then supplied to the LLM to generate an informed answer.
Q3. What is an embedding?
An embedding is a numerical representation of data, such as text, that captures useful semantic or other learned features.
Q4. Can we implement RAG without a vector database?
Yes. We can use keyword search, a relational database with vector support, or an in-memory similarity-search implementation. A dedicated vector database is one possible solution, not a mandatory requirement.
Q5. Name some vector databases.
Pinecone, Chroma, Qdrant, Weaviate, and Milvus are examples. FAISS is a popular vector similarity-search library, and PostgreSQL can support vector search using pgvector.


=====================================================================>

    :  http://127.0.0.1:8000/docs 
rag_venv => openapi => doc.py contains this code to execute the output ofnthe openapi,json when the url si this  :  
Suppose your main.py contains:
```
from fastapi import FastAPIapp = FastAPI()@app.get("/")def read_root():    return {"message": "Hello World"}
```
When you start the server:
```
uvicorn main:app --reload
```
FastAPI automatically does three things:
1. Reads your Python code
Finds routes such as @app.get("/") and @app.post("/ask").
2. Generates /openapi.json
Describes the API routes and their input/output schemas.
3. Swagger UI displays /docs
Shows buttons to test your API directly in the browser.
You generally do not need to write openapi.json yourself. FastAPI generates it from your application code and its type declarations.
Answer: OpenAPI is a standard specification used to describe REST APIs, including their endpoints, input parameters, request bodies, and responses.
Answer: It is the URL where FastAPI exposes the automatically generated OpenAPI specification in JSON format.
Answer: Swagger UI is a browser-based interface that reads the OpenAPI specification and allows developers to explore and test API endpoints.
Answer:
- /docs displays interactive API documentation.
- /openapi.json returns the underlying API specification as JSON.
Answer: No. FastAPI generates it automatically from route definitions and related schemas, unless you customize or disable this behavior.

=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>



=====================================================================>

 What is a WebSocket in FastAPI?
A WebSocket provides a persistent, bidirectional communication channel between a client and a server. 
In this code, FastAPI accepts a WebSocket connection, registers it with a connection manager, 
continuously listens for incoming text messages, and removes the connection when the client disconnects.
 Other backend code can use the connection manager to send real-time notifications to connected 
dashboard clients.  