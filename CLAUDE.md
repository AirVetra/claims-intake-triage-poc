# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Insurance Underwriting & Claims Triage — a training POC that extracts claim fields
and flags cases requiring human review. Given a case's input text, it:
- extracts 8 mandatory fields (name, policy, dates, loss, contact, documents);
- flags cases with missing data or high-value claims (loss > $100,000);
- provides privacy-minimized audit trail for governance.

## Hard constraints

- Python 3.11+.
- Synthetic data only — never use or request real personal/customer data.
- API key stored locally in `.env` (not committed); never logged or printed.
- No RAG, no vector database, no access controls or encryption (POC only).
- Extraction: Claude Haiku 4.5 with Structured Outputs (facts only).
- Triage decisions: deterministic rule-based (no LLM reasoning for decisions).

## Workflow

For every non-trivial task, follow this sequence explicitly:
1. Explore the relevant existing code/data first.
2. Propose a short plan.
3. Implement.
4. Verify (run it, check outputs against expectations).
5. Review the `git diff` before considering the task done.

## Extraction & Triage Logic

**Extraction (Claude Haiku 4.5 via Structured Outputs):**
- Extracts 8 mandatory fields from unstructured claim text
- Returns facts only; no decisions, no routing, no reasoning
- All extracted fields validated against fixed schema before use
- Input hashed (SHA-256); never logged raw

**Triage (Deterministic, post-extraction):**
- Validates mandatory fields present (flags missing data)
- Calculates high-value flag if loss > $100,000 (deterministic rule)
- Flags all cases for explicit human review (no auto-decisions)

**Audit Trail (Privacy-minimized):**
- Per-run record with metadata, field-presence status (not raw values)
- Loss bucketed as category (zero, 1-100k, over-100k, missing)
- No raw PII persisted; input hashed only
- For governance and traceability, not legal compliance

## Status

**POC complete.** Ready for demonstration with synthetic data. Production deployment requires:
- Append-only audit storage with tamper-evidence
- Access control logging and user authentication
- Encryption at rest and in transit
- Compliance review (legal, privacy, jurisdiction-specific)
