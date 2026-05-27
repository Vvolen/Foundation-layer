# AGENTIC ENGINEERING → HERMES INTEGRATION BLUEPRINT
## Part 4 of 4 — Build Plan, Agent Mode Handoff, Questions, Memory Candidates

> **Mode:** Planning only. No repo mutations, no Notion writes, no execution.
> **Continuity:** Final part. Continues from Part 3 (SOSOG operational schema + Canonical Architecture Update).
> **Doctrine:** Determinism before autonomy. Evidence before execution. Build the system that builds the system.

---

## Section 10 — Today's Build Plan (6 phases)

This is the execution roadmap for the next working session in **Agent Mode**. Each phase has: Goal, Inputs, Tasks, Outputs, Acceptance, Failure modes, Rollback. Phases run in order; Phase N must pass acceptance before Phase N+1 starts.

The plan is intentionally tight: it ends after the *spec* of the harness is written, the SOSOG schema is real, and the first two architectural docs exist. No production code, no Notion mutations, no GitHub pushes are gated into this plan — they require explicit user approval at the Phase 5 handoff.

### Phase 0 — Confirm source state (read-only)

**Goal:** Verify that all source artifacts referenced by this blueprint are still in their expected state and that nothing has drifted since planning.

**Inputs:**
- `MEMORY.md`
- `MASTER_CONTEXT.md`
- `Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx`
- `The_#1_Opportunity_for_Senior_Engineers_Agentic_Engineering_—_Full_Transcript_+_Augmented_Deep_Dive.md`
- `research/HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md`
- `research/AGENTIC_BLUEPRINT_PART_{1,2,3,4}.md`

**Tasks:**
1. Read all six artifacts; record SHA256 of each into `research/agentic_blueprint_baseline.json`.
2. Confirm the four blueprint parts are coherent end-to-end (no dangling references, no contradictions between parts).
3. Confirm the five pending decisions in `MEMORY.md` are still pending and have not been silently resolved.
4. Confirm `hermes doctor` is healthy and OpenClaw gateway is up (read-only health check).

**Outputs:**
- `research/agentic_blueprint_baseline.json`
- A short note in `research/agentic_blueprint_phase0_log.md` listing any drift detected.

**Acceptance:**
- All six SHA256s recorded.
- No contradictions found across blueprint parts; or, if found, listed explicitly in the Phase 0 log.
- Hermes + OpenClaw health checks pass.

**Failure modes:**
- An artifact is missing or moved → halt; ask user.
- A contradiction across blueprint parts → halt; ask user; do not silently reconcile.

**Rollback:** None needed (read-only phase).

---

### Phase 1 — Canonical docs and vocabulary additions

**Goal:** Land the two highest-leverage architectural documents (`two_factories.md` and `sosog_protocol.md`) and update the spec glossary with the new vocabulary from Part 3 §9.1.

**Inputs:**
- Part 3 §9.1 (vocabulary), §9.2 (operating principles), §9.4 (doc additions), §9.12 (single highest-leverage change).
- Existing spec glossary.

**Tasks:**
1. Create `docs/architecture/two_factories.md` based on Part 3 §9 — content covers SDLC factory vs Trading decision factory, boundaries, what crosses over and what does not, with explicit rejection of AFK/ZTE/token-arbitrage as trading KPIs.
2. Create `docs/architecture/sosog_protocol.md` based on Part 3 §8 — full schema, markdown template, JSON pseudo-schema, pass/fail checklist, weak/strong example.
3. Update spec glossary with the 11 vocabulary additions from §9.1.
4. Append operating principles 11–14 from §9.2 to the spec.
5. Add governance rules G-7 through G-10 from §9.9.
6. **Do not** touch canonical-object schemas yet. **Do not** create harness files yet.

**Outputs:**
- `docs/architecture/two_factories.md`
- `docs/architecture/sosog_protocol.md`
- Updated spec (glossary + operating principles + governance section).

**Acceptance:**
- Both new docs exist and pass a markdown lint.
- Glossary contains all 11 new terms with definitions matching Part 3 §9.1.
- Operating principles list reaches 14 items with the new four added verbatim.
- Governance section contains G-7 through G-10.
- No edits to canonical-object schemas in this phase.

