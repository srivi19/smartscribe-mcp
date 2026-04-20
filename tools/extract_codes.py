"""
extract_codes tool — Auto-detect and suggest ICD-10, SNOMED CT,
and CPT codes from clinical text.
"""

from services import llm_client


async def extract_codes(
    clinical_text: str,
) -> dict:
    """
    Extract medical codes (ICD-10, SNOMED CT, CPT) from any clinical text.

    Accepts a SOAP note, transcript, clinical summary, or any medical text.
    Returns suggested codes with confidence levels and the context that
    supports each code.

    Args:
        clinical_text: Any clinical text to extract codes from.

    Returns:
        Dict with icd10_codes, snomed_codes, cpt_codes lists and summary.
    """
    codes = await llm_client.extract_medical_codes(
        clinical_text=clinical_text,
    )

    # Count totals for summary
    total = (
        len(codes.get("icd10_codes", []))
        + len(codes.get("snomed_codes", []))
        + len(codes.get("cpt_codes", []))
    )

    return {
        "total_codes_found": total,
        "icd10_codes": codes.get("icd10_codes", []),
        "snomed_codes": codes.get("snomed_codes", []),
        "cpt_codes": codes.get("cpt_codes", []),
        "note_summary": codes.get("note_summary", ""),
        "disclaimer": (
            "AI-suggested medical codes. These are recommendations only "
            "and must be verified by a certified medical coder before use "
            "in billing or clinical documentation."
        ),
    }
