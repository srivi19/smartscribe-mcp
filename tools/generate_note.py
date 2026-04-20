"""
generate_note tool — Transform raw clinical transcript or bullet points
into a structured SOAP note.
"""

from services import llm_client


async def generate_note(
    transcript: str,
    note_type: str = "general",
    patient_age: int | None = None,
    patient_sex: str | None = None,
) -> dict:
    """
    Convert a raw clinician-patient transcript or bullet-point notes
    into a structured SOAP clinical note.

    Args:
        transcript: Raw encounter text — can be a conversation transcript,
                    bullet points, or rough notes.
        note_type: Clinical specialty context.
        patient_age: Patient age in years (for clinical context).
        patient_sex: Patient sex (for clinical context).

    Returns:
        Dict with subjective, objective, assessment, plan, and metadata.
    """
    soap = await llm_client.generate_soap_note(
        transcript=transcript,
        note_type=note_type,
        patient_age=patient_age,
        patient_sex=patient_sex,
    )

    return {
        "note_type": note_type,
        "patient_demographics": {
            "age": patient_age,
            "sex": patient_sex,
        },
        "soap_note": {
            "subjective": soap.get("subjective", "Not documented."),
            "objective": soap.get("objective", "Not documented."),
            "assessment": soap.get("assessment", "Not documented."),
            "plan": soap.get("plan", "Not documented."),
        },
        "disclaimer": (
            "AI-generated clinical note. Must be reviewed and verified by "
            "a licensed clinician before use in patient care. Generated using "
            "synthetic data for demonstration purposes."
        ),
    }
