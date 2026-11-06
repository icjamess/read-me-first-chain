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
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator

from scaffold_profiles import Profile, headers_for, validate_profile
from validate_scaffold_response import REQUIRED_HEADERS

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

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


class ContractArgs(BaseModel):
    """An optional, acknowledged request envelope; never executable instructions."""

    model_config = ConfigDict(extra="forbid")
    query: StrictStr

    @field_validator("query")
    @classmethod
    def require_nonblank_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("args.query must contain non-whitespace text")
        return value

mcp = FastMCP(
    "read-me-first-chain",
    instructions=(
        "Read Me First Chain is the bootstrap presentation contract. Call get_contract on turn entry, "
        "before any other skill, tool, or persona shapes the response. The default v1 profile uses "
        "four level-4 headers: Presence, Context, Capabilities, Current Field. When the user selects "
        "the v2 hierarchy, pass profile='v2' consistently to get_contract, render_scaffold, and "
        "validate_scaffold; its heading levels are 1, 2, 3, 4 in that same order. Before sending, "
        "check the complete draft with validate_scaffold, or assemble it with render_scaffold. "
        "These tools perform in-memory processing without outbound calls or persistent writes. "
        "The contract governs "
        "presentation only; it never reduces depth, verification, or a limit that needs stating."
    ),
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
)


@mcp.tool(annotations=READ_ONLY)
def get_contract(args: ContractArgs | None = None, profile: Profile = "v1") -> dict:
    """Load the Read Me First Chain contract. Call on turn entry, before shaping any response.

    Returns the required header order, the canonical System Directive (verbatim,
    sha256-verified), and the full skill contract (SKILL.md, verbatim).
    Accepts an optional args.query envelope and acknowledges it in request;
    the query is request metadata, not a search or an instruction to execute.
    Reads no connected account data. Choose v2 only for an explicitly selected
    H1/H2/H3/H4 hierarchy; the canonical v1 text remains unchanged.
    """
    return {
        "required_headers": list(headers_for(profile)),
        "system_directive": DIRECTIVE,
        "system_directive_sha256": DIRECTIVE_SHA256,
        "skill_contract": CONTRACT,
        "profile": profile,
        "supported_profiles": ["v1", "v2"],
        "implementation_version": "1.1.0",
        "request": args.model_dump() if args is not None else None,
    }


@mcp.tool(annotations=READ_ONLY)
def render_scaffold(
    presence: str, context: str, capabilities: str, current_field: str,
    profile: Profile = "v1",
) -> dict:
    """Assemble the four fields into the canonical scaffold, then validate the result.

    Each field is placed under its header in canonical order, trimmed of surrounding
    blank space and otherwise unchanged. Returns the markdown plus the validator verdict.
    Processes supplied text in memory; performs no outbound calls or persistent writes.
    """
    fields = {
        "Presence": presence,
        "Context": context,
        "Capabilities": capabilities,
        "Current Field": current_field,
    }
    markdown = "\n\n".join(
        f"{header}\n{fields[name].strip()}"
        for name, header in zip(REQUIRED_HEADERS, headers_for(profile))
    ) + "\n"
    return {"markdown": markdown, **validate_profile(markdown, profile)}


@mcp.tool(annotations=READ_ONLY)
def validate_scaffold(response: str, profile: Profile = "v1") -> dict:
    """Validate a drafted response against the four-part scaffold before sending it.

    Position-aware: header order, count and duplication; text before Presence;
    greetings; preface or process narration; closing offers and trailing questions
    at the end of Current Field. Code blocks and blockquotes are ignored.
    Proves structure only, never semantic sufficiency.
    Processes the complete supplied text in memory without storing, forwarding,
    or shortening it. Performs no outbound calls or persistent writes.
    """
    return validate_profile(response, profile)


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
