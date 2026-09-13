# Insurance Underwriting & Claims Triage POC

## Purpose

Synthetic-claims extraction POC with deterministic review flags. Extracts structured claim fields from unstructured intake text and flags cases requiring human review based on completeness and estimated loss thresholds.

## Architecture

- **Extraction:** Claude Haiku 4.5 extracts 8 mandatory fields (claimant name, policy number, incident date/type/description, estimated loss, contact details, available documents) using Structured Outputs.
- **Derivation:** Python deterministically calculates `high_value_flag` (true if loss > $100,000; false/null otherwise) — Claude does not participate in this decision.
- **Review:** All cases flagged for human review if any mandatory field is missing or loss exceeds $100,000.
- **Audit Trail:** Privacy-minimized per-run records saved to `audit_traces/` (metadata, field-presence status, bucketed loss, derived outcomes).

## Quick Start

Complete local setup and verified run path:

1. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create local `.env` file:**
   ```bash
   cp .env.example .env
   ```

5. **Add your Anthropic API key (local only, do not commit):**
   ```bash
   # Edit .env and add:
   # ANTHROPIC_API_KEY=sk-proj-your-key-here
   ```

6. **Run the triage:**
   ```bash
   python3 triage.py
   ```

## Pre-flight Check

Before running, verify:
- **`.env` exists locally** with your API key set (never commit this file)
- **Virtual environment is active** (you should see `(.venv)` in your prompt)
- **All 6 synthetic cases run successfully** (`python3 triage.py` completes without errors)
- **Audit traces created** in `audit_traces/` directory with no errors or warnings
- **No API key printed or logged** anywhere in terminal output or trace files

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

## Real Claims (Production Limitation)

**This POC accepts only `synthetic_cases.json`.**

Do NOT use this system to ingest real claims:
- Do not put real personal data or PII into local JSON files
- Do not persist real claims in audit traces
- Local traces are not encrypted, access-controlled, or retention-managed
- This is a demonstration system, not a production claims handler

**Production ingestion requires:**
- An approved secure channel (e.g., authenticated API, signed uploads, secure queue)
- Access controls and user authentication
- Data retention policy and automated redaction
- Encryption at rest and in transit
- Privacy and compliance review (jurisdiction-specific)

**Future interface (not implemented):**
- Validated input adapter or CLI with schema enforcement
- PII handled outside local logs (hashed at intake, tokenized in storage)
- Separate secure storage for raw claims (not in audit traces)

For now: development and testing only with synthetic data.

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
