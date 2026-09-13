"""
Privacy-minimized audit trail for immutable per-run records.
Captures trace metadata, model execution, field presence (not values), and governance.
No raw PII is persisted.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from schemas import MANDATORY_FIELDS

COMPLIANCE_LABEL = "Synthetic-data POC — EU AI Act-inspired auditability pattern, not legal compliance."


def generate_trace_id():
    """Generate a unique trace ID."""
    return f"tr_{uuid.uuid4().hex[:12]}"


def hash_input(text):
    """Hash input text using SHA-256 (PII-safe)."""
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"


def bucket_loss(estimated_loss):
    """Bucket estimated loss for privacy: zero, 1_to_100k, over_100k, missing."""
    if estimated_loss is None:
        return "missing"
    if estimated_loss == 0:
        return "zero"
    if estimated_loss <= 100000:
        return "1_to_100k"
    return "over_100k"


def field_presence_status(value):
    """Determine field presence status: present, missing, null."""
    if value is None:
        return "null"
    if value == "" or (isinstance(value, str) and value.strip() == ""):
        return "missing"
    return "present"


class AuditTrail:
    """Privacy-minimized per-run audit record (no raw PII persisted)."""

    def __init__(
        self,
        case_id,
        git_commit,
        app_version,
        model_id,
        prompt_version,
        schema_version,
        input_text,
        source_type="synthetic_cases.json",
    ):
        self.trace_id = generate_trace_id()
        self.case_id = case_id
        self.created_at_utc = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.git_commit = git_commit
        self.app_version = app_version
        self.model_id = model_id
        self.prompt_version = prompt_version
        self.schema_version = schema_version
        self.input_hash = hash_input(input_text)
        self.source_type = source_type

        # Execution data (filled during processing)
        self.latency_ms = None
        self.input_tokens = None
        self.output_tokens = None
        self.outcome = None
        self.error_category = None
        self.extraction_presence = None
        self.estimated_loss_bucket = None
        self.high_value_flag = None
        self.threshold_version = None
        self.missing_fields = None
        self.reviewer_reference = None
        self.review_decision = None
        self.reviewed_at_utc = None
        self.review_notes = None
        self.cohort = "synthetic_poc"
        self.experiment_id = None
        self.model_variant = None

    def record_extraction(self, extracted, latency_ms, input_tokens, output_tokens):
        """Record extraction result (presence/status only, no raw values)."""
        self.latency_ms = latency_ms
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.outcome = "success"
        self.error_category = None

        # Build presence map (no raw PII stored)
        self.extraction_presence = {}
        for field in MANDATORY_FIELDS:
            value = extracted.get(field)
            if field == "estimated_loss":
                # Special: bucket the value, don't store it
                self.estimated_loss_bucket = bucket_loss(value)
                self.extraction_presence[field] = "bucketed"
            else:
                # All other fields: presence status only
                self.extraction_presence[field] = field_presence_status(value)

    def record_extraction_error(self, error_category, error_message=None):
        """Record extraction failure."""
        self.outcome = "error"
        self.error_category = error_category

    def record_derivation(self, high_value_flag, threshold_version="1.0"):
        """Record deterministic derived fields."""
        self.high_value_flag = high_value_flag
        self.threshold_version = threshold_version

    def record_validation(self, missing_fields):
        """Record validation result."""
        self.missing_fields = missing_fields

    def record_human_review(self, reviewer_reference, decision, notes=""):
        """Record human review outcome."""
        self.reviewer_reference = reviewer_reference
        self.review_decision = decision
        self.reviewed_at_utc = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.review_notes = notes

    def record_monitoring_tags(self, cohort="production", experiment_id=None, model_variant=None):
        """Record monitoring tags for model comparison."""
        self.cohort = cohort
        self.experiment_id = experiment_id
        self.model_variant = model_variant

    def to_dict(self):
        """Serialize to audit record dictionary (privacy-minimized)."""
        record = {
            "trace": {
                "trace_id": self.trace_id,
                "case_id": self.case_id,
                "created_at_utc": self.created_at_utc,
                "git_commit": self.git_commit,
                "app_version": self.app_version,
            },
            "compliance": COMPLIANCE_LABEL,
            "input": {
                "input_hash": self.input_hash,
                "source_type": self.source_type,
            },
            "model_execution": {
                "model_id": self.model_id,
                "prompt_version": self.prompt_version,
                "schema_version": self.schema_version,
                "latency_ms": self.latency_ms,
                "token_usage": {
                    "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens,
                } if self.input_tokens is not None else None,
                "outcome": self.outcome,
                "error_category": self.error_category,
            },
            "extraction_presence": self.extraction_presence,
            "estimated_loss_bucket": self.estimated_loss_bucket,
            "derivation": {
                "threshold_version": self.threshold_version,
                "high_value_flag": self.high_value_flag,
            },
            "validation": {
                "missing_fields": self.missing_fields or [],
                "human_review_required": len(self.missing_fields or []) > 0 or self.high_value_flag,
            },
            "human_review": None,
            "governance": {
                "retention_policy_version": "1.0",
                "redaction_status": "pii_excluded_and_loss_bucketed",
            },
            "monitoring_tags": {
                "cohort": self.cohort,
                "experiment_id": self.experiment_id,
                "model_variant": self.model_variant,
            },
        }

        if self.reviewer_reference:
            record["human_review"] = {
                "reviewer_reference": self.reviewer_reference,
                "decision": self.review_decision,
                "reviewed_at_utc": self.reviewed_at_utc,
                "notes": self.review_notes,
            }

        return record

    def to_json(self):
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def save(self, output_dir="audit_traces"):
        """Save a per-run audit record to a local JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{self.trace_id}.json")
        with open(filepath, "w") as f:
            f.write(self.to_json())
        return filepath
