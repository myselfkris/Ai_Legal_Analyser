"""
prompts.py — Prompt Engineering for Legal Document Analysis
Builds structured prompts that instruct Gemini to act as an Indian lawyer
and return machine-readable JSON analysis of legal documents.
"""


# ── The exact JSON schema we expect Gemini to return ──────────────────────────
# Defining this separately keeps the prompt clean and lets us reuse it
# for validation in analyzer.py later.

EXPECTED_JSON_SCHEMA = """
{
  "document_type": "string (e.g. NDA, Service Agreement, Employment Contract)",
  "parties": ["Party A name and role", "Party B name and role"],
  "summary": "string — plain English summary of what this contract does (2-3 sentences)",
  "overall_risk_score": "integer between 0 and 100",
  "overall_risk_level": "string — one of: Low, Medium, High",
  "clauses": [
    {
      "clause_name": "string (e.g. Indemnity Clause)",
      "clause_type": "string (e.g. indemnity, ip_assignment, termination, nda, payment, liability, governing_law)",
      "original_text": "string — the exact or paraphrased clause text from the document",
      "risk_level": "string — one of: Low, Medium, High",
      "risk_score": "integer between 0 and 100",
      "explanation": "string — plain English explanation of what this clause means and why it is risky or safe",
      "india_law_reference": "string — relevant Indian law or section (e.g. Section 124, Indian Contract Act 1872)",
      "suggested_rewrite": "string — a safer, balanced rewrite of the clause (only for Medium and High risk)"
    }
  ],
  "red_flags": ["string — list of the most critical issues found"],
  "recommendations": ["string — list of actionable negotiation suggestions"]
}
"""


# ── The system instruction (tells Gemini WHO it is) ───────────────────────────
SYSTEM_INSTRUCTION = """You are a senior Indian commercial lawyer with 15+ years of experience 
in contract law, startup agreements, and freelancer protection. You specialize in:
- The Indian Contract Act, 1872
- The Information Technology Act, 2000
- The Digital Personal Data Protection (DPDP) Act, 2023
- Intellectual Property laws in India
- Employment and contractor agreements governed by Indian law

Your job is to protect the interests of startups and freelancers by identifying 
risky, one-sided, or legally problematic clauses in contracts."""


# ── Risk scoring guide (keeps Gemini consistent across all documents) ─────────
RISK_SCORING_GUIDE = """
RISK SCORING GUIDE — Follow this consistently:

Risk Score 0-30   → LOW RISK
  - Standard, balanced clause
  - Common in Indian commercial contracts
  - No significant disadvantage to either party

Risk Score 31-60  → MEDIUM RISK
  - Somewhat one-sided but not unusual
  - Could be negotiated for better terms
  - May have hidden implications worth flagging

Risk Score 61-100 → HIGH RISK
  - Severely one-sided or unfair clause
  - May be unenforceable under Indian law
  - Requires immediate attention and renegotiation
  - Examples: unlimited indemnity, perpetual IP assignment without compensation,
    no limitation of liability cap, automatic renewal with no notice
"""


# ── Clause types to look for (guides Gemini to be thorough) ───────────────────
CLAUSE_TYPES_TO_IDENTIFY = """
CLAUSE TYPES TO IDENTIFY (find as many as present in the document):
1.  indemnity          -- Who bears financial loss if something goes wrong
2.  ip_assignment      -- Who owns intellectual property created during the engagement
3.  termination        -- How and when the contract can be ended
4.  nda_confidentiality -- What information must be kept secret and for how long
5.  payment            -- Payment terms, delays, penalties
6.  liability          -- Caps or limits on damages
7.  governing_law      -- Which country/state laws apply, which courts have jurisdiction
8.  non_compete        -- Restrictions on working with competitors after contract ends
9.  data_protection    -- How personal data is handled (relevant to DPDP Act 2023)
10. force_majeure      -- What happens during unforeseen events (COVID, natural disasters)
11. dispute_resolution -- Arbitration vs court, mediation clauses
12. auto_renewal       -- Whether the contract auto-renews without explicit consent
"""


def build_analysis_prompt(contract_text: str) -> str:
    """
    Builds the complete prompt to send to Gemini for legal analysis.

    This combines:
    - System role (who Gemini is)
    - Risk scoring guide (how to score)
    - Clause detection guide (what to look for)
    - The actual contract text
    - Strict output instructions (return ONLY JSON)

    Args:
        contract_text: Raw text extracted from the uploaded PDF/DOCX

    Returns:
        A fully formatted prompt string ready to send to Gemini
    """

    prompt = f"""
{SYSTEM_INSTRUCTION}

{RISK_SCORING_GUIDE}

{CLAUSE_TYPES_TO_IDENTIFY}

------------------------------------------------------
CONTRACT TO ANALYZE:
------------------------------------------------------

{contract_text}

------------------------------------------------------
OUTPUT INSTRUCTIONS - READ CAREFULLY:
------------------------------------------------------

Analyze the contract above and return your analysis as VALID JSON ONLY.
Do NOT include any explanation, markdown, or text outside the JSON.
Do NOT wrap the JSON in ```json``` code blocks.
Start your response directly with {{ and end with }}.

Use EXACTLY this JSON structure:
{EXPECTED_JSON_SCHEMA}

Rules:
- overall_risk_score must be the weighted average of all clause risk scores
- Find ALL clause types present — do not skip clauses
- Write explanations in simple English that a non-lawyer can understand
- india_law_reference is mandatory for every clause — look it up carefully
- suggested_rewrite is required for every clause with risk_level Medium or High
- red_flags should list the 3-5 most critical issues in the document
- recommendations should be actionable (e.g. "Negotiate mutual indemnity cap of INR 10 lakhs")
"""

    return prompt.strip()


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # needed on Windows (CP1252 terminal)

    # Show a preview of what the prompt looks like with sample text
    sample_text = "[Sample contract text would go here - replaced by parser.py output]"
    prompt = build_analysis_prompt(sample_text)

    print("=" * 60)
    print("PROMPT PREVIEW")
    print("=" * 60)
    print(f"Total prompt length : {len(prompt):,} characters")
    print(f"Estimated tokens    : ~{len(prompt) // 4:,} tokens")
    print()
    print("--- FIRST 800 CHARACTERS ---")
    print(prompt[:800])
    print()
    print("--- LAST 400 CHARACTERS ---")
    print(prompt[-400:])
    print()
    print("[OK] prompts.py loaded successfully!")
