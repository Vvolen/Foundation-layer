# Agentic Engineering → Hermes Integration Blueprint
## Part 2 of 4 — Framework Extraction, Crosswalk, Hermes Strengths, Adopt/Adapt Decisions

---

## 4. IndyDevDan Framework Extraction (Operational Architecture)

### Pillar 1 — Agent Harness

- **Definition**: The runtime + coordination layer + configuration substrate within which an agent operates. It determines what context the agent sees, which tools it can call, how sub-agents are spawned, what memory it has, how output is validated, what guardrails apply.
- **Key practitioner insight**: The model is commodity. 200K tokens of the same model produce wildly different results based on harness design. **The harness is the source of differentiated leverage.**
- **Hidden implementation requirement**: The harness must treat configuration as **data, not code**. A harness you must edit Python/TypeScript to swap models, tools, or sub-agent topologies is a harness you do not own. Pi's pattern (system.md override, extension API, hot-reloading, session trees) instantiates this.
- **Failure mode if ignored**: You become a renter. Out-of-the-box harnesses (Claude Code, Codex, OpenCode) are 70%-effective on 100% of use cases — never specialized enough to beat a specialized harness in the same domain. You compete on prompts; specialists compete on systems.
- **Direct implication for Hermes**: The Hermes_Solana_Edge spec describes agents (search_memory, get_source_health, run_anti_alpha, etc.) but does not specify the *runtime*. That runtime IS the harness. **Hermes needs a Pi-based harness with a typed tool catalog matching the spec, sub-agent topology matching the agent council (Scout/Archivist/Plannotator/Bouncer/Guardian per MASTER_CONTEXT), and policy-as-data for autonomy ladder + guardrails.**
- **Vocabulary to preserve**: agent harness, harness engineering, sub-agent delegation, sandbox tool, model fallback, model routing, damage control, verifier harness, domain-specific harness, agent network, multi-agent orchestration.

### Pillar 2 — Software Factory / Dark Factory / ADW

- **Definition**: An automated pipeline of agents + code that converts a spec prompt into a near-production artifact through stages: spec → scout → build → validate → review → release. Templated, reproducible, on-spec every time.
- **Key practitioner insight**: A plan is a prompt scaled. The unit of engineering work shifts from feature → factory → spec. You stop writing features and start writing the system that writes features.
- **Hidden implementation requirement**: Every stage must be **machine-verifiable**. Specs must be schemas, not prose. Plans must be JSON or YAML, not bullet lists. Validators must be programs, not vibes. The factory only produces "on-spec results every time" if "spec" is a contract, not an aspiration.
- **Failure mode if ignored**: You climb to Level 2 (pairing with AI) or Level 3 (Waymo + safety driver) and plateau. Output scales linearly with hours, not with tokens. Other engineers compound past you in a few quarters.
- **Direct implication for Hermes**: There are **two factories** in Hermes — and they must NOT be conflated:
  - **The Hermes-build factory** (SDLC): produces signal-family modules, anti-alpha checks, evidence workers, dashboards. This factory should be aggressive, AFK-friendly, and run at Level 4–5.
  - **The Hermes-trade factory** (decision pipeline): candidate → evidence → gates → trade_card → execution. This factory must NEVER reach Level 5. Anti-alpha gates and human-in-the-loop are non-negotiable.
- **Vocabulary to preserve**: software factory, dark factory, ADW (AI Developer Workflow), spec prompt, plan prompt, plan reviewing, scouting, validating, reviewing, releasing, ZTE (Zero Touch Engineering), 5-level taxonomy (Shapiro).

### Pillar 3 — Extensible Software

