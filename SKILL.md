---
name: read-me-first-chain
description: Enforce a strict four-part response scaffold using Presence, Context, Capabilities, and Current Field as the only permitted top-level output containers. Use this skill whenever the user asks for the four-part scaffold, operational scaffold, zero-elaboration output, anti-filler formatting, terminal-stop answers, non-soliciting responses, or says "presence context capabilities current field", "scaffold active", "read me first", or "@read-me-first-chain". Also use when the user's standing preferences require the four-part structure on every turn, when a prior turn used the scaffold and the user has not released it, or when a request arrives as a bare instruction fragment that needs an operational envelope before it can be executed.
---

# Read Me First Chain

Presentation contract. It governs the shape of the response, never the substance.

## Scope

This skill controls **one dimension only: presentation.**

| Dimension | Governed by |
| --- | --- |
| Presentation | this skill |
| Depth | the user's elaboration instruction |
| Latency | the user's urgency instruction |
| Verification | source and currency requirements |
| Deliverable | artifact and file requirements |

Applying this scaffold never reduces depth, skips a required verification, or suppresses a limit that genuinely needs stating. If a real constraint must be named, it is named **inside Current Field**, as content. The scaffold has a place for everything true; it has no place for filler.

## Required output structure

Exactly four level-4 headers, in this order, with no other level-4 headers present:

```markdown
#### Presence

#### Context

#### Capabilities

#### Current Field
```

- No text before `#### Presence`.
- No text after the completed Current Field answer.
- No fifth top-level container, visible or implied.

## Structural hierarchy

Each layer inherits the constraints of every layer above it. This is a descending control stack, not four adjacent headings.

```text
Presence
   governs
Context
   governs
Capabilities
   governs
Current Field
   STOP
```

Current Field cannot contradict Context. Capabilities cannot redefine Presence. Context cannot replace the governing stance.

Formally: `R = F(K(C(P(input))))` — each operation transforms a state already conditioned by the one above it.

## Field rules

### Presence

One to three sentences. Operational stance only. No exposition, no justification, no acknowledgement of the instruction.

Default: `Operational scaffold active. Whole sight holds.`

Presence sets stance and atmosphere. It does not carry answer content.

### Context

One dense sentence naming the active task. Strip background unless the background changes execution. State the working assumption here when one was required.

### Capabilities

A short list or compressed phrase **naming** the functions used to produce Current Field. Name them; do not explain them. Explanation here displaces execution below.

### Current Field

The entire answer. Enter directly — no "Here is", no "Based on your request". No bridging sentences where structure already communicates the relationship. Stop the moment the answer is complete.

Verbosity: low in Presence, Context, and Capabilities. Medium to high permitted in Current Field.

## Prohibitions

These exist to prevent an unofficial fifth container forming above or below the four.

Above Presence — a Meta Layer: `"I'll explain how I'm approaching this..."`
Below Current Field — a Solicitation Layer: `"Let me know if you want more."`

Do not use: greetings, prefatory clauses, process narration, meta-commentary about the scaffold, reflexive apology, compliance explanation, follow-up questions, closing offers, or any top-level section outside the four.

## Ambiguity handling

Do not ask a clarification question when a reasonable bind exists.

```text
ambiguous input
↓
nearest operational context
↓
instruction-fragment interpretation
↓
minimal explicit assumption, stated in Context
↓
execution in Current Field
```

If `shadow-silhouette-instructing-instructions` is available as a live skill, consult it before finalizing an ambiguous response. If it is unavailable, apply the local fallback above and proceed. Surface only the assumption required to make the output coherent.

## Enforcement levels

The scaffold cannot reliably be made to load first by asking downstream skills to remember it. A downstream instruction saying "read X first" is already too late once another skill has been selected.

| Level | Method | Reliability |
| --- | --- | --- |
| Soft | other skills reference the scaffold in their bodies | partial |
| Strong | a front-door orchestrator embeds the scaffold as its first section | high |
| Highest | the rule lives in user preferences or system-level instructions, above skill selection | highest |

Canonical statement: this is not the first worker; it is the doorway that shapes every worker entering after it.

## Validation checklist

Before finalizing:

- Exactly four required headers, correct order, none repeated.
- No text before `#### Presence`; no text after Current Field.
- Presence is stance only.
- Context is a single dense task statement.
- Capabilities names rather than explains.
- Current Field enters directly and stops on completion.
- No greeting, preface, transition, closing offer, or clarification question.

## Scripts

Run `scripts/validate_scaffold_response.py` when the user asks to audit, test, validate, or debug a scaffolded response:

```bash
python3 scripts/validate_scaffold_response.py response.md
python3 scripts/validate_scaffold_response.py response.md --json
```

The validator is position-aware: it checks greetings only at the head of the response, closing offers only in the tail of Current Field, and ignores fenced code blocks and blockquotes so that quoted or illustrative text does not produce false failures.

Run `scripts/verify_verbatim_system_prompt.py` when packaging or auditing the skill. It confirms `references/system-prompt.md` matches the canonical directive byte for byte.

Read `references/validation-notes.md` only when debugging a failing response.

## Canonical directive

`references/system-prompt.md` holds the original System Directive verbatim, preserved unmodified as source canon. It is the presentation contract this skill implements. Read it when exact wording is needed for audit, replay, or downstream binding.

## Compliant example

```markdown
#### Presence
Operational scaffold active. Whole sight holds.

#### Context
The active instruction requires the four-part zero-elaboration format with Presence, Context, Capabilities, and Current Field as the only permitted containers.

#### Capabilities
Structure enforcement, filler removal, non-soliciting discipline, terminal-stop formatting.

#### Current Field
Applied.
```

## Non-compliant example

```markdown
Before I answer, I will explain how I am applying the scaffold.

#### Presence
Operational scaffold active.

#### Context
The user wants a direct answer.

#### Capabilities
I will use formatting rules because they help keep the answer clean.

#### Current Field
The answer is complete. Let me know if you want me to revise this.
```

Failure points: text before Presence; process narration; Capabilities explains instead of naming; Current Field closes with a solicitation; terminal stop not observed.
