# Agentic Engineering → Hermes Integration Blueprint

## Part 1 of 4 — Executive Verdict, Source Inventory, Prior Work Audit

**Mode:** Planning only. No mutations. No Agent Mode handoff executed.
**Date:** 2026-05-25
**Author:** SuperNinja (architect role)
**Inputs:** IndyDevDan transcript + augmented analysis, Hermes_Solana_Edge_Canonical_Build_Spec_v1, MASTER_CONTEXT.md, prior research (`research/HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md`, `research/SUPERNINJA_ENVIRONMENT_ASSESSMENT.md`), MEMORY.md.

---

## 1. Executive Verdict

The IndyDevDan video is not new philosophy. It is **vocabulary** — a clean, frontier-practitioner naming layer for things Hermes is already half-built around. The real opportunity is not to copy his framework. It is to **canonicalize** Hermes's existing discipline (deterministic sampling, anti-alpha gates, evidence bundles, replayability, agent trust, autonomy ladder) using his vocabulary, and then **adopt the two pieces Hermes is genuinely missing**: an **owned agent harness** and a **software factory**.

Stated bluntly:

**Hermes is already further down the agentic-engineering road than the video describes**, in the dimensions that matter for trading. Where IndyDevDan talks about "evaluator agents" and "validation phases" as aspirations, Hermes already has anti-alpha gates, reject_cards, agent_trust EWMA, schema-versioned signal families, and append-only provenance memory. The Hermes spec encodes a stricter operating doctrine than any harness blueprint surfaced in the augmented deep dive: *No evidence, no trade_card. No valid trade_card, no execution. No source freshness, no promotion. No replay, no research claim. No postmortem, no learning.* That doctrine is more rigorous than a generic "evaluator harness" because it ties autonomy to **realized financial outcome quality**, not to "did the code compile."

**Where Hermes is behind**: it does not yet own a **harness**. The user is currently renting Claude Code, Codex-style tooling, OpenClaw, and SuperNinja. Each is good at one thing, none of them is the *substrate* the Hermes operating doctrine runs on. The Hermes_Solana_Edge spec describes agent contracts, tools, guardrails, and an autonomy ladder, but it does not specify *the runtime in which those agents execute*. That is the gap. IndyDevDan's claim "whoever owns the harness controls the results" lands directly on this gap.

**Where Hermes is also behind**: it does not yet have a **software factory**. The build spec describes signal families, anti-alpha gates, evidence bundles, and a sprint plan, but it treats each component as a thing to be built by humans. The IndyDevDan thesis — *don't build the feature, build the system that builds the feature* — applied to Hermes means: build the spec-prompt → scout → build → validate → review → release pipeline that produces signal-family modules, anti-alpha checks, evidence workers, and dashboards on demand. Not for trading execution (that needs human-in-the-loop and anti-alpha gates), but for the *meta-engineering work of growing Hermes itself*.

**What changes about Hermes after reading this video:**

1. The "agent council" stops being a logical concept and becomes a **harness specification** — concrete runtime, tool catalog, sub-agent topology, memory boundaries, and policy-as-data configuration. Pi is the strongest candidate substrate based on prior research.
2. The Sprint 1 plan in the spec ("first two-week sprint") gets a new Sprint 0 above it: **build the factory that builds Sprint 1**. Spec prompts, plan reviewers, scouting agents, validators — applied to Hermes's *own* development, not to trading.
3. SOSOG becomes a **schema**, not a tradition. Right now SOSOG lives as a vibe ("two cited sources"). It should become a typed object stored alongside trade_cards and reject_cards, with a verification status field gating whether claims propagate to canonical docs.
4. Tokenomics gets a Hermes-specific reframing: token arbitrage in trading is **alpha**, not productivity. The "rising API bill is a KPI" reframe is correct for SDLC work but **dangerous for trading**. Anti-alpha gates exist precisely to prevent token-spend-as-success thinking from corrupting the trading loop.
5. The autonomy ladder in the Hermes spec gets renamed/reformatted in IndyDevDan's vocabulary: human → shadow → probe → live becomes "Level 3 (review) → Level 4 (long AFK cycles with approval) → Level 5 (dark factory)" — but the *gates* between levels are not time-based, they are evidence-based. Hermes's version is stricter and should remain so.

