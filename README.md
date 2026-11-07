# read-me-first-chain — remote MCP connector

The Read Me First Chain presentation contract, served to Claude over MCP.

## Tools
- `get_contract()` — required header order, the canonical System Directive (verbatim, sha256-checked), and the full skill contract
- `render_scaffold(presence, context, capabilities, current_field)` — assembles the four fields in canonical order and validates the result
- `validate_scaffold(response)` — position-aware structural check of a drafted response

Also exposed: the prompt `read-me-first-chain` and the resources `scaffold://system-directive` and `scaffold://contract`.

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
