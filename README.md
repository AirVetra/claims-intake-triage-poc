# Insurance Underwriting & Claims Triage POC

A minimal, transparent demonstration of AI-assisted claims intake using Claude API with Structured Outputs.

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
   python triage.py
   ```

## How It Works

- **Input:** Synthetic claim intake text (email, call notes)
- **Processing:** Claude API extracts 8 mandatory fields using Structured Outputs
- **Validation:** Missing mandatory fields are flagged
- **Output:** Terminal summary showing extracted facts and human-review status

## Files

- `triage.py` — Main application
- `schemas.py` — JSON schema and field definitions
- `synthetic_cases.json` — 3 test cases (complete, incomplete, high-value)
- `requirements.txt` — Python dependencies
- `.env.example` — Template for credentials (copy to `.env`)
- `.gitignore` — Excludes `.env` from Git

## Synthetic Test Cases

1. **case_001:** Complete intake with all fields present
2. **case_002:** Incomplete intake with missing policy number and loss amount
3. **case_003:** High-value claim with complete information

## Key Constraints

- Synthetic data only (no real personal information)
- No API key in Git (`.env` is ignored)
- Transparent Structured Outputs validation
- Deterministic missing-field check
- No coverage, liability, fraud, or payment decisions
