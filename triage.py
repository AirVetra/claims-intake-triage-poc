#!/usr/bin/env python3
"""
Minimal Claims Intake Triage POC.
Synthetic claim text → Claude Structured Output → missing-field check → terminal summary.
"""
import json
import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
from schemas import CLAIM_SCHEMA, MANDATORY_FIELDS

# Load .env from current directory (not committed to repo)
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in .env")
    print("Create .env with: ANTHROPIC_API_KEY=sk-proj-your-key")
    sys.exit(1)

client = Anthropic(api_key=api_key)
MODEL = "claude-sonnet-5"


def extract_claim(text):
    """Extract structured claim fields using Claude Structured Outputs."""
    system_prompt = """You are an insurance claims intake specialist. Extract structured information
from unstructured claim text. If a field is not present or unclear, set it to null.
For estimated_loss, extract only the numeric value (no currency symbol). Respond in JSON."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract claim information from this text:\n\n{text}"
                }
            ],
            output_config={
                "type": "json_schema",
                "json_schema": {
                    "name": "ClaimRecord",
                    "schema": CLAIM_SCHEMA,
                    "strict": True
                }
            }
        )
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")

    try:
        extracted = json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError, KeyError, AttributeError) as e:
        raise RuntimeError(f"Failed to parse API response as JSON: {e}")

    return extracted


def check_missing_fields(extracted):
    """Identify missing mandatory fields."""
    missing = []
    for field in MANDATORY_FIELDS:
        value = extracted.get(field)
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            missing.append(field)
    return missing


def print_summary(case_id, extracted, missing):
    """Print terminal summary of extracted claim and review status."""
    print(f"\n{'='*70}")
    print(f"Case ID: {case_id}")
    print(f"{'='*70}")

    print("\nExtracted Fields:")
    for field in MANDATORY_FIELDS:
        value = extracted.get(field)
        status = "✓" if field not in missing else "✗ MISSING"
        display_value = value if value is not None else "(null)"
        print(f"  {field:.<40} {display_value} {status}")

    print(f"\nMissing Fields: {len(missing)}")
    if missing:
        for field in missing:
            print(f"  - {field}")
        print(f"\n🚨 HUMAN REVIEW REQUIRED: {len(missing)} mandatory field(s) missing")
    else:
        print(f"\n✅ ALL MANDATORY FIELDS PRESENT: Ready for processing")

    print()


def main():
    """Process synthetic cases through triage."""
    # Resolve synthetic_cases.json relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cases_path = os.path.join(script_dir, "synthetic_cases.json")

    try:
        with open(cases_path) as f:
            cases = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: synthetic_cases.json not found at {cases_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: synthetic_cases.json is not valid JSON: {e}")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"Claims Intake Triage POC")
    print(f"Model: {MODEL}")
    print(f"Processing {len(cases)} synthetic case(s)...")
    print(f"{'='*70}")

    for case in cases:
        case_id = case["case_id"]
        input_text = case["input_text"]

        try:
            # Extract using Claude Structured Outputs
            extracted = extract_claim(input_text)

            # Check for missing mandatory fields
            missing = check_missing_fields(extracted)

            # Print summary
            print_summary(case_id, extracted, missing)

        except Exception as e:
            print(f"\n❌ Error processing {case_id}: {e}")
            sys.exit(1)

    print(f"{'='*70}")
    print("Triage complete.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
