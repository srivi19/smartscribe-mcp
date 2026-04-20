# SmartScribe — AI Clinical Note Generator & FHIR Writer

**An MCP Server for the Agents Assemble Healthcare AI Hackathon**

SmartScribe transforms messy clinician-patient conversation transcripts or bullet-point notes into properly structured, coded clinical documentation — complete with ICD-10, SNOMED CT, and CPT codes. It outputs FHIR-compliant resources ready to write to any EHR.

## Tools Exposed

| Tool | Description |
|------|-------------|
| `generate_note` | Convert raw transcript or bullet points into a structured SOAP note |
| `extract_codes` | Auto-detect and suggest ICD-10, SNOMED CT, and CPT codes from clinical text |
| `to_fhir_bundle` | Convert a structured clinical note into a FHIR R4 Bundle (Encounter, Condition, Observation resources) |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Test the tools
python test_tools.py

# 4. Run the MCP server
python server.py
```

Server starts at `http://localhost:8000/mcp`

## Project Structure

```
smartscribe-mcp/
├── server.py              # MCP server entry point
├── tools/
│   ├── generate_note.py   # Transcript → SOAP note
│   ├── extract_codes.py   # Clinical text → medical codes
│   └── to_fhir_bundle.py  # Structured note → FHIR R4 Bundle
├── services/
│   ├── llm_client.py      # Anthropic Claude API wrapper
│   └── fhir_builder.py    # FHIR R4 resource builder
├── models/
│   └── schemas.py         # Pydantic models
├── synthetic_data/
│   └── sample_transcripts.json  # Synthetic transcripts for testing
├── requirements.txt
├── Dockerfile
└── README.md
```

## Why SmartScribe?

- **The #1 problem in healthcare today:** Clinicians spend 2 hours on documentation for every 1 hour with patients
- **Pure AI play:** Converting unstructured natural language to structured medical output is impossible without GenAI
- **Universal composability:** Almost every clinical workflow ends with documentation — other agents on Prompt Opinion can call SmartScribe as their final step
- **Instant demo impact:** Messy transcript in → polished SOAP note out. Judges get it in 5 seconds.

## License

MIT
