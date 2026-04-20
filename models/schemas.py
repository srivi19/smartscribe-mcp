"""
Pydantic models for SmartScribe tool inputs and outputs.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────────────
# Input models
# ──────────────────────────────────────────────

class PatientContext(BaseModel):
    """SHARP-propagated patient context from the Prompt Opinion platform."""
    patient_id: Optional[str] = Field(None, description="FHIR Patient resource ID")
    fhir_token: Optional[str] = Field(None, description="OAuth bearer token for FHIR server")
    fhir_base_url: Optional[str] = Field(None, description="Base URL of the FHIR server")


# ──────────────────────────────────────────────
# Output models
# ──────────────────────────────────────────────

class SOAPNote(BaseModel):
    """A structured SOAP clinical note."""
    subjective: str = Field(description="Patient's reported symptoms, history, chief complaint")
    objective: str = Field(description="Clinician observations, vitals, exam findings")
    assessment: str = Field(description="Clinical assessment, differential diagnoses")
    plan: str = Field(description="Treatment plan, follow-up, referrals")


class MedicalCode(BaseModel):
    """A single medical code suggestion."""
    code: str = Field(description="The code value (e.g. 'J06.9')")
    system: str = Field(description="Code system: 'ICD-10', 'SNOMED-CT', or 'CPT'")
    display: str = Field(description="Human-readable description")
    confidence: str = Field(description="'high', 'medium', or 'low'")
    context: str = Field(description="Which part of the note this code relates to")


class CodeExtractionResult(BaseModel):
    """Result of medical code extraction."""
    icd10_codes: list[MedicalCode] = []
    snomed_codes: list[MedicalCode] = []
    cpt_codes: list[MedicalCode] = []
    note_summary: str = Field(default="", description="Brief summary of what was coded")


class FHIRResource(BaseModel):
    """A single FHIR resource in a bundle."""
    resource_type: str
    resource: dict
