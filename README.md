# luca-ops-kit & luca-dev-kit

> **Status: Early access / Pre-release.** These plugins are under active development. Features may change, break, or be removed without notice. Not ready for production use.

This marketplace ships two Claude plugins:

| Plugin | Audience | Purpose |
|--------|----------|---------|
| **luca-ops-kit** | Organizations and individuals | Craft reusable skills, maintain a self-improving setup, and govern your Claude skill library |
| **luca-dev-kit** | Developers | Pre-PR quality gates, autonomous Gemini review loop, and pre-commit hook management |
| **luca-reflection-kit** | Anyone | Self-reflection and cross-session learning: scan conversations for improvement points and mine recurring patterns |

Most companies and people using AI are stuck at the "clever individual prompts" stage: useful experiments, inconsistent execution, little reuse, and no lasting memory. These plugins provide guided workflows to make good procedures explicit and reusable, so know-how doesn't stay trapped in individual heads or chat histories.

## Installation

Install in Claude Code, Cowork, or both; if you use both apps, follow each procedure separately.

### luca-ops-kit

**Claude Code** (requires [Claude Code](https://claude.ai/code)):

```
/plugin marketplace add lucadellanna/luca-kit
/plugin install luca-ops-kit@lucadellanna
```

**Claude Cowork:** Left sidebar → Customize → Plugins → Personal → **+** → Add marketplace → `lucadellanna/luca-kit` → click on it → Install

**After installing**, run `/luca-ops-recommended-setup` to add best-practice rules and see a privacy/backup checklist.

**To uninstall:** If you ran `/luca-ops-recommended-setup`, run `/undo-setup` first to remove rules it added to your global Claude config. Then:

```
/plugin uninstall luca-ops-kit@lucadellanna/luca-kit
```

**To enable auto-updates (Claude Code):** Type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-ops-kit`, then select **Enable updates**.

**To enable auto-updates (Cowork):** Left sidebar → Customize → Browse Plugins → Personal → luca-ops-kit → **···** → Sync automatically

### luca-dev-kit

Claude Code only. Requires GitHub CLI (`gh`) and [Gemini Code Assist](https://codeassist.google/) installed on the repo.

If you already added the `lucadellanna/luca-kit` marketplace (e.g. for luca-ops-kit or luca-reflection-kit), skip the first command.

```
/plugin marketplace add lucadellanna/luca-kit
/plugin install luca-dev-kit@lucadellanna
```

**After installing** (persistent local checkout only, not needed in Conductor): run `/luca-dev-recommended-setup` to install pre-commit hooks and review the Gemini Code Assist requirement for `review-loop`.

**To uninstall:**

```
/plugin uninstall luca-dev-kit@lucadellanna/luca-kit
```

**To enable auto-updates:** Type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-dev-kit`, then select **Enable updates**.

### luca-reflection-kit

```
/plugin marketplace add lucadellanna/luca-kit
/plugin install luca-reflection-kit@lucadellanna
```

**To uninstall:**

```
/plugin uninstall luca-reflection-kit@lucadellanna/luca-kit
```

## Skills

### luca-ops-kit

| Skill | What it does |
|-------|-------------|
| **luca-ops-recommended-setup** | First-run wizard: adds three best-practice rules to your Claude config |
| **undo-setup** | Reverses everything /luca-ops-recommended-setup added so you can cleanly uninstall the plugin |
| **build-work-context** | Interviews you about your company and role, then saves a persistent profile so Claude doesn't need to ask "who do you work for?" every session |
| **create-skill** | Turns a procedure, SOP, checklist, or verbal description into a ready-to-use skill file, scoring and improving it before saving |
| **list-skills** | Lists every installed skill with its plugin, one-line description, and file size in a single table |
| **audit-skill** | Scores a single skill against 7 quality dimensions (clarity, security, instruction explicitness, and more), proposes improvements, and iterates until the bar is met |
| **audit-skills** | Scans your whole skill library for overlapping skills, then audits a rotating batch of 3 so every skill gets reviewed over time |
| **audit-claude** | Scans your CLAUDE.md and memory files for bloat and cross-file redundancy, proposes targeted cuts, and verifies nothing meaningful was lost |
| **setup-context-search** | *(Power users)* Installs [qmd](https://github.com/tobi/qmd) and configures it as an MCP server, giving Claude semantic search over your context files (customers, offerings, projects). Requires Node.js 22+ |

### luca-dev-kit

| Skill | Trigger | What it does |
|---|---|---|
| **luca-dev-recommended-setup** | `/luca-dev-recommended-setup` | One-time setup: installs pre-commit hooks, notes Gemini Code Assist requirement. Run once per machine in persistent local checkouts. |
| **open-pr** | "open pr", "create pr", "/open-pr" | Triple review, fix findings, typecheck, push, create PR, hand off to review-loop |
| **review-loop** | Auto-invoked by open-pr; or "review loop" | Polls Gemini, classifies threads, applies fixes, re-triggers review, repeats until clean |
| **triple-review** | "triple review" | Three-lens parallel review: principles, recurring bug patterns, structural integrity |
| **targeted-review** | "/targeted-review", "targeted review", "focused review of <file>" | Single-file ad-hoc review with a derived (or user-supplied) checklist; bug-only findings via a structural FINDINGS marker. Catches bugs broad reviews miss |
| **specs-adherence-review** | "check specs", "adheres to principles?" | Checks changed code against CLAUDE.md rules |
| **install-pre-commit-hooks** | Invoked by luca-dev-recommended-setup | One-time hook setup: em-dash check, gitleaks, optional typecheck |

## Hooks

### luca-ops-kit

Installed automatically with the plugin (no setup needed):

| Hook | Event | What it does |
|------|-------|-------------|
| **claude-md-tidy** | PostToolUse (Edit/Write) | After any edit to a CLAUDE.md or AGENTS.md file, injects a 7-criterion review (conciseness, duplication, contradictions, scope, ephemerality, vague triggers, context pollution) with quantitative metrics |
| **stop-apology-check** | Stop | When the response contains a self-correction phrase (e.g. "you're right", "my mistake", "I missed") without a `★ rule-update` widget, rule-file edit, error-log append, or explicit one-off escape, blocks the stop and asks Claude to apply the Error → rule update contract. Forces meta-cognitive learning to actually happen instead of being deferred. See `plugins/luca-ops-kit/CLAUDE.md` for the full contract. |
| **hedge-scan** | PostToolUse (Edit/Write/MultiEdit) | On edits to rule-like files (CLAUDE.md, SKILL.md, hook scripts, command files), warns when added list-item lines contain hedge words ("try to", "consider", "prefer", "should probably"). Strips quoted spans first, so hedge words used as quoted examples are not flagged. Enforces the "rules must use imperative language" principle. |

### luca-reflection-kit

| Skill | What it does |
|-------|-------------|
| **reflect** | After a session, extracts what went well, what went wrong, and what should become a memory update, skill improvement, or new skill |
| **dream** | Mines your /reflect logs to surface patterns across sessions: recurring issues never fixed, memory contradictions, and improvements that keep coming up but never land |

#### Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| **optimization-hint** | UserPromptSubmit | On every prompt, reminds Claude to append a one-sentence optimization hint if the prior response involved 8+ tool calls (reusable skill, memory-worthy pattern, or workflow improvement) |

## How it works

### luca-ops-kit

The plugin ships **meta-skills**: structured workflows for building, auditing, and improving procedures. You can use it standalone to create, audit, and govern your own skill library.

**Who uses it:**

| Role | What they do with it |
|------|---------------------|
| Manager | Points it at a procedure and asks what should become a skill |
| Admin | Turns a repeated reporting task into a reusable workflow |
| Salesperson | Converts a successful call-prep process into a skill |
| Frontline manager | Builds an SOP from tacit know-how |
| Local power user | Audits, consolidates, and governs the team's skill library |

### Context search (optional, power users)

As your context library grows (customers, offerings, projects, SOPs), finding the right file becomes harder. `/setup-context-search` installs [qmd](https://github.com/tobi/qmd), a local semantic search engine, and wires it into Claude as an MCP server. After setup, Claude can search your context files natively using keyword, semantic, or hybrid queries without you needing to remember file names or locations.

**Requirements:** Node.js 22+, npm or bun, ~2.2 GB disk for local AI models (runs entirely on your machine, no cloud).

**What it enables:**

| Query type | Example | How it works |
|---|---|---|
| Keyword | "Find the Acme Corp file" | Fast BM25 full-text search |
| Semantic | "Customers similar to Acme" | Vector similarity via local embeddings |
| Hybrid | "Healthcare clients with active contracts" | Keyword + semantic + LLM re-ranking |

Run `/setup-context-search` once; Claude gets the search tools permanently.

### luca-dev-kit

Write "open pr" and Claude handles the rest: pre-PR quality gates (triple-review against principles, recurring bug patterns, and structural integrity), PR creation, and an autonomous Gemini review loop that fixes comments and re-triggers review until the PR is clean.

## For holdco customers

If your organization receives luca-ops-kit through a holding company, franchisor, or trade association, skills are delivered in layers. Your holdco curates domain skills (the actual business procedures for your industry) on top of luca-ops-kit's meta-skills, and your team can further adapt them to local context.

| Layer | Who provides it | What it contains |
|-------|----------------|-----------------|
| luca-ops-kit | Luca Dellanna | Meta-skills: build, audit, and improve procedures |
| Holdco layer | Your holding company, franchisor, or trade association | Domain skills tailored to your industry (e.g., onboarding checklists, compliance workflows, reporting templates) |
| Partner layer | Your team | Local adaptations: company-specific terminology, approval chains, and tooling integrations |

## Disclaimer

These plugins (luca-ops-kit, luca-dev-kit, and luca-reflection-kit) are for business use only, and are intended exclusively for businesses and professionals acting in the course of a trade or profession. By using them, you represent that you are not a consumer under Italian law (Article 3, Codice del Consumo). They are designed exclusively for use with Claude (Anthropic); any adaptation to other AI providers is unsupported and at the user's sole risk. They are provided "as-is", without warranty of any kind, express or implied.

The plugins depend on third-party services (including Anthropic (Claude API) and Claude Code) that Luca Dellanna does not control. Changes to those services, including model deprecations, pricing changes, or discontinuation, are not Luca Dellanna's responsibility. The plugins run locally on your machine; Luca Dellanna does not collect or process your data.

Outputs are generated by Anthropic Claude; the plugins orchestrate prompts but do not themselves produce content. AI-generated outputs may contain errors, fabrications, or hallucinations, and may appear authoritative but be factually wrong. You are solely responsible for reviewing all outputs before acting on them. These plugins are not a substitute for professional legal, financial, medical, or other expert advice; do not use them for legal filings, medical decisions, financial transactions, regulated activities, or high-risk AI applications (EU AI Act, Reg. 2024/1689) without independent expert review.

To the maximum extent permitted by applicable law, and in any case limited to fees paid in the 12 months preceding the claim, Luca Dellanna accepts no liability for any loss, damage, or consequence, whether direct or indirect, arising from use of these plugins or reliance on their outputs. This includes losses caused by third-party service changes (Anthropic, Claude Code, etc.). Nothing in this disclaimer excludes liability that cannot be excluded under applicable law (including liability for fraud, gross negligence, or death or personal injury caused by negligence). Full terms will be published at luca-dellanna.com before commercial launch. This disclaimer is governed by Italian law; any disputes shall be resolved in the Italian courts.

*Disclaimer v1.0, 2026-05-10*

## License

Source-available, not open-source. You may inspect the repository and use it for personal evaluation. Commercial, client-facing, team, or organizational use requires a paid license. Contact [Luca@Luca-Dellanna.com](mailto:Luca@Luca-Dellanna.com) for more information.
