# SUPER_NINJA_MEMORY.md — User Context & Session State

## User Identity

- **Profile:** Self-taught AI orchestration architect in Tucson, AZ
- **Estimated IQ:** ~160
- **Cognitive Style:** ADHD hyperfocus (deep dive mode, not scattered attention), voice-first workflow
- **Experience:** 2+ years daily immersion in AI agent ecosystems, zero formal coding background
- **Philosophy:** "Context is the new code" — 5-layer context engineering stack

## Active Tool Stack

- **Primary Agents:** Claude, Hermes Agent, Manus AI, SuperNinja, GitHub Copilot Pro+
- **Infrastructure:** Supabase (V0 Hardcore Memory OS), OpenClaw (running in SuperNinja sandbox)
- **Workflow:** Wispr Flow (voice), n8n (automation)
- **Development:** GitHub, VS Code

## Key Projects

1. **Hermes Agent OS** — Building the canonical Solana trading intelligence stack on Hermes
2. **Solana Trading Intelligence Stack** — Evidence-first architecture, agent council, anti-alpha gates
3. **AWS AgentCore Architecture** — Cloud deployment patterns for agent workloads
4. **Polymarket Trading System** — Prediction market analysis and execution

## Critical Architecture Documents

- `Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx` — The "main spine of everything"
- `Supabase_check.txt` — Actual current Supabase state (NOT a build spec)
- `Memory_for_Hermes..txt` — 40-source Hermes memory ecosystem analysis
- `Phase_shift_skills.txt` — Top 10 phase-shift skills for agent development
- `LINKS_CATEGORIZED.md` — Categorized link library

## Communication Protocol

- **DO NOT:** Give generic advice, validate without pushback, stop at concepts, overwhelm with options
- **DO:** Push back when something won't work, go beyond concepts to implementation, present best-path recommendations rather than menus
- **PREFERRED:** Voice-first interaction, structured output, cited sources (SoSoG Protocol)

## Research Completed This Session

1. **Hermes vs OpenClaw Comprehensive Analysis** — Full comparison with SoSoG Protocol, saved to `research/HERMES_VS_OPENCLAW_COMPREHENSIVE_ANALYSIS.md`
2. **SuperNinja Environment Assessment** — Capability audit, deployment feasibility, saved to `research/SUPERNINJA_ENVIRONMENT_ASSESSMENT.md`
3. **All uploaded files read and indexed** — 9 files + 1 zip extraction
4. **Key web sources scraped** — Hermes Quickstart, Hermes Docker docs, Pi framework deep dive, OpenClaw Pi integration architecture, innfactory.ai comparison, HackerNoon comparison
5. **Agentic Blueprint (4 parts)** — Full framework verdict, crosswalk, SOSOG rewrite, and build plan. Saved to `research/AGENTIC_BLUEPRINT_PART_1-4_*.md`
6. **Frontier Memory File Research (SOSOG)** — 6 sources: Buildcamp CLAUDE.md guide, Claude Code memory docs, Anthropic context engineering paper, Claude-Mem context engineering, Turing Post Hermes vs OpenClaw, Steinberger blog. Key findings: file hierarchy > file size, under 300 lines hand-crafted, context rot is n², JIT retrieval beats pre-loading, Hermes 4-layer memory is state of art, hooks > instructions for enforcement

## Notion Integration — RESOLVED

