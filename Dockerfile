FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AGENT_PROJECT_ID=agentic-ai-hackathon-466105
ENV AGENT_LOCATION=us-central1
ENV AGENT_ID=eb408a62-fc2f-4055-a009-e0e75042f855

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
