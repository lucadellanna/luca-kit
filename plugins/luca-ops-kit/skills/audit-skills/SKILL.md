---
name: Audit Skills
description: Audit the full skill library: detect overlapping skills across scopes and run a rotating quality review. Trigger on "audit skills", "review all skills", or "check skill library".
version: 0.1.0
---

# Audit Skills

Scan all installed skills for overlaps, then run a quality audit on a rotating subset so every skill gets reviewed over time without exhausting a single session.

## Step 1: Collect skill data

Invoke list-skills with `mode: raw` in the opening message. The output begins with a `TOTAL:N` header line (e.g. `TOTAL:5`); skip it. Parse each remaining line as a TSV row: `(skill_name, attribution, description, line_count, path)`. `path` is the absolute path to the skill's `SKILL.md` and is the unique identifier used throughout this skill.

If zero rows returned: tell the user "No skills found. Check that skills are installed under `skills/`, `plugins/`, or `~/.claude/`." Stop.

## Step 2: Detect overlaps

Scan the TSV inline (no sub-agent needed; lightweight check). Identify:

- **Same-name overlap:** skill name appears in 2+ attributions (e.g. `audit-skill` in both `(global)` and a plugin). Likely a duplicate or version conflict.
- **Description overlap:** pairs whose one-line descriptions suggest the same function (semantic judgment; short, human-authored strings are well-suited to this).

If overlaps found, present:

| Skill | Scopes | Rationale |
|-------|--------|-----------|

If none found: print "No overlapping skills detected; no action needed." Then continue.

## Step 3: Load round-robin state

Read `.claude/audit-skills-state.json` (this file is already excluded via `.gitignore`; it tracks local rotation progress and should not be committed). If missing: create it fresh with `{"next_audit_path": null, "last_run_date": null, "batch_size": 3}`. If malformed (JSON parse error): recreate it fresh and notify the user: "State file was reset due to a read error."

Get the sorted list of all paths from Step 1. If empty: tell the user "No skills remain to audit." Stop.

Find the starting path:
- If `next_audit_path` is null: start from the first path in the sorted list.
- If `next_audit_path` is not in the sorted list (skill deleted): find the first path alphabetically greater; if none exist, wrap to the first path.
- Otherwise: start from `next_audit_path`.

Let `total_skills` = the number of paths in the sorted list. Let `start_index` = the 0-based index of the starting path in the sorted list.

Pick the next `min(batch_size, total_skills)` paths starting from `start_index`. Wrap back to the beginning if needed. No path appears twice in the same selection.

Compute the new `next_audit_path` (to save after Step 5): the path at position `(start_index + min(batch_size, total_skills)) % total_skills` in the sorted list. If `start_index + min(batch_size, total_skills) >= total_skills`, set a wrap flag. Defer the wrap notification to Step 6.

State file structure:
```json
{
  "next_audit_path": "/abs/path/to/skill-a/SKILL.md",
  "last_run_date": "2024-01-01",
  "batch_size": 3
}
```


## Step 4: Confirm with user

Use `AskUserQuestion` (multiSelect: true, all pre-selected):

> "I'm going to fully review these [N] skills. That usually takes a few minutes each. Ready to continue, or would you like to skip any?"

List the skills by name. If any two entries share the same name, display as `name (attribution)` to distinguish them. Internally track each selection by its path from the TSV. Proceed only with confirmed paths. If the user deselects all skills, skip Step 5 and go directly to Step 6.

## Step 5: Audit each confirmed skill

For each confirmed skill:

1. Use the `path` column from the TSV row directly. If the file does not exist at that path, note "Could not find SKILL.md for `<skill-name>`; skipping." and move to the next skill.
2. Invoke `audit-skill` and provide the path in the opening message; this satisfies `audit-skill`'s Step 1 condition so it proceeds without prompting. If `audit-skill` is unavailable, note "audit-skill not found; skipping `<skill-name>`." and move to the next skill.
3. Run `audit-skill` Steps 1–7 in full. The user will be prompted for improvement choices within each audit.
4. Present the result before moving to the next skill.

