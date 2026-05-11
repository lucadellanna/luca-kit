---
name: setup-context-search
description: One-time setup wizard that installs qmd (local semantic search engine) and configures it as an MCP server, giving Claude native search tools over the user's context files (customers, offerings, projects, etc.). Guides users of any technical level through prerequisites, installation, and configuration.
version: 0.2.0
---

# Setup Context Search

You guide the user through installing [qmd](https://github.com/tobi/qmd) and wiring it into Claude Code as an MCP server. After setup, Claude can search context files (customers, offerings, projects) using keyword, semantic, or hybrid queries via native tool calls.

**Audience:** Any user. Explain technical concepts inline when they first appear. Adjust depth of explanation based on user responses (if they pick "I'm not sure", give more context; if they pick confidently, skip the explainers).

**Tool rule:** Use AskUserQuestion for every decision point. Never present choices as plain text expecting the user to type a number.

## Step 1: Third-party notice and mode selection

Before anything else, show this notice:

> **About this setup**
>
> This will install [qmd](https://github.com/tobi/qmd), a local search engine created by [Tobi Lütke](https://github.com/tobi) (CEO of Shopify). It is a third-party open-source tool, not created or maintained by luca-ops-kit. You are responsible for deciding whether to install and use it. luca-ops-kit provides this guided setup as a convenience but assumes no liability for qmd or its dependencies.
>
> **How it works:** qmd indexes your markdown files into a local database and runs entirely on your machine. No data leaves your laptop.
>
> **About the AI models:**
>
> qmd downloads local AI models to power search. The initial setup downloads ~300 MB (Google's EmbeddingGemma). On first search, qmd may also download two additional models: a query expansion model (~1.1 GB, by qmd's author) and a reranker called Qwen3 (~640 MB, by Alibaba, China).
>
> The Qwen3 Reranker runs as a passive model weights file on your machine: it contains no executable code and makes no network calls. However, qmd may download it automatically on your first search regardless of configuration.
>
> If this concerns you, you have two options:

Use AskUserQuestion (options: "Proceed with setup (qmd may download all models, including Alibaba's, on first search)", "Cancel setup"):

- If "Cancel setup": stop.

## Step 2: Detect platform

```bash
uname -s 2>/dev/null || echo "Windows"
```

Also check for Windows specifically:
```bash
echo "$OS" | grep -i windows && echo "windows" || echo "not_windows"
```

Store as `$PLATFORM`: "macOS", "Linux", or "Windows".

- **macOS** (Darwin): proceed with Homebrew-based flow
- **Windows**: skip Homebrew/SQLite steps; npm global path differs; use `where` instead of `which`
- **Linux**: skip Homebrew; check if sqlite3 dev headers are available via system package manager

## Step 3: Check if already configured

```bash
command -v qmd >/dev/null 2>&1 && echo "qmd_installed" || echo "qmd_missing"
```

Check existing MCP config:

```bash
if [ -f ~/.claude/settings.json ]; then
  python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
with open(path) as f:
    cfg = json.load(f)
print('qmd_configured' if 'qmd' in cfg.get('mcpServers', {}) else 'qmd_not_configured')
" 2>/dev/null || echo "qmd_not_configured"
else
  echo "no_mcp_config"
fi
```

On Windows, replace `$HOME` with the appropriate path (`%USERPROFILE%`).

- If both `qmd_installed` and `qmd_configured`: tell the user "qmd is already installed and configured. Your context files are searchable." Use AskUserQuestion (options: "Reconfigure (change directories)", "Exit"). If Exit, stop.
- Otherwise: continue.

## Step 4: Check Node.js

```bash
node --version 2>/dev/null || echo "node_missing"
```

**If Node is missing or < 22**, explain:

> "qmd needs Node.js (version 22 or later). Node.js is a program that runs JavaScript tools on your computer. It's free and widely used."

Use AskUserQuestion (options: "Show me how to install Node.js", "I'll install it myself and come back"):

If "Show me how":
- macOS: "Run `brew install node@22` in your terminal, or download from https://nodejs.org"
- Windows: "Download the installer from https://nodejs.org (pick the LTS version 22+)"
- Linux: "Run `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs` or use your distro's package manager"

Stop after showing instructions. Tell user to re-run `/setup-context-search` after installing.

## Step 5: Install platform dependencies

### macOS only: SQLite

```bash
brew list sqlite 2>/dev/null && echo "sqlite_ok" || echo "sqlite_missing"
```

If missing:
> "qmd needs an enhanced version of SQLite (a database engine). I'll install it via Homebrew."

Use AskUserQuestion (options: "Install SQLite via Homebrew", "Skip (I'll handle it)"):

If approved:
```bash
brew install sqlite3
```

### Linux only: SQLite dev headers

```bash
dpkg -l libsqlite3-dev 2>/dev/null | grep -q ^ii && echo "ok" || echo "missing"
```

If missing, tell user:
> "qmd needs SQLite development headers. Install with: `sudo apt-get install libsqlite3-dev` (Debian/Ubuntu) or equivalent for your distro."

### Windows: no action needed

SQLite is bundled with the npm package on Windows.

## Step 6: Install qmd

First, detect what package managers are available:

```bash
npm --version 2>/dev/null && echo "npm_ok" || echo "npm_missing"
bun --version 2>/dev/null && echo "bun_ok" || echo "bun_missing"
pnpm --version 2>/dev/null && echo "pnpm_ok" || echo "pnpm_missing"
```

Build the options list from what's available. Always include npm (it comes with Node.js). Only show pnpm/bun if detected.

If only npm is available, skip the choice and tell the user:
> "I'll install qmd using npm (the package manager that comes with Node.js)."

Use AskUserQuestion (options: "Proceed with npm"):

If multiple are available, explain briefly:
> "A package manager installs software tools. You have several available. npm is the safest choice for this tool because it handles native compilation automatically."

Use AskUserQuestion (options built from available managers, npm first with "(recommended)" suffix, pnpm last with "(extra step required)" note):

### npm path:
```bash
npm install -g @tobilu/qmd
```

### bun path:
```bash
bun install -g @tobilu/qmd
```

### pnpm path:

Before installing, warn:
> "pnpm blocks native code compilation by default for security. After installing, you'll need to run one interactive command in your terminal to approve the required native modules. I can't do this for you because it requires selecting items from a menu."

Use AskUserQuestion (options: "Switch to npm instead (simpler)", "Continue with pnpm (I'll do the extra step)"):

If they switch: use npm path above.

If they continue with pnpm:
```bash
pnpm install -g @tobilu/qmd
```

Then tell user:
> "Now open a new terminal window and run:
> ```
> pnpm approve-builds -g
> ```
> In the menu that appears, select `better-sqlite3` and `node-llama-cpp` (use Space to select, Enter to confirm). Then come back here."

Use AskUserQuestion (options: "Done, I approved the builds", "I'm having trouble"):

If trouble: suggest switching to npm (`npm install -g @tobilu/qmd`).

### Verify installation:

After any install path, find the working binary. Important: if the user installed via multiple package managers (e.g., tried pnpm then switched to npm), `which qmd` may resolve to a broken binary while a working one exists elsewhere. Check all known paths:

```bash
which qmd 2>/dev/null
```

Test the resolved path:
```bash
qmd --version 2>&1
```

If this fails (exit code != 0 or produces a "bindings" error), try platform-specific global bin paths in order:
- macOS (npm): `/opt/homebrew/bin/qmd --version`
- macOS (Homebrew node): `/usr/local/bin/qmd --version`
- Linux (npm): `/usr/local/bin/qmd --version`
- Windows (npm): `"$APPDATA/npm/qmd" --version`

Use the **first path that succeeds** as `$QMD_PATH`. Store the full absolute path (e.g., `/opt/homebrew/bin/qmd`), not the bare command name. This path is used for all subsequent steps and for the MCP config.

If no path succeeds, tell the user: "Installation didn't complete successfully. The most common fix is to close and reopen your terminal, then try again." Stop.

### Functional verification:

After version check passes, test that native modules work:
```bash
"$QMD_PATH" status 2>&1
```

If this produces a bindings error (mentioning `better_sqlite3.node` or `node-llama-cpp`): native modules weren't built. Tell user:
> "The native modules weren't compiled correctly. This usually means build scripts were blocked."

Use AskUserQuestion (options: "Reinstall with npm (fixes most cases)", "Show me how to fix manually"):

If reinstall: `npm install -g @tobilu/qmd` and re-verify.

## Step 7: Choose context directory

> "Where do (or will) your context files live? These are markdown files about your business: customers, offerings, projects, SOPs, etc."

Use AskUserQuestion (options: "~/.claude/context/ (available everywhere)", "A custom path (I'll type it)"):

If custom: Use AskUserQuestion (open text prompt).

Expand the path and validate:
```bash
test -d "<expanded_path>" && echo "exists" || echo "missing"
```

If missing:
Use AskUserQuestion (options: "Create it now", "Let me pick a different path"):

If create:
```bash
mkdir -p "<expanded_path>"
```

## Step 8: Create collection, scan, and embed

Create the collection:
```bash
"$QMD_PATH" collection add "<expanded_path>" --name business-context --mask "**/*.md"
```

If this fails with "already exists": the collection was created in a previous run. Use AskUserQuestion (options: "Keep existing collection", "Remove and recreate"):

Scan the filesystem to populate the index:
```bash
"$QMD_PATH" update
```

Report the file count to the user (parse "Indexed: N new" from output). If 0 files found, warn:
> "No markdown files were found in that directory. You can add files later and run `qmd update && qmd embed` to index them."

If files were found, proceed to embedding:

> "This will download ~300 MB of AI models (Google's EmbeddingGemma) to power search. They stay on your machine permanently. This takes 1-2 minutes on a typical connection."

Use AskUserQuestion (options: "Start embedding now", "I'll run `qmd update && qmd embed` later"):

If now:
```bash
"$QMD_PATH" embed
```

This may take several minutes. Tell the user it's running and to wait.

After embedding completes, tell the user:
> "The embedding model is downloaded. Two additional models (query expansion ~1.1 GB, reranker ~640 MB) will download automatically the first time you search. Your first search may take a few extra minutes while these download; after that, searches are fast."

Verify:
```bash
$QMD_PATH status
```

Report the result (documents indexed, chunks embedded).

## Step 9: Configure MCP server

Determine the full path to qmd (use `$QMD_PATH` from Step 6).

On Windows, replace `fcntl` with `msvcrt` for file locking, or skip locking:

### macOS/Linux:

```python
import json, os, fcntl

path = os.path.expanduser("~/.claude/settings.json")
lock_path = path + ".lock"
qmd_path = "<QMD_PATH>"

os.makedirs(os.path.dirname(path), exist_ok=True)

with open(lock_path, "a") as lock_f:
    fcntl.flock(lock_f, fcntl.LOCK_EX)
    try:
        with open(path) as f:
            content = f.read().strip()
            settings = json.loads(content) if content else {}
    except FileNotFoundError:
        settings = {}
    except json.JSONDecodeError:
        print("ERROR: ~/.claude/settings.json contains invalid JSON.")
        raise SystemExit(1)

    if not isinstance(settings, dict):
        print("ERROR: ~/.claude/settings.json is not a JSON object.")
        raise SystemExit(1)

    if not isinstance(settings.get("mcpServers"), dict):
        settings["mcpServers"] = {}

    settings["mcpServers"]["qmd"] = {
        "command": qmd_path,
        "args": ["mcp"]
    }

    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    print("Done")
```

### Windows:

Same logic but use `os.path.join(os.environ["USERPROFILE"], ".claude", "settings.json")` for the path and skip `fcntl` (use a simple try/except for concurrent access).

Show the user what was written:

> "Added qmd to your Claude settings at `~/.claude/settings.json`:
> ```json
> "qmd": { "command": "<qmd_path>", "args": ["mcp"] }
> ```
> This gives Claude the `query`, `get`, `multi_get`, and `status` tools for searching your context files in every future session."

## Step 10: Verify and summarize

> "The MCP server will be available next time Claude Code starts a new session. To verify it's working, start a new session and ask Claude to search your context files."

Show the summary:

> **Setup complete.** Here's what you can now do:
>
> | What you want | What to do |
> |---------------|-----------|
> | Add more directories | `qmd collection add "<path>" --name <name> --mask "**/*.md"` |
> | Re-index after adding files | `qmd update && qmd embed` |
> | Search your context | Just ask Claude (e.g., "find my notes about Acme Corp") |
> | List what's indexed | `qmd collection list` |
>
> **Tips:**
> - Add YAML frontmatter to your context files (type, name, tags, summary) for better search results
> - Run `qmd update && qmd embed` after adding or editing files to keep the index current
> - To auto-reindex on file changes, run `qmd embed --watch` in a background terminal
> - Add descriptions to your collection for better search: `qmd context add qmd://business-context/ "Business context files: customers, services, pricing, SOPs"`
> - Check index health anytime with `qmd status`

## Step 11: Write marker

```bash
mkdir -p ~/.claude/luca-ops-kit && echo "qmd $("$QMD_PATH" --version 2>/dev/null) configured $(date +%Y-%m-%d)" > ~/.claude/luca-ops-kit/context-search-configured
```

## Error handling

- If any step fails, tell the user clearly what failed and how to fix it manually.
- Never leave partial state without informing the user what was and wasn't completed.
- If a command produces a "bindings" or "native module" error: the most common cause is pnpm blocking builds. Offer to reinstall with npm.
- If qmd's MCP interface has changed (no `mcp` subcommand detected), tell the user: "qmd's MCP server command may have changed. Check `qmd --help` for the current syntax and update `~/.claude/settings.json` under `mcpServers` manually."
- On Windows, if Python is not available, fall back to writing the JSON config via Node.js or instruct the user to add the entry manually.
