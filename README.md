# luca-ops-kit

A meta-workflow toolkit for Claude that helps non-technical organizations turn recurring tasks, SOPs, wiki pages, and managerial know-how into reusable Claude Skills.

Most companies using AI are stuck at the "clever individual prompts" stage: useful experiments, inconsistent execution, little reuse, no lasting memory. luca-ops-kit provides the guided workflows to make good procedures explicit and reusable, so know-how doesn't stay trapped in individual heads or chat histories.

## Installation

Install in Claude Code, Cowork, or both; if you use both apps, follow each procedure separately.

### Claude Code

Requires [Claude Code](https://claude.ai/code).

**To install:** Run these two commands in Claude Code:

```
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-ops-kit@lucadellanna
```

**To uninstall:**

If you ran `/luca-ops-recommended-setup`, run `/undo-setup` first to remove hooks and rules it added to your global Claude config. Then:

```
/plugin uninstall luca-ops-kit@lucadellanna/luca-ops-kit
```

**To enable auto-updates:** Type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-ops-kit`, then select **Enable updates**.

### Claude Cowork

**To install:** Left sidebar → Customize → Plugins → Personal → **+** → Add marketplace → `lucadellanna/luca-ops-kit` → click on it → Install

**To enable auto-updates:** Left sidebar → Customize → Browse Plugins → Personal → luca-ops-kit → **···** → Sync automatically

## Who uses it

| Role | What they do with it |
|------|---------------------|
| Manager | Points it at a procedure and asks what should become a skill |
| Admin | Turns a repeated reporting task into a reusable workflow |
| Salesperson | Converts a successful call-prep process into a skill |
| Frontline manager | Builds an SOP from tacit know-how |
| Local power user | Audits, consolidates, and governs the team's skill library |

## How it works

The plugin ships **meta-skills**: structured workflows for building, auditing, and improving procedures. Domain skills (the actual business procedures for your industry) are curated and added by your holding company.

| Layer | Who provides it | What it contains |
|-------|----------------|-----------------|
| luca-ops-kit | Luca Dellanna | Meta-skills for building and improving procedures |
| Holdco layer | Your holding company, franchisor, or trade association | Domain skills for your industry |
| Partner layer | Your team | Local adaptations of holdco domain skills |

## Skills

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

## License

Source-available, not open-source. You may inspect the repository and use it for personal evaluation. Commercial, client-facing, team, or organizational use requires a paid license. Contact [Luca@Luca-Dellanna.com](mailto:Luca@Luca-Dellanna.com) for more information.

---

# luca-dev-kit

Developer workflow automation for Claude Code. Run "open pr" and Claude handles the rest: pre-PR quality gates, PR creation, and an autonomous Gemini review loop that fixes comments and re-triggers review until the PR is clean.

## Installation

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

| Skill | Trigger | What it does |
|---|---|---|
| **open-pr** | "open pr", "create pr", "/open-pr" | Triple review, fix findings, typecheck, push, create PR, hand off to review-loop |
| **review-loop** | Auto-invoked by open-pr; or "review loop" | Polls Gemini, classifies threads, applies fixes, re-triggers review, repeats until clean |
| **triple-review** | "triple review" | Three-lens parallel review: principles, recurring bug patterns, structural integrity |
| **specs-adherence-review** | "check specs", "adheres to principles?" | Checks changed code against CLAUDE.md rules |
| **install-pre-commit-hooks** | "install hooks" | One-time hook setup: em-dash check, gitleaks, optional typecheck |

## License

Same terms as luca-ops-kit above.