After all confirmed skills are processed:
- If at least one skill was successfully audited: update the state object with the `next_audit_path` computed in Step 3 and the current date (run `date +%Y-%m-%d` via Bash), then write the full state file (preserving `batch_size`).
- If every confirmed skill was skipped due to errors: note "No audits completed; rotation not advanced." Do not write the state file.

## Step 6: Summary

1. **Overlaps:** If Step 2 found overlaps, print "See overlap analysis above." If none, print "No overlapping skills detected; no action needed."
2. **Audit results:** one row per audited skill: skill name, initial score, final score.
3. **Progress:** "Next run will pick up at `<skill_name>` (skill X of Y)." where `skill_name` = the `skill_name` field from the TSV row whose path matches `next_audit_path` (fall back to the parent directory name of `next_audit_path` if not found), X = 1-based index of `next_audit_path` in the sorted list, and Y = `total_skills`.
4. **Wrap (if applicable):** If the wrap flag was set in Step 3: "You've now reviewed every skill at least once. Starting a new full cycle."

## Self-reflection

If no skills were audited (all deselected or all skipped due to errors), note "Nothing audited this session; self-reflection skipped." and stop.

Otherwise, spawn a Haiku sub-agent. Pass it the Step 6 summary, the final state file contents, and the list of confirmed vs. skipped skills. Score each criterion 0–10. If average < 9.5, revise and re-score (max 3 iterations; stop if score stops improving). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md, show it to the user, and apply on approval.

1. **Overlap quality**: both same-name and description overlap types were checked; flagged pairs are genuinely similar; no obvious overlaps were missed
2. **Round-robin integrity**: `next_audit_path` advances by `batch_size`, resolved correctly when the prior path was deleted, state file written correctly
3. **Delegation fidelity**: each confirmed skill went through the full `audit-skill` 7-step flow with its path passed in the opening message
4. **User control**: no skill was audited without explicit user confirmation in Step 4
5. **Token efficiency**: Step 2 runs inline (no sub-agent); no unnecessary back-and-forth; batch size kept small relative to session budget
6. **Summary usefulness**: Step 6 gives the user a clear next action (which overlaps to address, which skills most need follow-up)

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Invoke list-skills in raw mode rather than embedding its script | Single source of truth for the data-collection script; raw mode is the DRY interface for skills that need structured data |
| Overlap detection runs every session | The skill library can change between runs; re-scanning is cheap relative to missing a new duplicate |
| No sub-agent for Step 2 (overlap scan) | ~76 TSV rows and lightweight semantic judgment; dispatching a sub-agent adds latency with no quality gain |
| Semantic judgment for description overlap, not string similarity | Skill descriptions are short and human-authored; Claude's semantic read is more reliable than word-overlap heuristics at this scale |
| `next_audit_path` advances by `batch_size`, not by confirmed count | Keeps cycle progress predictable; skipped skills return in the next rotation. Advancing by confirmed count would re-present already-audited skills when the cursor wraps |
| State stores only `next_audit_path`, not `skills_order` + cursor | `skills_order` is redundant (list-skills always returns the current list); storing the full list creates a synchronization problem. A single path is the minimal stable anchor: unique across scopes, unambiguous after reconciliation |
| Wrap message deferred to Step 6 | Firing it in Step 3 (before confirmation) would tell the user "cycle complete" before they've reviewed anything this session |
| `audit-skill` invoked as a sequential interactive session | `audit-skill` calls `AskUserQuestion` for improvement approvals; silently batching would violate the human-approval principle |
| Default batch size = 3 | Enough progress per session; small enough not to exhaust token budget on auditing alone |
| State file at `.claude/audit-skills-state.json` | Project-local; `.claude/` is the established container for project-level Claude metadata |
| Wrap flag fires even when `start_index = 0` | When `batch_size >= total_skills`, every session covers all skills; `start_index` is always 0 but the cycle genuinely completes each run. Guarding with `start_index > 0` would permanently silence the message for small libraries. |
| 6 self-reflection criteria (exceeds project norm of 2–5) | All 6 are genuinely distinct and collectively exhaustive for this multi-step orchestration skill; merging any two would lose precision |