- **Definition**: Software designed for change — open to extension, closed to modification. Pluggable adapters, hexagonal architecture, dependency inversion. Adding a new capability never requires editing the core.
- **Key practitioner insight**: At agent speed, brittle code is multiplicatively destructive. Every cross-module coupling forces the agent to load more context to make a safe change. Effective context shrinks relative to system complexity. Modular code lets the agent operate within bounded module context.
- **Hidden implementation requirement**: Hexagonal architecture with explicit ports/adapters. Domain core has zero dependencies on infrastructure. Adapters for LLM providers, databases, exchanges, RPCs are swappable without touching domain logic.
- **Failure mode if ignored**: The Hermes codebase becomes the cascading-if-statement mess Dan warns about. Every model change, vendor swap, or new signal family requires touching dozens of files. Agents make slow, error-prone changes. Velocity collapses.
- **Direct implication for Hermes**: The repo layout in the spec already gestures at this (`apps/`, `packages/schemas/`, `packages/sampler/`, `packages/gates/`) but does not enforce the hexagonal pattern. **Make the pattern explicit in the canonical doctrine: domain (signal families, gates, sampler) has no infrastructure imports; adapters wrap Birdeye/Dune/Helius/Tardis/Jupiter; ports are typed Pydantic/Zod schemas.**
- **Vocabulary to preserve**: extensible software, pluggable, composable, OCP (Open/Closed Principle), hexagonal architecture, ports & adapters, domain core, adapter swap, model agnosticism.

### Pillar 4 — Always-On / AFK Agents / Token Arbitrage / Tokenomics

- **Definition**: Three-level economic funnel: (1) spend tokens, (2) make tokens useful (value generation), (3) capture revenue from value. Only after Level 3 do you turn the agent on 24/7.
- **Key practitioner insight**: 90% of agent cron jobs are dead, useless, burning cash. The differentiator is not "agent runs all the time" — it is "agent runs all the time AND every token has positive marginal revenue."
- **Hidden implementation requirement**: An evaluation layer that quantifies value-per-token in real time. Without that, you cannot tell if AFK is producing or burning.
- **Failure mode if ignored**: Token-maxing — the agent runs forever, the bill goes up, no value is captured. Or worse: token spend is treated as a productivity KPI before arbitrage is verified, creating a confidence-spending loop with no underlying edge.
- **Direct implication for Hermes — TWO different reframings, do not conflate**:
  - **For SDLC work** (building Hermes itself): Token arbitrage = engineering throughput. Tokens that ship modules, schemas, evals, dashboards are valuable. Rising API bill IS a productivity KPI (per IndyDevDan). AFK overnight builds are good.
  - **For TRADING work**: Token arbitrage = realized PnL after slippage. Tokens that produce trade_cards which beat baselines after slippage and anti-alpha gates are valuable. Rising API bill is **NOT** a KPI; it is a cost to be amortized only against post-slippage PnL. AFK trading is the **autonomy ladder**, gated by agent_trust + evidence quality, not by time.
- **Vocabulary to preserve**: AFK agents, always-on agents, token maxing, token arbitrage, tokenomics 3-level funnel, token tax, token multiple (revenue/M tokens), API bill as KPI (with the trading caveat), graceful failure handling, blast radius controls.

### Pillar 5 — Agentic Access (API Reachability)

- **Definition**: Agents only command what they can programmatically reach. API access (CLI, REST, webhooks, RPC, MCP) is a requirement of agentic speed. Anything an agent does manually is a token tax.
- **Key practitioner insight**: Browser scraping a UI when an API exists is a 15× token-tax. Re-deriving state by reading files when an indexed search exists is a 10× tax. The tax compounds over thousands of operations.
- **Hidden implementation requirement**: Agent-first system design — CLIs before UIs, structured output (JSON) by default, idempotent operations, scoped permissions by default, principle-of-least-privilege for agents (more critical than for humans because errors compound at higher velocity).
- **Failure mode if ignored**: Agents grind through high-token inefficient paths to do things humans gave them no API for. Token cost goes up linearly with agent activity but value generation does not, so the token multiple collapses.
- **Direct implication for Hermes**: Every Hermes data source must have an adapter that returns typed JSON. No browser scraping in production paths. Solana RPC, Helius, Birdeye, Dune, Tardis, Jupiter, Arkham — all wrapped in adapters. Internal Hermes operations (memory query, candidate registry, evidence bundle creation, anti-alpha run, liquidity replay) must be exposed as **typed tool calls** to the harness, not as bash commands or file pokes.
- **Vocabulary to preserve**: agentic access, API access, CLI-first, structured output, idempotent operations, scoped permissions, token tax, principle of least privilege, MCP, RPC, REST, webhook, agent-first design.

---

## 5. Hermes Crosswalk Matrix

