#!/usr/bin/env python3
"""
Minimal Claims Intake Triage POC.
Synthetic claim text → Claude Structured Output → missing-field check → terminal summary.
Captures privacy-minimized audit trails for governance and model comparison.
"""
import json
import os
import sys
import subprocess
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from schemas import CLAIM_SCHEMA, MANDATORY_FIELDS
from audit_trail import AuditTrail

# Load .env from current directory (not committed to repo)
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in .env")
    print("Create .env with: ANTHROPIC_API_KEY=sk-proj-your-key")
    sys.exit(1)

client = Anthropic(api_key=api_key)
MODEL = "claude-haiku-4-5"
APP_VERSION = "0.1.0"
PROMPT_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
THRESHOLD_VERSION = "1.0"


def get_git_commit():
    """Get current git commit hash."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__)).decode().strip()[:7]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def extract_claim(text):
    """Extract structured claim fields using Claude Structured Outputs.
    Returns (extracted_dict, api_metadata_dict)."""
    system_prompt = """You are an insurance claims intake specialist. Extract structured information
from unstructured claim text. If a field is not present or unclear, set it to null.
For estimated_loss, extract only the numeric value (no currency symbol). Respond in JSON."""

    start_time = time.time()
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
                "format": {
                    "type": "json_schema",
                    "schema": CLAIM_SCHEMA
                }
            }
        )
    except Exception as e:
        raise RuntimeError(f"API call failed: {e}")

    latency_ms = int((time.time() - start_time) * 1000)
    input_tokens = response.usage.input_tokens if hasattr(response, "usage") else None
    output_tokens = response.usage.output_tokens if hasattr(response, "usage") else None

    try:
        extracted = json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError, KeyError, AttributeError) as e:
        raise RuntimeError(f"Failed to parse API response as JSON: {e}")

    # Deterministic high_value_flag: true only if loss > 100000
    if extracted.get("estimated_loss") is not None:
        extracted["high_value_flag"] = extracted["estimated_loss"] > 100000
    else:
        extracted["high_value_flag"] = None

    api_metadata = {
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    return extracted, api_metadata


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
        print(f"\n✅ All mandatory fields present — human review required.")

    if extracted.get("high_value_flag"):
        print(f"\n💰 High-value claim — human review required.")

    print()


def main():
    """Process synthetic cases through triage."""
    # Resolve synthetic_cases.json relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cases_path = os.path.join(script_dir, "synthetic_cases.json")
    git_commit = get_git_commit()

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
    print(f"Git commit: {git_commit}")
    print(f"Processing {len(cases)} synthetic case(s)...")
    print(f"Audit traces (privacy-minimized): audit_traces/")
    print(f"{'='*70}")

    for case in cases:
        case_id = case["case_id"]
        input_text = case["input_text"]

        # Initialize audit trail
        audit = AuditTrail(
            case_id=case_id,
            git_commit=git_commit,
            app_version=APP_VERSION,
            model_id=MODEL,
            prompt_version=PROMPT_VERSION,
            schema_version=SCHEMA_VERSION,
            input_text=input_text,
        )

        try:
            # Extract using Claude Structured Outputs
            extracted, api_metadata = extract_claim(input_text)
            audit.record_extraction(
                extracted=extracted,
                latency_ms=api_metadata["latency_ms"],
                input_tokens=api_metadata["input_tokens"],
                output_tokens=api_metadata["output_tokens"],
            )

            # Check for missing mandatory fields
            missing = check_missing_fields(extracted)
            audit.record_validation(missing_fields=missing)

            # Record deterministic derivation
            high_value_flag = extracted.get("high_value_flag")
            audit.record_derivation(
                high_value_flag=high_value_flag,
                threshold_version=THRESHOLD_VERSION,
            )

            # Set monitoring tags
            audit.record_monitoring_tags(
                cohort="synthetic_poc",
                experiment_id=None,
                model_variant="haiku-baseline",
            )

            # Save audit trail (privacy-minimized)
            trace_path = audit.save()

            # Print summary
            print_summary(case_id, extracted, missing)
            print(f"  Trace: {audit.trace_id}\n")

        except Exception as e:
            audit.record_extraction_error(
                error_category="api_error" if "API" in str(e) else "parsing_error",
            )
            audit.save()
            print(f"\n❌ Error processing {case_id}: {e}")
            sys.exit(1)

    print(f"{'='*70}")
    print("Triage complete.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
