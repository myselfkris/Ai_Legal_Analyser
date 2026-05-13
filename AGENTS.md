# Agent Instructions
> Last updated: 2026-05-13 by Antigravity

## Project Overview
- **Project**: AI Legal Document Analyzer
- **Stack**: Python 3, FastAPI, Google Gemini AI (`google-genai` SDK)
- **Repo**: https://github.com/myselfkris/Ai_Legal_Analyser.git
- **Status**: Backend complete, frontend not started yet

## File Map
| File | Purpose |
|------|---------|
| `backend/parser.py` | Extracts text from PDF (PyMuPDF) and DOCX (python-docx) |
| `backend/prompts.py` | Prompt templates, JSON schema, risk scoring guide for Gemini |
| `backend/analyzer.py` | Core AI engine — sends text to Gemini, parses & validates JSON response |
| `backend/main.py` | FastAPI entry point — `/analyze` (POST), `/health` (GET) |
| `backend/test_api.py` | Simple requests-based API test script |
| `backend/create_sample_contract.py` | Generates a sample NDA PDF for testing |
| `backend/.env` | Gemini API key (gitignored, NEVER commit) |
| `backend/requirements.txt` | fastapi, uvicorn, pymupdf, python-docx, google-genai, python-dotenv, pydantic |

## Architecture Flow
```
Upload (PDF/DOCX) → parser.py (extract text) → prompts.py (build prompt) → analyzer.py (Gemini API call) → Validate JSON → Return to client
```

## Key Decisions
- Model: `gemini-2.5-flash` (free tier, good at structured JSON)
- Temperature: 0.2 (low creativity, high consistency)
- All AI responses are validated with defaults so frontend always gets predictable schema
- Temp files cleaned up via FastAPI BackgroundTasks after response is sent
- UUID filenames prevent concurrent upload collisions

## Git Status
- 1 commit on `main`: `64ce0ba Initial commit`
- Untracked: `main.py`, `test_api.py`, `uploads/` (need to be committed)

## Changelog
- **2026-05-13**: Created AGENTS.md with full project context