| IndyDevDan Concept | Practitioner Meaning | Hermes Existing Equivalent | Hermes Gap | Decision | Priority | Concrete Artifact Needed | First Implementation Ticket |
|---|---|---|---|---|---|---|---|
| Agent harness | Runtime + coordination + config substrate for agents | None — currently renting Claude Code, OpenClaw, SuperNinja | **Major gap** — no owned harness | **ADOPT** | P0 | `packages/harness/` — Pi-based skeleton with system.md, tool registry, sub-agent topology, policy.yaml | HARNESS-001: scaffold Pi extension repo with Hermes system prompt, four base tools, hot-reload |
| Sub-agent orchestration | Multi-agent teams with orchestrator/leads/workers | Agent council described conceptually (Scout, Archivist, Plannotator, Bouncer, Guardian) | Topology not implemented; no message bus, no role-based prompts | **ADAPT** | P0 | `packages/harness/sub_agents.yaml` — declarative topology with role prompts, tool subsets, trust thresholds | HARNESS-002: define Scout, Bouncer, Guardian as Pi sub-agents with restricted tool access |
| Verifier harness | Evaluator agent that checks generator output | Anti-alpha gate module + agent_trust EWMA + reject_card | Verifier covers anti-alpha; does NOT cover generated *code* (e.g., new detector code) | **ADAPT** | P1 | `packages/harness/code_verifier.py` — schema-validates new signal-family modules before commit | HARNESS-003: code-level verifier for SDLC factory only (NOT trading path) |
| Software factory (SDLC) | Spec → scout → build → validate → review → release pipeline | None — sprint plan in spec is human-driven | **Major gap** for SDLC factory | **ADOPT** (for SDLC only) | P1 | `factories/sdlc/` — spec_prompt.md, scout_prompt.md, build_prompt.md, validate.py, review_prompt.md | FACTORY-001: build the spec-to-PR pipeline for new signal family modules |
| Software factory (TRADING) | Spec → scout → build → validate → release for trading decisions | candidate → evidence → gates → trade_card → execution | This IS Hermes's existing trade pipeline | **Already present, RENAME canonically** | P0 | Update spec to call this the "decision factory"; explicitly distinguish from SDLC factory | DOC-001: vocabulary update in canonical doctrine |
| Plan prompt / spec prompt | Templated meta-prompt that generates a structured execution plan | None — sprint plans are prose | Gap for SDLC; trading has typed candidate_signal which is the spec-equivalent | **ADOPT** for SDLC; trading already has it | P1 | `prompts/sdlc/spec_prompt.md`, `prompts/sdlc/plan_prompt.md` | PROMPT-001: write spec_prompt that converts a Hermes feature request into a typed plan |
| Plan review | Agent that critiques the plan before build | None | Gap | **ADOPT** for SDLC | P2 | `prompts/sdlc/plan_review_prompt.md` | PROMPT-002: plan reviewer with "what would break this?" prompt |
| Scouting | Agent reads existing codebase and annotates the plan with file-level impact | None | Gap | **ADOPT** for SDLC | P2 | `agents/scout/` (SDLC scout, separate from trading Scout) | AGENT-001: SDLC scout with read-only repo tools |
| Validation | Test runner agent that catches regressions | Existing pytest plan in spec; agent_trust tests | Tests not yet written; no test orchestrator agent | **ADAPT** | P1 | `tests/replay/`, `tests/integration/`, validation agent | TEST-001: replay test for sampler determinism |
| Testing (trading) | Backtest runner + forward test + replay | Backtest runner module already specified in section 16.4 | Not yet built | **BUILD per spec** | P0 | `apps/workers/backtest_runner/` | BACKTEST-001: persistence + second-leg detector backtest |
| Reviewing | Code/output review agent | None for code; agent_trust for trading outputs | Gap for code | **ADOPT** for SDLC | P2 | `prompts/sdlc/review_prompt.md` | PROMPT-003: code review agent with security + style checklist |
| Extensible plugins / adapters | Pluggable, swappable interfaces | Repo layout gestures at this; not enforced | Hexagonal pattern not formalized | **ADAPT** | P1 | `ARCHITECTURE.md` mandating hexagonal, port/adapter interfaces | DOC-002: architecture doc with adapter examples |
| Model routing / fallbacks | Dynamic model selection per task | None — Hermes uses one provider | Gap | **ADAPT** | P2 | `packages/harness/model_router.py` with fallback chain | HARNESS-004: model router with per-task model assignment |
| Sandboxing / damage control | Locked-down bash, scoped permissions | Pi has system.md override; Hermes spec mandates guardrails (`no_trade_without_valid_trade_card`) | Sandbox config not formalized | **ADAPT** | P0 | `packages/harness/sandbox.yaml` — bash allowlist, filesystem boundary, network policy | HARNESS-005: bash allowlist for trading agents (read-only RPC, no execute) |
| Token tax (avoid) | API access for everything an agent touches | Spec lists tools but does not enumerate token-tax audit | Gap | **ADAPT** | P1 | `docs/agentic_access_audit.md` — list every Hermes operation and its API | DOC-003: agentic access audit |
| Token arbitrage (SDLC) | Revenue per token in engineering throughput | None — no SDLC token accounting | Gap | **ADOPT** | P3 | Token spend tracking on factory runs | METRICS-001: token cost per ADW run |
| Token arbitrage (trading) | Realized post-slippage PnL per token | Edge equation in spec is the trading-side analog | Spec equation accounts for cost terms but not token cost specifically | **ADAPT — extend edge equation** | P2 | Update edge equation to include `token_cost_per_decision` | DOC-004: extended edge equation |
| AFK agents (SDLC) | Always-on engineering agents | None | Gap | **DEFER** until factory exists and produces value | P3 | Cron + monitoring | AFK-001 (deferred) |
| AFK agents (trading) | Always-on autonomous trade execution | Autonomy ladder (human → shadow → probe → live) | Spec is correct — autonomy is evidence-gated, not time-gated | **REJECT IndyDevDan framing for trading**; keep Hermes autonomy ladder | P0 | DOCTRINE statement: "trading AFK is governed by autonomy ladder, not by IndyDevDan AFK doctrine" | DOC-005: autonomy doctrine |
| Agentic access (general) | API reachability for all tools | Tools listed in spec section 16.5 | Adapter implementations not built | **ADOPT** | P1 | Adapter modules per source | ADAPTER-001 through ADAPTER-007: Birdeye, Dune, Helius, RPC, Tardis, Arkham, Nansen |
| MCP / CLI / API exposure | Agent-callable interfaces | Hermes itself is MCP-capable per prior research | Hermes-internal operations not exposed as MCP yet | **ADAPT** | P2 | MCP server exposing memory/candidate/evidence operations | MCP-001: Hermes-internal MCP server |
| Domain-specific harness | Specialized harness per domain | None — one general approach | Gap, but a feature: a Solana-trading-specific harness IS the moat | **ADOPT** | P0 | `packages/harness/solana_trading/` — specialized harness with trading tools, anti-alpha guardrails, autonomy enforcement | HARNESS-006: Solana-trading harness profile |
| ZTE / zero-touch engineering | Spec → production with zero human intervention | Existing autonomy ladder ends at "live execution" but only after evidence | **For SDLC**: aspirational, OK; **for trading**: REJECTED — Hermes will never be true ZTE | **ACCEPT for SDLC, REJECT for trading** | — | DOCTRINE statement | DOC-006 (already covered by DOC-005) |
| Always-on monitors | Continuous source-health, telemetry, kill-switch monitors | source_health object + Prometheus + kill switches in spec | Not yet wired | **BUILD per spec** | P1 | Monitor service | MONITOR-001: source_health monitor with kill-switch integration |
| Governed autonomy | Autonomy bounded by guardrails and trust | autonomy ladder + agent_trust + guardrails — strongest in spec | Already present | **CANONICALIZE** | P0 | DOCTRINE statement framing this as Hermes's strongest asset | DOC-007: governed autonomy is Hermes's signature |

