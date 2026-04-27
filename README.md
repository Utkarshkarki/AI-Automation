<div align="center">

<br/>

<img src="https://img.shields.io/badge/version-7.0.0-blue?style=for-the-badge" alt="version"/>
<img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="license"/>
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome"/>
<img src="https://img.shields.io/badge/maintained-yes-success?style=for-the-badge" alt="Maintained"/>

<br/><br/>

# 📧 SaaS Outreach Engine (Powered by Ollama)

### *Production-grade AI Email CRM with Multi-Day Sequences, IMAP Reply Detection, and Deliverability Protection.*

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-usage-guide">Usage Guide</a>
</p>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.ai/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-FF6F00?style=flat-square)](https://github.com/facebookresearch/faiss)

<br/>

> **Your Personal AI Sales Team.**
> Upload a CSV of leads, and ask the AI to manage your campaigns in plain English. The agent drafts hyper-personalized emails, schedules multi-day follow-up sequences, strictly protects your sender reputation, and auto-stops when a lead replies.

<br/>

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Available AI Tools](#-available-ai-tools)
- [License](#-license)

---

## ✨ Features

### 1. 🤖 Agentic CRM Management
No clicking through endless menus. Just tell the AI: *"Add Alice from TechCorp (alice@techcorp.com). Industry: SaaS. Pain point: churn is too high."* The agent uses its internal tools to update the relational database and pull this context later for hyper-personalization.

### 2. 📅 Multi-Day Sequences & Drip Campaigns
Create email templates with variables like `{{name}}` and `{{company}}`. Then ask the agent: *"Start the 'Q3 Outreach' campaign for all leads using Template #1, with follow-ups on Day 3 and Day 7."* The internal APScheduler will stagger the sends automatically.

### 3. 🛡️ Deliverability Protection
Sending too many emails too fast will get your Gmail account banned. This engine protects you:
- **Daily Send Limits**: Hard stops sending when your daily limit (e.g., 50 emails) is reached.
- **Random Send Delays**: Pauses randomly between 15-45 seconds between sends to mimic human behavior.
- **Duplicate Prevention**: Automatically skips leads who are already queued in a campaign.

### 4. 🧠 IMAP Reply Detection (Auto-Stop)
The background IMAP worker connects to your inbox every 5 minutes to read unread emails. If it detects a reply from a lead in your CRM, it feeds the email body to the local LLM to classify the intent (`interested`, `not_now`, `unsubscribe`, `ooo`). It then **automatically cancels** all future scheduled follow-ups for that lead.

### 5. 🎨 Premium SaaS Dashboard
A beautiful, responsive React frontend styled with Tailwind CSS "Glassmorphism." Features a persistent sidebar, a live metrics dashboard, a leads table with CSV upload, a campaign tracker, and the AI chat interface.

---

## 🛠️ Tech Stack

**Frontend:**
- React 19 + TypeScript
- Vite
- Tailwind CSS v3
- React Router DOM
- Lucide React (Icons)

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy (SQLite)
- APScheduler (Background Workers)
- Python `imaplib` & `smtplib`

**AI & Memory:**
- Ollama (Local LLM Execution)
- FAISS (Vector database for Semantic Memory)
- Sentence-Transformers (`all-MiniLM-L6-v2`)

---

## 🏗️ Architecture

The backend is built as a **Modular Monolith**. It consists of several domain services orchestrated by the `AgentLoop`.

1. **EmailService**: Handles SMTP sending, SQLite CRM CRUD operations, Template management, and Campaign scheduling.
2. **LLMService**: Interfaces directly with Ollama. Wraps raw LLM calls in an auto-correction retry loop to guarantee valid JSON tool responses.
3. **MemoryService**: Embeds the user's chat history and intents into FAISS for semantic retrieval on future prompts.
4. **MetricsService**: Tracks agent performance, tool usage success/fail rates, and intents detected.
5. **Background Workers (`APScheduler`)**:
    - `drip_campaign_job`: Runs every 1 min. Checks for queued emails scheduled for `now()` or earlier.
    - `imap_reply_check_job`: Runs every 5 mins. Connects to Gmail, reads unread emails, classifies replies via LLM, and auto-stops campaigns.

---

## 📁 Project Structure

```text
AIAutomation/
├── backend/
│   ├── agent/
│   │   ├── loop.py            # Orchestrator (Prompting & Tool execution)
│   │   └── tools.py           # Tool definitions & registry
│   ├── core/
│   │   ├── config.py          # SYSTEM_PROMPT, env vars, constants
│   │   └── exceptions.py      # Custom errors (HallucinationError)
│   ├── services/
│   │   ├── email/             # SMTP, IMAP, SQLite CRUD, Campaigns worker
│   │   ├── llm/               # Ollama interface & JSON correction
│   │   ├── memory/            # FAISS vector database
│   │   └── metrics/           # Performance tracking
│   ├── main.py                # FastAPI Composition Root
│   └── migrate.py             # DB Schema migrator
├── frontend/
│   ├── src/
│   │   ├── api/               # agent.ts (Fetch wrappers)
│   │   ├── components/        # ChatInterface.tsx, MetricsDashboard.tsx
│   │   ├── layouts/           # Sidebar.tsx, DashboardLayout.tsx
│   │   └── pages/             # Dashboard.tsx, Leads.tsx, Campaigns.tsx
│   ├── tailwind.config.js     # SaaS dark mode theme definition
│   └── package.json
└── .env                       # Secrets (SMTP/IMAP)
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **Ollama**: Download from [ollama.ai](https://ollama.ai/) and run `ollama serve`. Then pull your preferred model (e.g., `ollama pull llama3`).
4. **Gmail App Password**: You need a Gmail account with 2-Factor Authentication enabled. Generate an "App Password" in your Google Account Security settings.

### Configuration

Create a `.env` file in the `backend/` directory:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Gmail Configuration (SMTP & IMAP)
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the database migrations (if needed):
   ```bash
   python migrate.py
   ```
4. Start the FastAPI server (runs on port 8000):
   ```bash
   uvicorn main:app --reload --port 8000 --env-file .env
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server (runs on port 5173/5174):
   ```bash
   npm run dev
   ```

Open your browser to `http://localhost:5173` (or the port Vite provides) to view the SaaS dashboard!

---

## 📘 Usage Guide

1. **Upload Leads**: Navigate to the `Leads` tab. Click "Upload CSV". Your CSV must have headers (e.g., `email`, `name`, `company`, `industry`, `pain_points`).
2. **Create a Template**: Go to the Dashboard and ask the AI: *"Create a template called 'Cold Pitch' with the subject 'Hi {{name}}' and a body about how we can help {{company}}."*
3. **Start a Campaign**: Go to the Dashboard and ask the AI: *"Schedule the 'Q3 SaaS' campaign for all my contacts using Template 1. Follow up on Day 3 and Day 7."*
4. **Track Replies**: Let the background IMAP worker do its job. Ask the AI: *"Track my replies"* or *"Get my analytics"* to see your deliverability and response metrics.

---

## 🧰 Available AI Tools

The agent is securely sandboxed and can ONLY use the following internally registered tools:

- `generate_email`: Drafts hyper-personalized emails by reading lead context from SQLite.
- `send_email`: Instantly sends a one-off email.
- `add_contact`: Saves a lead and their rich context to the CRM.
- `list_contacts`: Retrieves CRM data.
- `create_template`: Saves a template with `{{variables}}`.
- `create_campaign`: Initializes a new outreach tracking entity.
- `schedule_campaign`: Queues up sequences (Day 0, 3, 7) for background sending.
- `pause_campaign`: Halts all outbound emails for a specific campaign.
- `track_replies`: Queries the database for replies parsed by the IMAP worker.
- `get_analytics`: Returns high-level sent/queued/failed metrics.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
