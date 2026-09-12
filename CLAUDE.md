# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Insurance Underwriting & Claims Triage — a training POC that performs a transparent,
rule-based first-pass triage of a synthetic insurance case. Given a case's input
fields, it:
- classifies the case as low, medium, or high risk;
- explains the decision in terms of the explicit input fields and rules that fired;
- flags missing information and cases that require human review.

## Hard constraints

- Python 3.11+.
- Synthetic data only — never use or request real personal/customer data.
- No API keys, no external services, no network calls.
- No RAG, no vector database, no LLM/ML inference in this first version — the
  triage logic is deterministic and rule-based.

## Workflow

For every non-trivial task, follow this sequence explicitly:
1. Explore the relevant existing code/data first.
2. Propose a short plan.
3. Implement.
4. Verify (run it, check outputs against expectations).
5. Review the `git diff` before considering the task done.

## Stage 2: AI-Assisted Extraction (Experimental)

For the Stage 2 POC only, Claude API (Anthropic, `claude-sonnet-5`) may be used to:
- Extract structured claim fields from unstructured intake text using Structured Outputs
- Return extracted facts only; may optionally draft follow-up messages

Guardrails (non-negotiable):
- Claude extracts facts only; does not make coverage, liability, fraud, payment, or routing decisions
- All extracted fields validated against fixed schema before use
- Deterministic missing-field validation applied after extraction
- No real personal data in API prompts or logs
- API key stored locally in `.env` (not committed); never logged or printed
- Every output flagged for explicit human review
- Results compared quantitatively against a deterministic baseline (Stage 1)

The deterministic baseline (Stage 1) is the reference system; Stage 2 is a demonstration of AI-assisted extraction quality for research purposes only.

## Status

No build tooling or tests exist yet. Commands will be added as the project scaffolding grows.
