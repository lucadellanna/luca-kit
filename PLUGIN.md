# luca-ops-kit — Plugin Reference

## Installation

```
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-operating-kit@luca-ops-kit
```

## Skills

Invoke by name in any Claude Code conversation.

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `create-skill` | `/create-skill` | Walks you through turning a procedure or SOP into a reusable Claude skill |
| `reflect` | `/reflect` | Reviews a conversation to surface learnings and propose skill improvements |

## How it works

Skills are structured workflows — Claude follows them step by step, asks you targeted questions, and produces a consistent output. You don't need to know how to prompt; the skill guides you.

Each skill includes a self-scoring loop: Claude scores its own output against defined success criteria and revises until the score is ≥ 9.5/10.

## Layer model

This plugin ships **meta-skills** only — tools for building and governing procedures. The actual business procedures for your industry come from your holding company or franchisor as a separate plugin installed on top.

## Updates

To get the latest version, remove and reinstall:

```
/plugin uninstall luca-operating-kit
/plugin marketplace remove luca-ops-kit
/plugin marketplace add lucadellanna/luca-ops-kit
/plugin install luca-operating-kit@luca-ops-kit
```
