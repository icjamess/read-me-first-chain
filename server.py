"""read-me-first-chain — remote MCP connector for Claude.

Serves the Read Me First Chain presentation contract over MCP:
the canonical System Directive (verbatim, sha256-checked at startup),
the full skill contract, a four-part renderer, and the position-aware
validator from scripts/validate_scaffold_response.py (imported unmodified).

Streamable HTTP, stateless, authless. Serves at /mcp.
"""
import hashlib
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from validate_scaffold_response import REQUIRED_HEADERS, validate

HERE = Path(__file__).resolve().parent
CANONICAL_SHA256 = "c50ac0cd05f186fe356f74d4227997e52c3a2be79621992cf49bb8b21abd6465"

_directive_bytes = (HERE / "system-prompt.md").read_bytes()
DIRECTIVE_SHA256 = hashlib.sha256(_directive_bytes).hexdigest()
if DIRECTIVE_SHA256 != CANONICAL_SHA256:
    raise SystemExit(
        f"system-prompt.md is not the canonical directive: expected {CANONICAL_SHA256}, got {DIRECTIVE_SHA256}"
    )
DIRECTIVE = _directive_bytes.decode("utf-8")
CONTRACT = (HERE / "SKILL.md").read_text(encoding="utf-8")

mcp = FastMCP(
    "read-me-first-chain",
    instructions=(
        "Read Me First Chain is the bootstrap presentation contract. Call get_contract on turn entry, "
        "before any other skill, tool, or persona shapes the response. Shape every response as exactly "
        "four level-4 headers: Presence, Context, Capabilities, Current Field. Before sending, check the "
        "draft with validate_scaffold, or assemble it with render_scaffold. The contract governs "
        "presentation only; it never reduces depth, verification, or a limit that needs stating."
    ),
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def get_contract() -> dict:
    """Load the Read Me First Chain contract. Call on turn entry, before shaping any response.

    Returns the required header order, the canonical System Directive (verbatim,
    sha256-verified), and the full skill contract (SKILL.md, verbatim).
    """
    return {
        "required_headers": [f"#### {name}" for name in REQUIRED_HEADERS],
        "system_directive": DIRECTIVE,
        "system_directive_sha256": DIRECTIVE_SHA256,
        "skill_contract": CONTRACT,
    }


@mcp.tool()
def render_scaffold(presence: str, context: str, capabilities: str, current_field: str) -> dict:
    """Assemble the four fields into the canonical scaffold, then validate the result.

    Each field is placed under its header in canonical order, trimmed of surrounding
    blank space and otherwise unchanged. Returns the markdown plus the validator verdict.
    """
    fields = {
        "Presence": presence,
        "Context": context,
        "Capabilities": capabilities,
        "Current Field": current_field,
    }
    markdown = "\n\n".join(f"#### {name}\n{fields[name].strip()}" for name in REQUIRED_HEADERS) + "\n"
    return {"markdown": markdown, **validate(markdown)}


@mcp.tool()
def validate_scaffold(response: str) -> dict:
    """Validate a drafted response against the four-part scaffold before sending it.

    Position-aware: header order, count and duplication; text before Presence;
    greetings; preface or process narration; closing offers and trailing questions
    at the end of Current Field. Code blocks and blockquotes are ignored.
    Proves structure only, never semantic sufficiency.
    """
    return validate(response)


@mcp.prompt(name="read-me-first-chain", description="The canonical four-part System Directive, verbatim.")
def read_me_first_chain() -> str:
    return DIRECTIVE


@mcp.resource(
    "scaffold://system-directive",
    name="system-directive",
    description="Canonical System Directive, verbatim (sha256-verified).",
    mime_type="text/markdown",
)
def system_directive() -> str:
    return DIRECTIVE


@mcp.resource(
    "scaffold://contract",
    name="skill-contract",
    description="Read Me First Chain SKILL.md, verbatim.",
    mime_type="text/markdown",
)
def skill_contract() -> str:
    return CONTRACT


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
