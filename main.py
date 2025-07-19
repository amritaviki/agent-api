from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.preview import agentbuilder
import os
import asyncio
import logging
import threading

app = FastAPI()
logger = logging.getLogger("uvicorn")

# Global state for agent
agent = None
initialization_complete = threading.Event()

def initialize_agent():
    global agent
    try:
        logger.info("⚙️ Starting Vertex AI agent initialization...")
        agent = agentbuilder.Agent(
            project=os.getenv("AGENT_PROJECT_ID"),
            location=os.getenv("AGENT_LOCATION"),
            agent_id=os.getenv("AGENT_ID")
        )
        logger.info("✅ Vertex AI agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {str(e)}")
    finally:
        initialization_complete.set()

# Start initialization in a separate thread
threading.Thread(target=initialize_agent, daemon=True).start()

class Query(BaseModel):
    message: str
    session_id: str

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 FastAPI application starting up")

@app.get("/startup-probe")
async def startup_probe():
    """Endpoint for Cloud Run startup check"""
    return {"status": "ready"}

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
    if initialization_complete.is_set() and agent is not None:
        return {"status": "ready"}
    return {"status": "initializing"}, 503

@app.post("/chat")
async def chat(q: Query):
    if agent is None:
        if initialization_complete.is_set():
            raise HTTPException(status_code=500, detail="Agent initialization failed")
        raise HTTPException(status_code=503, detail="Agent initializing")
    
    try:
        response = agent.send_message(q.message, q.session_id)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing error")

# For local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")