FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use Cloud Run's PORT variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 300