- **Workspace:** "Agentic Domain: The Door to the Future" (Nick Carter's)
- **Bot:** SuperNinja (ntn_466...)
- **Parent Page:** [Hermes vs OpenClaw Research — SuperNinja Session Output](https://www.notion.so/Hermes-vs-OpenClaw-Research-SuperNinja-Session-Output-36badf4473ce813899c3f299510689ef)
  - Child 1: [Hermes vs OpenClaw — Comprehensive Analysis](https://www.notion.so/Hermes-vs-OpenClaw-Comprehensive-Analysis-SoSoG-Protocol-36badf4473ce81c2911fcb87a3f136ed) (⚡)
  - Child 2: [SuperNinja Environment Assessment](https://www.notion.so/SuperNinja-Environment-Assessment-Deployment-Feasibility-36badf4473ce81909071d39c3a02e1cb) (🖥️)
  - Child 3: [Session Memory & Governance Protocol](https://www.notion.so/Session-Memory-User-Context-Governance-Protocol-36badf4473ce81c7b7f1edf3c2ee3cd6) (🧠)
- **GitHub MCP:** Running but bot token lacks repo/gist creation permissions
- **Direct Notion API:** Works perfectly via REST API with bot token

## Pending Decisions

1. **Hermes API key** — Which provider to configure? (Anthropic, OpenRouter, Nous Portal) Required to make Hermes functional
2. **SupabaseMemoryProvider** — Build for Hermes to connect existing memory OS?
3. **OpenClaw** — Keep running as messaging bridge, or stop to free resources?
4. **Obsidian integration** — Which path? (MCP Tools, Hermes Console, semantic MCP, Agent Client)
5. **Production deployment** — Run Hermes in this sandbox (tight) or external VPS (Hetzner CPX11 €4.15/mo recommended)?

## Frontier Research: Memory Files & Context Engineering (SOSOG-Backed)

Sources: Buildcamp CLAUDE.md guide, Claude Code memory docs, Anthropic context engineering paper, Claude-Mem context engineering docs, Turing Post Hermes vs OpenClaw, Peter Steinberger blog

### What the Frontier Is Doing

**1. File hierarchy matters more than file size.** The frontier has converged on a layered approach: a user-level global file (~/.claude/CLAUDE.md) for identity and universal rules, a project-root file (./CLAUDE.md) for project-specific context, a personal override file (./CLAUDE.local.md) that's gitignored, and a scoped rules directory (.claude/rules/*.md) with YAML frontmatter that loads rules only when relevant files are touched. This is progressive disclosure — the agent doesn't read everything every time, it loads what it needs when it needs it.

**2. Under 200-300 lines, hand-crafted, never auto-generated.** The consensus is clear: auto-generated memory files are worse than nothing because they create noise. Every line must be universally applicable to sessions in that scope. If something is only relevant sometimes, it belongs in a scoped rule file, not the main memory.

**3. Context rot is real and measurable.** Anthropic's own research shows that attention degrades quadratically (n²) as context grows. The "Goldilocks zone" for system prompts exists — too little and the agent lacks direction, too much and every token fights for attention. The discipline is finding the smallest set of high-signal tokens.

**4. Just-in-time retrieval beats pre-loading.** Instead of stuffing everything into memory upfront, the frontier uses retrieval that pulls relevant context on-demand. Hybrid approaches (some static core + dynamic retrieval) perform best. Hermes Agent does exactly this: ~1.3k tokens of static core (MEMORY.md + USER.md), then SQLite FTS5 for session history search, then optional Honcho layer for user modeling, then skills as a fourth "procedural memory" layer.

**5. Hermes' memory architecture is the current state of the art.** Four layers: (a) persistent core identity docs (~1.3k tokens), (b) SQLite FTS5 full-text search across session history, (c) Honcho user modeling for personalized behavior, (d) skills as procedural memory — workflows that were learned and can be re-executed. The self-improving loop is what makes it different: it converts successful workflows into reusable skills automatically.

**6. Hooks > instructions for deterministic enforcement.** If something MUST happen every time (like "always run the linter before committing"), use a hook (a script that runs automatically), not an instruction in a memory file. Memory files are for guidance, not enforcement. This is the difference between a policy and a law.

### What Files We Should Consider Adding

| File | Purpose | Loaded When |
|------|---------|-------------|
| `CLAUDE.md` (project root) | Project-specific rules, build commands, architecture decisions | Every session in this workspace |
| `CLAUDE.local.md` | Personal preferences, API keys, paths — gitignored | Every session, never shared |
| `.claude/rules/trading.md` | Scoped rules that load only when trading files are touched | When trading work happens |
| `.claude/rules/research.md` | Scoped rules for research workflow (SOSOG, citation standards) | When research work happens |
| `SOUL.md` | Agent identity — values, personality, boundaries | Every session (global, not workspace-tied) |
| `SKILLS/` directory | Procedural memory — learned workflows as executable scripts | On-demand |

### OpenClaw vs Hermes — The Real Story

Peter Steinberger built OpenClaw as a vibe-coded project — 450,000+ lines of code generated across 45 simultaneous Codex sessions. He spent $1.3M in tokens in a single month. OpenAI hired him to work on Codex. OpenClaw is now moving to a foundation. The architecture is control-plane-first: a central gateway that routes messages between models, with human-authored skills and workspace-tied identity.

Hermes Agent (Nous Research) came along and did what Steinberger did, but architecturally superior, because the people behind it actually design agent systems for a living. Hermes is execution-loop-first: the agent's own do-learn-improve cycle is the center, not a gateway. Skills are self-generated from experience, not human-authored. Identity is instance-global (SOUL.md), not workspace-tied. Memory is layered, not flat. Security is 5-layer by default. It can even auto-migrate from OpenClaw.

The key insight: OpenClaw is a router. Hermes is an organism. One routes messages, the other learns and evolves. For what you're building — trading intelligence that compounds over time — you need the organism, not the router.

## Self-Evolving Loop Structure

This memory file should be updated at the start and end of each session. The governance protocol is:
1. Read this file at session start
2. Update "Research Completed" and "Pending Decisions" as work progresses
3. Before session end, capture any new context that future sessions need
4. Apply SoSoG Protocol: any new claim added must have 2+ cited sources

## End-of-Session Summary Protocol

**RULE: At the end of every session, produce a summary with these sections:**

1. **What Happened** — 3-5 sentence plain-English summary of what was accomplished
2. **What Changed** — Files created, modified, or deleted (with paths)
3. **What's Pending** — Unresolved decisions, open questions, next steps
4. **What I Learned About You** — Any new context about the user's preferences, workflow, or thinking that future sessions should know

This summary should be appended to the session's final response AND used to update this MEMORY.md file before closing.

---

*Last updated: 2026-05-26 — Frontier research on memory.md/CLAUDE.md completed, end-of-session summary protocol added, OpenClaw turned OFF, HANDOFF.md created*
*Next update: When new research or decisions are made*
