"""
SmartScribe MCP Server
======================
AI Clinical Note Generator & FHIR Writer for the Prompt Opinion platform.

Uses the official Anthropic MCP SDK with json_response=True for
browser compatibility and Prompt Opinion integration.

Exposes 3 tools:
  - generate_note:   Raw transcript -> structured SOAP note
  - extract_codes:   Clinical text -> ICD-10, SNOMED CT, CPT codes
  - to_fhir_bundle:  Raw transcript -> complete FHIR R4 Bundle

Run:
  python server.py
"""

import os
import json
from mcp.server.fastmcp import FastMCP

from tools.generate_note import generate_note as _generate_note
from tools.extract_codes import extract_codes as _extract_codes
from tools.to_fhir_bundle import to_fhir_bundle as _to_fhir_bundle

# ──────────────────────────────────────────────
# Server setup
# json_response=True returns plain JSON instead of SSE streams
# This makes it work with browsers and Prompt Opinion
# ──────────────────────────────────────────────

mcp = FastMCP("SmartScribe", json_response=True)


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

    Args:
        transcript: Raw encounter text - conversation, bullet points,
                    or rough notes from a clinical encounter.
        note_type: Clinical specialty - general, cardiology, oncology,
                   psychiatry, pediatrics, orthopedics.
        patient_age: Patient age in years.
        patient_sex: Patient sex - male or female.
    """
    print(f"[generate_note] called with note_type={note_type}", flush=True)
    try:
        result = await _generate_note(
            transcript=transcript,
            note_type=note_type,
            patient_age=patient_age,
            patient_sex=patient_sex,
        )
        print(f"[generate_note] success", flush=True)
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"[generate_note] ERROR: {e}", flush=True)
        raise


# ──────────────────────────────────────────────
# Tool 2: extract_codes
# ──────────────────────────────────────────────

@mcp.tool()
async def extract_codes(
    clinical_text: str,
) -> str:
    """
    Extract and suggest medical codes from any clinical text.

    Suggests ICD-10-CM diagnosis codes, SNOMED CT clinical finding
    codes, and CPT procedure codes with confidence levels.

    Args:
        clinical_text: Any clinical text - SOAP note, transcript,
                       discharge summary, or clinical narrative.
    """
    print(f"[extract_codes] called", flush=True)
    try:
        result = await _extract_codes(clinical_text=clinical_text)
        print(f"[extract_codes] success", flush=True)
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"[extract_codes] ERROR: {e}", flush=True)
        raise


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

    Generates a SOAP note, extracts codes, and builds FHIR R4
    resources in one call.

    Args:
        transcript: Raw clinical encounter text.
        patient_id: FHIR Patient resource ID.
        practitioner_id: FHIR Practitioner resource ID.
        note_type: Clinical specialty.
        patient_age: Patient age in years.
        patient_sex: Patient sex - male or female.
    """
    print(f"[to_fhir_bundle] called with note_type={note_type}", flush=True)
    try:
        result = await _to_fhir_bundle(
            transcript=transcript,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            note_type=note_type,
            patient_age=patient_age,
            patient_sex=patient_sex,
        )
        print(f"[to_fhir_bundle] success", flush=True)
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"[to_fhir_bundle] ERROR: {e}", flush=True)
        raise


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("SMARTSCRIBE_PORT", 8000)))
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    print(f"Starting SmartScribe MCP Server on port {port}...", flush=True)
    print(f"MCP endpoint: http://0.0.0.0:{port}/mcp", flush=True)
    print(f"Tools: generate_note, extract_codes, to_fhir_bundle", flush=True)
    print(f"ANTHROPIC_API_KEY: {'SET' if api_key else 'MISSING!'}", flush=True)
    print(f"Response mode: JSON (not SSE)", flush=True)

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
