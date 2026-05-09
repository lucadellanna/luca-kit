# Design decisions

| Decision | Rationale |
|----------|-----------|
| Open-ended Q&A instead of field-by-field form | Non-technical users find structured forms intimidating; free text with extraction is more natural and captures nuance |
| Two interview questions before preview | Minimises friction; one gap-fill follow-up is enough if answers are thin; don't turn it into an interview |
| Step 3 explicitly asks for the user's name | Name is rarely volunteered in a professional context without prompting |
| Decision authority hinted in Step 3, gap check as safety net | Step 3 includes "what you can decide independently" to elicit authority naturally; gap check catches it if the user still omits it |
| Gap check covers all blank fields, not just decision authority | Hard-coding one field as the sole trigger would silently drop other missing fields |
| Partial update routing (company / role / both) | Binary update-or-keep forces a full re-run even when only a title changed; routing by section reduces friction for real-world partial updates. Skipped sections are carried forward from the existing file, never treated as blank, to prevent overwriting unchanged data or re-asking answered questions |
| Preview loop capped at 3 rounds | Prevents infinite correction loops; after 3 rounds, ask for explicit save confirmation |
| Voice-style answer handling | Voice input produces filler words and run-on sentences; extractor must handle gracefully, flagging blanks rather than hallucinating |
| File at `~/.claude/memory/work-context.md` | Global path: never in git, survives Conductor workspace rotation, available in every project and future workspace |
| Index pointer in `~/.claude/MEMORY.md` | Global MEMORY.md is loaded in all projects and all Conductor instances; the only index that satisfies the cross-workspace availability requirement |
| `last_updated` date in frontmatter | Context goes stale; the date makes staleness visible without opening the file |
| Do not collect: projects, KPIs, tech stack, team roster, competitive info | Too volatile or too sensitive; belongs in project-level context, not a persistent work profile |
| `last_updated` uses date from session context, not a system call | Claude Code provides `currentDate` in every session via system prompt; no tool call needed. The `YYYY-MM-DD` placeholder in the template is replaced at runtime with that value. |
| MEMORY.md update logic handles three cases explicitly | File exists with section, file exists without section, file doesn't exist. Three cases are necessary; simplifying to "append" would create duplicate entries on re-runs. |
| Self-modification in Self-reflection is intentional | Drafting a skill edit on scoring failure is the standard luca-ops-kit quality loop, applied in all skills. Changes require user approval before writing; no silent self-modification occurs. |
| POSIX tools assumed (`mkdir -p`, `~` expansion) | Claude Code runs on macOS and Linux; Windows is out of scope for this skill |
| Self-reflection runs after write, not before | Step 5 preview is the human quality gate for extraction accuracy; the self-reflection is retrospective skill improvement, not data correction. Moving scoring before write would add latency to the user-facing flow without adding safety beyond what Step 5 already provides. |
