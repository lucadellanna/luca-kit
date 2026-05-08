# luca-ops-kit project memory

## Workflow patterns

**Git commit with env-var prefix**: use `python3 -c "open('/tmp/msg.txt','w').write(msg)"` + `git commit -F /tmp/msg.txt` instead of heredocs when `SPECS_REVIEWED=1` or similar env-var prefixes are needed; shell metacharacter expansion breaks `$(cat <<'EOF'...)` syntax.

**Subagents: pass paths not content**: pass file paths to subagents; let them read with their own tools. Exception: filtering or transformation needed before the subagent sees the content.

**Subagent review prompts**: always include "quote the exact lines you are flagging" : prevents hallucinated findings that cite non-existent or misread content.

## Design patterns

**Raw-mode inter-skill data contract**: any skill that produces data another skill may consume must support `mode: raw` in the opening message: return structured TSV/JSON output, skip rendering. Never embed another skill's script inline; invoke in raw mode instead. Established in `list-skills` v0.2.
