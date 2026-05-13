"""
main.py — FastAPI Backend Entry Point for AI Legal Analyser

Receives document uploads, processes them through parser + Gemini AI,
and returns structured legal analysis results.
"""

import os
import shutil
import sys
import uuid
from datetime import datetime, timezone

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from parser import extract_text
from analyzer import analyze_document


# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Legal Analyser API",
    description="Backend for analyzing legal documents using Google Gemini AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def cleanup_file(file_path: str) -> None:
    """Delete a temporary file from disk after processing."""
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[CLEANUP] Deleted temporary file: {file_path}")


def validate_file_extension(filename: str) -> bool:
    """Return True if the file extension is PDF or DOCX."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in [".pdf", ".docx", ".doc"]


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Welcome endpoint — confirms the API is online and lists available routes."""
    return {
        "message": "Welcome to the AI Legal Analyser API ⚖️",
        "status": "online",
        "version": "1.0.0",
        "available_endpoints": {
            "/analyze": "POST - Upload a document for AI analysis",
            "/health": "GET - Check if API is working",
            "/docs": "GET - View interactive API documentation (Swagger UI)",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint — used by monitoring tools and load balancers."""
    return {"status": "healthy", "message": "API is running smoothly"}


@app.post("/analyze")
async def analyze_legal_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Core analysis endpoint.

    Workflow: validate → save → extract text → AI analysis → return results → cleanup.
    """

    # 1. Validate file type
    filename = file.filename
    if not validate_file_extension(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Please upload PDF or DOCX. Got: {os.path.splitext(filename)[1]}",
        )

    # 2. Save file temporarily (UUID avoids collisions from concurrent uploads)
    file_extension = os.path.splitext(filename)[1].lower()
    temp_filename = f"{uuid.uuid4()}{file_extension}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)

    try:
        print(f"[API] Saving uploaded file: {filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Schedule file cleanup after response is sent
    background_tasks.add_task(cleanup_file, temp_path)

    # 3. Extract text from document
    try:
        print(f"[API] Extracting text from {filename}...")
        parsed_data = extract_text(temp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract text: {str(e)}")

    # 4. Analyze with Gemini AI
    try:
        print(f"[API] Analyzing document with Gemini AI...")
        analysis_result = analyze_document(parsed_data["text"])

        analysis_result["file_metadata"] = {
            "original_filename": filename,
            "file_type": parsed_data.get("file_type", "UNKNOWN"),
            "word_count": parsed_data.get("word_count", 0),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        print(f"[API] ✅ Analysis complete for {filename}")
        return analysis_result

    except ValueError as ve:
        raise HTTPException(status_code=401, detail=f"API Authentication Error: {str(ve)}")
    except Exception as e:
        print(f"[ERROR] Analysis failed for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="AI analysis failed. Please try again later.")


# ── Run Server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("🚀 Starting AI Legal Analyser Backend...")
    print("📍 API: http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
