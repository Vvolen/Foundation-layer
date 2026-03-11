# GitHub Ecosystem Guide
## A Practical Deep-Dive for NickOS

> Written for Nick — a systems architect who is not a native developer but is becoming one.
> Goal: After reading this, you understand WHAT each GitHub tool is, HOW it works, WHEN to use each one, and HOW to bring external models (Claude, Codex) into these environments.
> Last updated: 2026-03-11

---

## Table of Contents

1. [GitHub Actions — Automation Engine](#1-github-actions--automation-engine)
2. [GitHub Copilot Coding Agent — Your AI Developer](#2-github-copilot-coding-agent--your-ai-developer)
3. [GitHub Copilot Agentic Workflows (gh aw)](#3-github-copilot-agentic-workflows-gh-aw)
4. [GitHub Codespaces + devcontainers — Your Cloud IDE](#4-github-codespaces--devcontainers--your-cloud-ide)
5. [Bringing External Models Into GitHub](#5-bringing-external-models-into-github-claude-codex-opus)
6. [When To Use Which Tool](#6-when-to-use-which-tool)
7. [Step-by-Step: Setting Everything Up](#7-step-by-step-setting-everything-up)

---

## 1. GitHub Actions — Automation Engine

### What Is It?

GitHub Actions is GitHub's built-in **task runner**. It lets you run any code automatically in response to events in your repository.

The core concept: you write a YAML file, put it in `.github/workflows/`, and GitHub runs it whenever the trigger fires. The trigger can be:
- A push to main
- A pull request being opened
- A cron schedule (like a cron job)
- Someone creating an issue
- Manual button click
- Another workflow completing

The code runs in a **container** (usually Ubuntu Linux) that GitHub spins up, runs your steps, then destroys. These containers are called **runners**.

### The Anatomy of a Workflow File

```yaml
name: My Workflow                          # Display name in GitHub UI

on:                                        # TRIGGER: when does this run?
  push:
    branches: [main]                       # On any push to main
  schedule:
    - cron: '0 3 * * *'                    # Every day at 3am UTC
  workflow_dispatch:                        # Manual run from GitHub UI

jobs:                                      # JOBS: what to run (can be parallel)
  my-job:
    runs-on: ubuntu-latest                 # RUNNER: what machine to use

    steps:                                 # STEPS: sequential commands

      - name: Checkout the code
        uses: actions/checkout@v4          # PRE-BUILT ACTION: clone the repo

      - name: Set up Python
        uses: actions/setup-python@v5      # PRE-BUILT ACTION: install Python
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt    # YOUR COMMAND: any shell command

      - name: Run your script
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}    # SECRETS: from repo settings
        run: python run_ingest.py --source youtube --url ${{ vars.NIGHTLY_URL }}
```

### Secrets Management

You can store API keys securely in GitHub and reference them as `${{ secrets.KEY_NAME }}`. They are:
- Encrypted at rest
- Never shown in logs (GitHub redacts them)
- Accessible only to workflows in your repo (or org, if you configure it)

**How to add a secret:**
1. Go to your repo on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name it (e.g., `OPENAI_API_KEY`) and paste the value
5. Reference it in your workflow as `${{ secrets.OPENAI_API_KEY }}`

### Pre-Built Actions (The Marketplace)

GitHub has thousands of pre-built actions you can use with `uses:`. The most useful ones for NickOS:

| Action | What It Does |
|--------|--------------|
| `actions/checkout@v4` | Clone your repo into the runner |
| `actions/setup-python@v5` | Install a specific Python version |
| `actions/upload-artifact@v4` | Save files from a run for later download |
| `actions/download-artifact@v4` | Load files from a previous run |
| `actions/cache@v4` | Cache pip packages between runs (faster) |
| `peter-evans/create-pull-request@v6` | Programmatically open a PR |

### Cron Schedule Format

GitHub Actions uses standard cron syntax: `minute hour day-of-month month day-of-week`

```
'0 3 * * *'      # 3:00am UTC every day
'0 */6 * * *'    # Every 6 hours
'0 4 * * 0'      # 4:00am UTC every Sunday
'30 9 * * 1-5'   # 9:30am UTC every weekday
```

### Matrix Builds

Run the same job across multiple configurations in parallel:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

This runs 3 parallel jobs — one for each Python version.

### Job Dependencies

You can make jobs run after other jobs complete:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: test              # Only runs if 'test' succeeds
    runs-on: ubuntu-latest
    steps: [...]
```

### Concrete NickOS Actions

**1. Run tests on every PR** (already created at `.github/workflows/test.yml`)

**2. Nightly ingestion** (already created at `.github/workflows/ingest-nightly.yml`)

**3. Trigger on issue creation** — automatically comment when an issue is opened:
```yaml
on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Thanks for the issue! @copilot will review this.'
            });
```

---

## 2. GitHub Copilot Coding Agent — Your AI Developer

### What Is It?

The GitHub Copilot coding agent is an AI agent you can assign to GitHub issues. It will:
1. Read the issue description
2. Look at your repository
3. Write code changes
4. Open a pull request with those changes for your review

You describe WHAT you want (in plain English, in a GitHub issue). The agent figures out HOW to do it and shows you a PR.

### How It Works — Step by Step

1. You create a GitHub issue: *"Implement the YouTube extractor in nodes/extractor.py — it should use youtube-transcript-api to extract the transcript, convert the video URL to video_id, and return an ExtractionResult."*
2. You assign the issue to `@copilot` (or the agent auto-picks it up based on your settings)
3. The agent creates a new branch: `copilot/implement-youtube-extractor`
4. It reads your repo — `CLAUDE.md`, the node file, the requirements, the tests
5. It writes the code and a test
6. It opens a PR from that branch → main
7. You review the PR, comment if changes needed, or merge it

### The `.github/copilot-instructions.md` File

This is your way to give repo-specific instructions to the Copilot agent. Without it, the agent uses generic behaviors. With it, you can tell it:
- What code style to use
- What order to build things in
- What NOT to do
- What constraints to respect

This file is already created at `.github/copilot-instructions.md` in this repo.

**Best practices for copilot-instructions.md:**
- Keep it focused on the repo-specific things the agent needs to know
- Include the most common mistakes to avoid
- Reference the schema and interface contracts explicitly

### The `CLAUDE.md` File

`CLAUDE.md` serves a similar purpose — it's the first file any AI agent reads when it opens your repo. It's not GitHub-specific; it works with Claude Code, Copilot, and any other agent. Always include:
- What the repo is
- What NOT to do
- The build order
- Key constraints

This file is already created at `CLAUDE.md` in this repo.

### What Makes a Good Issue for the Copilot Agent?

**Good issue** (specific, actionable, single responsibility):
> Implement `_extract_youtube(url: str) -> ExtractionResult` in `nodes/extractor.py`.
>
> Requirements:
> - Extract the video_id from the URL using a regex (handles youtu.be and youtube.com/watch?v= formats)
> - Call `YouTubeTranscriptApi.get_transcript(video_id)` from the `youtube-transcript-api` package
> - Concatenate all transcript segments into a single string with spaces
> - Return `ExtractionResult(raw_text=..., source_type='youtube', source_ref=url, metadata={'video_id': video_id})`
> - Raise `NodeExtractionError` if no transcript is available
>
> Add a test in `tests/test_extractor.py` using `unittest.mock.patch` to mock the `YouTubeTranscriptApi`.

**Bad issue** (too vague):
> Implement the YouTube extractor

The more specific the issue, the better the code the agent produces.

---

## 3. GitHub Copilot Agentic Workflows (gh aw)

### What Is It?

Agentic Workflows is a GitHub feature (via `githubnext/agentics`) that lets you define workflows in **markdown** instead of YAML. The workflow is executed by the Copilot coding agent — not a bash script — so it can understand context, read files, and make intelligent decisions.

**Key difference from regular Actions:**
- Regular Actions run bash scripts and Python scripts mechanically
- Agentic Workflows run the Copilot agent, which understands your repo and makes contextual decisions

### How It Works

1. You install a workflow: `gh aw add githubnext/agentics/workflows/daily-repo-status.md@<sha>`
2. GitHub compiles the markdown workflow definition to a `.lock.yml` file
3. The workflow can be triggered on a cron schedule or manually
4. When triggered, the Copilot agent reads the markdown instructions, executes them against your repo, and creates an issue or PR with the results

### Available Pre-Built Workflows (as of early 2026)

| Workflow | What It Does |
|----------|--------------|
| `daily-repo-status` | Generates a daily status report as a GitHub issue — what changed, what's stale, open PRs/issues summary |
| `contributor-stats` | Weekly analytics on contributions |
| `ci-doctor` | Monitors CI/CD health, identifies failing patterns |
| `document-workflows` | Auto-documents your GitHub Actions workflows |

### How to Install

```bash
# Prerequisites: gh CLI installed, authenticated
gh extension install githubnext/gh-aw

# Add a workflow
gh aw add githubnext/agentics/workflows/daily-repo-status.md@<sha>

# List installed workflows
gh aw list

# Run manually
gh aw run daily-repo-status
```

### NickOS Applications

The **self-evolution workflow** you designed for Versailles is a perfect fit for agentic workflows. Instead of a bash script that mechanically checks files, you'd write a markdown instruction like:

```markdown
# Self-Evolution Workflow

Every Sunday at 4am UTC:

1. Review all memory fragments in Supabase that haven't been accessed in 30+ days
2. Identify the top 10 themes across episodic fragments from the past week
3. Check if any skills in META_INDEX.md in Vvolen/Versailles are outdated or missing
4. Create a GitHub issue in Vvolen/Versailles summarizing: what's stale, what's new, recommended META_INDEX updates
```

The Copilot agent reads this, understands what you want, and executes it contextually.

---

## 4. GitHub Codespaces + devcontainers — Your Cloud IDE

### What Is It?

Codespaces gives you a **full VS Code development environment in the browser**, running in the cloud. No local setup required. Works on your iPad.

**What you get:**
- Full VS Code interface in the browser
- A Linux container with whatever environment you configure
- All your files, terminal, extensions
- Port forwarding (so you can run a server and access it)
- Persistent storage between sessions (unlike Actions runners)

### The devcontainer.json File

The `.devcontainer/devcontainer.json` file tells GitHub how to set up your Codespace. This repo's config (`.devcontainer/devcontainer.json`) specifies:
- Python 3.11
- Automatic `pip install -r requirements.txt` on first launch
- VS Code extensions (Python, Pylance, Jupyter, GitHub Copilot)
- Code formatting settings

### How to Open a Codespace

1. Go to `https://github.com/Vvolen/Foundation-layer`
2. Click the green **Code** button
3. Click the **Codespaces** tab
4. Click **"Create codespace on main"** (or your branch)
5. Wait ~1 minute for the container to build
6. VS Code opens in your browser, fully configured

**From your iPad:** Open `github.com` in Safari, same steps. The VS Code web interface works on iPad.

### Persistent Storage in Codespaces

Unlike GitHub Actions (ephemeral — everything deleted after the run), your Codespace **persists between sessions**. Your `.env` file, `pipeline_artifacts/`, and any installed packages stay until you delete the Codespace.

**Important:** Codespaces stop automatically after 30 minutes of inactivity (configurable). They don't delete — they just pause. Your files are preserved.

### Codespace vs. Actions vs. Copilot Agent

See Section 6 for the full comparison.

---

## 5. Bringing External Models into GitHub (Claude, Codex, Opus)

### The Core Insight

GitHub Actions are just compute environments — Linux containers where you can run any code. **You can call any API from a GitHub Action step.** This means you can run Claude, GPT-4, Codex, or any model inside an Action.

This is how you "bring Codex and Opus 4.6 into the environment" — you call their APIs from within your workflow steps.

### Example: Calling Claude API from a GitHub Action

```yaml
name: Claude-Powered Analysis

on:
  workflow_dispatch:
    inputs:
      text_to_analyze:
        description: "Text to send to Claude"
        required: true

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Anthropic SDK
        run: pip install anthropic

      - name: Call Claude API
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python - <<'EOF'
          import anthropic

          client = anthropic.Anthropic()

          message = client.messages.create(
              model="claude-opus-4-20250514",
              max_tokens=1024,
              messages=[
                  {
                      "role": "user",
                      "content": "${{ github.event.inputs.text_to_analyze }}"
                  }
              ]
          )

          print(message.content[0].text)
          EOF
```

### Example: Calling OpenAI Embeddings from a GitHub Action

```yaml
- name: Generate Embeddings
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python - <<'EOF'
    import openai
    import json

    client = openai.OpenAI()

    texts = ["The capital of France is Paris.", "Python is a programming language."]

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    for i, embedding in enumerate(response.data):
        print(f"Text {i}: {len(embedding.embedding)} dimensions")
    EOF
```

### Example: Full Ingestion Pipeline Triggered by Action

This is what the nightly ingestion workflow does — run `run_ingest.py` which internally calls the OpenAI and Supabase APIs:

```yaml
- name: Run NickOS Ingestion Pipeline
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
    NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
  run: |
    python run_ingest.py \
      --source youtube \
      --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Available Model APIs

| Provider | Best Model for NickOS | Use Case |
|----------|----------------------|----------|
| Anthropic | `claude-opus-4-20250514` | Complex reasoning, planning |
| Anthropic | `claude-sonnet-4-20250514` | Good balance of quality/cost |
| OpenAI | `gpt-4o` | Dedup gray zone review |
| OpenAI | `gpt-4o-mini` | Fact extraction (cheap, fast) |
| OpenAI | `text-embedding-3-small` | All embeddings |
| OpenAI | Codex (via Completions API) | Code generation in Actions |

### Security Note

When calling external APIs from Actions:
- ALWAYS use `${{ secrets.KEY_NAME }}` — never hardcode keys in YAML
- Never print API keys to logs
- Use `env:` block on the specific step, not at the job level, to minimize exposure

---

## 6. When To Use Which Tool

This is the question you asked. Here's the honest answer:

### Use Codespaces When...
- You want to **interactively explore** the codebase (open files, run commands, debug)
- You're **manually testing** something (run `python run_ingest.py` and watch it go)
- You're **developing a new node** and want to iterate quickly
- You're on your **iPad or a machine without a dev environment** set up
- You need **persistent state** between sessions (your `.env` file, half-finished checkpoint files)

**The dev container in this repo is pre-configured** — when you open a Codespace, Python 3.11 is installed, `pip install -r requirements.txt` runs automatically, and VS Code has Copilot enabled.

### Use GitHub Actions When...
- You want to **run the pipeline automatically** on a schedule (nightly, weekly)
- You want **tests to run automatically** on every PR (so you catch bugs before merging)
- You want to **call Claude or OpenAI APIs** on a schedule (weekly knowledge refresh, etc.)
- You want to **deploy** something or sync data between repos (Versailles META_INDEX refresh)
- You want **event-driven automation** (when an issue is created, do X)
- **No interaction needed** — you define what happens, GitHub executes it

**Important tradeoff:** Actions runners are **ephemeral** — they spin up, do the job, and disappear. No persistent filesystem. If your pipeline crashes partway through, the checkpoint file is lost (unless you upload it as an artifact). The checkpoint resume feature is designed to handle this by uploading artifacts.

### Use Copilot Coding Agent When...
- You want to **delegate a coding task** to an AI and review the result
- The task can be **fully specified in a GitHub issue**
- You want **code changes implemented** without doing the typing yourself
- You want the agent to handle **mechanical transformations** (add error handling everywhere, add type hints, write tests)

**The workflow:**
1. You write a clear issue with the exact requirements
2. You assign to `@copilot`
3. The agent opens a PR
4. You review, request changes if needed, merge

**Key constraint:** The Copilot agent is best for tasks that can be fully specified upfront. For exploratory/design work, use your own reasoning (or bring in Claude Sonnet/Opus via a Codespace or Actions call) to figure out the design first, then delegate implementation to Copilot.

### Use Copilot Agentic Workflows (gh aw) When...
- You want **recurring, contextual reports** about your repo health
- You want the agent to **autonomously monitor** your codebase on a schedule
- You want workflows that require **understanding** (not just mechanical execution)
- Phase 2+: when the Versailles self-evolution automation is ready

### The Power Move: Use All Three Together

Here's how they compose:

```
You write an issue → Copilot agent writes code → opens PR
                                                    ↓
                                          GitHub Actions: test.yml runs
                                          (Python tests, smoke tests)
                                                    ↓
                                          If tests pass → ready to merge
                                                    ↓
                                          You merge → Actions: deploy, notify
```

And on a schedule:
```
Cron 3am UTC → Actions: ingest-nightly.yml
                         ↓
               Calls Python run_ingest.py
                         ↓
               Calls OpenAI API (embeddings, fact extraction)
                         ↓
               Writes to Supabase (memory_fragments)
                         ↓
               Calls Notion API (summary page)
                         ↓
               Archives pipeline report as artifact
```

And for Versailles evolution (Phase 2):
```
Cron Sunday 4am → Copilot Agentic Workflow: evolve.yml
                   ↓
         Copilot agent reads Versailles repo + Supabase stats
                   ↓
         Intelligently identifies stale content, new themes
                   ↓
         Opens a PR in Vvolen/Versailles updating META_INDEX
```

**Recommendation for NickOS:** Use all three. They complement each other perfectly.
- Codespaces for development and debugging
- Actions for scheduling and automation
- Copilot agent for delegated implementation tasks

---

## 7. Step-by-Step: Setting Everything Up

### Step 1: Add Repository Secrets (Required for Actions)

1. Go to `https://github.com/Vvolen/Foundation-layer`
2. Click **Settings** tab
3. Left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these secrets one at a time:
   - `SUPABASE_URL` — from your Supabase project settings
   - `SUPABASE_SERVICE_KEY` — from Supabase project settings (service role key)
   - `OPENAI_API_KEY` — from platform.openai.com
   - `NOTION_API_KEY` — from notion.so/my-integrations
   - `NOTION_DATABASE_ID` — the ID at the end of your Notion database URL

### Step 2: Open a Codespace

1. Go to `https://github.com/Vvolen/Foundation-layer`
2. Click the green **Code** button
3. Click **Codespaces** tab
4. Click **Create codespace on main**
5. Wait ~1 minute for the container to build
6. VS Code opens in your browser with Python 3.11 and all dependencies installed
7. In the terminal: `cp .env.example .env`, then edit `.env` with your keys
8. Run: `python run_ingest.py --source text --text "Hello world"` to verify it works

### Step 3: Run the Supabase Schema

1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New query**
4. Copy the entire contents of `specs/supabase_schema.sql`
5. Paste into the SQL editor
6. Click **Run** (or press Cmd+Enter)
7. Verify: Go to **Table Editor** — you should see `memory_fragments`, `memory_contradictions`, `memory_provenance`, `schema_versions`

### Step 4: Enable and Test the CI Workflow

The `test.yml` workflow runs automatically on every PR. To test it:
1. Create a new branch: `git checkout -b test/verify-ci`
2. Make a trivial change (add a comment to README)
3. Push: `git push origin test/verify-ci`
4. Create a PR on GitHub
5. Watch the **Checks** tab — you should see "Tests" running
6. If it passes, CI is working

### Step 5: Assign an Issue to Copilot

1. Click **Issues** tab on the repo
2. Click **New issue**
3. Write a specific, actionable issue (see Section 2 for guidance)
4. In the right sidebar, click **Assignees**
5. Type `copilot` and select the Copilot agent
6. Submit the issue
7. Watch for the agent to create a PR (usually within a few minutes)

### Step 6: Configure Copilot Instructions

The file `.github/copilot-instructions.md` is already created in this repo. To update it:
1. Open the file in your Codespace or on GitHub
2. Edit the instructions as your understanding of the project evolves
3. The Copilot agent automatically reads this file when it works on issues in this repo

### Step 7: Enable Nightly Ingestion (When Ready)

1. Open `.github/workflows/ingest-nightly.yml`
2. Uncomment the `schedule:` section
3. Ensure all secrets are set (Step 1)
4. Commit and push
5. The cron job will activate automatically on GitHub's schedule

---

## Honest Tradeoffs

| Tool | Pros | Cons |
|------|------|------|
| **Codespaces** | Interactive, persistent, full IDE, iPad-friendly | Costs money (free tier = 60 hrs/month), slow to start |
| **Actions** | Automated, free (generous limits), event-driven | Ephemeral (no persistent state), YAML syntax has gotchas, debug is harder |
| **Copilot Agent** | Delegates implementation, respects your instructions, opens PRs for review | Quality varies, needs very specific issue descriptions, can make wrong assumptions |
| **Agentic Workflows** | AI-contextual, markdown-based, can understand repo | Still maturing, limited pre-built workflows, requires gh CLI |

---

## Resources

- GitHub Actions docs: https://docs.github.com/en/actions
- GitHub Codespaces docs: https://docs.github.com/en/codespaces
- GitHub Copilot workspace: https://githubnext.com/projects/copilot-workspace
- Copilot in GitHub.com: https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent-to-work-on-tasks
- Agentic workflows: https://github.com/githubnext/agentics
- Anthropic API docs: https://docs.anthropic.com
- OpenAI API docs: https://platform.openai.com/docs
