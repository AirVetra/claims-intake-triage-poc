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
- **Processing:** Claude Haiku 4.5 extracts 8 mandatory fields using Structured Outputs
- **Validation:** Missing mandatory fields are flagged; high-value flag (>$100,000) calculated deterministically
- **Output:** Terminal summary showing extracted facts and human-review status
- **Cost:** Lowest-cost model supporting Structured Outputs ($1.00/$5.00 per 1M tokens)

## Files

- `triage.py` — Main application
- `schemas.py` — JSON schema and field definitions
- `synthetic_cases.json` — 6 test cases (complete, incomplete, high-value, boundary, zero-loss, missing-loss)
- `requirements.txt` — Python dependencies
- `.env.example` — Template for credentials (copy to `.env`)
- `.gitignore` — Excludes `.env` from Git

## Synthetic Test Cases

1. **case_001:** Complete intake, $25,000 loss — all fields present
2. **case_002:** Incomplete intake with missing policy, loss, documents
3. **case_003:** High-value claim, $500,000 loss — triggers human review flag
4. **case_004:** Boundary case, exactly $100,000 loss — no high-value flag (threshold is >$100,000)
5. **case_005:** Zero-loss case, $0 — no high-value flag
6. **case_006:** Missing loss case — 1 mandatory field missing

## Key Constraints

- Synthetic data only (no real personal information)
- No API key in Git (`.env` is ignored)
- Transparent Structured Outputs validation
- Deterministic missing-field check
- No coverage, liability, fraud, or payment decisions
