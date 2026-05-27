# AGENTIC ENGINEERING → HERMES INTEGRATION BLUEPRINT
## Part 3 of 4 — SOSOG Audit & Upgrade + Canonical Architecture Update

> **Mode:** Planning only. No repo mutations, no Notion writes, no execution.
> **Continuity:** Continues from Part 2 (Framework Extraction, Crosswalk Matrix, Hermes Strengths, Adopt/Adapt/Defer/Reject).
> **Doctrine:** Context is the new code. Determinism before autonomy. Evidence before execution.

---

## Section 8 — SOSOG Audit and Upgrade

### 8.1 Why this section exists

The user's prompt explicitly flagged a structural weakness:

> "A Notion/document field that says 'SOSOG verified = contains two citations' is not sufficient."

This is a **correct and severe** self-criticism. In prior sessions and prior research outputs (including `HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md` and earlier canonical docs), SOSOG was operationalized as essentially a *citation count*. That is not a compliance object. That is a checkbox masquerading as rigor. It is the exact failure pattern Karpathy and Anthropic warn about when they describe "context-poor agents" — surface citations, no inference trail, no verification status, no decision lineage.

This section rewrites SOSOG as an **operational compliance object** with a typed schema, a Notion field mapping, a markdown template, weak/strong examples, and a pass/fail checklist. From this point forward, every claim that informs a Hermes design decision, a trade_card, an evidence_bundle, a candidate_signal, or a memory promotion **must** be backed by a SOSOG record that conforms to this schema.

### 8.2 Corrected definition

**SOSOG (Stand On Shoulders Of Giants)** is an operational compliance object that records, for any non-trivial claim used in Hermes design or execution, the *epistemic chain of custody*: which sources were consulted, what those sources actually said in context, what inference was drawn from them, what decision the inference produced, where that decision lands in the system, and whether it has been independently verified.

It is **not**:
- a citation count
- a "two links pasted at the bottom of a doc" affordance
- a tag in Notion
- a vibe

It **is**:
- a typed record with required fields
- replayable: anyone reading the record must be able to reconstruct the inference
- falsifiable: every record carries a `verification_status` and an explicit `failure_reason_if_any`
- governed: every record has a `reviewer` and a timestamp; unreviewed records cannot promote claims into canonical docs or trading paths

### 8.3 Required fields (canonical schema)

| Field | Type | Required | Purpose |
|---|---|---|---|
| `claim_id` | string (slug) | Yes | Stable identifier; format `sosog-YYYYMMDD-NNN-shortslug` |
| `claim_text` | string | Yes | The exact claim being defended, in one sentence |
| `claim_scope` | enum: `architecture` / `trading_logic` / `tooling` / `governance` / `eval` | Yes | Where this claim lands in Hermes |
| `source_1` | object: `{type, url_or_path, title, author, date, retrieval_method}` | Yes | First source |
| `source_1_context` | string (≥2 sentences) | Yes | The actual passage / behavior / data the source provides — quoted or paraphrased with locator |
| `source_2` | object (same shape as source_1) | Yes | Second source — must be **independent** of source_1 |
| `source_2_context` | string (≥2 sentences) | Yes | Same standard as source_1_context |
| `independence_note` | string | Yes | Why source_1 and source_2 are not the same chain (e.g. "source_1 is Karpathy keynote video; source_2 is Mario Zechner's blog and Pi repo — neither cites the other") |
| `inference_summary` | string (≥3 sentences) | Yes | The reasoning trail from sources → conclusion. Must reference both sources by name. |
| `decision` | string | Yes | The concrete decision produced by the inference (e.g. "Adopt typed tool catalog with 4 base tools + Hermes-specific extensions") |
| `implementation_target` | string | Yes | Where the decision lands: file path, doc section, ticket id, schema field |
| `confidence` | enum: `high` / `medium` / `low` | Yes | Subjective but typed; high requires both sources to be primary/authoritative |
| `verification_status` | enum: `Verified` / `Partial` / `Failed` / `Unreviewed` | Yes | Default `Unreviewed`; promoted only after explicit review |
| `failure_reason_if_any` | string \| null | Yes | If status is Partial or Failed, why. If Verified, must be `null`. |
| `reviewer` | string (handle) | Yes | Who reviewed and approved the record |
| `created_at` | ISO8601 | Yes | Auto |
| `updated_at` | ISO8601 | Yes | Auto |
| `supersedes` | claim_id \| null | No | If this record replaces an earlier one |
| `superseded_by` | claim_id \| null | No | Set when a newer record invalidates this one |
| `tags` | string[] | No | For retrieval (e.g. `["pillar:harness", "adopt"]`) |

