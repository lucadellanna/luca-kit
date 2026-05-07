# luca-ops-kit

A meta-workflow toolkit for Claude that helps non-technical organizations turn recurring tasks, SOPs, wiki pages, and managerial know-how into reusable Claude Skills.

Most companies using AI are stuck at the "clever individual prompts" stage: useful experiments, inconsistent execution, little reuse, no lasting memory. luca-ops-kit provides the guided workflows to make good procedures explicit and reusable — so know-how doesn't stay trapped in individual heads or chat histories.

## Installation

Install in Claude Code, Cowork, or both — if you use both apps, follow each procedure separately.

### Claude Code

Requires [Claude Code](https://claude.ai/code).

**To install:** Run these two commands in Claude Code:

```
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-ops-kit@lucadellanna
```

**To uninstall:**

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

The plugin ships **meta-skills** — structured workflows for building, auditing, and improving procedures. Domain skills (the actual business procedures for your industry) are curated and added by your holding company.

| Layer | Who provides it | What it contains |
|-------|----------------|-----------------|
| luca-ops-kit | Luca Dellanna | Meta-skills for building and improving procedures |
| Holdco layer | Your holding company, franchisor, or trade association | Domain skills for your industry |
| Partner layer | Your team | Local adaptations of holdco domain skills |

## Skills

| Skill | What it does |
|-------|-------------|
| **create-skill** | Guides you through turning a procedure, SOP, or task description into a reusable Claude skill with built-in quality scoring |
| **reflect** | Analyzes a conversation to surface learnings, catch errors, and propose skill improvements or new skills worth creating |

## License

Commercial — licensed to holding companies and their portfolio companies. Contact [luca@luca-dellanna.com](mailto:luca@luca-dellanna.com) to purchase a license.
