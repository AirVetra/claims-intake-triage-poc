# Insurance Underwriting & Claims Triage POC

## Purpose

Synthetic-claims extraction POC with deterministic review flags. Extracts structured claim fields from unstructured intake text and flags cases requiring human review based on completeness and estimated loss thresholds.

## Architecture

- **Extraction:** Claude Haiku 4.5 extracts 8 mandatory fields (claimant name, policy number, incident date/type/description, estimated loss, contact details, available documents) using Structured Outputs.
- **Derivation:** Python deterministically calculates `high_value_flag` (true if loss > $100,000; false/null otherwise) — Claude does not participate in this decision.
- **Review:** All cases flagged for human review if any mandatory field is missing or loss exceeds $100,000.
- **Audit Trail:** Privacy-minimized per-run records saved to `audit_traces/` (metadata, field-presence status, bucketed loss, derived outcomes).

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` (local, not committed):**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key:
   # ANTHROPIC_API_KEY=sk-proj-...
   ```

3. **Run the triage:**
   ```bash
   python3 triage.py
   ```

## Verification

Six synthetic test cases cover:
- **case_001:** Complete intake, $25,000 loss
- **case_002:** Incomplete (missing policy, loss, documents)
- **case_003:** High-value claim, $500,000 loss (triggers flag)
- **case_004:** Boundary case, exactly $100,000 (no flag; threshold is >$100,000)
- **case_005:** Zero-loss case, $0 (no flag)
- **case_006:** Missing loss field only (1 missing mandatory field)

## Audit Traces

Each run saves per-run audit records to `audit_traces/{trace_id}.json`:
- **Metadata:** Trace ID, case ID, timestamp, git commit, app version, model version
- **Field presence:** Status of each extracted field (present/missing/null) — not raw values
- **Loss bucketed:** Estimated loss stored as category (`zero`, `1_to_100k`, `over_100k`, `missing`) — not amount
- **Derived outcomes:** High-value flag, threshold version, missing field count, human review required
- **API metrics:** Model latency (ms), token usage (input/output)

## Privacy & Limitations

**Privacy (Current):**
- No raw PII stored in audit traces (names, policy numbers, contact details, incident descriptions excluded)
- Input text hashed (SHA-256) but never persisted
- Estimated loss bucketed, not stored as exact amount
- Synthetic data only; real personal data never used in this POC

**Limitations (Not Production-Ready):**
- Audit traces are local JSON files: not immutable, not tamper-evident, not access-controlled
- This is an EU AI Act-inspired auditability pattern demonstration, not legal compliance
- Production deployment would require: append-only database, cryptographic signing, retention enforcement, access logging

**Credentials:**
- API key must be stored locally in `.env` (not committed to Git)
- `.env` is in `.gitignore`; never expose or share your key

## Files

- `triage.py` — Main application
- `audit_trail.py` — Privacy-minimized audit trail module
- `schemas.py` — JSON schema and field definitions
- `synthetic_cases.json` — 6 test cases
- `requirements.txt` — Python dependencies
- `.env.example` — Template for credentials (copy to `.env`, add your key)
- `.gitignore` — Excludes `.env` and `audit_traces/`
