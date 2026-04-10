# AI Automation Agent v4.0

A production-grade AI automation agent with:
- 🧠 **FAISS vector memory** with semantic ranking
- 🛡️ **Tool hallucination prevention** + parameter validation
- 🔁 **LLM retry logic** with JSON recovery
- ⏱️ **Rate limiting** per tool
- 🤖 **Ollama** (local LLM) integration
- ⚛️ **React + Vite** frontend with dark-mode UI
- ⚡ **FastAPI** REST backend

---

## Quick Start

### 1. Prerequisites

- [Ollama](https://ollama.ai) installed and running
- Python 3.10+
- Node.js 18+

```bash
# Pull a model (one-time)
ollama pull llama3

# Start Ollama
ollama serve
```

### 2. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure (optional)
copy .env.example .env
# Edit .env to set OLLAMA_MODEL=llama3 (or mistral, qwen:7b, etc.)

# Start the API server
uvicorn main:app --reload --port 8000
```

Backend will be at: http://localhost:8000

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be at: http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/run` | Run agent with user input |
| `GET` | `/metrics` | Intent + tool usage stats |
| `GET` | `/memory` | All stored memory entries |
| `GET` | `/health` | Ollama + API health check |

### Example

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Send an email to john@company.com about the meeting tomorrow"}'
```

---

## Changing the LLM Model

Set `OLLAMA_MODEL` in `backend/.env`:

```
OLLAMA_MODEL=mistral
```

Or use any model you've pulled with `ollama pull <model>`.

---

## Architecture

```
frontend (React+Vite :5173)
    ↕ REST
backend (FastAPI :8000)
    ├── agent/loop.py       ← Orchestration
    ├── agent/memory.py     ← FAISS + embeddings
    ├── agent/llm.py        ← Ollama + retry
    ├── agent/tools.py      ← Registry + validation
    ├── agent/rate_limiter.py
    └── agent/metrics.py
```

## Features

- **Semantic memory**: Past interactions are embedded and retrieved by cosine similarity
- **Hallucination guard**: Any tool not in the registry raises `HallucinationError`
- **Rate limiting**: Sliding-window per-tool limits prevent abuse
- **Low-confidence fallback**: If confidence < 0.5, agent requests human review
- **Live metrics**: Frontend polls `/metrics` every 5 seconds
