# Fork Janitor

## What it does
Fork Janitor disables GitHub Actions on all repositories owned by you where `fork == true`, and leaves non-fork repositories untouched.

## Why it exists
Forks inherit upstream workflows, including scheduled/event-driven automation. On personal forks without required secrets, those workflows fail repeatedly and create noisy notifications.

## One-time setup
1. Create a fine-grained PAT: https://github.com/settings/personal-access-tokens/new
2. Set **Resource owner** to `Vvolen`
3. Set **Repository access** to **All repositories**
4. Set permissions:
   - `Administration: Read and write` (required to toggle Actions)
   - `Metadata: Read` (auto-included)
5. Open `Vvolen/Foundation-layer` → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
6. Name it exactly: `FORK_JANITOR_PAT`
7. Paste token and save

## How to run
- Manual: **Actions** tab → **Fork Janitor** → **Run workflow** → set `execute: true` to apply changes
- Automatic: Runs every Monday at 6:00 UTC in dry-run mode; inspect logs for newly detected noisy forks

## What it never touches
Fork Janitor only acts on repositories where `fork == true`. Repositories where `fork == false` are excluded by design, including:
- `Vvolen/Versailles`
- `Vvolen/Foundation-layer`
- `Vvolen/MUNCH-CONTEXT-PROTOCOL-MCP-`

## Reverting
To re-enable Actions on a specific fork:

```bash
gh api -X PUT repos/Vvolen/<name>/actions/permissions -f enabled=true
```

Or use the repository UI: **Settings** → **Actions**.
