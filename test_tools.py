#!/usr/bin/env python3
"""
Quick test of SmartScribe tools using synthetic transcript data.

Run: python test_tools.py

Requires ANTHROPIC_API_KEY environment variable to be set.
"""

import asyncio
import json
from tools.generate_note import generate_note
from tools.extract_codes import extract_codes
from tools.to_fhir_bundle import to_fhir_bundle


async def test_workflow():
    """Run a complete SmartScribe workflow with synthetic data."""

    print("=" * 60)
    print("SmartScribe Test — Synthetic Encounter Workflow")
    print("=" * 60)
    print()

    # Load synthetic transcript
    with open("synthetic_data/sample_transcripts.json") as f:
        data = json.load(f)
        encounter = data["transcripts"][0]  # Diabetes follow-up

    print(f"Encounter: {encounter['title']}")
    print(f"Patient: {encounter['patient_age']}yo {encounter['patient_sex']}")
    print(f"Specialty: {encounter['note_type']}")
    print()

    # Show a snippet of the raw input
    snippet = encounter['transcript'][:200]
    print(f"Raw transcript (first 200 chars):")
    print(f"  \"{snippet}...\"")
    print()

    # ── Step 1: Generate SOAP Note ──
    print("Step 1: Generating SOAP note from transcript...")
    print("-" * 60)

    note_result = await generate_note(
        transcript=encounter['transcript'],
        note_type=encounter['note_type'],
        patient_age=encounter['patient_age'],
        patient_sex=encounter['patient_sex'],
    )

    soap = note_result['soap_note']
    print(f"\nSUBJECTIVE:")
    print(f"  {soap['subjective'][:150]}...")
    print(f"\nOBJECTIVE:")
    print(f"  {soap['objective'][:150]}...")
    print(f"\nASSESSMENT:")
    print(f"  {soap['assessment'][:150]}...")
    print(f"\nPLAN:")
    print(f"  {soap['plan'][:150]}...")
    print()

    # ── Step 2: Extract Medical Codes ──
    print("Step 2: Extracting medical codes...")
    print("-" * 60)

    # Combine SOAP for coding
    full_note = (
        f"{soap['subjective']}\n{soap['objective']}\n"
        f"{soap['assessment']}\n{soap['plan']}"
    )

    codes_result = await extract_codes(clinical_text=full_note)

    print(f"\nTotal codes found: {codes_result['total_codes_found']}")

    if codes_result['icd10_codes']:
        print(f"\nICD-10 Codes:")
        for code in codes_result['icd10_codes'][:5]:
            print(f"  {code['code']} — {code['display']} (confidence: {code['confidence']})")

    if codes_result['snomed_codes']:
        print(f"\nSNOMED CT Codes:")
        for code in codes_result['snomed_codes'][:3]:
            print(f"  {code['code']} — {code['display']}")

    if codes_result['cpt_codes']:
        print(f"\nCPT Codes:")
        for code in codes_result['cpt_codes']:
            print(f"  {code['code']} — {code['display']}")
    print()

    # ── Step 3: Generate FHIR Bundle ──
    print("Step 3: Building FHIR R4 Bundle...")
    print("-" * 60)

    bundle_result = await to_fhir_bundle(
        transcript=encounter['transcript'],
        patient_id="synth-patient-001",
        note_type=encounter['note_type'],
        patient_age=encounter['patient_age'],
        patient_sex=encounter['patient_sex'],
    )

    summary = bundle_result['summary']
    print(f"\nFHIR Bundle generated:")
    print(f"  Total resources: {summary['total_resources']}")
    print(f"  Encounters: {summary['encounters']}")
    print(f"  DocumentReferences: {summary['document_references']}")
    print(f"  Conditions: {summary['conditions']}")

    if summary['icd10_codes_used']:
        print(f"\n  ICD-10 codes used:")
        for code in summary['icd10_codes_used']:
            print(f"    - {code}")

    # Show the bundle structure
    bundle = bundle_result['fhir_bundle']
    print(f"\n  Bundle type: {bundle['type']}")
    print(f"  Bundle ID: {bundle['id']}")
    print(f"  Resources:")
    for entry in bundle.get('entry', []):
        res = entry['resource']
        print(f"    - {res['resourceType']}/{res['id']}")

    print()
    print("=" * 60)
    print("Test complete! All 3 tools are working.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run the MCP server:  python server.py")
    print("  2. Test with inspector: fastmcp dev server.py")
    print("  3. Deploy to Railway and register on Prompt Opinion")


if __name__ == "__main__":
    asyncio.run(test_workflow())
