---
name: List Skills
description: List all installed skills with plugin, description, and line count. Trigger on "what skills do I have?", "list skills", or "show available workflows".
version: 0.2.0
---

# List Skills

## Step 1: Collect all skill data

Run this Python script via Bash. It scans all four locations and returns one TSV row per skill.

```python
import os, re, json

def get_skill_info(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        desc = None
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                m = re.search(r'^description:\s*[">]?\s*(.+)$', content[3:end], re.M)
                if m:
                    desc = m.group(1).strip().strip('"\'').replace('\t', ' ')
        return desc, len(lines)
    except Exception:
        return None, 0

def get_plugin_meta(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d.get('name', '?').replace('\t', ' '), d.get('author', {}).get('name', '?').replace('\t', ' ')
    except Exception:
        return '?', '?'

rows = []

# 1. Project plugins
for plugin_dir in sorted(os.listdir('plugins')) if os.path.isdir('plugins') else []:
    pname, pauthor = get_plugin_meta(f'plugins/{plugin_dir}/.claude-plugin/plugin.json')
    sdir = f'plugins/{plugin_dir}/skills'
    if not os.path.isdir(sdir):
        continue
    for skill in sorted(os.listdir(sdir)):
        p = f'{sdir}/{skill}/SKILL.md'
        if not os.path.isfile(p):
            continue
        desc, lcount = get_skill_info(p)
        rows.append((skill, f'{pname} / {pauthor}', desc or '—', lcount))

# 2. Project root skills
if os.path.isdir('skills'):
    for skill in sorted(os.listdir('skills')):
        p = f'skills/{skill}/SKILL.md'
        if not os.path.isfile(p):
            continue
        desc, lcount = get_skill_info(p)
        rows.append((skill, '(local)', desc or '—', lcount))

# 3. Global custom skills (~/.claude/skills/)
gskills = os.path.expanduser('~/.claude/skills')
if os.path.isdir(gskills):
    for skill in sorted(os.listdir(gskills)):
        p = f'{gskills}/{skill}/SKILL.md'
        if not os.path.isfile(p):
            continue
        desc, lcount = get_skill_info(p)
        rows.append((skill, '(global)', desc or '—', lcount))

# 4. Global plugin cache — latest version per plugin only
cache = os.path.expanduser('~/.claude/plugins/cache')
if os.path.isdir(cache):
    for mkt in sorted(os.listdir(cache)):
        for plugin_dir in sorted(os.listdir(f'{cache}/{mkt}')):
            versions = sorted(os.listdir(f'{cache}/{mkt}/{plugin_dir}'))
            if not versions:
                continue
            latest = versions[-1]
            base = f'{cache}/{mkt}/{plugin_dir}/{latest}'
            pname, pauthor = get_plugin_meta(f'{base}/.claude-plugin/plugin.json')
            sdir = f'{base}/skills'
            if not os.path.isdir(sdir):
                continue
            for skill in sorted(os.listdir(sdir)):
                if skill == 'upstream':
                    continue
                p = f'{sdir}/{skill}/SKILL.md'
                if not os.path.isfile(p):
                    continue
                desc, lcount = get_skill_info(p)
                rows.append((skill, f'{pname} / {pauthor}', desc or '—', lcount))

print(f'TOTAL:{len(rows)}')
for r in rows:
    print('\t'.join([str(r[0]), str(r[1]), str(r[2])[:100], str(r[3])]))
```

Note the `TOTAL:N` line — used in self-reflection.

## Step 2: Present

Parse the TSV output. If zero rows: say "No skills found. Check that skills are installed under `skills/`, `plugins/`, or `~/.claude/`." Stop.

Otherwise, render as a markdown table sorted by plugin then skill name:

| Skill | Plugin / Author | Description | Lines |
|-------|-----------------|-------------|-------|

End with: `<N> skills found across <M> source(s).`

No follow-up questions.

## Self-reflection

Spawn a Haiku sub-agent. Pass it the row count from `TOTAL:N`, the rendered table, and the raw TSV data from Step 1, with these criteria:

1. **Completeness** — row count in table matches `TOTAL:N` from the script
2. **Accuracy** — spot-check 3 random rows: description and line count match the file
3. **Attribution** — every row identifies its plugin/author or `(local)`/`(global)`

Score each 0–10. If any criterion scores below 8, draft a concise edit to this SKILL.md, show the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Embedded Python script for Steps 1–2 | 159 skills = 159 Read calls without a script; 2 Bash calls with one. Batch wins at any scale. |
| Latest version only for cached plugins | Multiple cached versions create duplicate rows; only the active version matters to the user |
| Skip `upstream/` subdirectories | These are upstream copies stored for diffing, not active skills |
| `~/.claude/skills/` via Python `os.listdir` | Glob tool may not reach this path due to sandbox restrictions; Python bypasses this |
| Frontmatter `description:` over body summary | Canonical one-liner; summarising the body risks paraphrasing |
| Sort by plugin then name | Groups related skills; pure alpha scatters plugin siblings |
| No search/filter in v0.1 | Sufficient for current scale; add when user asks |