**Hard rules:**
- Any record missing a required field → `verification_status` is forced to `Unreviewed`. It cannot be cited.
- A record with `verification_status: Failed` is preserved (append-only) but **cannot be referenced** as support for a downstream decision. It can be referenced as a *contradiction* artifact.
- `source_1_context` and `source_2_context` must contain actual content. "See link" is a fail.
- `independence_note` is the field that breaks the "two citations from the same article" failure mode.
- `inference_summary` must mention both sources by name. This breaks the "I read source 1 and ignored source 2" failure mode.

### 8.4 Notion field mapping

The Notion `SOSOG Records` database must have these properties (one-to-one with the schema above):

| Notion property | Type | Notes |
|---|---|---|
| Claim ID | Title | Primary key |
| Claim Text | Text | |
| Claim Scope | Select | Options match enum |
| Source 1 — Title | Text | |
| Source 1 — URL/Path | URL or Text | |
| Source 1 — Author | Text | |
| Source 1 — Date | Date | |
| Source 1 — Retrieval | Select: `web` / `pdf` / `repo` / `transcript` / `api` / `direct_observation` | |
| Source 1 — Context | Text (long) | Min 2 sentences |
| Source 2 — Title | Text | |
| Source 2 — URL/Path | URL or Text | |
| Source 2 — Author | Text | |
| Source 2 — Date | Date | |
| Source 2 — Retrieval | Select | |
| Source 2 — Context | Text (long) | Min 2 sentences |
| Independence Note | Text | |
| Inference Summary | Text (long) | |
| Decision | Text | |
| Implementation Target | Text or Relation (to Tickets DB) | |
| Confidence | Select: high/medium/low | |
| Verification Status | Select: Verified / Partial / Failed / Unreviewed | Default Unreviewed |
| Failure Reason | Text | Required if status ∈ {Partial, Failed} |
| Reviewer | Person or Text | |
| Created | Created time | Auto |
| Updated | Last edited time | Auto |
| Supersedes | Relation (self) | |
| Superseded By | Relation (self) | |
| Tags | Multi-select | |

> **Note for planning phase:** Notion mutations are deferred until Agent Mode. The schema above is the spec; the Notion update itself is a Phase 5 task in Part 4.

### 8.5 Markdown template (for in-repo SOSOG records)

Use this when a SOSOG record lives in `docs/sosog/` rather than (or in addition to) Notion. Plain markdown so it diffs cleanly in git.

