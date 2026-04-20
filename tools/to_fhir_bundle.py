"""
to_fhir_bundle tool — Convert a structured SOAP note and medical codes
into a FHIR R4 Bundle ready for EHR integration.
"""

from services import fhir_builder, llm_client


async def to_fhir_bundle(
    transcript: str,
    patient_id: str = "synth-patient-001",
    practitioner_id: str = "synth-practitioner-001",
    note_type: str = "general",
    patient_age: int | None = None,
    patient_sex: str | None = None,
) -> dict:
    """
    End-to-end pipeline: takes raw clinical text and produces a complete
    FHIR R4 Bundle with Encounter, DocumentReference, and Condition resources.

    This is the "one-shot" tool — it internally calls generate_note and
    extract_codes, then assembles everything into a FHIR transaction bundle.

    Args:
        transcript: Raw clinical encounter text.
        patient_id: FHIR Patient resource ID.
        practitioner_id: FHIR Practitioner resource ID.
        note_type: Clinical specialty context.
        patient_age: Patient age for context.
        patient_sex: Patient sex for context.

    Returns:
        Dict with the FHIR Bundle and metadata about what was generated.
    """
    # Step 1: Generate SOAP note
    soap = await llm_client.generate_soap_note(
        transcript=transcript,
        note_type=note_type,
        patient_age=patient_age,
        patient_sex=patient_sex,
    )

    # Step 2: Extract codes from the generated note
    full_note_text = (
        f"SUBJECTIVE: {soap.get('subjective', '')}\n"
        f"OBJECTIVE: {soap.get('objective', '')}\n"
        f"ASSESSMENT: {soap.get('assessment', '')}\n"
        f"PLAN: {soap.get('plan', '')}"
    )
    codes = await llm_client.extract_medical_codes(clinical_text=full_note_text)

    # Step 3: Build FHIR Bundle
    bundle = fhir_builder.build_fhir_bundle(
        soap_note=soap,
        codes=codes,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
    )

    # Summary stats
    num_conditions = len(codes.get("icd10_codes", []))
    num_entries = len(bundle.get("entry", []))

    return {
        "fhir_bundle": bundle,
        "summary": {
            "total_resources": num_entries,
            "encounters": 1,
            "document_references": 1,
            "conditions": num_conditions,
            "icd10_codes_used": [c["code"] + " — " + c["display"] for c in codes.get("icd10_codes", [])],
            "cpt_codes_suggested": [c["code"] + " — " + c["display"] for c in codes.get("cpt_codes", [])],
        },
        "disclaimer": (
            "AI-generated FHIR Bundle. All resources are marked as "
            "'ai-generated' and Conditions are set to 'provisional' status. "
            "Must be reviewed by a clinician before writing to an EHR."
        ),
    }
