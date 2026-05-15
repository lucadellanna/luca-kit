---
name: setup-context-search design decisions
version: 0.1.0
---

# Design Decisions

## Why qmd over alternatives

| Alternative | Why not |
|---|---|
| Manifest index (MANIFEST.md) | Works for < 200 files but breaks at scale; no semantic search; context window cost grows linearly with file count |
| Custom SQLite FTS script | Lighter than qmd but requires maintenance; no semantic search; reinvents what qmd already does well |
| Cloud search (Algolia, Typesense) | Adds network dependency, cost, and data-leaves-machine concern for non-technical users |
| Grep/Glob (status quo) | Requires knowing what to search for; no fuzzy/semantic matching; noisy at 50+ files |

qmd was chosen because: local-only (no data leaves the machine), MCP-native (Claude gets search tools natively), handles both keyword and semantic queries, and maintained by a credible author (Tobi Lutke).

## Why technical-only audience

luca-reflection-kit targets all Claude Code users, but this skill is a power-user path because:

1. qmd requires Node.js 22+, npm, and Homebrew (macOS) as prerequisites
2. First-run downloads ~2.2 GB of local models
3. Troubleshooting installation failures requires CLI comfort
4. The benefit (semantic search over context files) only materializes at file counts where technical setup is justified

Non-technical users continue using Claude's native Glob/Grep; this is an opt-in upgrade for users willing to install the prerequisites.

## Why MCP integration (not a wrapper skill)

Alternative: a `/search-context` skill that shells out to `qmd search` and parses output.

MCP is better because:
- Claude discovers qmd's tools automatically; no skill invocation needed for lookups
- qmd's MCP server handles structured output (JSON) natively
- No intermediate parsing layer to maintain
- Tool availability is visible in Claude's tool list, making it self-documenting

## Why global MCP config (~/.claude/settings.json)

Context files are typically global (customers, offerings span projects). A project-level config would only expose search within that project's Claude sessions. Global config (under `mcpServers` in `~/.claude/settings.json`) ensures the tools are always available.

## Why no self-reflection section

This skill produces no durable artifact that needs quality scoring. It runs imperative setup commands with binary success/failure. The marker file at the end records completion. If any step fails, the skill stops and tells the user what happened.

## Why there is no standard/hybrid mode split

Early versions offered "Keyword + Semantic only" (no Alibaba model) vs "Full hybrid" as a mode choice. This was removed because:

1. qmd's MCP `query` tool defaults `rerank: true` and there is no confirmed server-side flag to disable it
2. The reranker and query expansion models download lazily on first MCP query, regardless of CLI flags
3. Offering a "no Alibaba model" option that can't actually be enforced breaks user consent

Instead, Step 1 now transparently discloses that qmd may download all models (including Alibaba's Qwen3 reranker) on first search, and gives the user a clear proceed/cancel choice. Honesty about what we can and can't control is better than a false sense of control.

The third-party notice also clarifies that qmd is not part of luca-ops-kit, and that the user assumes responsibility for the decision to install it.

## Omitted: auto-reindexing hook

Considered adding a Claude Code hook that runs `qmd embed` after file writes. Rejected because:
- Embedding is slow enough (~1-2s per file) to be noticeable as a hook
- Users may edit context files outside Claude
- `qmd embed --watch` in a background terminal is simpler and already handles this

## Omitted: structured frontmatter enforcement

qmd indexes raw markdown content. Frontmatter improves search quality but is not required. The skill recommends it in the "Tips" section rather than enforcing it, to keep setup lightweight. A future `/add-context` skill could enforce schema.

## Lessons from live testing (2026-05-10)

Issues discovered during first real installation run:

| Issue | Root cause | Fix applied |
|---|---|---|
| `qmd embed` found 0 documents | `qmd update` must run between `collection add` and `embed` to scan the filesystem | Added explicit `qmd update` step |
| pnpm installed but binary crashed | pnpm v10+ blocks native build scripts (`better-sqlite3`, `node-llama-cpp`) interactively | Added pnpm warning; recommend npm as default |
| PATH resolved to broken pnpm binary over working npm binary | pnpm's global bin dir was earlier in PATH | Skill now uses full path from `which qmd` after verifying the binary works |
| `pnpm approve-builds -g` can't be automated | It presents an interactive multi-select in the terminal | Skill warns upfront; offers to switch to npm/bun instead |
| `pnpm remove -g` failed with virtual store error | pnpm internal state conflict | Another reason to recommend npm for global native packages |
| `vsearch` triggered a 1.28 GB model download after setup "completed" | qmd downloads reranker and query expansion models lazily on first use, not during `embed` | Added warning after embed that hybrid models download on first search |
| `which qmd` resolved to broken pnpm binary over working npm binary | Multiple package managers put binaries in different PATH locations | Skill now tries all known paths and uses the first one that passes functional verification |
| `qmd context add` shown in status tips | Adding collection descriptions improves search quality | Added to post-setup tips |

## Simulation testing required before shipping

Before merging a setup skill, run the full flow manually in a live session (not just code review). Code review caught 2 of 6 issues in this skill; live simulation caught the other 4:

| Issue | Found by code review? | Found by live test? |
|---|---|---|
| Wrong package name (`qmd` vs `@tobilu/qmd`) | Yes | - |
| Wrong `collection add` syntax | Yes | - |
| Missing `qmd update` step (0 files indexed) | No | Yes |
| pnpm build scripts blocked (runtime crash) | No | Yes |
| PATH resolving to broken binary | No | Yes |
| Lazy model downloads after "setup complete" | No | Yes |

This is referenced in root CLAUDE.md's "Setup command requirements" as "live-tested before shipping."

## Setup command requirements (applies to all setup skills)

Referenced from root `CLAUDE.md > Setup command requirements`. Key principles:

1. Live-tested before shipping
2. AskUserQuestion for every decision point
3. Cross-platform (macOS + Windows + Linux)
4. Accessible language with inline explanations of technical concepts
5. Package manager edge cases handled explicitly (pnpm build scripts, PATH conflicts)
6. Third-party attribution and liability disclaimer
7. Verify each critical step before proceeding
8. Atomic and resumable (idempotent re-runs)
