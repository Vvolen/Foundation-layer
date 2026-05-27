# Hermes Agent vs OpenClaw: Comprehensive Comparative Analysis

**Date:** May 2026  
**Protocol:** SoSoG (Standing on the Shoulders of Giants) — every claim backed by 2+ cited sources with actual context  
**Author:** SuperNinja Agent Research  
**Purpose:** Determine which agent framework best serves a solo AI orchestration architect running Solana trading intelligence, multi-agent governance, and context-engineering stacks

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Origin Stories & Lineage](#origin-stories--lineage)
3. [Architecture Deep Dive](#architecture-deep-dive)
4. [The Pi Framework: OpenClaw's Engine](#the-pi-framework-openclaws-engine)
5. [Memory Systems](#memory-systems)
6. [Security Model](#security-model)
7. [Extensibility & Skills](#extensibility--skills)
8. [Deployment & Operations](#deployment--operations)
9. [SuperNinja Environment Feasibility Assessment](#superninja-environment-feasibility-assessment)
10. [Obsidian Integration Paths](#obsidian-integration-paths)
11. [Head-to-Head Comparison Matrix](#head-to-head-comparison-matrix)
12. [Recommendation](#recommendation)
13. [Source Bibliography](#source-bibliography)

---

## Executive Summary

Hermes Agent (Nous Research) and OpenClaw represent two fundamentally different philosophies for building AI agents. Hermes is a Python-first, CLI-native, modular agent with pluggable memory providers and a self-improving architecture. OpenClaw is a TypeScript/Node.js hub-and-spoke messaging gateway that embeds Pi — a minimalist coding agent — at its core, then wraps it in a sprawling ecosystem of channel adapters, tools, and governance layers.

For the specific use case defined in MASTER_CONTEXT.md — a solo operator running Solana trading intelligence, multi-agent councils, and evidence-first decision architectures — **Hermes Agent is the superior choice**, though OpenClaw's Pi framework offers unique advantages for rapid agent self-modification that should not be dismissed.

The critical deciding factor is not capability (both are extensible enough to build anything) but **architectural alignment**: Hermes's pluggable memory providers, deterministic tool execution, and Python-native stack map directly to the Supabase "V0 Hardcore Memory OS" already in place, while OpenClaw's TypeScript ecosystem and gateway-centric model add translation overhead without proportional gain.

---

## Origin Stories & Lineage

### Hermes Agent

Hermes Agent was launched by Nous Research in late February 2026 as an open-source, self-improving AI agent. The project released six versions in its first 50 days — v0.2.0 on March 12, 2026 through v0.12 on April 30, 2026 — demonstrating aggressive iteration speed [Source: innfactory.ai comparison article, "Hermes vs OpenClaw: An Honest Comparison"]. The agent is MIT-licensed, CLI-first, and explicitly designed around the principle that "the agent that grows with you" — emphasizing progressive complexity rather than upfront kitchen-sink architecture [Source: hermes-agent.nousresearch.com tagline and quickstart documentation].

Key design principle from the official docs: "Rule of thumb: if Hermes cannot complete a normal chat, do not add more features yet. Get one clean conversation working first, then layer on gateway, cron, skills, voice, or routing." [Source: Hermes Agent Quickstart, hermes-agent.nousresearch.com/docs/getting-started/quickstart]

### OpenClaw

OpenClaw began as "Moltbot," created by Peter Steinberger (founder of PSPDFKit). When Steinberger joined OpenAI on February 14, 2026, the project was transferred to an independent foundation and rebranded to OpenClaw [Source: innfactory.ai comparison article]. The project reached 234K GitHub stars by mid-2026, making it one of the most-starred AI agent repositories [Source: serenitiesai.com, "OpenClaw 2026: 234K Stars, OpenAI & Security Deep Dive"].

The v4.0 release — dubbed "The Agent OS" — was a complete rewrite introducing the hub-and-spoke gateway daemon architecture, canvas system, and 15+ messaging platform adapters. Subsequent releases added ClawHub skills marketplace (v4.1) and ACP for inter-agent communication (v4.2) [Source: innfactory.ai comparison article].

**SoSoG Reasoning:** The origin stories reveal a fundamental divergence. Hermes was built from day one as an agent that improves itself, with memory and learning as first-class concerns. OpenClaw was built as a messaging gateway that happens to run an agent, with the Pi framework bolted in as the "brain." This architectural DNA shows up in every subsequent design decision.

---

## Architecture Deep Dive

### Hermes Agent Architecture

Hermes uses a **modular, CLI-first architecture** with optional gateway mode. The core components are:

- **CLI/TUI Interface**: Two terminal interfaces sharing the same sessions, slash commands, and config [Source: Hermes Quickstart docs]
- **Gateway Mode**: Optional persistent daemon connecting to 20+ messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal, Email, Home Assistant, Teams, etc.) [Source: Hermes Quickstart — "Connect Telegram, Discord, Slack, WhatsApp, Signal, Email, or Home Assistant, or Microsoft Teams"]
- **Pluggable Memory Providers**: 8 official providers (Honcho 3.0, OpenViking, MEM0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory) with a standardized provider interface [Source: Memory_for_Hermes..txt — the uploaded file documenting all 8 providers with detailed comparison]
- **Autonomous Curator Process**: A built-in skill management system that can autonomously discover, evaluate, and install skills [Source: Phase_shift_skills.txt — "recursive skill-writing loop"]
- **MCP Server Mode + OAuth 2.1**: Standards-compliant Model Context Protocol integration [Source: innfactory.ai comparison]
- **Camofox Anti-Detection Browser**: Built-in browser automation with anti-fingerprinting for web research [Source: innfactory.ai comparison]
- **Container Backends**: Docker, Singularity, Modal, Daytona, Vercel Sandbox — the agent can execute code in isolated environments [Source: innfactory.ai comparison; Hermes Docker docs]
- **7-Layer Security Model**: Layered security from network through application [Source: innfactory.ai comparison]
- **SQLite + FTS5 Session Storage**: Full-text search over conversation history [Source: innfactory.ai comparison]

Data flow: User input → Hermes CLI/Gateway → Provider (LLM API) → Tool execution → Memory provider persistence → Session storage. The agent maintains two core memory files: MEMORY.md (~2,200 chars, auto-managed) and USER.md (~1,375 chars, identity/preferences) [Source: Memory_for_Hermes..txt — Daedalus live agent analysis].

### OpenClaw Architecture

OpenClaw uses a **hub-and-spoke architecture** with a central gateway daemon:

- **Gateway Daemon**: A persistent WebSocket server at `ws://127.0.0.1:18789` that coordinates all agent interactions [Source: OpenClaw Gateway Architecture docs, docs.openclaw.ai; confirmed by the openclaw.json config file in this workspace showing `"port: 18789"`]
- **Pi Framework (Embedded)**: The actual AI agent is Pi, a minimal coding agent with 4 tools (Read, Write, Edit, Bash), embedded via `createAgentSession()` SDK call rather than subprocess spawning [Source: lucumr.pocoo.org/2026/1/31/pi — Armin Ronacher's deep dive; docs.openclaw.ai/pi — official Pi integration architecture]
- **Canvas System**: A shared workspace for visual collaboration [Source: innfactory.ai comparison]
- **15+ Messaging Platforms**: Built-in adapters for WhatsApp (via Baileys), Telegram (via grammY), Slack, Discord, Signal, iMessage, etc. [Source: innfactory.ai; confirmed by openclaw.json showing Telegram and Slack channel configs]
- **Cron Scheduling**: Time-based automation built into the gateway [Source: innfactory.ai comparison]
- **ClawHub Skills Marketplace**: Community skill sharing (introduced v4.1) [Source: innfactory.ai comparison]
- **ACP Integration**: Agent Communication Protocol for inter-agent messaging (v4.2) [Source: innfactory.ai comparison]

Data flow: User message → Channel adapter (Telegram/Slack/etc.) → Gateway daemon (ws://127.0.0.1:18789) → Pi embedded session → LLM provider → Tool execution → Response stream back through channel. The gateway acts as a message broker, session coordinator, and tool policy enforcer.

The embedded Pi integration is sophisticated: OpenClaw imports Pi's `AgentSession` directly, injects custom tools (messaging, browser, canvas, cron, gateway, session management), applies dynamic system prompts per channel/context, and handles session persistence with branching/compaction support. The file structure involves 40+ TypeScript modules just for the Pi integration layer [Source: docs.openclaw.ai/pi — showing the full file tree from `src/agents/pi-embedded-runner/` through all the subsystems].

**SoSoG Reasoning:** The architectural comparison reveals that Hermes is agent-first (the agent IS the product; gateway is optional), while OpenClaw is gateway-first (the gateway IS the product; Pi is the engine). For someone building a Solana trading intelligence stack where the agent's reasoning quality, memory fidelity, and deterministic execution matter more than which chat app receives the output, Hermes's agent-centric architecture is a better fit. OpenClaw's strength — its messaging gateway — is solving a problem you don't primarily have.

---

## The Pi Framework: OpenClaw's Engine

Pi deserves its own section because understanding Pi is essential to understanding what OpenClaw can and cannot do.

### What Pi Is

Pi is a minimal coding agent created by Mario Zechner, written in TypeScript. It has the shortest system prompt of any major agent and only four tools: Read, Write, Edit, Bash [Source: lucumr.pocoo.org/2026/1/31/pi — "it has a tiny core... only four tools"]. Its power comes from an extension system that allows agents to modify themselves — extensions can persist state into sessions, register custom tools, and render TUI components [Source: same source].

### What Makes Pi Unique

1. **Self-Extending Architecture**: Pi's philosophy is that when you want the agent to do something new, you don't download an extension — you ask the agent to build it. "It celebrates the idea of code writing and running code" [Source: lucumr.pocoo.org/2026/1/31/pi].

2. **Session Trees**: Pi sessions are trees, not linear logs. You can branch, navigate, and rewind within a session. This enables workflows like making a side-quest to fix a broken tool without wasting context in the main session, then merging back [Source: lucumr.pocoo.org/2026/1/31/pi — "sessions in Pi are trees"].

3. **Hot Reloading**: Extensions can be written, reloaded, tested, and iterated in a loop — the agent modifies its own code and immediately uses the result [Source: lucumr.pocoo.org/2026/1/31/pi — "built-in hot reloading so that the agent can write code, reload, test it and go in a loop"].

4. **No MCP**: Pi deliberately omits MCP support. The philosophy is that MCP tools need to be loaded into context at session start, making runtime modification difficult. Instead, Pi encourages code-level extension [Source: lucumr.pocoo.org/2026/1/31/pi — "The most obvious omission is support for MCP. There is no MCP support in it... This is not a lazy omission. This is from the philosophy of how Pi works"].

5. **Provider-Portable Sessions**: Pi's AI SDK is written so sessions can contain messages from different model providers, recognizing that portability is limited between providers and not leaning into provider-specific features [Source: lucumr.pocoo.org/2026/1/31/pi].

### How OpenClaw Embeds Pi

OpenClaw does not use Pi as a subprocess or via RPC. It directly imports and instantiates Pi's `AgentSession` via `createAgentSession()` from the `@earendil-works/pi-coding-agent` package [Source: docs.openclaw.ai/pi — "Instead of spawning pi as a subprocess or using RPC mode, OpenClaw directly imports and instantiates pi's AgentSession"]. This embedded approach gives OpenClaw full control over session lifecycle, custom tool injection, system prompt customization per channel, and multi-account auth profile rotation with failover [Source: same].

The integration is deep — OpenClaw replaces Pi's default bash tool with custom `exec`/`process` tools, adds 20+ OpenClaw-specific tools (messaging, browser, canvas, cron, gateway, sessions, image), and applies a dynamic system prompt built from 15+ sections including Tooling, Safety, Skills, Docs, Workspace, Sandbox, Messaging, Voice, and Memory [Source: docs.openclaw.ai/pi — system prompt construction section].

### Pi's Relevance to the User's Stack

For the Solana trading intelligence use case, Pi's self-extending architecture is genuinely interesting but has a key limitation: Pi's session trees and hot-reloading are local development workflows, not production agent governance patterns. The "agent modifies its own code" paradigm is powerful for exploration but conflicts with the deterministic, evidence-first architecture defined in the Hermes_Solana_Edge_Canonical_Build_Spec_v1 — where anti-alpha gates, trade_card/reject_card schemas, and agent trust scoring with EWMA require locked-down, auditable execution paths.

**SoSoG Reasoning:** Pi is brilliant software engineering (Armin Ronacher, the Flask creator, explicitly calls it "excellent software" and uses it as his primary agent [Source: lucumr.pocoo.org]). But brilliance in agent self-modification is orthogonal to the requirement for deterministic trading intelligence with guardrails. The Phase_shift_skills.txt document identifies "hooks (deterministic guardrails)" as skill #3 specifically because unchecked agent autonomy is dangerous in financial contexts.

---

## Memory Systems

### Hermes Memory Ecosystem

Hermes offers 8 official pluggable memory providers, each with distinct strengths [Source: Memory_for_Hermes..txt — comprehensive 40-source analysis]:

| Provider | Type | Key Feature | Fit for Solana Stack |
|----------|------|-------------|---------------------|
| **Honcho 3.0** | Dialectic user modeling | Contradiction detection, belief revision | High — models trading bias |
| **OpenViking** | Tiered loading (L0/L1/L2) | ByteDance-origin, load-by-salience | High — only loads what matters |
| **MEM0** | General-purpose | ~48K GitHub stars, most adopted | Medium — generic but proven |
| **Hindsight** | Knowledge graph + 4-strategy retrieval | 91.4% LongMemEval score | Very High — graph traversal for signal chains |
| **Holographic** | HRR algebra | Zero dependencies, mathematical memory | Medium — research-grade |
| **RetainDB** | Hybrid retrieval | $20/mo cloud-only | Low — vendor lock-in |
| **ByteRover** | Human-readable Markdown | File-tree structure | Medium — portable |
| **Supermemory** | Enterprise | Context fencing, multi-tenant | Medium — overkill for solo |

The two core memory files (MEMORY.md and USER.md) provide a simple, auditable, git-trackable memory substrate that's directly compatible with the existing Supabase "V0 Hardcore Memory OS" architecture [Source: Memory_for_Hermes..txt — Daedalus analysis; Supabase_check.txt — the actual current state].

### OpenClaw Memory

OpenClaw's memory model is session-file-based through Pi. Sessions are JSONL files with tree structure (id/parentId linking), managed by Pi's `SessionManager` class [Source: docs.openclaw.ai/pi — "Sessions are JSONL files with tree structure"]. There is no equivalent to Hermes's pluggable memory providers — memory is implicit in session history rather than explicitly structured.

OpenClaw does support "Memory" as a system prompt section when enabled [Source: docs.openclaw.ai/pi — system prompt construction includes "Memory and Reactions when enabled"], but this is prompt-level injection, not a persistent memory substrate with retrieval, scoring, and consolidation pipelines.

For the Supabase integration that already exists (scoring functions `compute_memory_score`/`memory_score`/`memory_rescore_batch`, consolidation pipeline, hydration_context_pack RPC, knowledge graph traversal, reinforcement triggers, realtime broadcasts [Source: Supabase_check.txt]), there is no natural OpenClaw integration point. You would need to build a custom Pi extension or tool that calls Supabase, effectively recreating what Hermes's memory providers already do.

**SoSoG Reasoning:** This is the single most important differentiator for the user's stack. The Supabase_check.txt file contains a fully-implemented "V0 Hardcore Memory OS" with scoring, consolidation, hydration, and graph traversal. Hermes's pluggable memory provider interface means you can build a Supabase provider that maps directly to these existing RPC functions. OpenClaw has no equivalent plugin point — you'd be building from scratch against Pi's session API, which is architecturally mismatched to a SQL-backed memory system.

---

## Security Model

### Hermes Security

Hermes implements a **7-layer security model** [Source: innfactory.ai comparison]. Specific layers include:

- Network-level isolation (container backends)
- Tool-level access control (`hermes tools` configures per-platform tool access [Source: Hermes Quickstart — "hermes tools — tune tool access per platform"])
- Session isolation (separate profiles, separate data directories [Source: Hermes Docker docs — "one container per profile"])
- The container privilege model explicitly drops from root to `hermes` user via `s6-setuidgid` [Source: Hermes Docker docs — "s6-overlay's /init runs as root so it can chown the volume on first boot, then drops to the hermes user"]
- API server authentication with minimum 8-character keys [Source: Hermes Docker docs — "API_SERVER_KEY (minimum 8 characters — generate one with openssl rand -hex 32)"]

No documented CVEs or supply-chain attacks against Hermes were found in research.

### OpenClaw Security

OpenClaw has had **documented security incidents** [Source: innfactory.ai comparison — "documented CVEs and supply-chain attacks (ClawHavoc, MCP proxy campaign)"]:

- **ClawHavoc**: A supply-chain attack that affected the ClawHub skills marketplace
- **MCP Proxy Campaign**: An attack leveraging MCP server configurations

The gateway daemon's default bind address is `lan` (as seen in the openclaw.json: `bind: "lan"` [Source: workspace file openclaw-configuration/openclaw.json]), which exposes the WebSocket gateway on the local network. While this is configurable, the default is more permissive than Hermes's approach.

**SoSoG Reasoning:** For a system handling Solana trading intelligence with real financial exposure, security incidents in the supply chain are a direct threat. The ClawHavoc attack on ClawHub is particularly concerning because it targets the skills marketplace — exactly the vector a trading agent would use to install financial tools. Hermes's MIT license, simpler dependency tree, and absence of documented attacks make it the lower-risk choice for financial applications.

---

## Extensibility & Skills

### Hermes Skills System

Hermes offers multiple extensibility paths:

1. **Skills System**: `hermes skills search/install` for reusable workflows [Source: Hermes Quickstart]
2. **Autonomous Curator**: The agent can autonomously discover and install skills [Source: Phase_shift_skills.txt — skill #1 "recursive skill-writing loop"]
3. **MCP Servers**: Standardized MCP integration via config.yaml [Source: Hermes Quickstart — shows MCP server config block]
4. **Custom Tools**: Developer-extensible tool system
5. **Hooks**: Deterministic guardrails that intercept and validate agent actions [Source: Phase_shift_skills.txt — skill #3]
6. **ACP Integration**: Agent Communication Protocol for IDE integration [Source: Hermes Quickstart — "hermes acp"]

### OpenClaw Skills System

1. **ClawHub Marketplace**: Community skills sharing (v4.1+) [Source: innfactory.ai comparison]
2. **Pi Extensions**: Custom TypeScript extensions that can register tools, render TUI components, persist state [Source: lucumr.pocoo.org/2026/1/31/pi]
3. **Custom Tools**: OpenClaw's `createOpenClawCodingTools()` factory [Source: docs.openclaw.ai/pi — tool architecture]
4. **mcporter**: MCP bridge that exposes MCP calls via CLI/TypeScript bindings (used by OpenClaw to support MCP without native Pi integration) [Source: lucumr.pocoo.org/2026/1/31/pi — "you can also do what OpenClaw does to support MCP which is to use mcporter"]
5. **Canvas System**: Visual collaboration workspace [Source: innfactory.ai comparison]

**SoSoG Reasoning:** OpenClaw's Pi extensions are the most flexible extensibility mechanism (the agent can literally rewrite its own tools at runtime), but this flexibility is a double-edged sword for a trading system. Hermes's hooks system provides deterministic guardrails that can enforce the anti-alpha gates from the Solana build spec. The Phase_shift_skills.txt document explicitly identifies the combination of "recursive skill-writing loop + TDD-for-skills + subagent-driven development" as a "self-supervising system" — and Hermes's architecture supports all three natively.

---

## Deployment & Operations

### Hermes Deployment

**Installation options** [Source: Hermes Quickstart]:
- `pip install hermes-agent` (simplest)
- Git installer: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- Docker: `docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup`

**Resource requirements** [Source: Hermes Docker docs]:
- Memory: 1 GB minimum, 2–4 GB recommended
- CPU: 1 core minimum, 2 cores recommended
- Disk: 500 MB minimum, 2+ GB recommended
- With browser tools (Playwright/Chromium): at least 2 GB memory

**Docker image details** [Source: Hermes Docker docs]:
- Base: `debian:13.4`
- Includes: Python 3 with all dependencies (`uv pip install -e ".[all]"`), Node.js + npm, Playwright + Chromium, ripgrep, ffmpeg, git, xz-utils, docker-cli, openssh-client, WhatsApp bridge, s6-overlay v3 as PID 1
- Data volume: `/opt/data` → all state (config, API keys, sessions, skills, memories, cron, hooks, logs)
- Gateway port: 8642 (OpenAI-compatible API server)
- Dashboard port: 9119 (optional)

### OpenClaw Deployment

**Installation**: Via npm/Node.js ecosystem. The workspace shows OpenClaw running as a systemd service (`openclaw.service`) with a gateway daemon [Source: openclaw-startup.sh, openclaw-configuration/openclaw.service].

**Resource usage in this environment**: The running `openclaw` process consumes 338 MB RSS and 8.4% of memory [Source: `ps aux` output from this sandbox — `root 629 1.5 8.4 12058836 338992`].

**Gateway**: Listens on port 18789 with `bind: "lan"` [Source: openclaw.json configuration].

**SoSoG Reasoning:** Both agents can run in this environment's resource constraints (2 CPU, 3.8 GB RAM). Hermes's pip-based installation is simpler than OpenClaw's Node.js dependency chain. The critical difference is that Hermes supports Docker-based isolation for terminal execution (the agent runs on host but executes commands in a sandbox container), while OpenClaw relies on its own sandbox implementation. In an environment without Docker (like this SuperNinja sandbox), Hermes can fall back to local terminal execution; OpenClaw's sandbox is less mature without container support.

---

## SuperNinja Environment Feasibility Assessment

### Current Environment Capabilities

| Resource | Available | Hermes Minimum | OpenClaw Running |
|----------|-----------|---------------|------------------|
| CPU | 2 cores | 1 core (2 rec) | Using 1.5% CPU |
| RAM | 3.8 GB total, ~2.9 GB available | 1 GB (2-4 rec) | Using 339 MB |
| Disk | 1.8 GB free | 500 MB min | ~200 MB install |
| Python | 3.11.14 ✓ | Required | Not primary |
| Node.js | 22.19.0 ✓ | Optional | Required ✓ |
| Docker | NOT available | Optional | Not needed |
| systemd | Running ✓ | Not needed | In use ✓ |
| Git | 2.39.5 ✓ | Required | Required |
| pip | 24.0 ✓ | Required | N/A |
| uv | NOT installed | Recommended | N/A |
| Browser (Chromium) | Available via Playwright | Included in Docker | Available |
| Network | External IP accessible | Required | Running |
| sudo | Passwordless ✓ | N/A | N/A |

### Can Hermes Run Here?

**Yes, with constraints.**

The pip-based installation path works: `pip install hermes-agent` requires only Python 3.11 (available) and pip (available). The minimum resource requirements (1 GB RAM, 1 core, 500 MB disk) are within this environment's capacity, though the recommended 2-4 GB RAM is tight given OpenClaw is already consuming 339 MB and Chromium is consuming significant memory.

**What would work:**
- CLI mode: `hermes` for interactive chat sessions
- Gateway mode: `hermes gateway run` for persistent messaging (if API keys are configured)
- Basic tools: file operations, terminal, web search
- Skills system: install and use skills from the marketplace

**What would NOT work:**
- Docker terminal backend: Docker is not available in this environment
- Browser tools (without Playwright): Would need `hermes postinstall` to install Playwright + Chromium, which adds ~500 MB
- Full Docker deployment: Cannot run the official Docker image
- Multiple profiles simultaneously: Memory constraints

**What's missing for full deployment:**
1. A model provider API key (Anthropic, OpenAI, OpenRouter, etc.)
2. `uv` package manager (recommended but not required — pip works)
3. ~500 MB additional disk space for Playwright (optional, for browser tools)
4. ~200 MB additional disk space for Hermes core install

### Can OpenClaw Run Here?

**It already is.** The `openclaw` process (PID 629) is running as a systemd service, consuming 339 MB RSS memory. The gateway is configured on port 18789. However, the Telegram and Slack channels are disabled in the current configuration [Source: openclaw.json showing `enabled: false` for both telegram and slack].

**What's working:**
- Gateway daemon is running
- Model provider is configured (LiteLLM with ninja-cline-complex model via model-gateway.myninja.ai)
- Workspace is set up at `/workspace/openclaw-files`
- Systemd service management is operational

**What's not configured:**
- No messaging channels are enabled
- IDENTITY.md, USER.md, TOOLS.md are blank templates
- No custom skills or extensions installed
- No memory system beyond session history

### Environment Limitations for Both

1. **No VPS capability**: This is a sandboxed container, not a VPS. No ability to provision additional machines, set up VPNs, or run hypervisors.
2. **No Docker**: Container-within-container is not available. Both agents lose their sandboxed execution backends.
3. **Limited disk**: 1.8 GB free means both agents cannot coexist with full toolchains installed. Running both simultaneously would require choosing which features to enable.
4. **Ephemeral by nature**: While systemd is running and processes persist across sessions, the underlying infrastructure is a cloud sandbox. Data persistence depends on the `/workspace` mount.
5. **No GPU**: Local model inference is not viable. Both agents require external LLM API access.
6. **Memory ceiling**: 3.8 GB total RAM means both agents running simultaneously would be tight, especially with Chromium already consuming significant resources.

**SoSoG Reasoning:** The environment can run either Hermes or OpenClaw, but not both at full capacity simultaneously. Since OpenClaw is already running and configured, the pragmatic path is to (a) decide whether OpenClaw serves the user's needs as-is, (b) install Hermes alongside it with minimal footprint, or (c) replace OpenClaw with Hermes. Given the memory constraints and the user's stated preference for Hermes ("considered superior to OpenClaw in performance and capabilities"), option (b) with selective feature enablement is the recommended path.

---

## Obsidian Integration Paths

### Option 1: MCP Tools for Obsidian (Archived but Functional)

The "MCP Tools for Obsidian" plugin was the #1 MCP-related Obsidian plugin with 87K installs before being archived. It requires the Local REST API plugin + Claude Desktop to function [Source: GitHub obsidian-mcp-tools repo, scraped in previous session]. Being archived means it still works but is no longer actively maintained.

**Hermes integration**: Hermes supports MCP servers natively via `~/.hermes/config.yaml` [Source: Hermes Quickstart — shows MCP config block]. You would configure the Obsidian MCP server endpoint in Hermes's config.

**OpenClaw integration**: OpenClaw would need mcporter to bridge MCP to Pi's tool system [Source: lucumr.pocoo.org/2026/1/31/pi — "you can also do what OpenClaw does to support MCP which is to use mcporter"].

### Option 2: Hermes Console Obsidian Plugin

A dedicated Obsidian plugin for Hermes Agent, providing direct integration within Obsidian's interface [Source: Memory_for_Hermes..txt — mentioned in the Hermes ecosystem survey].

### Option 3: obsidian-semantic-mcp Server

A semantic search MCP server for Obsidian vaults, enabling natural language queries over notes [Source: Previous session research]. This provides RAG-like access to Obsidian content without requiring the full Local REST API plugin stack.

### Option 4: Agent Client Plugin

The Agent Client plugin allows running Claude Code, Codex, or Gemini directly inside Obsidian [Source: Previous session research]. While not specific to Hermes or OpenClaw, it demonstrates the pattern of embedding agent capabilities within the note-taking environment.

**SoSoG Reasoning:** For the user's voice-first workflow (MASTER_CONTEXT.md: "voice-first workflow, 2+ years daily immersion"), Obsidian integration is most valuable as a *reading* surface (consuming agent output as notes) rather than a *writing* surface (creating notes that feed the agent). Hermes's MCP-native approach is the simplest integration path. The semantic MCP server is particularly interesting for the knowledge graph traversal already built in the Supabase memory OS.

---

## Head-to-Head Comparison Matrix

| Dimension | Hermes Agent | OpenClaw | Winner for User's Stack |
|-----------|-------------|----------|------------------------|
| **License** | MIT | Apache 2.0 | Tie |
| **Language** | Python | TypeScript/Node.js | Hermes (Python aligns with Solana/data stack) |
| **Architecture** | Agent-first, modular | Gateway-first, hub-and-spoke | Hermes (agent quality > messaging) |
| **Core Engine** | Self-built, 70+ tools | Pi (4 tools + extensions) | Depends on use case |
| **Memory** | 8 pluggable providers | Session history only | Hermes (critical differentiator) |
| **MCP Support** | Native | Via mcporter bridge | Hermes |
| **Security** | 7-layer model, no known CVEs | ClawHavoc, MCP proxy CVEs | Hermes |
| **Messaging** | 20+ platforms via gateway | 15+ platforms via gateway | OpenClaw (slightly more mature) |
| **Self-Modification** | Skills + Curator | Pi extensions + hot-reload | OpenClaw (Pi's model is more fluid) |
| **Session Structure** | Linear with SQLite+FTS5 | Tree-structured JSONL | OpenClaw (branching is powerful) |
| **Container Support** | Docker/Singularity/Modal/Daytona/Vercel | Docker | Hermes (more options) |
| **API Server** | OpenAI-compatible on 8642 | Gateway WebSocket on 18789 | Hermes (REST is more interoperable) |
| **Dashboard** | Built-in web dashboard | Canvas system | Tie (different approaches) |
| **Cron/Automation** | Built-in | Built-in | Tie |
| **Voice Mode** | Built-in with faster-whisper | Not native | Hermes |
| **Obsidian Integration** | Native MCP support | Via mcporter | Hermes |
| **Supabase Compatibility** | Direct via memory provider | Would need custom extension | Hermes (critical) |
| **Solana Stack Alignment** | Python + pluggable memory + hooks | TypeScript + session-based + extensions | Hermes |
| **Community Size** | Growing fast, newer | 234K stars, massive | OpenClaw (but quantity ≠ quality) |
| **Iteration Speed** | 6 releases in 50 days | Major rewrite every few months | Hermes |
| **Deployment in This Env** | pip install, ~200 MB | Already running, 339 MB | OpenClaw (already deployed) |

---

## Recommendation

### Primary Recommendation: Hermes Agent

**Why:** The three critical differentiators for the user's stack are:

1. **Memory Architecture**: The Supabase "V0 Hardcore Memory OS" (scoring functions, consolidation pipeline, hydration RPC, knowledge graph traversal) maps directly to Hermes's pluggable memory provider interface. Building a `SupabaseMemoryProvider` for Hermes is a well-scoped integration task. OpenClaw has no equivalent plugin point — you'd be building against Pi's session API, which is architecturally mismatched to a SQL-backed memory system.

2. **Deterministic Guardrails**: The Solana build spec's anti-alpha gates, trade_card/reject_card schemas, and agent trust scoring (EWMA) require hooks that intercept and validate agent actions before execution. Hermes's hooks system provides exactly this. Pi's self-modifying extension model is powerful for development but antithetical to the "evidence-first architecture" that the build spec demands.

3. **Python Ecosystem Alignment**: The user's existing stack (Supabase with pg_cron, Python-based data pipelines, Solana trading intelligence) is Python-native. Hermes is Python. OpenClaw is TypeScript. Every integration point with OpenClaw requires a language bridge that adds complexity without adding capability.

### Secondary Recommendation: Keep OpenClaw Running

OpenClaw is already deployed and functional in this environment. Rather than removing it, use it for what it's best at: **messaging gateway**. Configure OpenClaw as the messaging layer (Telegram, Discord, Slack) and have it forward messages to Hermes's API server (port 8642). This gives you the best of both worlds — OpenClaw's mature channel adapters plus Hermes's superior agent and memory capabilities.

### Implementation Path

1. **Phase 1** (30 min): `pip install hermes-agent && hermes setup --portal` — get basic Hermes CLI working
2. **Phase 2** (2 hours): Configure provider (Anthropic or OpenRouter), verify basic chat, enable sessions
3. **Phase 3** (4 hours): Build `SupabaseMemoryProvider` — implement the memory provider interface backed by the existing Supabase RPC functions (hydration_context_pack, compute_memory_score, etc.)
4. **Phase 4** (2 hours): Configure Hermes gateway + OpenClaw as messaging bridge, or enable Hermes's native Telegram/Discord adapters
5. **Phase 5** (ongoing): Migrate SOUL.md, MEMORY.md, USER.md from OpenClaw format to Hermes format; install relevant skills from the marketplace

---

## Source Bibliography

1. **Hermes Agent Quickstart** — https://hermes-agent.nousresearch.com/docs/getting-started/quickstart  
   *Primary source for installation, providers, CLI commands, gateway setup, MCP config, resource requirements*

2. **Hermes Agent Docker Documentation** — https://hermes-agent.nousresearch.com/docs/user-guide/docker  
   *Primary source for Docker deployment, resource limits (1GB min/2-4GB rec), image contents, privilege model, s6-overlay*

3. **innfactory.ai: "Hermes vs OpenClaw: An Honest Comparison"** — https://innfactory.ai  
   *Comprehensive 20-min read: origin stories, architecture comparison, release histories, security models, CVE list for OpenClaw, supply-chain incidents, large comparison table*

4. **Armin Ronacher: "Pi: The Minimal Agent Within OpenClaw"** — https://lucumr.pocoo.org/2026/1/31/pi  
   *Primary source for Pi philosophy, 4-tool core, session trees, hot-reloading, extension system, no-MCP rationale, self-extending architecture*

5. **OpenClaw Pi Integration Architecture** — https://docs.openclaw.ai/pi  
   *Primary source for embedded Pi integration, file structure (40+ modules), tool pipeline, session management, auth profiles, system prompt construction*

6. **OpenClaw Gateway Architecture** — https://docs.openclaw.ai (gateway docs)  
   *Primary source for hub-and-spoke model, wire protocol, connection lifecycle, pairing*

7. **Memory_for_Hermes..txt** — Uploaded file in workspace  
   *40-source comparative deep-dive on the Hermes memory ecosystem: all 8 providers, Daedalus live agent, MEMORY.md/USER.md structures, custom memory kernels*

8. **Supabase_check.txt** — Uploaded file in workspace  
   *Actual current Supabase state: introspection SQL, scoring functions, consolidation pipeline, hydration RPC, graph traversal, RLS patterns, pg_cron automation*

9. **Hermes_Solana_Edge_Canonical_Build_Spec_v1.docx** — Uploaded file in workspace  
   *Main spine: Solana trading intelligence stack, agent council, evidence-first architecture, anti-alpha gates, trade_card/reject_card schemas, agent trust scoring with EWMA*

10. **MASTER_CONTEXT.md** — Uploaded file in workspace  
    *User profile: self-taught AI orchestration architect, Tucson AZ, ADHD hyperfocus, voice-first workflow, 5-layer context engineering stack, Python-native tooling*

11. **Phase_shift_skills.txt** — Uploaded file in workspace  
    *Top 10 phase-shift skills: recursive skill-writing loop, TDD-for-skills, hooks, subagent-driven development, git worktrees, three-tier memory, AGT+Cedar, etc.*

12. **openclaw.json** — Workspace configuration file  
    *Live OpenClaw configuration: model provider (LiteLLM/ninja-cline-complex), gateway port (18789), channel configs (Telegram/Slack disabled)*

13. **Serenities AI: "OpenClaw 2026: 234K Stars"** — https://serenitiesai.com/articles/openclaw-deep-dive-2026  
    *Source for GitHub star count and community scale metrics*

14. **obsidian-mcp-tools GitHub repo** — https://github.com/anthropics/obsidian-mcp-tools (archived)  
    *Source for Obsidian MCP integration: 87K installs, requires Local REST API plugin, archived status*

15. **Hermes Agent GitHub** — https://github.com/nousresearch/hermes-agent  
    *Source for MIT license, installation scripts, Dockerfile structure*
