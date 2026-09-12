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

## Status

No code, build tooling, or tests exist yet — this file will gain a "Commands"
section (run/test/lint) once the project scaffold is created. Do not invent
commands or infrastructure ahead of that.
