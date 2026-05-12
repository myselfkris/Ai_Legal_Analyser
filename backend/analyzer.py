"""
analyzer.py — Core AI Analysis Engine
Takes extracted document text, sends it to Google Gemini with legal prompts,
and returns structured JSON analysis with risk scores and clause breakdowns.

This is the BRAIN of the app:
    parser.py (text) + prompts.py (instructions) --> analyzer.py --> Gemini --> JSON result

UPDATED: Now uses the new `google.genai` SDK (replaces deprecated `google.generativeai`)
"""

import json
import os
from google import genai                         # NEW SDK
from google.genai import types                    # For config objects
from dotenv import load_dotenv
from prompts import build_analysis_prompt, SYSTEM_INSTRUCTION


# ── Load API key from .env file ───────────────────────────────────────────────
load_dotenv()

def _get_api_key() -> str:
    """Get Gemini API key from environment. Fails clearly if missing."""
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "paste_your_key_here":
        raise ValueError(
            "GEMINI_API_KEY not set!\n"
            "1. Open backend/.env\n"
            "2. Replace 'paste_your_key_here' with your real key\n"
            "3. Get a free key at: https://aistudio.google.com/apikey"
        )
    return key


# ── Configure Gemini Client ───────────────────────────────────────────────────
# The model we use for analysis
MODEL_NAME = "gemini-2.5-flash"

def _create_client():
    """
    Creates and returns a configured Gemini client.

    Why google.genai instead of google.generativeai?
    - google.generativeai is DEPRECATED (no more updates or bug fixes)
    - google.genai is the new official SDK with better features
    - Same API key works with both

    Why Gemini 2.5 Flash?
    - Free tier available (no credit card needed)
    - Faster and smarter than 2.0 Flash
    - Better at structured JSON output
    - Separate quota from 2.0 models (so if 2.0 is exhausted, 2.5 may still work)
    """
    client = genai.Client(api_key=_get_api_key())
    return client


# ── JSON Parsing Helper ───────────────────────────────────────────────────────
def _clean_and_parse_json(raw_response: str) -> dict:
    """
    Gemini sometimes wraps JSON in ```json``` code blocks or adds
    extra text despite instructions. This function handles those cases.

    Steps:
    1. Try parsing directly (ideal case)
    2. Strip markdown code blocks if present
    3. Find the JSON object boundaries { ... }
    4. Raise a clear error if nothing works
    """
    text = raw_response.strip()

    # Attempt 1: Direct parse (Gemini followed instructions perfectly)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Strip markdown code block wrapper
    if text.startswith("```"):
        # Remove ```json or ``` at start and ``` at end
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Attempt 3: Find JSON boundaries manually
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_substring = text[first_brace:last_brace + 1]
        try:
            return json.loads(json_substring)
        except json.JSONDecodeError:
            pass

    # All attempts failed
    raise ValueError(
        f"Failed to parse Gemini response as JSON.\n"
        f"Raw response (first 500 chars):\n{raw_response[:500]}"
    )


# ── Result Validation ─────────────────────────────────────────────────────────
def _validate_result(result: dict) -> dict:
    """
    Validates and fixes the AI response to ensure it has all required fields.

    Why do we need this?
    - Gemini might skip optional fields
    - Risk score might be a string instead of int
    - Clauses list might be missing

    This ensures the frontend ALWAYS gets a predictable structure.
    """
    # Ensure top-level fields exist with defaults
    result.setdefault("document_type", "Unknown")
    result.setdefault("parties", [])
    result.setdefault("summary", "No summary generated.")
    result.setdefault("clauses", [])
    result.setdefault("red_flags", [])
    result.setdefault("recommendations", [])

    # Fix overall_risk_score — must be an integer 0-100
    risk_score = result.get("overall_risk_score", 50)
    if isinstance(risk_score, str):
        try:
            risk_score = int(risk_score)
        except ValueError:
            risk_score = 50
    result["overall_risk_score"] = max(0, min(100, int(risk_score)))

    # Fix overall_risk_level based on score (in case Gemini gets it wrong)
    score = result["overall_risk_score"]
    if score <= 30:
        result["overall_risk_level"] = "Low"
    elif score <= 60:
        result["overall_risk_level"] = "Medium"
    else:
        result["overall_risk_level"] = "High"

    # Validate each clause
    validated_clauses = []
    for clause in result.get("clauses", []):
        clause.setdefault("clause_name", "Unnamed Clause")
        clause.setdefault("clause_type", "other")
        clause.setdefault("original_text", "")
        clause.setdefault("risk_level", "Medium")
        clause.setdefault("risk_score", 50)
        clause.setdefault("explanation", "No explanation provided.")
        clause.setdefault("india_law_reference", "Not specified")
        clause.setdefault("suggested_rewrite", "")

        # Fix clause risk_score type
        if isinstance(clause["risk_score"], str):
            try:
                clause["risk_score"] = int(clause["risk_score"])
            except ValueError:
                clause["risk_score"] = 50
        clause["risk_score"] = max(0, min(100, int(clause["risk_score"])))

        validated_clauses.append(clause)

    result["clauses"] = validated_clauses

    return result


