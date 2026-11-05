# read-me-first-chain — remote MCP connector

The Read Me First Chain presentation contract, served to Claude over MCP.

## Tools
- `get_contract()` — required header order, the canonical System Directive (verbatim, sha256-checked), and the full skill contract
- `render_scaffold(presence, context, capabilities, current_field)` — assembles the four fields in canonical order and validates the result
- `validate_scaffold(response)` — position-aware structural check of a drafted response

Also exposed: the prompt `read-me-first-chain` and the resources `scaffold://system-directive` and `scaffold://contract`.

## Explicit requests and heading profiles

The original no-argument call and four H4 headings remain the default (`profile="v1"`).
A populated request envelope is also supported and acknowledged in the result:

```json
{"args":{"query":"'://read-me'"},"profile":"v2"}
```

`args.query` must be a nonblank string. It records the caller's request; it does not
perform a search or execute the query. Invalid envelopes produce an MCP input error.

For an explicitly selected v2 hierarchy, pass `profile="v2"` to **all three tools**.
The headers are `# Presence`, `## Context`, `### Capabilities`, `#### Current Field`.
Validation examines the complete response and rejects mixed profiles, missing,
reordered, or repeated fields. It never silently changes the selected profile.
The canonical v1 directive, skill, and validator remain unchanged; v2 is an explicit
compatibility profile layered over the original validator.

All tools declare read-only, non-destructive, idempotent, closed-world annotations.
Their functions do not write payloads to disk or make outbound requests. These
annotations describe implementation behavior; they do not grant authorization or
override a client's approval policy. Remote calls still send their input to the
deployed service. Hosting/proxy logging is outside this source-level guarantee.

`get_contract` reports `implementation_version="1.1.0"`, the selected profile, and
the unchanged directive hash so callers can distinguish this release from an old
deployment. Redeploy the service and refresh the client's tool schema before using
the new arguments. A source commit alone does not update an existing connector.

Run regression and MCP boundary tests with `python -m unittest discover -s tests -v`.

## Files
- `server.py` — the MCP server
- `validate_scaffold_response.py` — the skill's validator, unmodified
- `system-prompt.md` — the canonical System Directive, unmodified (the server refuses to start if its sha256 changes)
- `SKILL.md` — the skill contract, unmodified
- `requirements.txt` — `mcp>=1.10,<2` (the `<2` pin is required)
- `Dockerfile`

## Run locally
    pip install -r requirements.txt
    python server.py          # serves http://localhost:8000/mcp

## Deploy (must be public HTTPS — Claude connects from Anthropic's cloud)
Any container host works (Render, Railway, Fly.io, Cloud Run):
    docker build -t read-me-first-chain . && docker run -p 8000:8000 read-me-first-chain
The host must set PORT or expose 8000.

## Add to Claude
Customize → Connectors → **+** → Add custom connector
- Name: `read-me-first-chain`
- URL: `https://<your-host>/mcp`   ← single slash after host, ends in /mcp
- Advanced settings: leave blank (authless)

Then enable it in the chat's tools menu.
