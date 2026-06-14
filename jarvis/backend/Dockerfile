# JARVIS Graph API — read-only FastAPI over the dev_graph in Neo4j.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

EXPOSE 8000
# NEO4J_* are injected by docker-compose (or the environment) at runtime.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
