"""
SmartScribe MCP Server
======================
AI Clinical Note Generator & FHIR Writer for the Prompt Opinion platform.

Exposes 3 tools:
  - generate_note:   Raw transcript → structured SOAP note
  - extract_codes:   Clinical text → ICD-10, SNOMED CT, CPT codes
  - to_fhir_bundle:  Raw transcript → complete FHIR R4 Bundle (end-to-end)

Run:
  python server.py

Test with MCP Inspector:
  fastmcp dev server.py
"""

import os
import json
from fastmcp import FastMCP

from tools.generate_note import generate_note as _generate_note
from tools.extract_codes import extract_codes as _extract_codes
from tools.to_fhir_bundle import to_fhir_bundle as _to_fhir_bundle

# ──────────────────────────────────────────────
# Server setup
# ──────────────────────────────────────────────

mcp = FastMCP(
    "SmartScribe",
    description=(
        "AI Clinical Note Generator & FHIR Writer — transform messy "
        "clinician-patient transcripts into structured SOAP notes with "
        "auto-suggested medical codes (ICD-10, SNOMED CT, CPT) and "
        "FHIR R4-compliant resources. Built for the Prompt Opinion "
        "healthcare AI platform."
    ),
)


# ──────────────────────────────────────────────
# Tool 1: generate_note
# ──────────────────────────────────────────────

@mcp.tool()
async def generate_note(
    transcript: str,
    note_type: str = "general",
    patient_age: int | None = None,
    patient_sex: str | None = None,
) -> str:
    """
    Transform a raw clinician-patient transcript or bullet-point notes
    into a properly structured SOAP clinical note.

    Use this tool when a clinician has rough notes, a conversation
    transcript, or bullet points from a patient encounter and needs
    them converted into a formal clinical note.

    The output includes Subjective, Objective, Assessment, and Plan
    sections formatted according to clinical documentation standards.

    IMPORTANT: This tool uses AI and produces SYNTHETIC output only.
    All generated notes must be reviewed by a licensed clinician.

    Args:
        transcript: Raw encounter text — conversation, bullet points,
                    or rough notes from a clinical encounter.
        note_type: Clinical specialty context — "general", "cardiology",
                   "oncology", "psychiatry", "pediatrics", "orthopedics".
        patient_age: Patient age in years (helps with clinical context).
        patient_sex: Patient sex — "male" or "female" (helps with context).
    """
    result = await _generate_note(
        transcript=transcript,
        note_type=note_type,
        patient_age=patient_age,
        patient_sex=patient_sex,
    )
    return json.dumps(result, indent=2)


# ──────────────────────────────────────────────
# Tool 2: extract_codes
# ──────────────────────────────────────────────

@mcp.tool()
async def extract_codes(
    clinical_text: str,
) -> str:
    """
    Extract and suggest medical codes from any clinical text.

    Analyzes clinical documentation and suggests appropriate:
    - ICD-10-CM diagnosis codes
    - SNOMED CT clinical finding codes
    - CPT procedure/E&M codes

    Each code includes a confidence level (high/medium/low) and
    the specific context from the text that supports it.

    Use this tool after generating a note, or on any existing
    clinical text that needs coding.

    IMPORTANT: These are AI suggestions only. A certified medical
    coder should verify all codes before use in billing.

    Args:
        clinical_text: Any clinical text — a SOAP note, transcript,
                       discharge summary, or clinical narrative.
    """
    result = await _extract_codes(
        clinical_text=clinical_text,
    )
    return json.dumps(result, indent=2)


# ──────────────────────────────────────────────
# Tool 3: to_fhir_bundle
# ──────────────────────────────────────────────

@mcp.tool()
async def to_fhir_bundle(
    transcript: str,
    patient_id: str = "synth-patient-001",
    practitioner_id: str = "synth-practitioner-001",
    note_type: str = "general",
    patient_age: int | None = None,
    patient_sex: str | None = None,
) -> str:
    """
    End-to-end pipeline: transform a raw clinical transcript into a
    complete FHIR R4 transaction Bundle.

    This tool does everything in one call:
    1. Generates a structured SOAP note from the transcript
    2. Extracts ICD-10, SNOMED CT, and CPT codes
    3. Builds FHIR R4 resources (Encounter, DocumentReference, Conditions)
    4. Packages them into a transaction Bundle ready for an EHR

    Use this when you want the full pipeline — from messy notes to
    FHIR-ready output — in a single tool call.

    The Bundle includes:
    - 1 Encounter resource (the clinical visit)
    - 1 DocumentReference (the full SOAP note)
    - N Condition resources (one per identified diagnosis)

    All resources are tagged as "ai-generated" and Conditions are
    set to "provisional" verification status.

    Args:
        transcript: Raw clinical encounter text.
        patient_id: FHIR Patient resource ID to reference.
        practitioner_id: FHIR Practitioner resource ID to reference.
        note_type: Clinical specialty — "general", "cardiology", etc.
        patient_age: Patient age in years.
        patient_sex: Patient sex — "male" or "female".
    """
    result = await _to_fhir_bundle(
        transcript=transcript,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        note_type=note_type,
        patient_age=patient_age,
        patient_sex=patient_sex,
    )
    return json.dumps(result, indent=2)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("SMARTSCRIBE_PORT", 8000))
    print(f"Starting SmartScribe MCP Server on port {port}...")
    print(f"MCP endpoint: http://localhost:{port}/mcp")
    print(f"Tools: generate_note, extract_codes, to_fhir_bundle")
    mcp.run(transport="streamable-http", port=port)
