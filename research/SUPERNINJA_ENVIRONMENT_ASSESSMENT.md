# SuperNinja Environment Capability Assessment

**Date:** May 2026  
**Purpose:** Determine what this SuperNinja sandbox can and cannot do, and whether it's worth investing time in

---

## Environment Profile

| Dimension | Value | Notes |
|-----------|-------|-------|
| **OS** | Debian Linux (slim) | Container-based |
| **Kernel** | 6.1.155 SMP PREEMPT_DYNAMIC | Modern kernel |
| **Architecture** | x86_64 | Standard |
| **CPU** | 2 cores | Adequate for single-agent workloads |
| **RAM** | 3.8 GB total, ~2.9 GB available | Tight for multiple agents |
| **Swap** | 0 B | No swap — memory is hard ceiling |
| **Disk** | 8.8 GB total, 1.8 GB free (80% used) | Very limited |
| **External IP** | 52.12.117.99 | AWS us-west-2 region |
| **systemd** | Running | 188 units loaded |
| **sudo** | Passwordless | Full root access |

## What This Environment CAN Do

### 1. Run Long-Running Processes
systemd is active. Services can be created, enabled, and started. OpenClaw already runs as a systemd service. Any process that can be described in a `.service` file can be daemonized.

### 2. Execute Shell Commands
Full bash access with sudo. Can install packages via `apt`, `pip`, `npm`. Can compile from source if needed.

### 3. Run Python Applications
Python 3.11.14 with pip. Can install any Python package. Virtual environments work. Jupyter could be installed.

### 4. Run Node.js Applications
Node.js 22.19.0 with npm. Can run any Node.js application. OpenClaw is already running as a Node.js process.

### 5. Browser Automation
Chromium is pre-installed via Playwright (version 1217). Xvfb is running on display :99. The browser can be automated for web scraping, testing, etc.

### 6. Expose Ports to the Internet
The `expose_port` tool can make any port publicly accessible. This means:
- Web applications can be deployed and shared
- API servers can be made publicly accessible
- WebSocket servers can be exposed

### 7. Deploy Static Websites
The `deploy` tool can deploy static HTML/CSS/JS to S3 with a public URL (`{name}.pages.dev`).

### 8. Git Operations
Git 2.39.5 is installed. Can clone, push, pull to any accessible repository. GitHub authentication would require token setup.

### 9. File Processing
Full suite of file processing tools: poppler-utils (PDF), wkhtmltopdf (HTML to PDF), antiword (Word docs), unrtf (RTF), catdoc, jq (JSON), csvkit (CSV), xmlstarlet (XML).

### 10. Network Access
Outbound HTTP/HTTPS works. Can scrape web pages, download files, make API calls. Inbound connections require port exposure via the `expose_port` tool.

## What This Environment CANNOT Do

### 1. Run Docker
Docker is not installed. Cannot run containers, build images, or use Docker-based sandboxing. This means:
- Hermes's Docker terminal backend is unavailable
- Hermes's official Docker image cannot be used
- Any tool requiring Docker (containerized testing, isolated builds) is blocked

### 2. Provision VPS or Additional Machines
This is a single sandbox. No ability to:
- Create additional VMs or containers
- Set up VPNs or private networks
- Scale horizontally
- Run hypervisors

### 3. Run GPU Workloads
No GPU access. Local model inference (vLLM, Ollama with larger models) is not viable. All LLM access must be through external API providers.

### 4. Guarantee Persistence
While systemd services survive across tool calls within a session, the underlying infrastructure is a cloud sandbox. There is no guarantee that:
- Data persists indefinitely outside `/workspace`
- Services survive sandbox recreation
- Network configurations survive restarts

### 5. Run Memory-Intensive Workloads
With 3.8 GB RAM and no swap, memory-intensive operations will fail:
- Local LLM inference (even small models)
- Large dataset processing in memory
- Running both Hermes and OpenClaw with full browser automation simultaneously

