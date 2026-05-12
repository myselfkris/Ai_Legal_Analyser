"""
create_sample_contract.py — Generates a realistic sample NDA PDF for testing parser.py
Run once: python create_sample_contract.py
"""

import fitz  # PyMuPDF


def create_sample_nda_pdf(output_path: str):
    """Creates a 2-page realistic NDA PDF using PyMuPDF."""
    doc = fitz.Document()

    # ── Page 1 content ────────────────────────────────────────────────────────
    content_p1 = """\
NON-DISCLOSURE AGREEMENT (NDA)

This Non-Disclosure Agreement ("Agreement") is entered into as of 1st May 2026, by and
between:

  Party A: TechCorp Solutions Pvt. Ltd., a company incorporated under the Companies
           Act, 2013, having its registered office at 100, MG Road, Bengaluru - 560001,
           Karnataka, India ("Disclosing Party")

  Party B: Freelancer Rajesh Kumar, residing at 45, Koramangala 5th Block,
           Bengaluru - 560095, Karnataka, India ("Receiving Party")

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information
relating to its AI-powered SaaS product ("Confidential Information"); and

WHEREAS, the Receiving Party desires to receive certain of said Confidential Information
for the purpose of evaluating a potential business relationship;

NOW, THEREFORE, in consideration of the mutual covenants and agreements hereinafter set
forth, and for other good and valuable consideration, the parties agree as follows:

1. CONFIDENTIAL INFORMATION

   "Confidential Information" means any data or information that is proprietary to the
   Disclosing Party and not generally known to the public, whether in tangible or
   intangible form, whenever and however disclosed, including but not limited to:

   (a) any marketing strategies, plans, financial information, or projections,
       operations, sales estimates, business plans and performance results relating
       to the past, present or future business activities;
   (b) plans for products or services, and customer or supplier lists;
   (c) any scientific or technical information, invention, design, process, procedure,
       formula, improvement, technology or method;
   (d) source code, algorithms, software architecture, and system design documents;
   (e) any concepts, reports, data, know-how, works-in-progress, designs, development
       tools, specifications, computer software, databases, and trade secrets.

2. OBLIGATIONS OF RECEIVING PARTY

   The Receiving Party agrees to:
   (a) Hold all Confidential Information in strict confidence;
   (b) Not disclose Confidential Information to any third parties without prior written
       consent from the Disclosing Party;
   (c) Use the Confidential Information solely for the purpose of evaluating a potential
       business engagement with the Disclosing Party;
   (d) Protect the Confidential Information using the same degree of care it uses to
       protect its own confidential information, but in no event less than reasonable care.
"""

    # ── Page 2 content ────────────────────────────────────────────────────────
    content_p2 = """\
3. INDEMNIFICATION

   The Receiving Party shall indemnify, defend, and hold harmless the Disclosing Party
   and its officers, directors, employees, agents, and successors from and against any
   and all losses, damages, liabilities, deficiencies, claims, actions, judgments,
   settlements, interest, awards, penalties, fines, costs, or expenses of whatever kind,
   including reasonable attorneys' fees, arising out of or relating to any breach of this
   Agreement by the Receiving Party.

   NOTE: This indemnification clause is one-sided and places full financial liability on
   the Receiving Party with no cap on damages — HIGH RISK under Section 124 of the Indian
   Contract Act, 1872.

4. INTELLECTUAL PROPERTY

   All Confidential Information disclosed by the Disclosing Party shall remain the
   exclusive property of the Disclosing Party. The Receiving Party acknowledges that any
   work product, inventions, or improvements created by the Receiving Party using or
   derived from the Confidential Information shall be automatically and irrevocably
   assigned to the Disclosing Party without any additional compensation.

   This perpetual, irrevocable IP assignment with no compensation is HIGH RISK.

5. TERM AND TERMINATION

   This Agreement shall commence on the date first written above and continue for FIVE (5)
   years, unless earlier terminated by either party upon thirty (30) days written notice.

   Upon termination, confidentiality obligations survive for an additional TEN (10) years.

6. GOVERNING LAW AND JURISDICTION

   This Agreement shall be governed by the laws of India, specifically the Indian Contract
   Act, 1872 and the Information Technology Act, 2000. Disputes shall be subject to the
   exclusive jurisdiction of courts in Bengaluru, Karnataka.

   Data handling under this Agreement shall comply with the Digital Personal Data
   Protection (DPDP) Act, 2023.

7. LIMITATION OF LIABILITY

   IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, OR
   CONSEQUENTIAL DAMAGES. HOWEVER, THIS LIMITATION DOES NOT APPLY TO THE RECEIVING
   PARTY'S INDEMNIFICATION OBLIGATIONS UNDER SECTION 3.

   NOTE: No cap on direct damages is specified — MEDIUM RISK clause.

8. ENTIRE AGREEMENT

   This Agreement constitutes the entire agreement between the parties and supersedes all
   prior agreements, understandings, and discussions between the parties.

IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date above.

TechCorp Solutions Pvt. Ltd.           Rajesh Kumar
By: ____________________________       By: ____________________________
Name: Ananya Sharma                    Name: Rajesh Kumar
Title: Chief Executive Officer         Title: Independent Contractor
Date: 01/05/2026                       Date: 01/05/2026
"""

    # ── Create pages and insert text ──────────────────────────────────────────
    margin = 50
    fontsize = 9.5

    # Page 1
    doc.new_page(width=595, height=842)
    page1 = doc[0]  # Access via index — required in PyMuPDF 1.27+
    page1.insert_textbox(
        fitz.Rect(margin, margin, 595 - margin, 842 - margin),
        content_p1,
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),
        align=0,
    )

    # Page 2
    doc.new_page(width=595, height=842)
    page2 = doc[1]
    page2.insert_textbox(
        fitz.Rect(margin, margin, 595 - margin, 842 - margin),
        content_p2,
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),
        align=0,
    )

    doc.save(output_path)
    doc.close()
    print(f"[OK] Sample NDA PDF created at: {output_path}")
    print(f"   2 pages | Indemnity, IP, NDA, Termination, Governing Law clauses included")


if __name__ == "__main__":
    create_sample_nda_pdf("sample_contract.pdf")
