#!/usr/bin/env python3
"""Validate a Read Me First Chain scaffold response.

Usage:
  python3 scripts/validate_scaffold_response.py response.md
  cat response.md | python3 scripts/validate_scaffold_response.py
  python3 scripts/validate_scaffold_response.py response.md --json

Position-aware by design. Greetings are only errors at the head of the response.
Closing offers are only errors in the tail of Current Field. Fenced code blocks
and blockquotes are masked before pattern matching so that quoted, illustrative,
or code content cannot produce false failures.

Structural drift is caught deterministically. Semantic sufficiency is not, and is
never claimed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_HEADERS = ["Presence", "Context", "Capabilities", "Current Field"]
HEADER_RE = re.compile(r"^####\s+(.+?)\s*$", re.MULTILINE)

GREETING_RE = re.compile(r"^\s*(hi|hello|hey|dear|greetings|good\s+(morning|afternoon|evening))\b", re.IGNORECASE)
PREFACE_RE = re.compile(
    r"^\s*(before i answer|here is|here's|based on your request|i will explain|let me|i'll start by|to begin)\b",
    re.IGNORECASE | re.MULTILINE,
)
NARRATION_RE = re.compile(
    r"^\s*(i am applying|i'm applying|i will use|my approach|my process|i'm going to)\b",
    re.IGNORECASE | re.MULTILINE,
)
OFFER_RE = re.compile(
    r"\b(let me know|just let me know|if you want me to|if you'd like me to|i can also|would you like|shall i|do you want)\b",
    re.IGNORECASE,
)
TAIL_QUESTION_RE = re.compile(r"\?\s*$")


def mask_noncontent(text: str) -> str:
    """Blank out fenced code blocks and blockquotes, preserving line offsets."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        if fenced or line.lstrip().startswith(">"):
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def split_fields(text: str) -> tuple[list[tuple[str, int, int]], str]:
    """Return [(name, body_start, body_end)] and the preamble before the first header."""
    matches = list(HEADER_RE.finditer(text))
    if not matches:
        return [], text
    preamble = text[: matches[0].start()]
    fields = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        fields.append((m.group(1), m.end(), end))
    return fields, preamble


def validate(text: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    raw = text.replace("\r\n", "\n")

    if not raw.strip():
        return {"valid": False, "errors": ["response is empty"], "warnings": []}

    masked = mask_noncontent(raw)
    fields, preamble = split_fields(masked)
    names = [name for name, _, _ in fields]

    for required in REQUIRED_HEADERS:
        count = names.count(required)
        if count == 0:
            errors.append(f"missing required header: #### {required}")
        elif count > 1:
            errors.append(f"repeated required header: #### {required}")

    extra = [n for n in names if n not in REQUIRED_HEADERS]
    if extra:
        errors.append(f"extra level-4 headers present: {extra}")

    if names and [n for n in names if n in REQUIRED_HEADERS] != REQUIRED_HEADERS:
        errors.append("required headers are not in the canonical order")

    if preamble.strip():
        errors.append("text appears before #### Presence")
        if GREETING_RE.search(preamble):
            errors.append("response opens with a greeting")

    bodies = {name: masked[start:end] for name, start, end in fields}

    presence = bodies.get("Presence", "")
    if presence.strip() and GREETING_RE.search(presence):
        errors.append("greeting detected in Presence")

    for name in ("Presence", "Context", "Capabilities"):
        body = bodies.get(name, "")
        if PREFACE_RE.search(body) or NARRATION_RE.search(body):
            errors.append(f"process narration or preface detected in {name}")
        if not body.strip():
            errors.append(f"{name} is empty")

    context = bodies.get("Context", "").strip()
    if context:
        sentences = len([s for s in re.split(r"[.!]\s", context) if s.strip()])
        if sentences > 1:
            warnings.append("Context may contain more than one sentence")

    current = bodies.get("Current Field", "")
    if not current.strip():
        errors.append("Current Field is empty")
    else:
        lines = [ln for ln in current.strip().split("\n") if ln.strip()]
        tail = "\n".join(lines[-3:])
        if OFFER_RE.search(tail):
            errors.append("Current Field ends with a closing offer")
        if TAIL_QUESTION_RE.search(tail.strip()):
            errors.append("Current Field ends with a question")
        head = lines[0] if lines else ""
        if PREFACE_RE.match(head):
            errors.append("Current Field opens with a prefatory clause")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    p = argparse.ArgumentParser(description="Validate a Read Me First Chain scaffold response.")
    p.add_argument("path", nargs="?", help="path to a response file; stdin used when omitted")
    p.add_argument("--json", action="store_true", help="print machine-readable json")
    a = p.parse_args()

    text = Path(a.path).read_text(encoding="utf-8") if a.path else sys.stdin.read()
    result = validate(text)

    if a.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for e in result["errors"]:
            print(f"error: {e}")
        for w in result["warnings"]:
            print(f"warning: {w}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
