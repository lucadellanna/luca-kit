# Design decisions

| Decision | Rationale |
|----------|-----------|
| `git remote show origin` for base branch detection (not `git symbolic-ref`) | `git symbolic-ref refs/remotes/origin/HEAD` is not reliably set in all clone types (shallow, sparse). `git remote show origin` is consistent across all three skills and the subsequent `git fetch` already incurs network I/O. |
| Remote name hardcoded to `origin` (not dynamic detection) | Dynamic detection via `git remote | head -n 1` is unreliable: remotes have no defined ordering. `origin` is the standard convention and is used consistently for push and PR creation throughout all three skills. Fork-based workflows where the primary push remote differs from `origin` are out of scope. |
| Structural detection uses git tools, not token scanning | Token scanning misses content changes that don't use listed keywords (constants, config strings, CSS, SQL). `git diff --name-status | grep -v '^R100'` and `git diff -w --ignore-blank-lines` are language-agnostic and reliable. |