```markdown
---
claim_id: sosog-20251125-001-pi-harness-minimalism
claim_text: A minimal 4-tool agent harness (read/write/edit/bash) with a hot-reloadable system prompt is sufficient as the kernel of an agentic engineering loop.
claim_scope: architecture
confidence: high
verification_status: Unreviewed
reviewer: null
created_at: 2025-11-25T00:00:00Z
updated_at: 2025-11-25T00:00:00Z
supersedes: null
superseded_by: null
tags: [pillar:harness, adopt, hermes-harness]
---

## Source 1
- **Title:** Pi: a tiny coding agent (blog post)
- **URL/Path:** https://mariozechner.at/posts/2025-pi/
- **Author:** Mario Zechner
- **Date:** 2025
- **Retrieval:** web (read directly)

### Source 1 Context
Mario describes Pi as a coding agent built around four primitive tools — read, write, edit, bash — plus a single editable `system.md` that the agent reloads on every turn. He explicitly argues that *most* of what people call "agent frameworks" are wrappers around these four primitives, and that the leverage comes from owning the system prompt and the tool surface, not from the framework. The repo (referenced in the post) shows the loop is roughly: read system.md → call model → dispatch tool → append result → loop.

## Source 2
- **Title:** Building Effective AI Agents — Anthropic engineering post and accompanying 3-pattern reference (orchestrator/worker, evaluator/optimizer, prompt chaining)
- **URL/Path:** https://www.anthropic.com/research/building-effective-agents
- **Author:** Anthropic
- **Date:** 2024
- **Retrieval:** web

### Source 2 Context
Anthropic's guidance is that effective agents are built from a small set of composable patterns over a thin tool layer; complexity should live in *evals and orchestration*, not in the harness. They explicitly recommend "start with the simplest thing that could work" and warn against premature framework adoption. Their reference implementations use ~3–6 tools and a tight loop, matching Pi's shape.

## Independence Note
Mario Zechner's Pi post is an independent open-source project blog. Anthropic's "Building Effective Agents" is a vendor engineering post. Neither cites the other. They converge on the same architectural conclusion via independent reasoning paths (Mario from "I want to read the source code", Anthropic from "we audited customer agent failures").

## Inference Summary
Both Mario (Pi) and Anthropic ("Building Effective Agents") arrive at the same conclusion from independent vantage points: the kernel of a useful agent is a thin tool surface (≤~6 tools) plus a hot-editable prompt, and the leverage is in the prompt + evals, not the framework. Mario demonstrates this empirically in <1k LOC; Anthropic demonstrates it across audited deployments. Therefore, for Hermes, the harness should be Pi-shaped — minimal kernel, typed tools, owned prompt — rather than LangChain/AutoGen-shaped. The Hermes-specific extension is that the tool catalog must include Hermes domain primitives (candidate_signal.read, evidence_bundle.build, trade_card.validate, etc.) governed by the autonomy ladder.

## Decision
Adopt a Pi-shaped harness as the Hermes agent kernel. Define a typed tool catalog: 4 base tools (read/write/edit/bash) + Hermes-specific tools that wrap canonical objects. The system prompt lives in the repo, is hot-reloaded, and is versioned.

## Implementation Target
- `docs/architecture/hermes_harness_spec.md` (new)
- `agent/system.md` (new, owned)
- `agent/tools/` (typed tool catalog)
- Spec section 16.5 (existing) — cross-reference

## Failure Reason
null
```

### 8.6 JSON pseudo-schema (for code that emits SOSOG records)

```jsonc
{
  "$schema": "https://hermes.local/schemas/sosog/v1.json",
  "claim_id": "string (regex: ^sosog-\\d{8}-\\d{3}-[a-z0-9-]+$)",
  "claim_text": "string (1..280)",
  "claim_scope": "architecture|trading_logic|tooling|governance|eval",
  "source_1": {
    "type": "blog|paper|video|repo|spec|api|direct_observation",
    "url_or_path": "string",
    "title": "string",
    "author": "string",
    "date": "YYYY-MM-DD|YYYY",
    "retrieval_method": "web|pdf|repo|transcript|api|direct_observation"
  },
  "source_1_context": "string (min 2 sentences, must contain content not just a link)",
  "source_2": { /* same shape as source_1 */ },
  "source_2_context": "string (min 2 sentences)",
  "independence_note": "string (must explain why s1 and s2 are not the same chain)",
  "inference_summary": "string (min 3 sentences, must reference s1 and s2 by name)",
  "decision": "string",
  "implementation_target": "string (file path | doc section | ticket id | schema field)",
  "confidence": "high|medium|low",
  "verification_status": "Verified|Partial|Failed|Unreviewed",
  "failure_reason_if_any": "string|null",
  "reviewer": "string|null",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "supersedes": "claim_id|null",
  "superseded_by": "claim_id|null",
  "tags": ["string"]
}
```

A linter (`tools/sosog_lint.py`, deferred to Agent Mode) will enforce:
1. All required fields present.
2. `source_1_context` and `source_2_context` ≥ 2 sentences and not equal to `url_or_path`.
3. `inference_summary` mentions both source titles or authors literally.
4. `independence_note` is non-empty.
5. If `verification_status` ∈ {Partial, Failed}, `failure_reason_if_any` is non-null.
6. If `verification_status` == Verified, `reviewer` is non-null.

