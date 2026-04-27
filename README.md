<div align="center">

<br/>

<img src="https://img.shields.io/badge/version-4.0.0-blue?style=for-the-badge" alt="version"/>
<img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="license"/>
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome"/>
<img src="https://img.shields.io/badge/maintained-yes-success?style=for-the-badge" alt="Maintained"/>

<br/><br/>

# 🤖 AI Automation Agent

### *Production-grade AI agent with semantic memory, hallucination prevention, and local LLM execution*

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-docker">Docker</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api-reference">API Docs</a> •
  <a href="#-contributing">Contributing</a>
</p>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-FF6F00?style=flat-square)](https://github.com/facebookresearch/faiss)

<br/>

> **Describe a task in plain English.**
> The agent understands your intent, retrieves relevant context from memory,
> validates tool calls against a strict registry, and executes — all locally.
> **No OpenAI. No cloud. No API bills.**

<br/>

</div>

---

## 📋 Table of Contents

- [Why AI Automation Agent?](#-why-ai-automation-agent)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
  - [Docker (Recommended)](#-docker-recommended)
  - [Manual Setup](#manual-setup)
- [Available Tools](#-available-tools)
- [API Reference](#-api-reference)
- [How Memory Works](#-how-memory-works)
- [Configuration](#-configuration)
- [Safety & Guardrails](#-safety--guardrails)
- [Extending the Agent](#-extending-the-agent)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 Why AI Automation Agent?

Most AI agent frameworks are either too simple (no memory, no validation) or too complex (vendor lock-in, expensive APIs). This project hits the sweet spot:

| Problem | Our Solution |
|---------|-------------|
| 🔴 LLMs hallucinate tool names | ✅ `HallucinationError` blocks any unregistered tool |
| 🔴 Agents forget past interactions | ✅ FAISS vector memory with semantic retrieval |
| 🔴 Cloud APIs are expensive | ✅ Runs entirely locally via Ollama |
| 🔴 Hard to debug agent behavior | ✅ Live metrics dashboard + reasoning display |
| 🔴 Rate limit abuse | ✅ Per-tool sliding-window rate limiting |
| 🔴 Low-quality LLM output | ✅ JSON retry loop with progressive correction |

---

## ✨ Features

<table>
<tr>
<td width="50%">

**🧠 Semantic Memory**
Every interaction is embedded (`all-MiniLM-L6-v2`) and stored in a FAISS index. Relevant past context is retrieved and ranked by cosine similarity before each prompt.

</td>
<td width="50%">

**🛡️ Hallucination Guard**
A strict tool registry prevents the LLM from calling tools that don't exist. Any unknown tool name raises a typed `HallucinationError` before execution.

</td>
</tr>
<tr>
<td width="50%">

**🔁 Retry + JSON Recovery**
Malformed LLM responses are automatically corrected — up to 3 attempts with appended correction prompts and multi-strategy JSON extraction.

</td>
<td width="50%">

**⏱️ Rate Limiting**
Per-tool sliding-window rate limits. Default: 100 emails/hour, 200 DB queries/minute. Fully configurable in `rate_limiter.py`.

</td>
</tr>
<tr>
<td width="50%">

**📊 Live Metrics Dashboard**
The React sidebar polls `/metrics` every 5 seconds showing intents detected, tool success/fail counts, total runs, and live success rate with a progress bar.

</td>
<td width="50%">

**🔒 Low-Confidence Fallback**
If the agent scores < 0.5 confidence, it halts execution and flags the output for human review instead of blindly acting.

</td>
</tr>
</table>

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | [Ollama](https://ollama.ai) | Local inference — llama3, mistral, qwen |
| **Embeddings** | `all-MiniLM-L6-v2` | 384-dim sentence embeddings |
| **Vector DB** | [FAISS](https://github.com/facebookresearch/faiss) | Fast approximate nearest-neighbor search |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com) | Async REST API |
| **Frontend** | [React](https://react.dev) + [Vite](https://vitejs.dev) | TypeScript UI |
| **Serving** | [Nginx](https://nginx.org) | Production static file server + proxy |
| **Containers** | [Docker](https://docker.com) + Compose | Full stack orchestration |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   React + Vite (Port 5173 / 80)              │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐   │
│  │ 📊 Metrics     │  │  💬 Chat Panel   │  │ 🧠 Memory  │   │
│  │   Sidebar      │  │   (center)       │  │   Panel     │   │
│  └────────────────┘  └──────────────────┘  └─────────────┘   │
└─────────────────────────────┬────────────────────────────────┘
                              │  REST  (JSON)
┌─────────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend (Port 8000)               │
│                                                              │
│   /run ──► agent_loop()                                      │
│                │                                             │
│     ┌──────────┼────────────┬────────────────┐               │
│     ▼          ▼            ▼                ▼               │
│  memory.py  llm.py      tools.py      rate_limiter.py        │
│  (FAISS +   (Ollama +   (Registry +   (Sliding window)       │
│  ranking)   retry)      validation)                          │
│     │            │                                           │
│  metrics.py   loop.py   ◄── orchestrates all of the above    │
└─────────────────────────────┬────────────────────────────────┘
                              │
              ┌───────────────▼───────────────┐
              │         Ollama (Port 11434)   │
              │   llama3 · mistral · qwen:7b  │
              └───────────────────────────────┘
```

**Request lifecycle:**

```
User Input
  → Embed input (384-dim vector)
  → Search FAISS (top-10 by L2)
  → Re-rank by cosine similarity + recency
  → Build prompt (system + memory context + input)
  → Call Ollama → parse JSON (retry up to 3×)
  → confidence < 0.5? → return "review" status
  → validate each action (hallucination check)
  → rate limit check per tool
  → execute tool → record metrics
  → store interaction in FAISS
  → return results to UI
```

---

## 📁 Project Structure

```
AIAutomation/
│
├── 🐳 docker-compose.yml          # Full stack: Ollama + backend + frontend
├── .env                           # OLLAMA_MODEL=llama3
│
├── backend/
│   ├── Dockerfile                 # Multi-stage Python build
│   ├── requirements.txt
│   ├── .env.example
│   ├── main.py                    # FastAPI app + endpoints
│   └── agent/
│       ├── config.py              # System prompt v4.0, constants
│       ├── memory.py              # FAISS + embeddings + ranking
│       ├── tools.py               # Registry, validation, executors
│       ├── rate_limiter.py        # Sliding-window limits
│       ├── llm.py                 # Ollama client + retry
│       ├── metrics.py             # Intent + tool counters
│       └── loop.py                # Main orchestration loop
│
└── frontend/
    ├── Dockerfile                 # React build → Nginx
    ├── nginx.conf                 # Static serve + /api proxy
    ├── vite.config.ts
    └── src/
        ├── api/agent.ts           # Typed fetch client
        ├── App.tsx                # 3-panel layout + health polling
        ├── index.css              # Dark mode design system
        └── components/
            ├── ChatInterface.tsx   # Messages, input, example prompts
            ├── MessageBubble.tsx   # User/agent bubbles + metadata
            ├── ConfidenceBadge.tsx # Color-coded score pill
            ├── ToolResultCard.tsx  # Collapsible JSON output
            ├── MemoryPanel.tsx     # Ranked context viewer
            └── MetricsDashboard.tsx # Live stats + progress bar
```

---

## 🚀 Quick Start

### 🐳 Docker (Recommended)

The fastest way — one command starts everything.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
# Clone the repo
git clone https://github.com/your-username/ai-automation-agent.git
cd ai-automation-agent

# (Optional) choose a different model
echo "OLLAMA_MODEL=mistral" > .env

# Start everything
docker compose up --build
```

Docker automatically:
- Pulls and starts **Ollama**
- Downloads your chosen **LLM model**
- Builds and starts the **FastAPI backend**
- Builds React and serves it via **Nginx**

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost |
| ⚡ Backend + Swagger | http://localhost:8000/docs |
| 🤖 Ollama API | http://localhost:11434 |

<details>
<summary><b>More Docker commands</b></summary>

```bash
# Run in the background
docker compose up -d

# Tail logs for a specific service
docker compose logs -f backend
docker compose logs -f ollama

# Stop everything (keeps volumes)
docker compose down

# Stop and wipe all data including downloaded models
docker compose down -v

# Rebuild after code changes
docker compose up --build

# Switch model without rebuilding
OLLAMA_MODEL=qwen:7b docker compose up -d
```

</details>

<details>
<summary><b>GPU Acceleration (NVIDIA)</b></summary>

Uncomment the `deploy` block in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Requires [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

</details>

---

### Manual Setup

<details>
<summary><b>Step 1 — Install & start Ollama</b></summary>

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows — download from https://ollama.ai

# Pull a model (choose one)
ollama pull llama3      # best quality
ollama pull mistral     # good balance
ollama pull qwen:7b     # fastest / lightest

# Start the server
ollama serve
```

</details>

<details>
<summary><b>Step 2 — Start the backend</b></summary>

```bash
cd backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

# Configure (optional)
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
# edit OLLAMA_MODEL=llama3

uvicorn main:app --reload --port 8000
```

✅ Backend → http://localhost:8000  
📖 Swagger → http://localhost:8000/docs

</details>

<details>
<summary><b>Step 3 — Start the frontend</b></summary>

```bash
cd frontend
npm install
npm run dev
```

✅ UI → http://localhost:5173

</details>

---

## 🛠️ Available Tools

Tools are stub implementations — replace with your real integrations.

| Tool | Required | Optional | Description |
|------|----------|----------|-------------|
| `send_email` | `to`, `message` | `cc`, `subject` | Send email to a recipient |
| `query_database` | `query` | `limit` | Run a SELECT query (DML blocked) |
| `create_lead` | `email` | `name`, `company` | Create CRM lead entry |

### ➕ Adding a Custom Tool

```python
# backend/agent/tools.py

# 1 — Define the schema
TOOL_REGISTRY["slack_message"] = {
    "description": "Send a message to a Slack channel.",
    "required": ["channel", "text"],
    "optional": ["thread_ts"],
}

# 2 — Write the executor
def slack_message_executor(channel: str, text: str, thread_ts: str = None) -> dict:
    # call Slack API here
    return {"status": "sent", "channel": channel}

# 3 — Register
register_tool("slack_message", slack_message_executor)
```

The agent can now call `slack_message` in responses. No other changes needed.

---

## 🔌 API Reference

> Full interactive docs available at **http://localhost:8000/docs** (Swagger UI)

### `POST /run` — Execute agent

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Send a kickoff email to alice@example.com"}'
```

<details>
<summary><b>Response schema</b></summary>

```json
{
  "status": "ok",
  "output": {
    "intent": "send_communication",
    "confidence": 0.91,
    "actions": [
      {
        "tool": "send_email",
        "params": {
          "to": "alice@example.com",
          "message": "Hi Alice, the project is kicking off!"
        }
      }
    ],
    "reasoning": "User wants to send an email. Using send_email tool."
  },
  "results": [
    {
      "tool": "send_email",
      "status": "success",
      "result": { "status": "sent", "to": "alice@example.com" }
    }
  ],
  "memory_context": [
    {
      "timestamp": "2026-04-10T17:30:00",
      "user_input": "Email the team about the standup",
      "intent": "send_communication"
    }
  ]
}
```

| Status | Meaning |
|--------|---------|
| `ok` | All actions executed |
| `review` | Confidence < 0.5 — human review needed |

</details>

### `GET /metrics` — Usage statistics

```json
{
  "intents": { "send_communication": 4, "query_data": 2 },
  "tools": { "send_email": { "success": 4, "fail": 0 } },
  "total_runs": 6,
  "successful_runs": 5,
  "success_rate": 0.833
}
```

### `GET /memory` — Stored interactions

Returns all past interactions (embeddings excluded for serialization).

### `GET /health` — System status

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

## 🧠 How Memory Works

```
New Input
    │
    ▼
[Embed] → 384-dim vector (all-MiniLM-L6-v2)
    │
    ▼
[FAISS Search] → top-10 by L2 distance
    │
    ▼
[Re-rank] → cosine similarity × recency tiebreak → top-3
    │
    ▼
[Format] → token-budget-aware text block (max 500 tokens)
    │
    ▼
[Inject] → added to LLM prompt as "MEMORY CONTEXT"
    │
    ▼
[Store] → current interaction upserted to FAISS after execution
```

Memory is **in-process** by default (session-scoped). To persist across restarts:

```python
import faiss
# Save
faiss.write_index(vector_db.index, "memory.index")
import json; open("memory_meta.json","w").write(json.dumps(vector_db.metadata))
# Load
vector_db.index = faiss.read_index("memory.index")
vector_db.metadata = json.load(open("memory_meta.json"))
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3` | Model to use (`ollama list` to see options) |

Configure via `backend/.env`:

```env
OLLAMA_MODEL=mistral
```

**Supported models** (any model pulled via Ollama):

```bash
ollama pull llama3       # Meta — best reasoning
ollama pull mistral      # Mistral AI — fast + smart
ollama pull qwen:7b      # Alibaba — lightweight
ollama pull phi3         # Microsoft — very small
```

---

## 🛡️ Safety & Guardrails

| Guard | Mechanism |
|-------|-----------|
| **Tool whitelist** | Only `TOOL_REGISTRY` entries are callable |
| **`HallucinationError`** | Unknown tool name → blocked before execution |
| **`MissingParameterError`** | Required param absent → blocked with clear error |
| **SQL safety** | `DROP`, `DELETE`, `TRUNCATE`, `INSERT`, `UPDATE` → rejected |
| **Rate limiting** | Sliding-window per tool — configurable thresholds |
| **Max actions** | Hard cap of 3 actions per LLM response |
| **Confidence threshold** | < 0.5 → halts and requests human review |

---

## 🔧 Extending the Agent

<details>
<summary><b>Swap the LLM backend</b></summary>

Replace `_call_ollama()` in `backend/agent/llm.py`:

```python
# OpenAI example
import openai

def _call_ollama(prompt: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
```

</details>

<details>
<summary><b>Add persistent FAISS memory</b></summary>

```python
# On shutdown — save
faiss.write_index(vector_db.index, "memory.faiss")
with open("memory_meta.json", "w") as f:
    json.dump(vector_db.metadata, f, default=str)

# On startup — load
if os.path.exists("memory.faiss"):
    vector_db.index = faiss.read_index("memory.faiss")
    with open("memory_meta.json") as f:
        vector_db.metadata = json.load(f)
```

</details>

<details>
<summary><b>Build a multi-agent system</b></summary>

```python
from agent.loop import agent_loop
from agent.tools import TOOL_REGISTRY, register_tool

# Specialist agents with scoped tool sets
EMAIL_TOOLS = {"send_email"}
DB_TOOLS    = {"query_database"}

def email_agent(user_input: str):
    # restrict registry to email tools
    ...

def db_agent(user_input: str):
    # restrict registry to DB tools
    ...
```

</details>

---

## 🗺️ Roadmap

- [x] FAISS vector memory
- [x] Tool hallucination prevention
- [x] Ollama LLM integration with retry
- [x] Rate limiting
- [x] React + Vite frontend
- [x] Docker support
- [ ] Persistent FAISS memory (disk-backed)
- [ ] Streaming LLM responses (SSE)
- [ ] Plugin system for dynamic tool loading
- [ ] WebSocket live updates
- [ ] Multi-agent orchestration
- [ ] Auth + multi-user support
- [ ] OpenAI / Anthropic adapter

---

## 🤝 Contributing

Contributions are what make open source amazing. Any contribution you make is **greatly appreciated**.

1. **Fork** the repository
2. **Create** your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "feat: add amazing feature"
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) and follow [Conventional Commits](https://www.conventionalcommits.org/).

### 🐛 Reporting Bugs

Found a bug? [Open an issue](https://github.com/your-username/ai-automation-agent/issues/new?template=bug_report.md) with:
- Steps to reproduce
- Expected vs actual behaviour
- Your OS, Python version, Ollama model

### 💡 Feature Requests

Have an idea? [Start a discussion](https://github.com/your-username/ai-automation-agent/discussions) or open a feature request issue.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai) — making local LLMs a reality
- [FAISS](https://github.com/facebookresearch/faiss) — Meta's blazing-fast vector search
- [Sentence Transformers](https://www.sbert.net) — `all-MiniLM-L6-v2` embeddings
- [FastAPI](https://fastapi.tiangolo.com) — the best Python API framework
- [Vite](https://vitejs.dev) — lightning-fast frontend tooling

---

<div align="center">

**If this project helped you, please consider giving it a ⭐ on GitHub!**

<br/>

Made with ❤️ · [Report Bug](https://github.com/your-username/ai-automation-agent/issues) · [Request Feature](https://github.com/your-username/ai-automation-agent/issues)

<br/>

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

</div>