---

## 6. What Hermes Already Has That Is Stronger

This section is critical: do not let the IndyDevDan vocabulary import erode Hermes's existing rigor. The following Hermes elements are **stronger than the augmented deep dive's prescriptions** and must be preserved.

### 6.1 Deterministic sampler vs. generic agent harnessing

- **IndyDevDan's view**: Harness is the substrate; tools are commodity.
- **Hermes's view**: Sampling is itself a tool, and it must be **deterministic with replay_epoch + sampler_version + HMAC salt** (spec section 16.1).
- **Why Hermes wins for trading**: A generic harness samples non-deterministically. Hermes's deterministic sampler produces auditable, replayable evidence — necessary because every trade decision must be reconstructible at any future point. **Trading evidence is a legal/forensic artifact, not a debug aid.**
- **Implication**: The Hermes harness must enforce that any tool that produces evidence emits sampler metadata. This is **stricter** than IndyDevDan's harness blueprint.

### 6.2 Anti-alpha gates vs. generic validation

- **IndyDevDan's view**: An "evaluator agent" calibrated with rubrics catches what the generator misses.
- **Hermes's view**: Every signal is **guilty until it survives falsification** (spec section 9). Hard fails (`TINY_LIQUIDITY`, `LIQUIDITY_SLIPPAGE_GT_LIMIT`, `WASH_SCORE_GT_LIMIT`) and soft warnings are typed, deterministic, and explainable — not "agent reviews agent."
- **Why Hermes wins**: Adversarial markets reward agents that abstain. Generic LLM-evaluator harnesses will get gamed by wash trading, sybil attacks, and spoofed liquidity. Deterministic gates with structured failure codes are not gameable in the same way.
- **Implication**: Anti-alpha gates are **infrastructure**, not agent reasoning. The harness exposes them as tools, but their logic is in `packages/gates/` as deterministic Python — never an LLM call.