### 8.7 Pass / Fail checklist (for human review)

A SOSOG record is **Verified** if and only if all of the following are true:

- [ ] `claim_text` is one specific testable sentence (not a vibe like "agents are good")
- [ ] `source_1` is primary or near-primary (author's own writing, repo, paper, direct observation)
- [ ] `source_2` is primary or near-primary AND independent of source_1
- [ ] `source_1_context` contains actual content (a quote, a behavior, a number, a code path) — not "see link"
- [ ] `source_2_context` contains actual content
- [ ] `independence_note` explains why the sources are not the same chain
- [ ] `inference_summary` references both sources by name and explains how the conclusion follows
- [ ] `decision` is concrete (a thing that can be done, not "consider X")
- [ ] `implementation_target` is a real path / section / ticket
- [ ] `reviewer` is set
- [ ] `failure_reason_if_any` is null
- [ ] No required field is empty

If any box fails: status is **Partial** (if the record is salvageable with edits) or **Failed** (if a source is wrong / contradicted / hallucinated). `failure_reason_if_any` is mandatory in both cases.

### 8.8 Strong vs weak example (calibration)

**Weak (would have passed the old "two citations" rule, fails the new schema):**

> Claim: "We should use AFK agents for Hermes."
> Source 1: IndyDevDan video.
> Source 2: IndyDevDan video transcript.
> Inference: Dan says AFK is the future.
> Decision: Adopt AFK.

This fails: sources are not independent (same chain), contexts are absent, inference does not engage with Hermes constraints (autonomy ladder, anti-alpha gates), decision is unscoped (AFK *what*? SDLC or trading?).

**Strong (passes):**

> Claim: "AFK / always-on agent operation is appropriate for Hermes' SDLC factory but must be rejected for the trading decision factory in its current form."
> Source 1: IndyDevDan transcript §Pillar 4 — argues "rising API bill is a KPI" and frames AFK as economic arbitrage on token cost vs senior engineer cost.
> Source 1 Context: Dan's framing assumes the work product is *code* whose downside is bounded by review and revert. He explicitly does not address domains where the agent's actions have unbounded financial downside.
> Source 2: Hermes Canonical Build Spec §3 (autonomy ladder) and §7 (anti-alpha gates) — defines evidence-gated autonomy, hard_fails, agent_trust EWMA with hysteresis.
> Source 2 Context: The spec mandates that promotion from shadow → probe → live is *evidence-gated, not time-gated*, and that any trade_card lacking a valid evidence_bundle cannot execute. AFK operation without these gates would violate the spec's "no evidence, no trade_card" principle.
> Independence Note: IndyDevDan's transcript is an external creator's framework; the Hermes spec is the user's own canonical artifact. They were authored independently and the spec predates the transcript ingestion.
> Inference: Dan's AFK argument is sound for code (bounded downside, revertable). The Hermes spec establishes that trading has unbounded downside and requires deterministic, gated execution. Therefore AFK is a clean fit for the SDLC factory (where Dan's economics apply) and a clean reject for the trading factory in its raw form. A constrained variant — "AFK research only, with human or council promotion to live" — is acceptable.
> Decision: Adopt AFK for SDLC factory. Reject AFK for trading execution. Adopt constrained AFK ("research-only AFK") for trading research with mandatory human or council promotion gate.
> Implementation Target: `docs/architecture/two_factories.md` §"AFK boundaries"; spec §3 cross-reference.
> Confidence: high. Verification Status: Verified. Reviewer: Nick.

### 8.9 Migration plan for existing claims

Every claim currently embedded in:
- `Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx`
- `MASTER_CONTEXT.md`
- `MEMORY.md`
- `research/HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md`
- This blueprint (Parts 1–4)

…must, over time, get a corresponding SOSOG record. This is **not** a today-task. The today-task is:

1. Stand up the schema (Section 9 below).
2. Write the first ~10 SOSOG records for the highest-leverage architectural claims (the ones in Part 2's Adopt/Adapt/Defer/Reject table).
3. Backfill the rest as claims are touched during normal work (lazy migration, not a rewrite sprint).

Hard rule going forward: **any new architectural claim added to canonical docs requires a SOSOG record before merge.**

---

## Section 9 — Canonical Architecture Update

This section specifies the *delta* the Hermes canonical artifacts need in order to absorb the IndyDevDan framework cleanly. It does not rewrite the spec; it lists the additions, the renamings, and the cross-references. Actual edits happen in Agent Mode.

### 9.1 New canonical vocabulary (additions to spec glossary)

| Term | Definition | Origin | Hermes scope |
|---|---|---|---|
| **Agent harness** | The minimal kernel: tool catalog + system prompt + loop. | IndyDevDan / Mario Zechner (Pi) | Hermes harness wraps canonical objects; lives in `agent/`. |
| **Software factory** | A repeatable, evaluated pipeline that produces software artifacts with declining marginal cost per unit. | IndyDevDan / Dan Shapiro / StrongDM | Hermes has **two** factories: SDLC factory and Trading decision factory. |
| **SDLC factory** | The factory that produces Hermes' own code, docs, evals, and tooling. | This blueprint | AFK-friendly. Token-arbitrage applies. |
| **Trading decision factory** | The factory that produces candidate_signals → evidence_bundles → trade_cards → execution decisions. | This blueprint | NOT AFK. Governed by autonomy ladder + anti-alpha gates. |
| **ADW (AI Developer Workflow)** | A scripted, evaluated agent loop targeted at a specific developer task. | IndyDevDan | Hermes ADWs live in `agent/workflows/`; each has an eval. |
| **AFK agent** | An agent run without continuous human supervision. | IndyDevDan | Permitted in SDLC factory; restricted to research-only in trading factory. |
| **Token arbitrage** | The economic delta: cost of agent tokens vs cost of equivalent human labor. | IndyDevDan | Tracked as KPI for SDLC factory only. Explicitly NOT a KPI for trading. |
| **Agentic access** | An agent's ability to act on the world via APIs, tools, or accounts. | IndyDevDan | Hermes scopes access via the autonomy ladder; access ≠ authorization. |
| **Extensible software** | Software designed to be modified by agents, not just humans (typed surfaces, machine-readable docs, OCP). | IndyDevDan | Hermes already practices this via canonical objects + ports/adapters. Reinforce. |
| **SOSOG record** | An operational compliance object (see §8). | Hermes (corrected definition) | Required for all non-trivial claims. |
| **Two-factory rule** | Any framework imported from external sources must be evaluated separately for SDLC vs Trading factory applicability. | This blueprint | Governance rule. |

### 9.2 New / clarified operating principles

Append to spec §2 (operating principles):

> 11. **Two factories, two regimes.** The SDLC factory and the Trading decision factory share infrastructure (canonical objects, memory, harness) but are governed by different rules. SDLC factory optimizes for token-arbitrage and throughput. Trading decision factory optimizes for evidence quality, replayability, and edge preservation. Practices appropriate to one are not automatically appropriate to the other.
> 12. **No SOSOG, no canon.** Any architectural claim added to canonical docs requires a SOSOG record (Verified or at minimum Unreviewed-with-intent-to-verify). Failed records cannot support canon claims.
> 13. **Harness ownership.** The Hermes agent harness, system prompt, and tool catalog are first-class repo artifacts, not vendor-supplied. They are versioned, hot-reloadable, and evaluated.
> 14. **Access ≠ authorization.** An agent having credentials to act does not authorize action. Authorization comes from the autonomy ladder + anti-alpha gates + agent_trust state.

### 9.3 Agent role additions / clarifications

Hermes spec §4 (agent council) should be extended with the following roles. Names are placeholders; the user gets to rename.

| Role | Purpose | Factory | Authority |
|---|---|---|---|
| **Harness Steward** | Owns `agent/system.md`, tool catalog, harness evals. | SDLC | Can merge harness changes after passing harness eval. |
| **SOSOG Reviewer** | Reviews SOSOG records for Verified status. | Both | Can promote `Unreviewed` → `Verified`. Cannot promote claims into canonical docs without record. |
| **Factory Auditor** | Audits two-factory rule compliance: catches "AFK in trading" or "ZTE in trading" violations. | Both | Veto over autonomy promotions. |
| **Eval Owner** | Owns the eval suite for each ADW and each canonical-object validator. | SDLC | Required signoff for any agent_trust EWMA parameter change. |

These roles can be played by the same human (Nick) initially. The point is the *role surface*, not headcount. When agents take over individual roles, the surface is already defined.

### 9.4 Document additions (planning targets — Agent Mode will create)

New documents, all under `docs/architecture/` unless noted:

1. `docs/architecture/two_factories.md` — defines SDLC factory vs Trading decision factory; their boundaries; the rules each obeys; the practices that cross over and the practices that do not. **This is the most important new doc.**
2. `docs/architecture/hermes_harness_spec.md` — Pi-shaped harness specification: tool catalog (typed), system prompt structure, loop semantics, hot-reload behavior, harness eval suite.
3. `docs/architecture/sosog_protocol.md` — operational SOSOG schema (mirrors §8 above), markdown template, JSON schema, lint rules, Notion field mapping.
4. `docs/architecture/agentic_access_policy.md` — what credentials Hermes agents may hold, how access is granted, how the autonomy ladder maps to access scopes, audit requirements.
5. `docs/architecture/adw_catalog.md` — index of ADWs (AI Developer Workflows): each ADW has a purpose, inputs, outputs, eval, and owner.
6. `docs/architecture/extensibility_charter.md` — how Hermes maintains OCP / extensibility for agent-driven modifications: typed canonical objects, machine-readable schemas, port/adapter discipline, deprecation policy.
7. `docs/governance/two_factory_rule.md` — the rule itself, with examples of correct and incorrect application.

### 9.5 Repo folder additions (planning targets)

```
hermes/
├── agent/
│   ├── system.md                     # NEW — owned, versioned, hot-reload
│   ├── tools/                        # NEW — typed tool catalog
│   │   ├── base/                     # read, write, edit, bash
│   │   └── hermes/                   # candidate_signal, evidence_bundle, trade_card, ...
│   ├── workflows/                    # NEW — ADWs, each with eval
│   └── evals/                        # NEW — harness + ADW evals
├── docs/
│   ├── architecture/                 # NEW docs listed in §9.4
│   ├── governance/
│   │   └── two_factory_rule.md       # NEW
│   └── sosog/                        # NEW — markdown SOSOG records
├── schemas/
│   └── sosog/v1.json                 # NEW — JSON schema for SOSOG
└── tools/
    └── sosog_lint.py                 # NEW — schema linter
```

### 9.6 Schema additions (planning — no creation in this mode)

In addition to the existing canonical schemas (`candidate_signal`, `evidence_bundle`, `trade_card`, `reject_card`):

- **`sosog_record/v1`** — see §8.6
- **`adw_definition/v1`** — name, purpose, inputs, outputs, eval_id, owner, factory (sdlc | trading_research)
- **`harness_eval_result/v1`** — eval_id, harness_version, pass/fail per case, regression vs prior version, agent_trust delta if any
- **`tool_catalog_entry/v1`** — tool name, signature, side-effects, factory restrictions, autonomy_min_level

All schemas live in `schemas/<name>/<version>.json` and follow the existing canonical schema discipline (versioned, additive-only, supersedes pointers).

### 9.7 Prompt additions (planning)

The `agent/system.md` (the Hermes harness system prompt) must, at minimum, encode:

- Hermes' core principles (the six "no X, no Y" lines).
- The two-factory rule.
- The autonomy ladder current level for the running agent.
- The tool catalog index.
- The SOSOG requirement for any architectural claim.
- The instruction: "If you believe a trade_card is justified but cannot produce a valid evidence_bundle, emit a reject_card and stop."

This is *not* a prompt to be written today (planning mode). It is a spec for what the prompt must contain.

### 9.8 Eval additions (planning)

| Eval | Scope | Pass condition |
|---|---|---|
| `harness_loop_eval` | Harness reads system.md, dispatches a tool, ingests result, re-prompts. | 100% deterministic pass on golden cases. |
| `tool_catalog_eval` | Each tool's signature is honored; side-effects are gated by autonomy level. | All tools pass; any failing tool is removed from catalog until fixed. |
| `sosog_lint_eval` | Run `sosog_lint.py` against `docs/sosog/`. | All records pass schema lint; any `Verified` record without reviewer fails. |
| `two_factory_audit` | Static check: any doc proposing AFK/ZTE/token-arbitrage as KPI in a trading-factory context fails. | Zero violations. |
| `evidence_bundle_replayability` | Existing eval; reinforced by harness. | Unchanged. |
| `agent_trust_hysteresis` | Existing eval. | Unchanged. |

### 9.9 Governance rule additions (planning)

Append to spec §governance:

> G-7. **Two-factory rule.** Before importing any external practice into Hermes (book, blog, video, framework), evaluate it independently for SDLC factory and Trading decision factory applicability. Document the decision in a SOSOG record with `claim_scope: governance`.
>
> G-8. **SOSOG-gated canon.** New text in the canonical spec, master context, or memory must reference at least one Verified SOSOG record. Unreferenced claims are quarantined to `docs/drafts/` until backed.
>
> G-9. **Harness eval gate.** Changes to `agent/system.md` or the tool catalog cannot merge without passing `harness_loop_eval` and `tool_catalog_eval`.
>
> G-10. **Reject-card-first discipline.** When evidence is insufficient for a trade_card, the harness must emit a reject_card. A trade_card without a valid evidence_bundle is a system bug, not a judgment call.

### 9.10 What does NOT change

Explicit non-changes (so we don't accidentally unwind hard-won structure):

- The edge equation stays. IndyDevDan's framework does not modify it.
- The autonomy ladder stays. AFK does not promote level; evidence does.
- The anti-alpha gates stay. They are stronger than anything in the framework.
- The deterministic sampler (HMAC salt + replay_epoch + sampler_version) stays. The framework does not address determinism; Hermes is ahead here.
- The append-only provenance memory stays. The framework's "context engineering" emphasis aligns; the implementation is already stronger.
- The trade_card / reject_card / evidence_bundle / candidate_signal canonical objects stay. They are Hermes' shape. The framework gets adapted *to* them, not the other way around.

### 9.11 Cross-reference index (so spec readers know where to look)

| Concept | Existing spec section | New doc to create |
|---|---|---|
| Agent harness | §16.5 (tool catalog) | `docs/architecture/hermes_harness_spec.md` |
| Two factories | (implicit in §3 + §7) | `docs/architecture/two_factories.md` |
| SOSOG | (referenced informally) | `docs/architecture/sosog_protocol.md` |
| Agentic access | (implicit in §3 autonomy ladder) | `docs/architecture/agentic_access_policy.md` |
| ADW catalog | (none) | `docs/architecture/adw_catalog.md` |
| Extensibility | (implicit in canonical objects) | `docs/architecture/extensibility_charter.md` |
| Two-factory rule | (none) | `docs/governance/two_factory_rule.md` |

### 9.12 Single highest-leverage architectural change

If only one architectural change is made from this entire blueprint, it should be:

> **Write `docs/architecture/two_factories.md` and the SOSOG protocol doc, in that order.**

Rationale: The two-factory doc prevents the entire IndyDevDan framework from being misapplied to trading (which would be a catastrophic category error: AFK trading, ZTE trading, token-arbitrage as trading KPI). The SOSOG protocol doc converts the user's existing rigor instinct into an enforceable schema. Every other change in this blueprint is downstream of these two documents.

---

## End of Part 3

**Next:** Part 4 contains Section 10 (Today's Build Plan — 6 phases), Section 11 (Agent Mode Handoff prompt), Section 12 (Questions for User), Section 13 (Memory Candidates).