**What to do today:** produce the canonical doctrine document, the SOSOG schema, and the Pi-based Hermes harness skeleton — all as planning artifacts. Do not commit code. Do not stand up infrastructure. Do not configure provider keys yet. The single highest-leverage move is **agreeing on the canonical vocabulary and doctrine in writing, then specifying the harness**. Code follows.

**What NOT to do today:** Do not start writing the deterministic sampler, anti-alpha gate, or any Hermes module until the harness is specified. Do not push the Hermes_Solana_Edge spec to a public GitHub repo before the SOSOG audit completes. Do not stand up always-on agents before evidence-loop infrastructure exists. Do not import the IndyDevDan "rising API bill is a KPI" framing into the trading layer — it belongs only in the SDLC/factory layer.

The single highest-leverage move is **specifying the Pi-based Hermes harness with a typed tool catalog matching the spec's `tools:` section, a sub-agent topology matching the agent council, and policy-as-data configuration that encodes the operating principles**. That artifact is what unlocks every subsequent build sprint and is what the next agent should produce in Agent Mode.

---

## 2. Source Inventory and Confidence

| Source | Contribution | Reliability | Cannot Prove | Canonical? |
|---|---|---|---|---|
| `The_#1_Opportunity_for_Senior_Engineers_Agentic_Engineering_—_Full_Transcript_+_Augmented_Deep_Dive.md` | Five-pillar vocabulary; Karpathy/Sequoia framing; Pi/Mario harness substrate; Dan Shapiro 5-level taxonomy; tokenomics 3-level funnel; Anthropic 3-agent harness reference | High for vocabulary and framing; Medium for specific implementation claims (transcript + 16 cited references, but most refs are blog posts and Reddit threads, not peer-reviewed) | Whether IndyDevDan's "one new harness per day" actually scales; whether StrongDM's Level-5 dark factory is reproducible outside their domain; whether Pi remains the right substrate as Anthropic / OpenAI iterate | **Yes for vocabulary**, no for specific implementation prescriptions. Adopt the words; verify the practices independently. |
| `Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx` (existing) | Full architecture: edge equation, autonomy ladder, agent contracts, anti-alpha gates, canonical objects (candidate_signal, evidence_bundle, trade_card, reject_card), sampler design, sprint plan, repo layout, schema appendices | High — this is the user's own canonical document. The discipline encoded (no evidence/no trade_card, replayability, append-only memory) is more rigorous than the augmented deep dive's prescriptions. | Whether the chosen first signal family (persistence + second-leg continuation) actually has positive forward edge after slippage; whether the EWMA agent_trust formula calibrates well in practice | **Yes — this is the spine.** All other docs reference this. |
| `MASTER_CONTEXT.md` | User identity, cognitive style, tool stack, project list, communication preferences, philosophy ("context is the new code") | High for current state; medium for "current" because dated May 12 — tools may have shifted | Whether all listed projects are still active; whether "Hermes v0.1" tooling is current vs. evolved | **Yes — identity layer.** Should be referenced by every agent. |
| `research/HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md` (prior session) | 600-line SoSoG comparison; concludes Hermes superior for this stack due to (1) pluggable memory providers mapping to Supabase, (2) deterministic hooks, (3) Python ecosystem alignment; identifies Pi as OpenClaw's embedded engine | Medium-High — heavy citations, internally consistent, but written before the IndyDevDan vocabulary landed; needs vocabulary refresh | Whether Hermes's official memory providers (Honcho/MEM0/etc) actually integrate cleanly with the Supabase Hardcore Memory OS without a custom SupabaseMemoryProvider being built | **Yes for content**, but should be augmented with IndyDevDan vocabulary and re-stamped after this blueprint lands. |
| `research/SUPERNINJA_ENVIRONMENT_ASSESSMENT.md` (prior session) | Sandbox capability audit (3.8 GB RAM, 1.8 GB disk, no Docker, no GPU); recommends Hetzner CPX11 €4.15/mo for production | High for environment facts; medium for VPS recommendation (Hetzner is reasonable but not benchmarked against alternatives) | Whether Hermes + OpenClaw + Hermes harness will all fit in the Hetzner CPX11 simultaneously; whether the user actually wants to leave the SuperNinja sandbox | **Yes for environment**, action item: revisit deployment target after harness skeleton exists. |
| `MEMORY.md` (prior session) | User context, active tool stack, pending decisions, governance protocol, Notion integration status | High — current as of this session start | Whether "pending decisions" are still pending after this blueprint | **Yes — session memory.** Will be updated at end of this planning task. |
| Notion workspace pages (3, created prior session) | External persistence of HERMES_VS_OPENCLAW + ENVIRONMENT_ASSESSMENT + MEMORY | High that they exist; the API call returned 200 + URLs | Whether the user has reviewed them; whether their content matches local files exactly (block conversion may have lossy edges) | Reference only. Local files are canonical. |

