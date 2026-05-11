# bump-plugin-versions workflow: design decisions

## Version bump level for this PR (0.1.0 → 0.2.0, not 0.1.1)

**Decision:** both plugins were bumped to 0.2.0 (minor), not 0.1.1 (patch).

**Rationale:** the auto-update mechanism compares the installed version string against the
marketplace version. Both were 0.1.0, so no update ever fired -- users were stuck on a
13-commit-old snapshot. Any version change unblocks the update; 0.2.0 was chosen to signal
that this is a meaningful release, not a trivial fix. The semver policy defined in this PR
(minor for structural additions, patch for content changes) applies to future automated bumps,
not retroactively to the manual bump that introduced it.

**Gemini thread:** PRRT_kwDOSVNdGM6BEy8E / PRRT_kwDOSVNdGM6BEy8W -- rejected in PR #23.

## paths-ignore prevents re-trigger (not a missing file)

**Decision:** the bump commit is prevented from re-triggering the workflow via `paths-ignore`
on `plugins/*/.claude-plugin/plugin.json`, not via commit message inspection.

**Rationale:** commit message inspection requires reading `github.event.head_commit.message`,
which is an untrusted input and flagged by the GitHub Actions security guidance. `paths-ignore`
is a declarative trigger filter evaluated by GitHub's own runner before the job starts -- no
string parsing, no injection surface. The bump commit only ever touches plugin.json files, so
the ignore pattern is guaranteed to match it.

**Gemini thread:** PRRT_kwDOSVNdGM6BEy8B -- rejected in PR #23 (Gemini incorrectly claimed
the workflow file was absent; it is present at `.github/workflows/bump-plugin-versions.yml`).