### 6. Expand Disk Space
1.8 GB free is tight. Installing additional large packages (Playwright, Docker images, language runtimes) requires careful space management.

## Is It Worth Investing Time In?

**Yes, with clear-eyed expectations.**

### What makes it worthwhile:
1. **It's a real Linux environment with root access** — not a toy playground
2. **OpenClaw is already running** — demonstrates that agent workloads are viable
3. **Network access is unrestricted** — can reach any API, scrape any site
4. **Port exposure works** — can share results, host dashboards, test webhooks
5. **Python + Node.js coexist** — can run both ecosystem's tools
6. **Browser automation is available** — can do web research, testing, screenshots
7. **systemd enables persistence** — services can run continuously

### What limits the investment:
1. **Disk space is the binding constraint** — 1.8 GB means you must choose tools carefully
2. **Memory is the second constraint** — one agent at a time with browser tools
3. **No Docker limits isolation** — everything runs in the same namespace
4. **Ephemerality undermines long-term investment** — any infrastructure you build could disappear

### Optimal Use Pattern
The best use of this environment is as a **development and testing sandbox** for agent configurations, not as a **production deployment target**. Use it to:
- Test Hermes Agent installation and configuration
- Develop and test the SupabaseMemoryProvider
- Validate skill installations and custom tool integrations
- Prototype the Solana trading intelligence stack components
- Generate research output and documentation

For production, deploy to a VPS (DigitalOcean, Hetzner, AWS EC2) with Docker support, 8+ GB RAM, and 50+ GB SSD. The configurations developed here transfer directly.

---

## Hermes Agent Deployment Plan for This Environment

### Step 1: Install Hermes Core (minimal footprint)
```bash
pip install hermes-agent --no-deps  # Install core only
pip install hermes-agent  # Full install with deps
# Estimated: ~150-200 MB disk, ~100 MB RAM at idle
```

### Step 2: Configure Provider
```bash
hermes model
# Select OpenRouter or Anthropic (requires API key)
# Or: hermes config set OPENROUTER_API_KEY sk-or-...
```

### Step 3: Verify Basic Functionality
```bash
hermes --tui
# Test with a simple prompt
# Verify sessions work: hermes --continue
```

### Step 4: Configure Gateway (optional)
```bash
hermes gateway setup
# Connect to Telegram or Discord
# This adds ~50 MB RAM overhead
```

### Step 5: Skip Browser Tools (save resources)
```bash
# Do NOT run: hermes postinstall
# Playwright + Chromium would add ~500 MB disk + 200 MB RAM
# The existing Chromium in the environment may be usable via custom config
```

### Step 6: Build SupabaseMemoryProvider
```bash
# Create ~/.hermes/skills/supabase-memory/
# Implement the memory provider interface backed by Supabase RPCs
# This is a Python package that calls the existing Supabase functions
```

### Resource Budget After Installation

| Component | RAM | Disk |
|-----------|-----|------|
| OpenClaw (running) | 339 MB | ~200 MB |
| Hermes Agent | ~100 MB | ~200 MB |
| Hermes Gateway | ~50 MB | minimal |
| Python deps | ~100 MB | ~150 MB |
| OS + Chrome + services | ~2.5 GB | ~6.5 GB |
| **Total** | ~3.1 GB | ~7.1 GB |
| **Remaining** | ~0.7 GB | ~1.7 GB |

This is tight but feasible. If memory becomes critical, stop the OpenClaw service (`systemctl stop openclaw`) to free 339 MB.

---

## Alternative: Run Hermes Outside This Environment

Given the constraints, the most robust deployment path is:

1. **$5-10/month VPS** (Hetzner CPX11: 2 vCPU, 4 GB RAM, 40 GB SSD — €4.15/month)
2. **Docker installation** of Hermes Agent
3. **Supabase cloud** for memory (already in use)
4. **Telegram/Discord** as the primary messaging interface

This gives you Docker isolation, adequate resources, and production-grade persistence for less than the cost of a coffee subscription.