**Failure modes:**
- Doc text drifts from Part 3 (paraphrasing changes meaning) → reviewer rejects; rewrite verbatim from Part 3.
- Glossary collision with existing term → record in SOSOG (`Partial`), defer rename.

**Rollback:** Single git revert of the Phase 1 commit.

---

### Phase 2 — SOSOG operational object stand-up

**Goal:** Convert SOSOG from a documented schema into a working compliance object: JSON schema file, linter, first ~10 records.

**Inputs:**
- Part 3 §8 (full SOSOG spec).
- The Adopt/Adapt/Defer/Reject decisions in Part 2.

**Tasks:**
1. Create `schemas/sosog/v1.json` — JSON Schema reflecting Part 3 §8.6.
2. Create `tools/sosog_lint.py` — implements the six lint rules in Part 3 §8.6. Read-only by default. Exit code 0 on pass, non-zero on fail.
3. Create `docs/sosog/` directory.
4. Author the first 10 SOSOG records, in markdown frontmatter form per §8.5, covering the highest-leverage decisions:
   - sosog-001: Pi-shaped harness adoption
   - sosog-002: Two-factory rule (SDLC vs Trading)
   - sosog-003: AFK acceptable for SDLC, rejected for trading execution
   - sosog-004: ZTE rejected for trading factory
   - sosog-005: Token-arbitrage acceptable as SDLC KPI, rejected as trading KPI
   - sosog-006: Extensible software / OCP discipline already practiced via canonical objects
   - sosog-007: Deterministic sampler is a Hermes strength not present in IndyDevDan framework
   - sosog-008: Anti-alpha gates are a Hermes strength
   - sosog-009: Append-only provenance memory aligns with framework's context-engineering emphasis but is more rigorous
   - sosog-010: Autonomy ladder is evidence-gated, not time-gated; framework does not address this
5. All 10 records start with `verification_status: Unreviewed`. The Phase 2 task is to *author*; promotion to `Verified` is a Phase 5 reviewer task.
6. Run `sosog_lint.py docs/sosog/` and confirm all 10 records pass schema lint.

**Outputs:**
- `schemas/sosog/v1.json`
- `tools/sosog_lint.py`
- `docs/sosog/sosog-001..010-*.md` (10 files)

