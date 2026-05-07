---
name: Audit Skills
description: Audit the full skill library — detect overlapping skills across scopes and run a rotating quality review. Trigger on "audit skills", "review all skills", or "check skill library".
version: 0.1.0
---

# Audit Skills

Scan all installed skills for overlaps, then run a quality audit on a rotating subset so every skill gets reviewed over time without exhausting a single session.

## Step 1 — Collect skill data

Invoke list-skills with `mode: raw` in the opening message. Capture the TSV rows: `(skill_name, attribution, description, line_count, path)`. `path` is the absolute path to the skill's `SKILL.md` and is the unique identifier used throughout this skill.

If zero rows returned: tell the user "No skills found. Check that skills are installed under `skills/`, `plugins/`, or `~/.claude/`." Stop.

## Step 2 — Detect overlaps

Scan the TSV inline (no sub-agent needed — lightweight check). Identify:

- **Same-name overlap:** skill name appears in 2+ attributions (e.g. `audit-skill` in both `(global)` and a plugin). Likely a duplicate or version conflict.
- **Description overlap:** pairs whose one-line descriptions suggest the same function (semantic judgment — short, human-authored strings are well-suited to this).

If overlaps found, present:

| Skill | Scopes | Rationale |
|-------|--------|-----------|

If none found: print "No overlapping skills detected — no action needed." Then continue.

## Step 3 — Load and reconcile round-robin state

Read `.claude/audit-skills-state.json`. If missing or malformed (JSON parse error): create it fresh and notify the user: "State file was reset due to a read error."

Build the current skill list: all skill names from Step 1, sorted alphabetically.

Reconcile against saved `skills_order` (a list of paths):
- Remember which path sits at the current cursor position in the saved list.
- Build the new list: all paths from Step 1, sorted alphabetically. Add paths not in the saved list at the end; drop paths that no longer exist.
- Find that remembered path in the new list and resume from there. If it was deleted, move forward one step at a time — wrapping from the last entry back to the first if needed — until a surviving path is found.
- If the list is empty: tell the user "No skills remain to audit." Stop.

Pick the next `batch_size` paths starting from the current position. Wrapping occurs when the selection reaches the end of the list and restarts from the beginning. Defer the wrap notification to Step 6.

State file structure:
```json
{
  "skills_order": ["/abs/path/to/skill-a/SKILL.md", "/abs/path/to/skill-b/SKILL.md"],
  "cursor": 2,
  "last_run_date": "2026-05-07",
  "batch_size": 3
}
```

Note on first creation: this file may or may not be git-tracked depending on your project's `.gitignore` — check before assuming it will be shared across machines.

## Step 4 — Confirm with user

Use `AskUserQuestion` (multiSelect: true, all pre-selected):

> "I'm going to fully review these [N] skills. That usually takes a few minutes each. Ready to continue, or would you like to skip any?"

List the skills by name (display only). Internally track each selection by its path from the TSV. Proceed only with confirmed paths. If the user deselects all skills, skip Step 5 and go directly to Step 6.

## Step 5 — Audit each confirmed skill

For each confirmed skill:

1. Use the `path` column from the TSV row directly. If the file does not exist at that path, note "Could not find SKILL.md for `<skill-name>` — skipping." and move to the next skill.
2. Open an `audit-skill` session and provide the path in the opening message — this satisfies `audit-skill`'s Step 1 condition so it proceeds without prompting. If `audit-skill` is unavailable, note "audit-skill not found — skipping `<skill-name>`." and move to the next skill.
3. Run `audit-skill` Steps 1–7 in full. The user will be prompted for improvement choices within each audit.
4. Present the result before moving to the next skill.

After all confirmed skills are processed:
- Advance cursor by `batch_size` (the planned window, regardless of how many were confirmed — skipped skills stay in rotation and reappear on the next pass).
- Apply `mod total_skills` to wrap correctly.
- Set `last_run_date` to today.
- Write the state file.

## Step 6 — Summary

1. **Overlaps:** If Step 2 found overlaps, print "See overlap analysis above." If none, print "No overlapping skills detected — no action needed."
2. **Audit results:** one row per audited skill — skill name, initial score, final score.
3. **Progress:** "You've covered X of Y skills this cycle. Next run will pick up at `<skill_name>`."
4. **Wrap (if applicable):** If the cursor wrapped during this run: "You've now reviewed every skill at least once. Starting a new full cycle."

## Self-reflection

If no skills were audited (all deselected or all skipped due to errors), note "Nothing audited this session — self-reflection skipped." and stop.

Otherwise, spawn a Haiku sub-agent. Pass it the Step 6 summary, the final state file contents, and the list of confirmed vs. skipped skills. Score each criterion 0–10. If average < 9.5, revise and re-score (max 3 iterations; stop if score stops improving). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md, show it to the user, and apply on approval.

1. **Overlap quality** — both same-name and description overlap types were checked; flagged pairs are genuinely similar; no obvious overlaps were missed
2. **Round-robin integrity** — cursor advanced by `batch_size`, anchored by path after reconciliation, state file written correctly
3. **Delegation fidelity** — each confirmed skill went through the full `audit-skill` 7-step flow with its path passed in the opening message
4. **User control** — no skill was audited without explicit user confirmation in Step 4
5. **Token efficiency** — Step 2 runs inline (no sub-agent); no unnecessary back-and-forth; batch size kept small relative to session budget
6. **Summary usefulness** — Step 6 gives the user a clear next action (which overlaps to address, which skills most need follow-up)

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Invoke list-skills in raw mode rather than embedding its script | Single source of truth for the data-collection script; raw mode is the DRY interface for skills that need structured data |
| Overlap detection runs every session | The skill library can change between runs; re-scanning is cheap relative to missing a new duplicate |
| No sub-agent for Step 2 (overlap scan) | ~76 TSV rows and lightweight semantic judgment — dispatching a sub-agent adds latency with no quality gain |
| Semantic judgment for description overlap, not string similarity | Skill descriptions are short and human-authored; Claude's semantic read is more reliable than word-overlap heuristics at this scale |
| Cursor advances by `batch_size`, not by confirmed count | Skipped skills stay in rotation and reappear naturally; advancing by confirmed count would silently drop skips |
| Cursor anchored by path, not index | Index-based cursor breaks when skills are deleted before the cursor; path-based anchoring is unique across scopes (unlike names, which can duplicate) and stable across list changes. Caveat: paths for cached plugin skills change on version bumps — the cursor advances to the next surviving path in that case |
| Wrap message deferred to Step 6 | Firing it in Step 3 (before confirmation) would tell the user "cycle complete" before they've reviewed anything this session |
| `audit-skill` invoked as a sequential interactive session | `audit-skill` calls `AskUserQuestion` for improvement approvals — silently batching would violate the human-approval principle |
| Default batch size = 3 | Enough progress per session; small enough not to exhaust token budget on auditing alone |
| State file at `.claude/audit-skills-state.json` | Project-local; `.claude/` is the established container for project-level Claude metadata |
| 6 self-reflection criteria (exceeds project norm of 2–5) | All 6 are genuinely distinct and collectively exhaustive for this multi-step orchestration skill; merging any two would lose precision |