**Sources I do NOT have access to that would change confidence:**

- The IndyDevDan video itself (only the transcript). No way to verify visual demos (UI A J team multi-agent chat, Pi extension demos).
- The current state of the `foundation-layer` directory in `/workspace` — listed in `ls` but not opened.
- The GitHub repo `Vvolen/Foundation-layer` — referenced in the system message but not browsed.
- Any actual Hermes runtime artifacts. Hermes v0.14.0 was installed in the prior session but never configured with a provider key, so no real session output exists.
- The user's Supabase project state — `Supabase_check.txt` exists but was treated as "actual current state" rather than build spec; not re-verified this session.
- The current state of the `openclaw-files/` workspace — IDENTITY/SOUL/USER markdown files exist but are blank templates per prior session notes.

---

## 3. Prior Work Audit

### 3.1 What was actually built or changed (verified)

- **Hermes v0.14.0 installed via `pip install hermes-agent`** in the SuperNinja sandbox. `hermes doctor` returned healthy. 8 memory providers detected (byterover, hindsight, holographic, honcho, mem0, openviking, retaindb, supermemory). 13/26 tools active. **No provider API key configured** — the agent cannot actually run a chat session yet. **Verified.**
- **OpenClaw running as systemd service** in the sandbox. PID varies across restarts; gateway listens on port 18789; `/health` returns `{"ok":true,"status":"live"}`. Settings sync service also running. **Verified across 10+ health checks this session and previous.**
- **3 Notion pages created** in the user's "Agentic Domain" workspace under parent page "Hermes vs OpenClaw Research — SuperNinja Session Output" (ID `36badf44-73ce-8138-99c3-f299510689ef`). Direct REST API used; MCP path was timing out. **Verified — page IDs and URLs returned by API.**
- **Local research artifacts** in `/workspace/research/`: HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md (38 KB) and SUPERNINJA_ENVIRONMENT_ASSESSMENT.md (8 KB), with local git repo initialized and one commit. **Not pushed to any remote** — bot token lacks repo creation permissions on `gh`. **Verified.**
- **MEMORY.md** at `/workspace/MEMORY.md` — session memory file with user context extracted from MASTER_CONTEXT.md, governance protocol, pending decisions, Notion integration status. **Verified.**

### 3.2 What was proposed but not built

