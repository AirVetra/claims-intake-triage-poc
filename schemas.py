from dataclasses import dataclass
from typing import Optional

@dataclass
class ClaimRecord:
    claimant_name: Optional[str]
    policy_number: Optional[str]
    incident_date: Optional[str]
    incident_type: Optional[str]
    incident_description: Optional[str]
    estimated_loss: Optional[float]
    contact_details: Optional[str]
    available_documents: Optional[str]
    high_value_flag: Optional[bool]

CLAIM_SCHEMA = {
    "type": "object",
    "properties": {
        "claimant_name": {"type": ["string", "null"]},
        "policy_number": {"type": ["string", "null"]},
        "incident_date": {"type": ["string", "null"]},
        "incident_type": {"type": ["string", "null"]},
        "incident_description": {"type": ["string", "null"]},
        "estimated_loss": {"type": ["number", "null"]},
        "contact_details": {"type": ["string", "null"]},
        "available_documents": {"type": ["string", "null"]},
        "high_value_flag": {"type": ["boolean", "null"]}
    },
    "required": [
        "claimant_name",
        "policy_number",
        "incident_date",
        "incident_type",
        "incident_description",
        "estimated_loss",
        "contact_details",
        "available_documents",
        "high_value_flag"
    ],
    "additionalProperties": False
}

MANDATORY_FIELDS = [
    "claimant_name",
    "policy_number",
    "incident_date",
    "incident_type",
    "incident_description",
    "estimated_loss",
    "contact_details",
    "available_documents"
]
