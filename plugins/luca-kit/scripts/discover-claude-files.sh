#!/usr/bin/env bash
# Discover the files that Claude Code loads automatically (CLAUDE.md, memory, path rules).
# Usage: discover-claude-files.sh [all]
#   (default: project scope only; pass "all" to include global files)

scope="${1:-project}"

PROJECT_CLAUDE="$(pwd)/CLAUDE.md"
PROJECT_MEM_DIR="$(pwd)/.claude/memory"
PROJECT_RULES_DIR="$(pwd)/.claude/rules"
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"
GLOBAL_MEM_DIR="$HOME/.claude/memory"
GLOBAL_RULES_DIR="$HOME/.claude/rules"

test -f "$PROJECT_CLAUDE" \
  && echo "project CLAUDE.md: $PROJECT_CLAUDE ($(wc -l < "$PROJECT_CLAUDE") lines, $(wc -c < "$PROJECT_CLAUDE") chars)" \
  || echo "project CLAUDE.md: missing"
find "$PROJECT_MEM_DIR"   -maxdepth 1 -name '*.md' 2>/dev/null \
  | while IFS= read -r f; do echo "project memory: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done
find "$PROJECT_RULES_DIR" -maxdepth 1 -name '*.md' 2>/dev/null \
  | while IFS= read -r f; do echo "project rule: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done

if [ "$scope" = "all" ]; then
  test -f "$GLOBAL_CLAUDE" \
    && echo "global CLAUDE.md: $GLOBAL_CLAUDE ($(wc -l < "$GLOBAL_CLAUDE") lines, $(wc -c < "$GLOBAL_CLAUDE") chars)" \
    || echo "global CLAUDE.md: missing"
  find "$GLOBAL_MEM_DIR"   -maxdepth 1 -name '*.md' 2>/dev/null \
    | while IFS= read -r f; do echo "global memory: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done
  find "$GLOBAL_RULES_DIR" -maxdepth 1 -name '*.md' 2>/dev/null \
    | while IFS= read -r f; do echo "global rule: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done
fi