### 6.3 trade_card / reject_card vs. generic planning artifacts

- **IndyDevDan's view**: A plan is a prompt scaled.
- **Hermes's view**: A trade_card is an evidence-bound, forensically-traceable, schema-versioned, slippage-aware decision artifact. A reject_card captures correct abstention and is treated as an asset (spec section 8.4).
- **Why Hermes wins**: IndyDevDan's "plan as scaled prompt" is appropriate for SDLC. For trading, plans must include execution mode, route provider, TTL, evidence refs, and manual review flags. **A "plan" without these fields is unsafe.**
- **Implication**: Do not import the "plan = prompt" framing into the trading layer. It already has trade_card. Use IndyDevDan's plan vocabulary only for SDLC factory.

### 6.4 Append-only provenance memory vs. generic agent memory

- **IndyDevDan's view**: Externalize memory; filesystem and artifact stores are working memory; persistent knowledge in retrieval layer.
- **Hermes's view**: Never mutate primary fact records. Add superseding records with valid_from/valid_to. Every record stores source, source_id, actor, ingest_time, schema_version, confidence, canonical_hash. Contradictions are first-class (spec section 13).
- **Why Hermes wins**: Append-only memory + provenance enables **post-hoc audit of any decision at any time**. Generic externalized memory does not. For trading, this is the difference between "we caught a regulator's question" and "we are exposed."
- **Implication**: Any memory provider integration (Honcho, MEM0, Supabase, etc.) must respect Hermes's append-only contract. The SupabaseMemoryProvider work item must enforce this.

### 6.5 Truth / Evidence / Learning loops vs. generic software factory

- **IndyDevDan's view**: Spec → scout → build → validate → review → release.
- **Hermes's view**: Three connected loops — sources → candidate registry → evidence → gates → trade_card → execution → post-trade attribution → memory + trust updates (spec section 4).
- **Why Hermes wins**: Hermes's loops include **post-trade attribution feeding agent_trust + signal_family_scores** — a self-correcting system. Generic factory diagrams stop at "release."
- **Implication**: Use the IndyDevDan factory pattern only for SDLC. Hermes's three-loop trading pattern is non-negotiable.

### 6.6 Autonomy ladder vs. generic AFK agents

- **IndyDevDan's view**: Once token arbitrage is positive, turn the agent on 24/7.
- **Hermes's view**: Autonomy is gated by agent_trust EWMA with hysteresis (block below 0.35, recover only above 0.45) AND evidence-loop completeness AND no critical telemetry gaps (spec section 5.1).
- **Why Hermes wins**: IndyDevDan's "token arbitrage → AFK" is correct for SDLC where mistakes are reversible (revert a commit). For trading, mistakes are capital losses. Time-based AFK is **dangerous**. Evidence-based autonomy is **necessary**.
- **Implication**: Reject "always-on AFK trading" framing. Keep the autonomy ladder. Frame AFK trading as the *outcome* of the ladder, not its goal.

### 6.7 Source-health and telemetry gates vs. generic always-on agents

