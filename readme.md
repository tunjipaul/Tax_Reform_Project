# Nigerian Tax Reform Bills 2024 — Q&A Assistant (Agentic RAG)

**Project:** Tax Reform Bills 2024 Q&A Assistant

**Overview**

This repository contains a student capstone project that builds an Agentic Retrieval-Augmented Generation (RAG) assistant to help Nigerians understand the 2024 tax reform bills. The assistant answers questions using official documents (bills, explanatory memoranda, press releases) and cites sources for every answer.

🔥 **Chosen problem:** Nigerian Tax Reform Bills 2024 Q&A Assistant

---

## 🚀 Features

- Agentic RAG engine (LangGraph / LangChain patterns) that conditionally retrieves documents
- Semantic search using a vector DB (Chroma or equivalent)
- Source citation for every response
- Conversation memory and follow-up handling
- FastAPI backend serving chat/session endpoints
- React frontend chat UI (clean, mobile-friendly)

---

## 📚 Data Sources

- The four Tax Reform Bills (PDFs from the National Assembly)
- Explanatory memoranda and Presidential clarifications
- FIRS clarifications and public statements
- State government positions and submissions

(Place raw PDFs / canonical sources in `data/` or `data/tax_bills/` and add checksums or source notes.)

---

## 🛠️ Quickstart (local development)

> Notes: Adapt commands to your local environment (Windows PowerShell shown). If `requirements.txt` or `package.json` are missing, install packages listed below manually or add them to the repo.

1. Create a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Typical Python dependencies:
`fastapi`, `uvicorn[standard]`, `langchain`, `langgraph`, `chromadb`, `sentence-transformers`, `openai` (or the embedding provider you use), `pydantic`.

2. Backend

```powershell
cd backend  # or wherever FastAPI app lives
uvicorn app.main:app --reload --port 8000
```

3. Frontend

```powershell
cd frontend
npm install
npm run dev  # or npm start
```

4. AI Engine setup

- Put source PDFs into `data/tax_bills/`
- Run your ingestion script to chunk, embed, and build the vector store (e.g., `python -m scripts.ingest_tax_bills`)
- Start the agent (the backend will expose endpoints that connect the agent to the frontend)

---

## 🔧 Project Structure (suggested)

- `backend/` — FastAPI app and endpoints
- `frontend/` — React + Tailwind UI
- `ai/` or `src/ai_engine/` — RAG ingestion, vector DB, agent logic
- `data/tax_bills/` — source documents (PDFs)
- `notebooks/` — analysis & demos (includes `PROJECT.ipynb`)
- `requirements.txt` / `package.json`
- `README.md` (this file)

---

## 💡 Usage

- Run ingestion to populate vector DB with the tax bills and references.
- Start backend and frontend.
- Open the chat UI and ask user-facing questions like:
  - "Will my income tax increase under the new bill?"
  - "How will VAT derivation affect my state?"
  - Ask comparative questions and request citations.

---

## ✅ Deliverables

- Working Agentic RAG system with conditional retrieval and citations
- FastAPI backend with conversational endpoints
- React frontend with chat UI
- README with setup and usage (this file)
- Demo video (5–10 minutes)
- Presentation slides

---

## 🧪 Tests & Evaluation

- Manually validate that the agent cites the correct section of the source documents
- Unit tests for ingestion and retrieval components
- Integration test for end-to-end QA flow

---

## 👥 Team & Roles

- Suggested roles: 2 AI engineers (ingestion, model/agent), 2 devs (backend + frontend)
- Add team member names and GitHub handles in `CONTRIBUTORS.md` or below.

---

## 📎 Notes / TODOs

- Add `requirements.txt` and `package.json` if missing
- Add an ingestion script with clear flags for rebuild / incremental update
- Create demo script or Postman collection for the API

---

## 📜 License

Add a license of your choice (e.g., MIT).

---

## 📍 Notebook & Project Info

This repository includes `documents/PROJECT.ipynb` which describes the capstone challenge and the Tax Reform problem statement used for the project; it is the source of the project scope and grading rubric.

---

## Contact

Questions or issues — open an issue or contact the project lead: **(add name / email / slack handle)**

---

Good luck — let's build a trustworthy, source-backed assistant that helps millions understand the Tax Reform Bills! 🇳🇬
