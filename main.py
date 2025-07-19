from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.preview import agentbuilder
import os
import asyncio
import threading
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn")

# Global agent instance
agent = None
init_lock = threading.Lock()
is_initialized = False

def initialize_agent():
    global agent, is_initialized
    try:
        logger.info("Initializing Vertex AI agent...")
        agent = agentbuilder.Agent(
            project=os.getenv("AGENT_PROJECT_ID"),
            location=os.getenv("AGENT_LOCATION"),
            agent_id=os.getenv("AGENT_ID")
        )
        logger.info("Agent initialized successfully")
        is_initialized = True
    except Exception as e:
        logger.error(f"Agent initialization failed: {str(e)}")
        raise RuntimeError("Agent initialization failed") from e

@app.on_event("startup")
async def startup_event():
    # Run initialization in separate thread to avoid blocking
    init_thread = threading.Thread(target=initialize_agent)
    init_thread.daemon = True
    init_thread.start()

class Query(BaseModel):
    message: str
    session_id: str

@app.get("/health")
async def health_check():
    if is_initialized:
        return {"status": "ready"}
    return {"status": "initializing"}, 503

@app.post("/chat")
async def chat(q: Query):
    if not is_initialized:
        raise HTTPException(status_code=503, detail="Agent initializing")
    
    try:
        response = agent.send_message(q.message, q.session_id)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing error") from e