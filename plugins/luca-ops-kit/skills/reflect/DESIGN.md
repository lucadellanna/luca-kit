# Design decisions

| Decision | Rationale |
|----------|-----------|
| Haiku sub-agent for findings scoring (Step 3) | CLAUDE.md-mandated pattern; reduces confirmation bias and is cheaper than inline scoring; apparent token overhead is intentional |
| Haiku sub-agent for self-reflection | CLAUDE.md mandates a Haiku-scored self-reflection section in every skill; inline gate-checks would save tokens but violate the plugin convention |
| Bash dotfile check, not Glob | Glob excludes dotfiles by default and would silently miss `.enabled`/`.disabled`, re-prompting every session |
| All findings logged, not just acted-on ones | Gap between `findings` and `actions_taken` is the primary /dream signal |
| Structured `actions_taken` objects | Free-text lists can't be grouped across sessions; /dream needs typed, targetable entries |
| `memory_target` field on memory findings | Enables structured contradiction detection in /dream without free-text NLP |
| `finding_id` + `actions_taken[].finding_id` FK | Multiple findings can share `type` + `skill` in one session; without an explicit FK, /dream cannot distinguish which finding an action resolved, making "never acted on" detection unreliable |
| Python for atomic JSONL append | Single buffered write prevents partial lines from interrupted processes breaking /dream's line parser |
