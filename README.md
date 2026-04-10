<div align="center">

# 🤖 AI Automation Agent

**A production-grade AI agent with semantic memory, tool validation, and local LLM support**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5%2B-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-red?style=flat-square)](https://github.com/facebookresearch/faiss)

<br/>

> Describe a task in plain English. The agent understands your intent, retrieves relevant memory, validates tool calls, and executes — all locally with no cloud dependencies.

</div>

---

## 📸 Overview

The AI Automation Agent is a self-contained, local-first AI system built with:

- A **FastAPI** backend running the full agent loop
- A **React + Vite** frontend with a dark-mode, 3-panel UI
- **FAISS** vector memory for semantic retrieval across interactions
- **Ollama** as the local LLM inference engine
- A strict **tool registry** that prevents hallucinated tool calls

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Semantic Memory** | Every interaction is embedded and stored in FAISS. Relevant past context is retrieved and injected into each new prompt. |
| 🛡️ **Hallucination Guard** | Any tool not in the registry raises a `HallucinationError`. The LLM can only call tools that exist. |
| 🔁 **Retry Logic** | Malformed LLM responses are corrected automatically — up to 3 attempts with progressive JSON fix prompts. |
| ⏱️ **Rate Limiting** | Sliding-window per-tool rate limits prevent runaway execution. |
| 📊 **Live Metrics** | Frontend polls `/metrics` every 5 seconds — intent counts, tool success/fail rates, total runs. |
| 🔒 **Low-Confidence Fallback** | If the agent scores < 0.5 confidence, it flags the output for human review instead of acting. |
| ⚡ **Local-First** | No OpenAI. No cloud. Runs entirely on your machine via Ollama. |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│              React + Vite Frontend (:5173)           │
│   ┌──────────┐  ┌────────────────┐  ┌─────────────┐  │
│   │ Metrics  │  │  Chat Panel    │  │   Memory    │  │
│   │ Sidebar  │  │  (center)      │  │   Panel     │  │
│   └──────────┘  └────────────────┘  └─────────────┘  │
└──────────────────────────┬───────────────────────────┘
                           │ REST API
┌──────────────────────────▼───────────────────────────┐
│              FastAPI Backend (:8000)                 │
│                                                      │
│   POST /run ──► agent/loop.py                        │
│                     │                                │
│          ┌──────────┼──────────┐                     │
│          ▼          ▼          ▼                     │
│      memory.py   llm.py    tools.py                  │
│      (FAISS)   (Ollama)  (Registry)                  │
│          │                    │                      │
│     rate_limiter.py      metrics.py                  │
└──────────────────────────────────────────────────────┘
                           │
             ┌─────────────▼──────────────┐
             │     Ollama (:11434)        │
             │  llama3 / mistral / qwen   │
             └────────────────────────────┘
```

---

## 📁 Project Structure

```
AIAutomation/
├── backend/
│   ├── agent/
│   │   ├── config.py          # System prompt v4.0 + constants
│   │   ├── memory.py          # FAISS vector DB + semantic ranking
│   │   ├── tools.py           # Tool registry + hallucination guard
│   │   ├── rate_limiter.py    # Sliding-window rate limiting
│   │   ├── llm.py             # Ollama client + retry wrapper
│   │   ├── metrics.py         # Intent + tool counters
│   │   └── loop.py            # Main agent orchestration loop
│   ├── main.py                # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    └── src/
        ├── api/
        │   └── agent.ts           # Typed API client
        ├── components/
        │   ├── ChatInterface.tsx   # Main chat panel
        │   ├── MessageBubble.tsx   # Message rendering
        │   ├── ConfidenceBadge.tsx # Color-coded confidence score
        │   ├── ToolResultCard.tsx  # Collapsible tool outputs
        │   ├── MemoryPanel.tsx     # Ranked memory viewer
        │   └── MetricsDashboard.tsx # Live metrics
        ├── App.tsx
        └── index.css              # Full dark-mode design system
```

---

## 🐳 Docker (Recommended)

The easiest way to run the entire stack — Ollama, backend, and frontend — in one command.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run Everything

```bash
# 1. Clone/navigate to the project
cd AIAutomation

# 2. (Optional) Change the model in .env
# OLLAMA_MODEL=mistral

# 3. Start all services
docker compose up --build
```

That's it. Docker will:
1. Start **Ollama** and pull `llama3` automatically
2. Build and start the **FastAPI backend**
3. Build the **React app** and serve it via **Nginx**

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost |
| ⚡ Backend API | http://localhost:8000 |
| 🤖 Ollama | http://localhost:11434 |

### Useful Docker Commands

```bash
# Run in background
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f ollama

# Stop everything
docker compose down

# Rebuild after code changes
docker compose up --build

# Change model without rebuilding
OLLAMA_MODEL=mistral docker compose up -d

# Remove all data (including downloaded models)
docker compose down -v
```

### Docker Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Network: bridge             │
│                                              │
│  ┌──────────┐   ┌──────────┐  ┌──────────┐  │
│  │ frontend │   │ backend  │  │  ollama  │  │
│  │  :80     │──▶│  :8000   │─▶│  :11434  │  │
│  │  nginx   │   │  fastapi │  │          │  │
│  └──────────┘   └──────────┘  └──────────┘  │
│                      │                       │
│              ┌───────┴───────┐               │
│              │    Volumes    │               │
│              │ ollama_data   │  (models)     │
│              │ hf_cache      │  (embeddings) │
│              └───────────────┘               │
└─────────────────────────────────────────────┘
```

> **GPU Support**: Uncomment the `deploy` section in `docker-compose.yml` to enable NVIDIA GPU passthrough to Ollama for faster inference.

---

## 🚀 Manual Setup (Without Docker)


### Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Ollama | Latest | [ollama.ai](https://ollama.ai/) |

### 1. Pull an Ollama Model

```bash
# Pull a model (one-time setup)
ollama pull llama3        # recommended
# or
ollama pull mistral
# or
ollama pull qwen:7b       # lighter, faster

# Start the Ollama server
ollama serve
```

### 2. Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure your model
copy .env.example .env
# Edit .env → set OLLAMA_MODEL=llama3

# Launch the API server
uvicorn main:app --reload --port 8000
```

✅ API ready at: http://localhost:8000  
📖 Swagger docs at: http://localhost:8000/docs

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ UI ready at: **http://localhost:5173**

---

## 🛠️ Available Tools

The agent ships with three stub executors. Swap in real implementations as needed.

| Tool | Required Params | Optional Params | Description |
|------|-----------------|-----------------|-------------|
| `send_email` | `to`, `message` | `cc`, `subject` | Send an email to a recipient |
| `query_database` | `query` | `limit` | Run a SELECT query (unsafe queries are blocked) |
| `create_lead` | `email` | `name`, `company` | Create a new CRM lead entry |

### Adding a New Tool

```python
# In backend/agent/tools.py

# 1. Register the schema
TOOL_REGISTRY["my_tool"] = {
    "description": "Does something useful.",
    "required": ["param1"],
    "optional": ["param2"],
}

# 2. Write the executor
def my_tool_executor(param1: str, param2: str = None) -> dict:
    # your logic here
    return {"status": "done"}

# 3. Register it
register_tool("my_tool", my_tool_executor)
```

---

## 🔌 API Reference

### `POST /run`

Run the agent loop with a natural language input.

**Request:**
```json
{
  "input": "Send an email to alice@example.com about the project kickoff"
}
```

**Response:**
```json
{
  "status": "ok",
  "output": {
    "intent": "send_communication",
    "confidence": 0.91,
    "actions": [
      {
        "tool": "send_email",
        "params": { "to": "alice@example.com", "message": "..." }
      }
    ],
    "reasoning": "User wants to send an email, using send_email tool."
  },
  "results": [
    { "tool": "send_email", "status": "success", "result": { "status": "sent" } }
  ],
  "memory_context": [...]
}
```

**Status values:**
- `ok` — executed successfully
- `review` — confidence too low, human review needed

### `GET /metrics`

```json
{
  "intents": { "send_communication": 4, "query_data": 2 },
  "tools": { "send_email": { "success": 4, "fail": 0 } },
  "total_runs": 6,
  "successful_runs": 5,
  "success_rate": 0.833
}
```

### `GET /memory`

Returns all stored memory entries (embeddings excluded).

### `GET /health`

```json
{
  "api": "ok",
  "ollama_running": true,
  "model": "llama3",
  "model_available": true,
  "memory_entries": 12
}
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3` | Ollama model name to use |

Set via `backend/.env`:

```env
OLLAMA_MODEL=mistral
```

Run `ollama list` to see all locally available models.

---

## 🧠 How Memory Works

Every time the agent runs:

1. The user's input is **embedded** using `all-MiniLM-L6-v2` (384-dim)
2. Top-10 similar past interactions are **retrieved** from FAISS by L2 distance
3. Retrieved memories are **re-ranked** by cosine similarity + timestamp
4. Top-3 memories are **formatted** into a context block (token-budget-aware)
5. The interaction is **stored** back to FAISS after execution

This gives the agent persistent, session-spanning context without a traditional database.

---

## 🛡️ Safety & Guardrails

- **Tool whitelist** — only tools in `TOOL_REGISTRY` can be called
- **`HallucinationError`** — raised if LLM invents a tool name
- **`MissingParameterError`** — raised if required params are absent
- **SQL injection guard** — `DROP`, `DELETE`, `TRUNCATE` etc. are blocked in `query_database`
- **Rate limiting** — per-tool sliding window (default: 100 emails/hour, 200 queries/minute)
- **Max 3 actions** — hard cap per LLM response

---

## 🔧 Extending the System

### Swap the LLM

The `backend/agent/llm.py` module wraps Ollama. To use a different provider (e.g. OpenAI):

```python
# Replace _call_ollama() with your provider's API call
def _call_ollama(prompt: str) -> str:
    # e.g. openai.chat.completions.create(...)
    ...
```

### Add Persistent Memory

Currently memory is in-process (resets on restart). To persist:

```python
# Save/load FAISS index
faiss.write_index(vector_db.index, "memory.index")
faiss.read_index("memory.index")
```

### Multi-Agent Support

Call `agent_loop()` from multiple specialized agent instances with different tool registries.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  Built with ❤️ using FastAPI · React · FAISS · Ollama
</div>