# ── MAIN FUNCTION — The one that main.py will call ────────────────────────────
def analyze_document(document_text: str) -> dict:
    """
    Analyzes a legal document using Google Gemini AI.

    This is the MAIN function that brings everything together:
    1. Takes raw text from parser.py
    2. Builds the prompt using prompts.py
    3. Sends it to Gemini
    4. Parses and validates the JSON response
    5. Returns a clean, predictable result dict

    Args:
        document_text: Raw text extracted from a PDF/DOCX by parser.py

    Returns:
        A validated dict matching the EXPECTED_JSON_SCHEMA from prompts.py

    Raises:
        ValueError: If API key is missing or response can't be parsed
        Exception: If Gemini API call fails (network, quota, etc.)
    """
    # Step 1: Build the prompt
    prompt = build_analysis_prompt(document_text)

    # Step 2: Create the Gemini client
    client = _create_client()

    # Step 3: Send to Gemini and get response
    print("[ANALYZER] Sending document to Gemini for analysis...")
    print(f"[ANALYZER] Document size: {len(document_text):,} chars / ~{len(document_text) // 4:,} tokens")
    print(f"[ANALYZER] Using model: {MODEL_NAME}")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,        # Low = more consistent, less creative
            top_p=0.8,              # Focus on high-probability tokens
            max_output_tokens=8192, # Enough for detailed analysis
        ),
    )

    # Step 4: Extract the text response
    if not response or not response.text:
        raise ValueError("Gemini returned an empty response. The document may be too short or unclear.")

    raw_text = response.text
    print(f"[ANALYZER] Gemini responded with {len(raw_text):,} characters")

    # Step 5: Parse JSON from response
    result = _clean_and_parse_json(raw_text)

    # Step 6: Validate and fix the result
    result = _validate_result(result)

    # Step 7: Add metadata about the analysis
    result["_meta"] = {
        "model": MODEL_NAME,
        "input_chars": len(document_text),
        "input_words": len(document_text.split()),
        "clauses_found": len(result["clauses"]),
        "red_flags_found": len(result["red_flags"]),
    }

    print(f"[ANALYZER] Analysis complete!")
    print(f"[ANALYZER] Found {len(result['clauses'])} clauses, {len(result['red_flags'])} red flags")
    print(f"[ANALYZER] Overall risk: {result['overall_risk_score']}/100 ({result['overall_risk_level']})")

    return result


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # Windows CP1252 fix

    from parser import extract_text

    # Use the sample contract PDF we generated earlier
    test_file = "sample_contract.pdf"

    if not os.path.exists(test_file):
        print(f"[ERROR] Test file '{test_file}' not found.")
        print("Run first: python create_sample_contract.py")
        sys.exit(1)

    print("=" * 60)
    print("ANALYZER END-TO-END TEST")
    print("=" * 60)

    # Step 1: Extract text
    print("\n[STEP 1] Extracting text from PDF...")
    parsed = extract_text(test_file)
    print(f"  Extracted {parsed['word_count']:,} words from {parsed['file_name']}")

    # Step 2: Analyze with Gemini
    print("\n[STEP 2] Analyzing with Gemini AI...")
    try:
        result = analyze_document(parsed["text"])
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Gemini API call failed: {e}")
        sys.exit(1)

    # Step 3: Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    print(f"\n  Document Type : {result['document_type']}")
    print(f"  Parties       : {', '.join(result['parties'])}")
    print(f"  Risk Score    : {result['overall_risk_score']}/100 ({result['overall_risk_level']})")
    print(f"\n  Summary:\n  {result['summary']}")

    print(f"\n  --- CLAUSES ({len(result['clauses'])}) ---")
    for i, clause in enumerate(result["clauses"], 1):
        risk_tag = f"[{clause['risk_level'].upper()}]"
        print(f"\n  {i}. {clause['clause_name']} {risk_tag} (Score: {clause['risk_score']})")
        print(f"     Law: {clause['india_law_reference']}")
        print(f"     Why: {clause['explanation'][:120]}...")
        if clause.get("suggested_rewrite"):
            print(f"     Fix: {clause['suggested_rewrite'][:120]}...")

    if result["red_flags"]:
        print(f"\n  --- RED FLAGS ({len(result['red_flags'])}) ---")
        for flag in result["red_flags"]:
            print(f"  [!] {flag}")

    if result["recommendations"]:
        print(f"\n  --- RECOMMENDATIONS ({len(result['recommendations'])}) ---")
        for rec in result["recommendations"]:
            print(f"  --> {rec}")

    # Step 4: Save full JSON to file for inspection
    output_file = "analysis_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n  Full JSON saved to: {output_file}")

    print("\n" + "=" * 60)
    print("[OK] Analyzer test complete!")
    print("=" * 60)
