---
name: list-skills
description: List all installed skills with plugin, description, and line count. Trigger on "what skills do I have?", "list skills", or "show available workflows".
version: 0.2.0
---

# List Skills

**Raw mode**: If another skill invokes this one and passes `mode: raw` in the opening message, run Step 1 only and return the TSV rows as-is. Skip Step 2 (table rendering). Raw mode exists so other skills can reuse the data collection script without parsing a rendered table.

## Step 1: Collect all skill data

Run this Python script via Bash. It scans all four locations and returns one TSV row per skill.

```python
import os, re, json

def get_skill_info(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        desc = None
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                m = re.search(r'^description:\s*[">]?\s*(.+)$', content[3:end], re.M)
                if m:
                    desc = m.group(1).strip().strip('"\'').replace('\t', ' ')
        help_path = os.path.join(os.path.dirname(os.path.abspath(path)), 'HELP.md')
        if os.path.isfile(help_path):
            with open(help_path, 'r', encoding='utf-8') as f:
                first = next((l.strip() for l in f if l.strip()), '')
            first = re.split(r'(?<=[.!?])\s', first, maxsplit=1)[0]
            first = re.sub(r'\*\*([^*]+)\*\*', r'\1', first).replace('\t', ' ')
            if first:
                desc = first
        return desc, len(content.splitlines())
    except (FileNotFoundError, IOError):
        return None, 0

def get_plugin_meta(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if not isinstance(d, dict):
            return '?', '?'
        name = str(d.get('name') or '?').replace('\t', ' ')
        author = d.get('author')
        author_name = str(author.get('name') or '?').replace('\t', ' ') if isinstance(author, dict) else '?'
        return name, author_name
    except (FileNotFoundError, IOError, json.JSONDecodeError, AttributeError, TypeError):
        return '?', '?'

def scan_skills(sdir, attribution, rows):
    if not os.path.isdir(sdir):
        return
    for skill in sorted(os.listdir(sdir)):
        if skill == 'upstream':
            continue
        p = os.path.join(sdir, skill, 'SKILL.md')
        if not os.path.isfile(p):
            continue
        desc, lcount = get_skill_info(p)
        rows.append((skill, attribution, desc or 'n/a', lcount, os.path.abspath(p)))

rows = []

# 1. Project plugins
if os.path.isdir('plugins'):
    for plugin_dir in sorted(os.listdir('plugins')):
        pname, pauthor = get_plugin_meta(os.path.join('plugins', plugin_dir, '.claude-plugin', 'plugin.json'))
        scan_skills(os.path.join('plugins', plugin_dir, 'skills'), f'{pname} / {pauthor}', rows)

# 2. Project root skills
scan_skills('skills', '(local)', rows)

# 3. Global custom skills (~/.claude/skills/)
scan_skills(os.path.expanduser('~/.claude/skills'), '(global)', rows)

# 4. Global plugin cache: latest version per plugin only
cache = os.path.expanduser('~/.claude/plugins/cache')
if os.path.isdir(cache):
    for mkt in sorted(os.listdir(cache)):
        mkt_path = os.path.join(cache, mkt)
        if not os.path.isdir(mkt_path):
            continue
        for plugin_dir in sorted(os.listdir(mkt_path)):
            plugin_path = os.path.join(mkt_path, plugin_dir)
            if not os.path.isdir(plugin_path):
                continue
            versions = sorted([d for d in os.listdir(plugin_path) if os.path.isdir(os.path.join(plugin_path, d))])
            if not versions:
                continue
            base = os.path.join(plugin_path, versions[-1])
            pname, pauthor = get_plugin_meta(os.path.join(base, '.claude-plugin', 'plugin.json'))
            scan_skills(os.path.join(base, 'skills'), f'{pname} / {pauthor}', rows)

print(f'TOTAL:{len(rows)}')
for r in rows:
    print('\t'.join([str(col).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ') for col in r]))
```

Note the `TOTAL:N` line; used in self-reflection.

## Step 2: Present

Parse the TSV output. If zero rows: say "No skills found. Check that skills are installed under `skills/`, `plugins/`, or `~/.claude/`." Stop.

Otherwise, render as a markdown table sorted by plugin then skill name:

| Skill | Plugin / Author | Description | Lines |
|-------|-----------------|-------------|-------|

End with: `<N> skills found across <M> source(s).`

No follow-up questions.

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent. Pass it the row count from `TOTAL:N`, the rendered table, and the raw TSV data from Step 1, with these criteria:

1. **Completeness**: row count in table matches `TOTAL:N` from the script
2. **Accuracy**: spot-check 3 random rows: description and line count match the file
3. **Attribution**: every row identifies its plugin/author or `(local)`/`(global)`

Score each 0–10. If any criterion scores below 8, draft a concise edit to this SKILL.md, show the user, and apply on approval.

