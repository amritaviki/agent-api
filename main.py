from fastapi import FastAPI
from pydantic import BaseModel
from vertexai.preview import agentbuilder
import os
import uvicorn

app = FastAPI()

agent = agentbuilder.Agent(
    project=os.getenv("AGENT_PROJECT_ID"),
    location=os.getenv("AGENT_LOCATION"),
    agent_id=os.getenv("AGENT_ID")
)

class Query(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(q: Query):
    response = agent.send_message(q.message, q.session_id)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
