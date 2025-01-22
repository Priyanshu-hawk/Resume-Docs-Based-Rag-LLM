from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import shutil
from datetime import datetime
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from main import get_llm_settings
from dotenv import load_dotenv
load_dotenv()

ngrok_key = os.getenv("NGROK_AUTHTOKEN")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_llm_settings(contect_window=4096, max_new_token=1024)

# Create a directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatMessage(BaseModel):
    human: str
    assistant: str

class ChatRequest(BaseModel):
    chat_history: List[ChatMessage] = []
    message: str

def save_uploaded_file(uploaded_file: UploadFile) -> str:
    # Generate a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return file_path

index = VectorStoreIndex.from_documents(documents="", service_context=settings)
query_engine = index.as_query_engine()
def chat_with_llama(chat_history: List[ChatMessage], message: str, file_path: Optional[str] = None):
    # print('thinking...')
    # Prepare context from chat history
    context = "\n".join([f"<|USER|>{item.human}\n<|ASSISTANT|>{item.assistant}" for item in chat_history[-10:]])
    full_query = f"{context}\n<|USER|>{message}<|ASSISTANT|>"

    # If a file was uploaded, you might want to process it here
    if file_path:
      documents = SimpleDirectoryReader(UPLOAD_DIR).load_data()
      index = VectorStoreIndex.from_documents(documents=documents, service_context=settings)
      global query_engine
      query_engine = index.as_query_engine()

    # Query the engine
    response = query_engine.query(full_query)  # Make sure query_engine is defined
    # print('your response: ', response)
    return response

@app.get("/")
def home():
    return "Welcome to the Chat API!"

@app.post("/chat")
async def chat(request: Request, data: str = Form(...), file: Optional[UploadFile] = File(None)):
    try:
        # print("Received data:", data)
        # print("Received file:", file)

        chat_request = json.loads(data)
        message = chat_request.get('message', '')
        chat_history = [ChatMessage(**msg) for msg in chat_request.get('chat_history', [])]

        # print('Parsed data:', chat_request)
        # print('chat_history:', chat_history)
        # print('message:', message)

        if not message:
            raise HTTPException(status_code=400, detail="No message provided")

        file_path = None
        if file and len(chat_history) == 0:  # Only save the file if it's the first message
            file_path = save_uploaded_file(file)
            print(f"File saved at: {file_path}")

        # Process the message with your LLM or chatbot logic here
        response = chat_with_llama(chat_history, message, file_path)
        # print('Response:', response)
        return {"response": str(response)}
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.post("/new_chat")
async def new_chat():
    try:
        chat_history = []
        # delete all files in the upload directory
        for file in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return {"response": "Chat history cleared."}
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

if __name__ == "__main__":
    import asyncio, uvicorn
    from pyngrok import ngrok

    async def start_uvicorn():
        # Create a public URL using ngrok
        public_url = ngrok.connect(7000)
        print("Public URL for server (Copy this):", public_url)
        config = uvicorn.Config(app, host="0.0.0.0", port=7000)
        server = uvicorn.Server(config)
        await server.serve()

        await asyncio.create_task(start_uvicorn())
        
    asyncio.run(start_uvicorn())