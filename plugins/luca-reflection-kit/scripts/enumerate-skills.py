import glob
import os


def parse_fm(path):
    try:
        with open(path) as f:
            s = f.read(4000)
    except OSError:
        return None, None
    if not s.startswith("---"):
        return None, None
    end = s.find("---", 3)
    if end < 0:
        return None, None
    fm = s[3:end]
    name = desc = ""
    lines = fm.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("name:"):
            name = stripped[5:].strip().strip("\"'")
        elif stripped.startswith("description:"):
            val = stripped[12:].strip().strip("\"'")
            if val in (">", "|", ">-", "|-"):
                block = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                    block.append(lines[i].strip())
                    i += 1
                desc = " ".join(block)
                continue
            else:
                desc = val
        i += 1
    return name, desc[:140].replace("\n", " ")


skill_paths = (
    glob.glob(os.path.expanduser("~/.claude/plugins/cache/*/*/*/skills/*/SKILL.md"))
    + glob.glob(os.path.expanduser("~/.claude/skills/*/SKILL.md"))
    + glob.glob(".claude/skills/*/SKILL.md")
)
cmd_paths = (
    glob.glob(os.path.expanduser("~/.claude/plugins/cache/*/*/*/commands/*.md"))
    + glob.glob(os.path.expanduser("~/.claude/commands/*.md"))
    + glob.glob(".claude/commands/*.md")
)

print("=== SKILLS AVAILABLE ===")
for p in sorted(set(skill_paths)):
    n, d = parse_fm(p)
    if n:
        print(f"- {n}: {d}")

print()
print("=== COMMANDS AVAILABLE ===")
for p in sorted(set(cmd_paths)):
    n, d = parse_fm(p)
    if not n:
        n = os.path.basename(p)[:-3]
    print(f"- {n}: {d}")
