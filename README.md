# luca-ops-kit & luca-dev-kit

> **Status: Early access / Pre-release.** These plugins are under active development. Features may change, break, or be removed without notice. Not ready for production use.

This marketplace ships two Claude plugins:

| Plugin | Audience | Purpose |
|--------|----------|---------|
| **luca-ops-kit** | Organizations and individuals | Craft reusable skills, maintain a self-improving setup, and extract lasting learnings from every session |
| **luca-dev-kit** | Developers | Pre-PR quality gates, autonomous Gemini review loop, and pre-commit hook management |

Most companies and people using AI are stuck at the "clever individual prompts" stage: useful experiments, inconsistent execution, little reuse, and no lasting memory. These plugins provide guided workflows to make good procedures explicit and reusable, so know-how doesn't stay trapped in individual heads or chat histories.

## Installation

Install in Claude Code, Cowork, or both; if you use both apps, follow each procedure separately.

### luca-ops-kit

**Claude Code** (requires [Claude Code](https://claude.ai/code)):

```
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-ops-kit@lucadellanna
```

**Claude Cowork:** Left sidebar → Customize → Plugins → Personal → **+** → Add marketplace → `lucadellanna/luca-ops-kit` → click on it → Install

**To uninstall:** If you ran `/luca-ops-recommended-setup`, run `/undo-setup` first to remove hooks and rules it added to your global Claude config. Then:

```
/plugin uninstall luca-ops-kit@lucadellanna/luca-ops-kit
```

**To enable auto-updates (Claude Code):** Type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-ops-kit`, then select **Enable updates**.

**To enable auto-updates (Cowork):** Left sidebar → Customize → Browse Plugins → Personal → luca-ops-kit → **···** → Sync automatically

### luca-dev-kit

Claude Code only. Requires GitHub CLI (`gh`) and [Gemini Code Assist](https://codeassist.google/) installed on the repo.

If you already added the `lucadellanna/luca-ops-kit` marketplace (e.g. for luca-ops-kit), skip the first command.

```
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-dev-kit@lucadellanna
```

**To uninstall:**

```
/plugin uninstall luca-dev-kit@lucadellanna/luca-dev-kit
```

**To enable auto-updates:** Type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-dev-kit`, then select **Enable updates**.

## Skills

### luca-ops-kit

| Skill | What it does |
|-------|-------------|
| **luca-ops-recommended-setup** | First-run wizard: adds three best-practice rules to your Claude config and offers two automation hooks (skill-check reminder, long-prompt clarity check) |
| **undo-setup** | Reverses everything /luca-ops-recommended-setup added (rules, hooks, and scripts) so you can cleanly uninstall the plugin |
| **build-work-context** | Interviews you about your company and role, then saves a persistent profile so Claude doesn't need to ask "who do you work for?" every session |
| **create-skill** | Turns a procedure, SOP, checklist, or verbal description into a ready-to-use skill file, scoring and improving it before saving |
| **list-skills** | Lists every installed skill with its plugin, one-line description, and file size in a single table |
| **audit-skill** | Scores a single skill against 7 quality dimensions (clarity, security, instruction explicitness, and more), proposes improvements, and iterates until the bar is met |
| **audit-skills** | Scans your whole skill library for overlapping skills, then audits a rotating batch of 3 so every skill gets reviewed over time |
| **audit-claude** | Scans your CLAUDE.md and memory files for bloat and cross-file redundancy, proposes targeted cuts, and verifies nothing meaningful was lost |
| **reflect** | After a session, extracts what went well, what went wrong, and what should become a memory update, skill improvement, or new skill |
| **dream** | Mines your /reflect logs to surface patterns across sessions: recurring issues never fixed, memory contradictions, and improvements that keep coming up but never land |

### luca-dev-kit

| Skill | Trigger | What it does |
|---|---|---|
| **open-pr** | "open pr", "create pr", "/open-pr" | Triple review, fix findings, typecheck, push, create PR, hand off to review-loop |
| **review-loop** | Auto-invoked by open-pr; or "review loop" | Polls Gemini, classifies threads, applies fixes, re-triggers review, repeats until clean |
| **triple-review** | "triple review" | Three-lens parallel review: principles, recurring bug patterns, structural integrity |
| **specs-adherence-review** | "check specs", "adheres to principles?" | Checks changed code against CLAUDE.md rules |
| **install-pre-commit-hooks** | "install hooks" | One-time hook setup: em-dash check, gitleaks, optional typecheck |

## How it works

### luca-ops-kit

The plugin ships **meta-skills**: structured workflows for building, auditing, and improving procedures. Domain skills (the actual business procedures for your industry) are curated and added by your holding company.

| Layer | Who provides it | What it contains |
|-------|----------------|-----------------|
| luca-ops-kit | Luca Dellanna | Meta-skills for building and improving procedures |
| Holdco layer | Your holding company, franchisor, or trade association | Domain skills for your industry |
| Partner layer | Your team | Local adaptations of holdco domain skills |

**Who uses it:**

| Role | What they do with it |
|------|---------------------|
| Manager | Points it at a procedure and asks what should become a skill |
| Admin | Turns a repeated reporting task into a reusable workflow |
| Salesperson | Converts a successful call-prep process into a skill |
| Frontline manager | Builds an SOP from tacit know-how |
| Local power user | Audits, consolidates, and governs the team's skill library |

### luca-dev-kit

Write "open pr" and Claude handles the rest: pre-PR quality gates (triple-review against principles, recurring bug patterns, and structural integrity), PR creation, and an autonomous Gemini review loop that fixes comments and re-triggers review until the PR is clean.

## Disclaimer

These plugins (luca-ops-kit and luca-dev-kit) are for business use only, and are intended exclusively for businesses and professionals acting in the course of a trade or profession. By using them, you represent that you are not a consumer under Italian law (Article 3, Codice del Consumo). They are designed exclusively for use with Claude (Anthropic); any adaptation to other AI providers is unsupported and at the user's sole risk. They are provided "as-is", without warranty of any kind, express or implied.

The plugins depend on third-party services — including Anthropic (Claude API) and Claude Code — that Luca Dellanna does not control. Changes to those services, including model deprecations, pricing changes, or discontinuation, are not Luca Dellanna's responsibility. The plugins run locally on your machine; Luca Dellanna does not collect or process your data.

Outputs are generated by Anthropic Claude; the plugins orchestrate prompts but do not themselves produce content. AI-generated outputs may contain errors, fabrications, or hallucinations, and may appear authoritative but be factually wrong. You are solely responsible for reviewing all outputs before acting on them. These plugins are not a substitute for professional legal, financial, medical, or other expert advice; do not use them for legal filings, medical decisions, financial transactions, regulated activities, or high-risk AI applications (EU AI Act, Reg. 2024/1689) without independent expert review.

To the maximum extent permitted by applicable law, and in any case limited to fees paid in the 12 months preceding the claim, Luca Dellanna accepts no liability for any loss, damage, or consequence — direct or indirect — arising from use of these plugins or reliance on their outputs. This includes losses caused by third-party service changes (Anthropic, Claude Code, etc.). Nothing in this disclaimer excludes liability that cannot be excluded under applicable law (including liability for fraud, gross negligence, or death or personal injury caused by negligence). Full terms will be published at luca-dellanna.com before commercial launch. This disclaimer is governed by Italian law; any disputes shall be resolved in the Italian courts.

*Disclaimer v1.0 — 2026-05-10*

## License

Source-available, not open-source. You may inspect the repository and use it for personal evaluation. Commercial, client-facing, team, or organizational use requires a paid license. Contact [Luca@Luca-Dellanna.com](mailto:Luca@Luca-Dellanna.com) for more information.