- **IndyDevDan's view**: Always-on monitors are good.
- **Hermes's view**: A candidate cannot be promoted if primary source is stale, secondary source contradicts materially, or vendor response is missing required lineage (spec section 6.1). Source health is a **gate**, not a dashboard.
- **Why Hermes wins**: Generic always-on agents keep running on stale data because no one wired source_health into their gates. Hermes refuses to act when telemetry is bad.
- **Implication**: source_health is the kill-switch. The harness must respect it. Any "always-on" Hermes agent has source_health veto power over its own actions.

---

## 7. Adopt / Adapt / Defer / Reject Decision Table

| Item | Category | Reason | SOSOG Support | Implementation Artifact | Owner Module | Acceptance Criteria |
|---|---|---|---|---|---|---|
| Pi-based agent harness | **Adopt immediately** | No owned harness exists; Pi is the strongest substrate per prior research and IndyDevDan endorsement; aligns with "context is the new code" doctrine | Sources: IndyDevDan transcript [Pillar 1 + Resources section]; lucumr.pocoo.org/2026/1/31/pi (Pi deep dive); HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md (prior session, 4-tool minimalism analysis) — **Status: SOSOG-Verified** | `packages/harness/` repo skeleton with system.md, tool registry, policy.yaml, sub-agent topology | Harness package | Skeleton compiles + loads system prompt + registers 4 base tools + hot-reloads on config change |
| SDLC software factory | **Adopt immediately** (scaffolding only) | High leverage for building Hermes itself; reversible mistakes; Level 4 target reasonable | Sources: IndyDevDan Pillar 2; Dan Shapiro 5-level taxonomy [danshapiro.com]; Anthropic 3-agent harness [infoq.com] — **Status: SOSOG-Verified** | `factories/sdlc/` directory with spec_prompt.md, plan_review.md, scout, validator, reviewer | Factory package | Single round-trip: spec prompt → plan → scouted plan → builder writes a stub module → validator runs pytest → reviewer outputs PR comment |
| Hexagonal architecture mandate | **Adopt immediately** | Spec already gestures at this; making it explicit prevents drift | Sources: IndyDevDan Pillar 3; Hermes_Solana_Edge spec section 15.2 (repo layout) — **Status: SOSOG-Partial** (one frontier source + one canonical doc; would benefit from a third architecture text) | `ARCHITECTURE.md` defining domain core, ports, adapters | Doctrine doc | Doc states "no domain module imports infrastructure; all I/O via adapters; ports are typed schemas" |
| SOSOG schema upgrade | **Adopt immediately** | Current SOSOG is informal; cannot scale to canonical doc gating | Sources: User's stated SOSOG protocol (MASTER_CONTEXT + repeated emphasis); current "2 citations" weakness self-evident — **Status: Self-evident from prompt** | `schemas/sosog_claim.json` + Notion DB schema + markdown template | Schema package | Schema validates a sample claim; Notion DB has all required fields; markdown template renders correctly |
| Solana-trading-specific harness profile | **Adopt immediately** (scaffolding) | Specialization is the moat; this IS the differentiator | Sources: IndyDevDan Pillar 1 ("specialization is the moat"); Hermes_Solana_Edge spec sections 5, 9, 11 (agent contracts + anti-alpha + execution) — **Status: SOSOG-Verified** | `packages/harness/solana_trading/profile.yaml` | Harness package | Profile loads, restricts tool access to trading-relevant only, enforces autonomy ladder gate |
| Token-tax audit | **Adopt** | High-ROI exercise; identifies missing adapters | Sources: IndyDevDan Pillar 5; Hermes spec section 6 (data source strategy) — **Status: SOSOG-Verified** | `docs/agentic_access_audit.md` listing every Hermes operation + its API | Doc | Doc enumerates all Hermes ops; gaps marked; ranked by token cost |
| Spec / plan prompt templates (SDLC only) | **Adopt** (after harness scaffolded) | Required for SDLC factory; trading already has trade_card | Sources: IndyDevDan Pillar 2; Anthropic 3-agent harness — **Status: SOSOG-Partial** (one frontier source + one industry blog) | `prompts/sdlc/*.md` | Prompt library | Spec prompt produces typed plan JSON; plan review prompt produces structured critique |
| Plan reviewer agent (SDLC) | **Adapt** | Adds verifier rigor without copying generic evaluator pattern | Sources: IndyDevDan; Anthropic 3-agent (planner/generator/evaluator) — **Status: SOSOG-Verified** | `agents/sdlc/plan_reviewer/` | Factory | Reviewer can flag a deliberately-bad plan as bad on a known test case |
| Code-level verifier (SDLC) | **Adapt** | Anti-alpha is for trading; SDLC needs a separate code verifier | Sources: IndyDevDan; Anthropic — **Status: SOSOG-Partial** | `factories/sdlc/code_verifier.py` | Factory | Verifier runs pytest + lint + import-cycle check + schema validation on generated module |
| Model router with fallbacks | **Adapt** (after harness exists) | Hermes spec only assumes one provider; multi-provider routing improves reliability | Sources: IndyDevDan Pillar 1 (model fallbacks as harness feature); Modern Agent Harness Blueprint [GitHub Gist] — **Status: SOSOG-Verified** | `packages/harness/model_router.py` | Harness | Router falls back from primary to secondary on rate-limit/error |
| AFK agents for SDLC factory | **Adopt** | Reversible work; AFK overnight builds compound | Sources: IndyDevDan Pillar 4 (with prerequisites); StrongDM/Anthropic precedent — **Status: SOSOG-Verified** | `factories/sdlc/afk_runner/` | Factory | AFK runner picks queued specs, runs full ADW, posts results to Slack/Notion |
| AFK trading | **Reject as currently framed** | IndyDevDan time-based AFK is incompatible with autonomy ladder; only evidence-based progression to live trading is acceptable | Sources: Hermes_Solana_Edge spec section 5.1 (autonomy ladder), section 18 ("what I would not build yet"), section 19 (operating principles); IndyDevDan Pillar 4 — **Status: SOSOG-Verified contradiction** | DOCTRINE statement: trading autonomy is evidence-gated only | Doctrine doc | Doctrine doc explicit that "AFK trading" is the outcome of the autonomy ladder, never the goal |
| Token arbitrage = revenue/M tokens for trading | **Reject as primary metric** | Trading metric is post-slippage PnL after anti-alpha gates, not generic value/token | Sources: Hermes spec edge equation; IndyDevDan tokenomics — **Status: SOSOG-Verified contradiction** | DOCTRINE statement | Doctrine doc | Doctrine states trading uses extended edge equation, not token-multiple framing |
| ZTE for trading | **Reject** | Trading is irreversible; ZTE incompatible with anti-alpha + autonomy ladder | Sources: IndyDevDan; Hermes spec section 18 — **Status: SOSOG-Verified** | DOCTRINE statement | Doctrine doc | Stated explicitly |
| ZTE for SDLC | **Prototype carefully** | Long-term aspiration; not a current goal | Sources: Dan Shapiro 5-level (Level 5); IndyDevDan — **Status: SOSOG-Verified** as aspiration | None today | Future | Not a 2026 goal; revisit when SDLC factory is at Level 4 |
| Always-on KOL/social monitor | **Defer until signal proof** | Hermes spec explicitly defers this; social signals need cross-validation first | Sources: Hermes spec sections 1.2, 18 — **Status: SOSOG-Verified** | None | Future | Re-evaluate after first signal family graduates |
| Heavy local GPU hosting | **Defer** | Spec section 18 defers; not a bottleneck | Sources: Hermes spec section 18 — **Status: SOSOG-Partial** | None | Future | Re-evaluate when latency/cost/privacy becomes blocking |
| Multi-panel dashboard before objects stable | **Defer** | Spec explicitly warns against | Sources: Hermes spec section 18 — **Status: SOSOG-Verified** | None | Future | Build dashboard only after trade_card/reject_card/evidence_bundle stable |
| MCP server exposing Hermes internals | **Adapt** (later) | Useful for cross-tool agentic access; not P0 | Sources: IndyDevDan Pillar 5; HERMES_VS_OPENCLAW prior research (Hermes is MCP-capable) — **Status: SOSOG-Verified** | `apps/mcp_server/` | App | MCP server exposes memory query, candidate registry, evidence bundle creation as MCP tools |
| Obsidian integration | **Adapt** (later) | User has 4 candidate paths; choose after harness exists | Sources: prior session research — **Status: SOSOG-Partial** | TBD | App | Choose path after harness profile is stable |