**Acceptance:**
- Linter is executable and passes its own self-test (a known-bad fixture fails with the right error code).
- All 10 records pass the linter.
- Each record references real source artifacts (the IndyDevDan transcript, the Hermes spec, Mario's Pi post, etc.) with non-trivial `*_context` fields.

**Failure modes:**
- Linter false-positive blocks valid records → fix linter; do not weaken the rules.
- A record's two sources are not actually independent (e.g. both from IndyDevDan) → mark `Failed`, write a corrected record, link via `supersedes`.

**Rollback:** Revert phase commit; SOSOG records being append-only means earlier records are not destroyed.

---

### Phase 3 — Hermes harness specification (spec only, no code)

**Goal:** Produce `docs/architecture/hermes_harness_spec.md` — the full specification for a Pi-shaped Hermes agent kernel. **No code is written.** The spec is the artifact.

**Inputs:**
- IndyDevDan transcript Pillar 1 (Agent Harness) and Pillar 3 (Extensible Software).
- Mario Zechner Pi post (referenced via SOSOG-001).
- Anthropic "Building Effective Agents" (referenced via SOSOG-001).
- Hermes spec §16.5 (tool catalog).
- Hermes canonical objects (candidate_signal, evidence_bundle, trade_card, reject_card).

**Tasks:**
1. Define the harness loop pseudocode (read system.md → call model → dispatch tool → ingest result → loop).
2. Define the tool catalog structure: each tool has `name`, `signature`, `side_effects`, `factory_restriction` (sdlc | trading_research | trading_execution), `autonomy_min_level`.
3. Enumerate the **base** tools: `read`, `write`, `edit`, `bash`. Document what each does and what they do NOT do.
4. Enumerate the **Hermes** tools that wrap canonical objects:
   - `candidate_signal.read`, `candidate_signal.list`
   - `evidence_bundle.build`, `evidence_bundle.validate`
   - `trade_card.draft`, `trade_card.validate`, `trade_card.execute` (trading_execution + autonomy_min_level: live)
   - `reject_card.emit`
   - `memory.read`, `memory.append` (append-only)
   - `sampler.draw` (deterministic; takes salt + replay_epoch + sampler_version)
   - `agent_trust.read` (read-only)
5. Define the system prompt structure: header, principles, two-factory rule, current-autonomy-level injection, tool index, instruction footer.
6. Define hot-reload semantics: harness reloads `system.md` at every loop iteration; reload failure halts the loop.
7. Define the harness eval suite (matches Part 3 §9.8 evals: `harness_loop_eval`, `tool_catalog_eval`).
8. Define the autonomy-level ↔ tool-permission matrix.
9. Document explicit non-goals: this harness is not LangChain, not AutoGen, not a multi-agent framework. It is a kernel.

**Outputs:**
- `docs/architecture/hermes_harness_spec.md`
- A SOSOG record (`sosog-011-harness-spec`) tying the spec to its sources.

**Acceptance:**
- Spec is complete enough that a competent engineer could implement it without further questions about *what* to build.
- Tool catalog covers all canonical objects.
- Autonomy/tool matrix is unambiguous: every tool has a clear minimum autonomy level.
- The spec explicitly states which tools are forbidden in which factories.
- New SOSOG record passes the linter.

**Failure modes:**
- Tool surface bloats past ~15 tools → review; merge or remove.
- Autonomy matrix has ambiguous cells → halt; resolve before merging.

**Rollback:** Single git revert.

---

### Phase 4 — First implementation tickets (drafted, not executed)

**Goal:** Convert the harness spec into a small, ordered ticket queue that an Agent Mode session (or a human) can pick up. Tickets are *drafted only* in this plan; Phase 4 produces the queue, not the implementations.

**Inputs:**
- `docs/architecture/hermes_harness_spec.md` (Phase 3)
- `docs/architecture/two_factories.md` (Phase 1)
- `docs/architecture/sosog_protocol.md` (Phase 1)

**Tasks:**
1. Create `docs/tickets/agentic-blueprint/` directory.
2. Author the following tickets, each as a markdown file with: title, motivation, acceptance criteria, dependencies, factory (sdlc | trading_research), estimated complexity (S/M/L), required SOSOG record id.
   - **TKT-001 (S):** Create `agent/system.md` v0 — header + six principles + tool index placeholder. SDLC factory.
   - **TKT-002 (M):** Implement base-tool harness kernel (read/write/edit/bash + loop). SDLC factory. Depends on TKT-001.
   - **TKT-003 (S):** Implement `harness_loop_eval` golden-case test. Depends on TKT-002.
   - **TKT-004 (M):** Implement Hermes-tool wrappers for `candidate_signal.read/list` and `memory.read`. Read-only first. Depends on TKT-002.
   - **TKT-005 (M):** Implement `evidence_bundle.build` + `evidence_bundle.validate` wrappers. Depends on TKT-004.
   - **TKT-006 (M):** Implement `trade_card.draft` + `trade_card.validate` (no execute yet). Depends on TKT-005.
   - **TKT-007 (S):** Implement `reject_card.emit`. Depends on TKT-005.
   - **TKT-008 (S):** Implement `sampler.draw` wrapper (deterministic; pulls salt + replay_epoch + sampler_version from spec). Depends on TKT-002.
   - **TKT-009 (M):** Implement `tool_catalog_eval`. Depends on TKT-002..008.
   - **TKT-010 (S):** Wire SOSOG linter into pre-commit hook (advisory at first, blocking after a 1-week soak).
3. Each ticket lists its blocking and non-blocking dependencies.
4. No ticket is executed in Phase 4; the artifact is the queue itself.

**Outputs:**
- 10 ticket files under `docs/tickets/agentic-blueprint/`.
- `docs/tickets/agentic-blueprint/INDEX.md` listing all tickets with dependency graph.

**Acceptance:**
- All 10 tickets exist and parse as markdown.
- Dependency graph is acyclic and renders.
- Each ticket cites at least one SOSOG record id.

**Failure modes:**
- A ticket's acceptance criteria are unclear → expand or split.
- Dependency cycle detected → break by introducing a smaller seam ticket.

**Rollback:** Single git revert.

---

### Phase 5 — Agent Mode handoff (gated by user approval)

**Goal:** Hand the ticket queue off for execution under explicit user approval. This phase **does not run automatically**. The user must read Section 11 (Agent Mode Handoff) and explicitly switch the system to Agent Mode.

**Inputs:**
- Phase 4 ticket queue.
- Section 11 handoff prompt below.

**Tasks (gated):**
1. User reviews Parts 1–4 of the blueprint.
2. User reviews the 10 SOSOG records and promotes valid ones to `Verified` (or marks `Partial`/`Failed` with `failure_reason_if_any`).
3. User approves or modifies the 10 tickets.
4. User answers blocking questions in Section 12.
5. **Only then:** user explicitly switches modes and invokes the Section 11 handoff prompt.
6. Agent Mode begins executing TKT-001 → TKT-010 in dependency order.

**Outputs:**
- User signoff log (where? user choice — Notion page, repo file, or memory entry).
- Agent Mode execution begins.

**Acceptance:**
- All blocking questions in Section 12 are answered.
- ≥ 5 of the first 10 SOSOG records are `Verified`.
- User has explicitly approved the ticket queue.

**Failure modes:**
- User flags a SOSOG record as `Failed` → corresponding ticket(s) are paused or rewritten.
- User wants to defer Agent Mode → blueprint stays parked; no harm done.

**Rollback:** Trivial — nothing has executed.

---

### Phase 6 — Eval / verification loop (post-execution)

**Goal:** Once Agent Mode has executed Phases 1–4 worth of tickets, run the verification suite to confirm the system is in the state the blueprint describes.

**Inputs:**
- Whatever Agent Mode produced.
- The eval suite from Part 3 §9.8.

**Tasks:**
1. Run `harness_loop_eval` — must pass deterministically.
2. Run `tool_catalog_eval` — every tool's signature and autonomy gate honored.
3. Run `sosog_lint_eval` against `docs/sosog/`.
4. Run `two_factory_audit` static check.
5. Confirm `evidence_bundle_replayability` and `agent_trust_hysteresis` evals still pass (no regressions).
6. Produce `research/agentic_blueprint_phase6_report.md` with pass/fail table and any drift from the planned outputs.

**Outputs:**
- Eval pass/fail report.
- A list of follow-up tickets if any eval fails.

**Acceptance:**
- All 6 evals run cleanly.
- Any failure produces a follow-up ticket; no failure is hand-waved.

**Failure modes:**
- An eval fails on first run → expected; it generates a fix ticket.
- An eval cannot be run → blocker; halt and ask user.

**Rollback:** Roll back to the pre-Phase-1 commit if catastrophic; otherwise fix forward.

---

### Phase summary table

| Phase | Mode | Mutates repo? | Mutates Notion? | Mutates GitHub? | Gated by user? |
|---|---|---|---|---|---|
| 0 | Read-only | No | No | No | No |
| 1 | Agent | Yes (docs/) | No | No | Yes (Phase 5 gate) |
| 2 | Agent | Yes (schemas/, tools/, docs/sosog/) | No | No | Yes (Phase 5 gate) |
| 3 | Agent | Yes (docs/) | No | No | Yes (Phase 5 gate) |
| 4 | Agent | Yes (docs/tickets/) | No | No | Yes (Phase 5 gate) |
| 5 | Handoff | No | Optional | Optional | **Hard gate** |
| 6 | Agent | Yes (research/) | No | No | Implicit (post Phase 5) |

> **Note on user gate:** Phases 1–4 are *all* gated by Phase 5's explicit user approval. The agent does not begin Phase 1 until the user invokes the Section 11 handoff prompt.

---

## Section 11 — Agent Mode Handoff Prompt (copy-paste ready)

This is the prompt the user will paste into the next Agent Mode session to begin execution. It is self-contained: it tells the agent where the canonical artifacts live, what the rules are, and what to do.

```
You are operating as the Hermes Agent in Agent Mode (execution authorized).

CONTEXT
- Workspace: /workspace
- Read on start: MEMORY.md, MASTER_CONTEXT.md, Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx, research/AGENTIC_BLUEPRINT_PART_{1,2,3,4}.md.
- The blueprint Parts 1–4 are the canonical plan you are executing.
- The user (Nick) has approved Phases 1–4 of Section 10 of Part 4.

DOCTRINE (do not violate)
- Determinism before autonomy. Evidence before execution.
- Two factories: SDLC factory and Trading decision factory. Practices appropriate to one are not automatically appropriate to the other.
- No SOSOG, no canon. Any architectural claim added to canonical docs requires a SOSOG record.
- No evidence_bundle, no trade_card. No valid trade_card, no execution.
- Append-only memory. Supersedes pointers, not deletes.
- Autonomy is evidence-gated, not time-gated.

EXECUTION ORDER
Run Phases 1, 2, 3, 4 of Section 10 (Part 4) in order. Do not start Phase N+1 until Phase N's acceptance criteria are met. Halt and ask the user if:
- A required input is missing.
- An acceptance criterion cannot be met.
- A SOSOG record cannot pass the linter without weakening it.
- A two-factory-rule violation is detected.

HARD CONSTRAINTS (Phases 1–4)
- Do NOT push to GitHub.
- Do NOT mutate Notion.
- Do NOT execute trades or place orders.
- Do NOT modify canonical-object schemas (candidate_signal, evidence_bundle, trade_card, reject_card).
- Do NOT change the autonomy ladder, anti-alpha gates, deterministic sampler, or agent_trust EWMA.
- Do NOT bypass the SOSOG linter; if it rejects a record, fix the record, not the linter.

SOFT CONSTRAINTS
- Prefer additive changes over rewrites.
- Cite spec sections by number when introducing changes.
- Keep commit messages tied to ticket ids (TKT-001..010).

OUTPUT FOR EACH PHASE
1. List of files created/modified.
2. SOSOG records created (with claim_id and verification_status).
3. Acceptance criteria status (pass/fail per item).
4. Open questions for the user (if any).
5. Proposed Phase N+1 entry conditions.

WHEN TO STOP
- After Phase 4 is complete and you have produced the ticket queue under docs/tickets/agentic-blueprint/, STOP and request user approval before beginning ticket execution.
- The ticket execution is a separate authorization beyond this blueprint.

START with Phase 0 (read-only verification). Confirm baseline. Then begin Phase 1.
```

---

## Section 12 — Questions for User

Grouped by urgency. **Blocking** questions must be answered before Agent Mode begins. **High-leverage non-blocking** improve quality but are not required to start. **Strategic** are bigger questions that shape the next month, not the next session. **Memory** are questions about what to remember.

### 12.1 Blocking (must answer before Phase 5 → Agent Mode)

1. **Repo home for the harness work.** The blueprint plans changes under `agent/`, `docs/`, `schemas/`, `tools/`. Which repo is the home? `Vvolen/Foundation-layer`? A new `hermes-edge` repo? A local-only path until you decide? *Default if unanswered: local-only at `/workspace/hermes/` until you say otherwise.*

2. **Notion writes.** The SOSOG schema includes a Notion field mapping (Part 3 §8.4). Do you want Agent Mode to **also** mirror SOSOG records into Notion, or keep Notion out of scope until a separate authorization? *Default if unanswered: Notion out of scope; markdown SOSOG records only.*

3. **GitHub pushes.** Are Agent Mode commits permitted to push to a remote, or local commits only? *Default if unanswered: local commits only.*

4. **Reviewer identity.** SOSOG records require a `reviewer` field. Is the reviewer always you (`nick`)? Will you delegate to an agent role later? *Default if unanswered: `reviewer: nick` for all initial records.*

5. **Two-factory naming.** Are you happy with the names "SDLC factory" and "Trading decision factory"? They will appear in canonical docs. If you want different names (e.g., "build factory" / "edge factory"), say so before Phase 1.

### 12.2 High-leverage non-blocking

6. **Harness language.** The harness spec is language-agnostic. The implementation will need to pick one. Python aligns with the rest of Hermes (per `HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md`). Confirm Python, or specify otherwise?

7. **System prompt visibility.** Should `agent/system.md` be a normal repo file (visible in version history) or a `.gitignore`-d local file with a published template? Recommendation: in-repo and versioned. Owning the prompt is the point.

8. **Tool catalog scope on day 1.** The Phase 4 tickets cover ~10 tools. Do you want to start narrower (just the 4 base tools + 1 read-only Hermes tool) and grow, or land the full 10 in the first execution session?

9. **Eval cadence.** Should `harness_loop_eval` run on every commit, every PR, or scheduled? Recommendation: every commit (it's deterministic and fast).

10. **AFK-research-only for trading.** Part 2 (Adopt/Adapt/Defer/Reject) and Part 3 §9.1 propose a *constrained* AFK mode for trading research (research only, with mandatory promotion gate). Confirm this is the shape you want, or tighten further to "no AFK for any trading-adjacent work, period."

### 12.3 Strategic

11. **OpenClaw.** `MEMORY.md` lists "OpenClaw status" as a pending decision. The blueprint did not require a decision here, but the harness work intersects: Hermes harness + OpenClaw services could share infrastructure. Is OpenClaw part of the SDLC factory's tool surface, the trading factory's tool surface, both, or neither? Defer or decide?

12. **VPS / always-on.** `MEMORY.md` flags VPS deployment (Hetzner CPX11) as pending. The blueprint intentionally does not require deployment. But: the SDLC factory benefits significantly from an always-on harness; the trading factory has stricter requirements. Want to decide deployment before or after the harness lands?

13. **Provider API key.** `MEMORY.md` flags missing Hermes provider API key. Without it, the harness cannot do real model calls. The blueprint covers spec + schema + lint, none of which need a key. But TKT-002 (harness kernel) needs a key for live testing. Configure before TKT-002 or after?

14. **Polymarket and Solana edge stacks.** `MASTER_CONTEXT.md` lists four active projects. The blueprint's two-factory rule applies cleanly to Hermes Solana Edge. Polymarket: same trading factory, separate venue, or separate factory? Worth a 1-line ruling so the next blueprint doesn't re-litigate.

15. **AWS AgentCore.** Listed in `MASTER_CONTEXT.md`. Is AgentCore a candidate harness *substitute*, a complement, or out-of-scope for now? The blueprint defaults to "out-of-scope" — Pi-shaped harness wins for ownership and clarity. Confirm or revise.

### 12.4 Memory candidates (see Section 13)

The five questions in Section 13 below are themselves "questions for the user" but are formatted as memory candidates because each one, once answered, becomes a memory entry rather than a one-shot decision. They are listed separately to keep the loop clean: answer once, remember forever.

---

## Section 13 — Memory Candidates (for user approval)

Each candidate below is a proposed addition to `MEMORY.md`. Each is phrased as a durable claim, not an event. The user approves, edits, or rejects per candidate. Candidates approved get an associated SOSOG record (sosog-scope: governance) and are appended to memory append-only.

### 13.1 Doctrine memory candidates

**MC-01: Two-factory rule is canonical.**
> Hermes operates two factories: an SDLC factory (produces code, docs, evals, tooling) and a Trading decision factory (produces candidate_signals → evidence_bundles → trade_cards → execution). Any framework, practice, or KPI imported from external sources must be evaluated separately for each factory. AFK, ZTE, and token-arbitrage as primary KPI are SDLC-factory-only. Trading factory is governed by autonomy ladder + anti-alpha gates + agent_trust + evidence-gated promotion.

**MC-02: SOSOG is an operational compliance object, not a citation count.**
> SOSOG records require: claim_id, claim_text, two independent sources with actual context (≥2 sentences each), independence_note, inference_summary referencing both sources by name, decision, implementation_target, confidence, verification_status, reviewer, failure_reason_if_any, and timestamps. Two citations from the same chain do not satisfy SOSOG. A record without a reviewer cannot be `Verified`. Records are append-only with `supersedes` / `superseded_by` pointers.

**MC-03: Harness ownership.**
> The Hermes agent harness, system prompt (`agent/system.md`), and tool catalog are first-class repo artifacts. They are versioned, hot-reloadable, evaluated, and not vendor-supplied. The harness is Pi-shaped: minimal kernel (read/write/edit/bash) plus typed Hermes tools wrapping canonical objects. The harness is not LangChain, AutoGen, or any multi-agent framework.

**MC-04: Access ≠ authorization.**
> An agent holding credentials to act on a system does not constitute authorization to act. Authorization is computed at decision time from autonomy ladder level + anti-alpha gates + agent_trust state + factory rules. This applies to API keys, RPC endpoints, exchange accounts, GitHub tokens, and Notion tokens identically.

**MC-05: Single highest-leverage move (this cycle).**
> The single highest-leverage move identified by the Agentic Engineering → Hermes Integration Blueprint is: write `docs/architecture/two_factories.md` and `docs/architecture/sosog_protocol.md` (in that order), because every other planned change is downstream of these two documents. Recorded so that future-Nick does not re-litigate priority.

### 13.2 Decision memory candidates (only after user answers Section 12)

These are *templates* that get filled in once the user answers the corresponding blocking question:

**MC-06 (template, fills from Q1):** *Repo home for harness work is `<answer>`.*
**MC-07 (template, fills from Q2):** *Notion mirroring of SOSOG is <enabled | deferred until <date> | rejected>.*
**MC-08 (template, fills from Q3):** *Agent Mode commits <may | may not> push to remote during Phases 1–4.*
**MC-09 (template, fills from Q4):** *SOSOG reviewer is <handle> until further notice.*
**MC-10 (template, fills from Q5):** *Factory names are "<sdlc-name>" and "<trading-name>".*

### 13.3 Anti-memory (things to NOT remember as durable doctrine)

The following items appeared in source material and should explicitly **not** become memory:

- "AFK is the future" (true for SDLC, false for trading; do not store unconditionally).
- "Rising API bill is a KPI" (SDLC-factory-only; misapplied to trading is dangerous).
- "ZTE / Robotaxi-level autonomy is the goal" (rejected for trading factory; SDLC-only and even there gated by evals).
- "Token-arbitrage > human-labor cost is the metric" (one metric among many for SDLC; not a metric for trading).
- "Vibe coding raises the floor; agentic engineering raises the ceiling" — true as a slogan but not actionable as memory; the actionable forms are MC-01 through MC-05.

Anti-memory entries should be stored as `failed_sosog_record` artifacts with explicit `failure_reason_if_any` so future agents do not silently re-import them.

---

## End of Part 4 — Blueprint complete

### Index

- **Part 1** — Executive Verdict, Source Inventory, Prior Work Audit (Sections 1–3)
- **Part 2** — Framework Extraction, Crosswalk Matrix, Hermes Strengths, Adopt/Adapt/Defer/Reject (Sections 4–7)
- **Part 3** — SOSOG Audit and Upgrade, Canonical Architecture Update (Sections 8–9)
- **Part 4** — Today's Build Plan, Agent Mode Handoff, Questions for User, Memory Candidates (Sections 10–13)

### Final reminders to user (planning mode close)

1. Nothing in this blueprint has executed. No repo files were created. No Notion pages were written. No GitHub commits were made. The artifacts that exist are the four blueprint files in `/workspace/research/`.
2. To proceed, answer the **5 blocking questions** in §12.1 and explicitly invoke the Section 11 handoff prompt under Agent Mode.
3. The single highest-leverage move, if you do nothing else: write `docs/architecture/two_factories.md`. It prevents the largest category error available (applying SDLC-factory practices to trading).
4. The blueprint deliberately does not solve `MEMORY.md`'s 5 pending items (API key, SupabaseMemoryProvider, OpenClaw status, Obsidian path, VPS deployment). Those are orthogonal decisions.
5. Doctrine, restated: *Context is the new code. Stand on the shoulders of giants. Determinism before autonomy. Evidence before execution. Build the system that builds the system.*
