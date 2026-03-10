# 🎓 LearnAI Platform — Project Context & Instructions

## Project Overview
**LearnAI** is an AI-driven e-learning platform developed for the DIGITA 2026 Laboratory. It uses **Claude 3.5 (Sonnet & Haiku)** on **AWS Bedrock** to provide personalized training for employees. The platform is built with **Streamlit** (Frontend), **LangGraph/LangChain** (AI Orchestration), and **SQLite** (Data Storage).

### Core Technologies
- **UI:** Streamlit (v1.30+)
- **AI Orchestration:** LangGraph & LangChain
- **LLMs:** Amazon Bedrock (Claude 3.5 Sonnet/Haiku)
- **Database:** SQLite (Relational) & ChromaDB (Vector Store for RAG)
- **Storage:** Amazon S3 (for PDF/Document storage)
- **Data Handling:** Pandas, Plotly (Visualization), PyPDF2 (Text extraction)

---

## Architecture & Directory Structure
The project follows a **Three-Tier Architecture** focused on multi-agent orchestration.

```text
/
├── platform_sdk/         # Core SDK (LLM, DB, Agents) — DO NOT MODIFY
├── src/
│   ├── agents/           # LangGraph agents (Orchestrator, ContentGen, PracticeGen)
│   ├── core/             # Auth and Core configurations
│   ├── services/         # Business logic (e.g., Recommender)
│   └── tools/            # RAG Engine, PDF Parser, etc.
├── views/                # Streamlit UI pages (Student, Login, etc.)
├── database/             # SQL Schema (Nuovo_schema.sql) and Seed data
├── docs/                 # Detailed documentation (ARCHITECTURE.md, PRD.md)
├── app.py                # Main Entry Point (Routing)
├── config.py             # Global Configuration
└── .env                  # AWS Credentials & Environment variables
```

### Key Components
- **Orchestrator (`src/agents/orchestrator.py`):** The main supervisor agent ("Lea"). It handles natural language interaction and routes tasks to specialized tools/agents.
- **Content Engine (`src/agents/content_gen.py`):** Generates theoretical lessons based on uploaded materials using RAG.
- **Practice Engine (`src/agents/practice_gen.py`):** Creates Quizzes, Flashcards, and Mermaid Diagrams for active recall.
- **Database Helper (`platform_sdk/database.py`):** A simplified CRUD wrapper for SQLite. Use the global `db` instance.

---

## Building and Running

### Prerequisites
- Python 3.11+
- AWS Credentials (Access Key & Secret Key)

### Setup
1. **Initialize Environment:**
   - Windows: `setup.bat`
   - Mac/Linux: `chmod +x setup.sh && ./setup.sh`
2. **Configure Credentials:** Update the `.env` file with your AWS keys.
3. **Initialize Database:**
   ```bash
   python -c "from platform_sdk.database import db; db.init()"
   ```

### Running the App
```bash
streamlit run app.py
```

### Testing
Tests are located in the `tmp/` directory (e.g., `test_orchestrator.py`, `test_content_gen.py`). Run them using `pytest` or directly as python scripts.

---

## Development Conventions

### AI & Agent Development
- **SDK Usage:** Always prefer `platform_sdk` wrappers for AI and DB operations.
  - `llm.chiedi`, `llm.chiedi_con_contesto`, `llm.genera_json`.
  - `db.inserisci`, `db.trova_uno`, `db.aggiorna`.
- **LangGraph Memory:** Memory is managed via `st.session_state` to survive Streamlit reruns. Use `thread_id` for state persistence.
- **Context Awareness:** The orchestrator uses `tool_leggi_contesto` to understand the current page/course.
- **Thread Safety:** When calling agents from Streamlit, use module-level variables or specific state management for `user_id`, as LangGraph may run in background threads where `st.session_state` is inaccessible.

### Database Standards
- **Naming:** Follow the table names defined in `Nuovo_schema.sql`.
- **Role Validation:** Verify `users.ruolo` before performing `INSERT` operations on role-specific tables (e.g., `studenti_corsi`).
- **Idempotency:** Use flags like `is_processed` (for materials) and `embedding_sync` (for chunks) to avoid redundant AI processing.

### UI/UX (Streamlit)
- **Routing:** Handled in `app.py` based on `st.session_state["user_role"]`.
- **Language:** The user-facing AI (Lea) must speak Italian. Internal code and documentation should remain in English.
- **Data Privacy:** Never show internal IDs (e.g., `user_id`, `piano_id`) to the end-user.

---

## Instruction for AI Agents (Gemini CLI)
1. **Reference Docs:** Consult `docs/ARCHITECTURE.md` for system design and `GUIDA_SDK.md` for function signatures.
2. **Safety:** Never expose the contents of `.env` or AWS credentials.
3. **Vibe Coding:** Align with the established patterns in `src/agents/` when adding new capabilities.
