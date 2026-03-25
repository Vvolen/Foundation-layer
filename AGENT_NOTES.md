# AGENT_NOTES.md — NickOS Foundation-layer

> **What this file is:** A living, append-only journal written by every AI agent that works in
> this repository. Each session ends with a mandatory entry here. The goal is to build collective
> intelligence over time — so each new agent inherits the hard-won insights of every agent
> that came before it.
>
> **Read this file before starting work.** The last few entries tell you what's been discovered,
> what's uncertain, and what the next agent should focus on.
>
> **Write to this file when you finish work.** Even a short session deserves an entry.
> Future you — or another agent entirely — will be grateful.

---

## RULES FOR AGENTS

### Mandatory Protocol

Every agent working in this repository **MUST**:

1. **Read** the last 3 entries in this file before starting any work
2. **Write** a new entry here before ending a session (even partial work counts)
3. **Never edit** a past entry — append only, always at the bottom
4. **Be honest** — if something is uncertain, broken, or confusing, say so

### Entry Format

Use this exact structure (copy-paste the template):

```
## Entry N — YYYY-MM-DD — <Agent Name> — <Task in ≤8 words>

**Session type:** feature | fix | refactor | research | planning | review
**Phase:** Phase 0 (scaffolding) | Phase 1 (pipeline) | Phase 2 (memory) | Phase 3 (agents)
**Files touched:** list the key files you changed or read
**Time:** approximate (e.g., "~15 min", "~2 hours")

**Key insight:**
One to three sentences. The single most important thing you learned or discovered in this
session that is not already documented elsewhere. If nothing surprised you, say that.

**Suggestion for next agent:**
One specific, actionable thing the next agent should do or investigate. Not a vague "continue
the work" — something concrete like "check whether the dedup threshold produces false positives
on technical content" or "the retry logic in fact_extractor.py should use httpx instead of
raw requests for timeout handling."

**Open question:**
Something you are genuinely uncertain about. A hypothesis you couldn't test. A design decision
that might be wrong. Honest uncertainty is more valuable than false confidence.

**Tags:** #tag1 #tag2 #tag3
(Pick 1–5 tags from: #architecture #performance #dedup #testing #pipeline #memory
#schema #embedding #security #ux #docs #ci #research #tooling — or invent new ones)

**Confidence in suggestions:** low | medium | high
(low = gut feeling, medium = tested assumption, high = empirical evidence from this session)

---
```

### Quality Bar

- **Key insight** must be specific. "The pipeline works" is not an insight.
  "YouTube auto-captions include sponsor text that inflates fact count by ~15%" is an insight.
- **Suggestion** must be actionable in one session. "Rewrite everything" is not a suggestion.
- **Open question** must be genuinely open. If you know the answer, put it in Key Insight.
- Length: keep each entry under 250 words total. Brevity is a form of respect for future agents.

### What NOT to Write

- Do not repeat what is already in `plans/findings.md` (that's for architectural decisions)
- Do not repeat what is already in `plans/progress.md` (that's for session status)
- Do not write about what you *plan* to do — write about what you *observed* and *concluded*
- Do not be falsely positive — if something is fragile or sketchy, say so

---

## REFERENCE: What Each Planning File Is For

| File | Purpose | Who writes it |
|------|---------|---------------|
| `AGENT_NOTES.md` | Session-level insights, surprises, suggestions | **Every agent, every session** |
| `AGENTS.md` | Cross-tool agent context (universal standard) | Human + senior agent |
| `plans/progress.md` | Status tracking — what's done, what's next | Every agent |
| `plans/findings.md` | Permanent architectural decisions | Agent + human review |
| `CLAUDE.md` | Cold-start instructions for new agents | Human + senior agent |
| `plans/COLLECTIVE_INTELLIGENCE.md` | Ideas for evolving this system itself | Read this too |

---

## ENTRIES

<!-- ========================================================================
     APPEND NEW ENTRIES AT THE BOTTOM OF THIS SECTION.
     Do not edit entries above yours.
     ======================================================================== -->

## Entry 1 — 2026-03-25 — Copilot Coding Agent — Set up agent notes system

**Session type:** planning / research
**Phase:** Phase 1 complete, bridging to Phase 2
**Files touched:** `AGENT_NOTES.md` (created), `plans/COLLECTIVE_INTELLIGENCE.md` (created),
`CLAUDE.md` (updated), `.github/copilot-instructions.md` (updated), `tests/test_smoke.py` (updated)
**Time:** ~45 min

**Key insight:**
The repo already has three files that partially fill the "agent memory" role
(`progress.md`, `findings.md`, `CLAUDE.md`), but none of them is designed for *cross-agent
synthesis* — they're logs and decisions, not a layer for collective reasoning. The gap
is a file where agents write observations that *don't fit elsewhere* but are still worth
preserving: surprises, hunches, friction points, and suggestions. That's what this file is.

**Suggestion for next agent:**
After you write your entry here, check if any suggestions from earlier entries can be
"promoted" to `plans/findings.md` as a new architectural decision. An insight that has
appeared in two or more entries independently is probably solid enough to formalize.

**Open question:**
At what point does this file become too long to read efficiently? A rough guess is ~50 entries
(~12,500 words). Before we hit that, we need either a summary/digest mechanism (see
`plans/COLLECTIVE_INTELLIGENCE.md` Idea 4) or a rolling archive strategy. Neither is
implemented yet.

**Tags:** #architecture #docs #research #memory
**Confidence in suggestions:** medium

---

<!-- ADD YOUR ENTRY HERE ↓ -->

## Entry 2 — 2026-03-25 — Copilot Coding Agent (Opus) — Augment agent memory system

**Session type:** feature / research
**Phase:** Phase 0 (scaffolding)
**Files touched:** `AGENT_NOTES.md` (updated template + entry), `AGENTS.md` (created),
`plans/COLLECTIVE_INTELLIGENCE.md` (added Part 3 with 3 new ideas), `CLAUDE.md` (updated
file map), `tests/test_smoke.py` (added 4 new tests)
**Time:** ~45 min

**Key insight:**
The repo's approach — using the repository itself as the coordination medium for multi-agent
intelligence — is now independently validated by several 2026 projects (agent-soul, SAMEP
protocol, gitagent spec). The key differentiator here is human-readable markdown vs. JSON
event streams. The markdown approach trades machine efficiency for human auditability, which
is the right trade-off at this scale. The biggest missing piece is *trust verification* —
any agent can write confident-but-wrong insights. Added Idea 11 (Entry Verification Gate)
to address this.

**Suggestion for next agent:**
Implement the Entry Verification Gate (Idea 11) as a CI check in `.github/workflows/test.yml`.
It's a regex scan for `**Evidence:**` in new AGENT_NOTES entries. Cost: ~10 lines of shell.
Value: prevents hallucinated insights from polluting the knowledge base. This is the
highest-leverage single improvement before the system scales to 10+ entries.

**Open question:**
The repo now has three context files (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`).
Without a sync mechanism (Idea 13), they will drift. At what point does the maintenance cost
of keeping them aligned exceed the benefit of cross-tool compatibility? Is two files enough,
or should we consolidate to `AGENTS.md` + tool-specific deltas?

**Tags:** #architecture #docs #research #memory #tooling
**Confidence in suggestions:** high

---