- **SupabaseMemoryProvider** for Hermes — listed as the "critical integration point" in the prior session's analysis. Not implemented. No code, no schema, no plugin scaffold.
- **OpenClaw → Hermes migration** — `hermes claw migrate` exists; the `openclaw-migration` skill was blocked by Hermes's security scan. Override path identified (`--force`) but not exercised.
- **Hermes provider configuration** — no API key configured, no `~/.hermes/.env` populated. Provider choice (Anthropic vs OpenRouter vs Nous Portal) was raised as a pending decision but not resolved.
- **Production VPS deployment** — Hetzner CPX11 recommended; no provisioning attempted.

### 3.3 Questions the previous agent asked

The previous session ended with five pending decisions (from MEMORY.md):

1. **Hermes API key** — which provider? (Anthropic / OpenRouter / Nous Portal)
2. **SupabaseMemoryProvider** — build it?
3. **OpenClaw** — keep running or stop?
4. **Obsidian integration** — which path? (MCP Tools / Hermes Console / semantic MCP / Agent Client)
5. **Production deployment** — sandbox or VPS?

**Audit verdict**: Questions #1, #4, #5 are operational; they should be answered after the harness is specified, not before, because the harness specification will constrain the answers. Question #2 (SupabaseMemoryProvider) is a real architectural decision and should be answered as part of the harness spec — the answer is almost certainly **yes**, but only after the Pi-based harness contract is defined. Question #3 (keep OpenClaw running) is RAM-budget housekeeping and should be deferred until harness deployment target is chosen.

### 3.4 Which prior outputs were SOSOG-verified, partially verified, weak

| Output | SOSOG Status | Notes |
|---|---|---|
| HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md | **Partial** — has 15 cited sources, but many are blog posts and one comparison article (innfactory.ai) is cited heavily. Inference trail is documented but not always explicit. | Needs upgrade per SOSOG audit (Section 8 of this blueprint). |
| SUPERNINJA_ENVIRONMENT_ASSESSMENT.md | **Verified** for environment facts (uname, free, df all confirmed); **Weak** for production VPS recommendation (Hetzner CPX11 cited from one source, no benchmarking) | Hetzner claim should be marked SOSOG-partial. |
| MEMORY.md | **Verified** for user context (sourced directly from MASTER_CONTEXT.md); **Inferred** for pending decisions framing (not all framings were validated by the user) | Re-affirm with user. |
| Notion pages | **Verified** that pages exist; **Cannot verify** content fidelity (block conversion may have lost markdown table formatting, code blocks, etc.) | Treat local files as canonical. |

### 3.5 What is missing from the audit trail

- No record of **what the user actually consumed** vs. what was produced. The user has not confirmed reviewing the Notion pages or local research files.
- No **changelog file** — research/ directory has one git commit but no CHANGELOG.md mapping decisions to artifacts.
- No **decision log** — pending decisions are listed but not numbered/dated/linked to the artifacts that depend on them.
- No **explicit non-goals list** for prior session — research scope grew (OpenClaw deep dive, environment assessment, Notion integration) without an upfront non-goals declaration.

### 3.6 What needs to be checked before Agent Mode

Minimum information needed checklist:

- [ ] User confirms the Notion pages have been reviewed and are acceptable as external persistence
- [ ] User confirms the Hermes_Solana_Edge spec is the **current** canonical spec (no newer version exists locally or in Notion)
- [ ] User confirms which GitHub repo should be canonical for Hermes Solana Edge (`Vvolen/Foundation-layer` mentioned in system messages — is that the target?)
- [ ] User confirms which Notion workspace/database should host the upgraded SOSOG schema and the canonical doctrine document
- [ ] User confirms SuperNinja sandbox is the development environment, NOT production
- [ ] User confirms preferred LLM provider for Hermes (Anthropic / OpenRouter / Nous Portal) — this affects harness configuration
- [ ] User confirms whether OpenClaw stays running (RAM budget) or stops (free 426 MB for harness experiments)
- [ ] User confirms today's blast radius: documents only, or document + skeleton repo + skeleton schema files?
