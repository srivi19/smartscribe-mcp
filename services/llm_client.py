"""
LLM client wrapper for clinical note generation, medical code
extraction, and summarization.

Uses the Anthropic Claude API.
"""

import os
import json
import anthropic


_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Lazy-initialize the Anthropic client."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Get one at https://console.anthropic.com/"
            )
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


async def generate_soap_note(
    transcript: str,
    note_type: str = "general",
    patient_age: int | None = None,
    patient_sex: str | None = None,
) -> dict:
    """
    Generate a structured SOAP note from a raw transcript or bullet points.

    Args:
        transcript: Raw clinician-patient conversation or bullet-point notes.
        note_type: Specialty type — general, cardiology, oncology, psychiatry, etc.
        patient_age: Optional patient age for context.
        patient_sex: Optional patient sex for context.

    Returns:
        Dict with subjective, objective, assessment, plan fields.
    """
    client = _get_client()

    demographics = ""
    if patient_age or patient_sex:
        parts = []
        if patient_age:
            parts.append(f"{patient_age}-year-old")
        if patient_sex:
            parts.append(patient_sex)
        demographics = f"\nPatient demographics: {' '.join(parts)}"

    system_prompt = f"""You are an expert medical scribe AI. Your job is to transform raw clinical encounter notes into properly structured SOAP notes.

SPECIALTY CONTEXT: {note_type}
{demographics}

RULES:
- Use only information present in the transcript. NEVER fabricate clinical details.
- Use standard medical terminology and abbreviations appropriate for clinical documentation.
- Write concisely in clinical note style (sentence fragments are fine, as used in real clinical notes).
- If information for a SOAP section is not available in the transcript, write "Not documented in encounter."
- For the Assessment section, list problems/diagnoses as a numbered problem list.
- For the Plan section, organize by problem number matching the Assessment.
- Include relevant negatives mentioned by the patient.
- This is SYNTHETIC data for demonstration purposes only.

Respond ONLY with a valid JSON object (no markdown, no backticks):
{{
  "subjective": "Chief complaint, HPI, review of systems, relevant history as reported by patient",
  "objective": "Vitals, physical exam findings, any test results mentioned",
  "assessment": "Numbered problem list with clinical assessment",
  "plan": "Treatment plan organized by problem number"
}}"""

    user_prompt = f"""Transform the following clinical encounter into a structured SOAP note:

---
{transcript}
---

Generate the SOAP note as JSON."""

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "subjective": "Error: Could not parse note. Please review transcript.",
            "objective": "Not documented.",
            "assessment": "Unable to generate structured note from provided input.",
            "plan": "Manual review of transcript recommended.",
        }


async def extract_medical_codes(
    clinical_text: str,
) -> dict:
    """
    Extract ICD-10, SNOMED CT, and CPT codes from clinical text.

    Args:
        clinical_text: Any clinical text — a SOAP note, transcript, or summary.

    Returns:
        Dict with icd10_codes, snomed_codes, cpt_codes lists and a note_summary.
    """
    client = _get_client()

    system_prompt = """You are a medical coding specialist AI. Your job is to identify and suggest appropriate medical codes from clinical documentation.

CODE SYSTEMS:
- ICD-10-CM: Diagnosis codes (e.g., E11.9 for Type 2 Diabetes, J06.9 for Upper respiratory infection)
- SNOMED CT: Clinical finding codes (e.g., 44054006 for Type 2 Diabetes Mellitus)
- CPT: Procedure and E/M codes (e.g., 99213 for Established patient office visit, 99214 for detailed visit)

RULES:
- Only suggest codes that are clearly supported by the clinical text.
- Assign a confidence level: "high" (explicitly stated), "medium" (strongly implied), "low" (possible but uncertain).
- Include the relevant context from the note that supports each code.
- For CPT E/M codes, consider the complexity of the encounter documented.
- Use the most specific code available (e.g., E11.65 for Type 2 DM with hyperglycemia, not just E11.9).
- These are SUGGESTIONS only — a certified coder should verify.

Respond ONLY with a valid JSON object (no markdown, no backticks):
{
  "icd10_codes": [
    {"code": "E11.9", "system": "ICD-10", "display": "Type 2 diabetes mellitus without complications", "confidence": "high", "context": "Patient reports diabetes managed with metformin"}
  ],
  "snomed_codes": [
    {"code": "44054006", "system": "SNOMED-CT", "display": "Type 2 diabetes mellitus", "confidence": "high", "context": "Documented diagnosis"}
  ],
  "cpt_codes": [
    {"code": "99213", "system": "CPT", "display": "Office visit, established patient, low complexity", "confidence": "medium", "context": "Brief follow-up visit documented"}
  ],
  "note_summary": "Brief 1-sentence summary of what was coded"
}"""

    user_prompt = f"""Extract all appropriate medical codes from this clinical text:

---
{clinical_text}
---

Identify ICD-10, SNOMED CT, and CPT codes. Return as JSON."""

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "icd10_codes": [],
            "snomed_codes": [],
            "cpt_codes": [],
            "note_summary": "Error: Could not extract codes. Manual coding recommended.",
        }
