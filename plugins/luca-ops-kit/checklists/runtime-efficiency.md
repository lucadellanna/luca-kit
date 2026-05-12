# Runtime efficiency checklist for skills

How to use this checklist: for each item, scan the target `SKILL.md` for the **Pattern**. If found, quote the offending text and propose the **Fix**. A skill that triggers no items scores high on runtime efficiency.

Consumers: `audit-skill` (scoring `Runtime efficiency` in `REQUIREMENTS.md`), `create-skill` (Step 5 conditional review), manual review.

## Category 1: Model tier discipline

### 1. Sonnet default for deterministic work
- **Pattern**: A step performs file parsing, frontmatter checks, or simple TSV scans without naming a model tier (implicit Sonnet).
- **Fix**: Mark the step "Haiku", or move the work to a Bash/Python script invoked via Bash so no model runs at all.

### 2. Opus for non-reasoning work
- **Pattern**: A step invokes Opus for tasks that don't require deep reasoning (simple text rewrites, formatting, well-defined rule application).
- **Fix**: Downgrade to Sonnet or Haiku based on the actual reasoning demand.

### 3. Tier-switching without justification
- **Pattern**: Steps alternate between Haiku, Sonnet, and Opus without explicit reason in the step text.
- **Fix**: Justify each switch or unify on one tier; tier switches have a setup cost that may exceed the savings.

## Category 2: Sub-agent restraint

### 4. Sub-agent for trivial task
- **Pattern**: A sub-agent is spawned for work the main model could complete in 1–2 sentences.
- **Fix**: Inline the work in the main step.

### 5. Sequential sub-agents that could be one pass
- **Pattern**: Two or more sub-agents spawned sequentially with similar prompts on the same input.
- **Fix**: Merge into one sub-agent with a combined prompt.

### 6. Full SKILL.md passed when only frontmatter is needed
- **Pattern**: A sub-agent receives the entire SKILL.md when its task only needs the frontmatter, a single step, or a section.
- **Fix**: Pass only the necessary slice (frontmatter, step text, or extracted section).

### 7. Iteration loop without plateau detection
- **Pattern**: A scoring loop iterates up to its cap even when scores stop improving between iterations.
- **Fix**: Stop when the score doesn't improve from the previous iteration.

### 8. Iteration loop without hard cap
- **Pattern**: A loop has no maximum iteration count.
- **Fix**: Add a hard cap (typically 3 iterations).

### 9. Auto-iterate when first pass meets threshold
- **Pattern**: A scoring loop runs unconditionally when the initial pass would already satisfy the bar.
- **Fix**: Check the threshold after the first pass; skip subsequent iterations if met.

## Category 3: Tool selection

### 10. LLM judgment for binary file existence
- **Pattern**: The model is asked to "check whether X exists" using Read.
- **Fix**: Use Bash `test -f <path>` and let the exit code answer.

### 11. LLM judgment for simple grep match
- **Pattern**: The model Reads a whole file to find a string or pattern.
- **Fix**: Use the Grep tool with a pattern.

### 12. Model iterates filenames
- **Pattern**: The model enumerates directory contents step by step.
- **Fix**: Use the Glob tool with a pattern (e.g., `**/SKILL.md`).

### 13. Bash wrapper around dedicated tools
- **Pattern**: Bash is used to run `grep`, `cat`, `find`, or `ls` when Grep/Read/Glob would do it.
- **Fix**: Use the dedicated tool. Bash output goes to the model's context as raw text; dedicated tools return structured results.

## Category 4: Batching and parallelism

### 14. Sequential independent tool calls
- **Pattern**: Multiple independent Read or Bash calls in sequential turns.
- **Fix**: Batch them in a single response (parallel tool calls).

### 15. Multiple sequential AskUserQuestion calls
- **Pattern**: Several related questions asked one at a time.
- **Fix**: Batch into one AskUserQuestion with multiple fields, or use `multiSelect: true`.

### 16. Sequential reads of related files
- **Pattern**: Multiple Read calls in separate turns when the files could have been read in parallel.
- **Fix**: Issue parallel Read calls in a single message.

## Category 5: Context hygiene

### 17. Re-reading files already in context
- **Pattern**: A file is Read more than once within the same skill execution.
- **Fix**: Cache the relevant content after the first Read; refer to it from memory.

### 18. Full Read when only metadata is needed
- **Pattern**: Read used to check file size, line count, or existence.
- **Fix**: Use Bash `wc -l`, `test -f`, or `stat`.

### 19. Large inline scripts in SKILL.md
- **Pattern**: Python or Bash code blocks ≥30 lines embedded in the SKILL.md body.
- **Fix**: Move to `plugins/<plugin>/scripts/<name>.py` (or `.sh`) and invoke via Bash. Avoid loading the script into model context on every run.

### 20. Large embedded data in SKILL.md
- **Pattern**: JSON, TSV, or example data ≥20 lines in SKILL.md.
- **Fix**: Externalize to a data file; reference its path.

## Category 6: Pipeline structure

### 21. Plan mode for non-writing steps
- **Pattern**: `EnterPlanMode` used for steps that don't write files or take external action.
- **Fix**: Replace with a plain show-and-confirm via AskUserQuestion.

### 22. Sub-skill invocation not at the terminal step
- **Pattern**: A sub-skill is invoked mid-pipeline; subsequent steps in the parent depend on resuming the flow.
- **Fix**: Move the sub-skill to the terminal step. Sub-skills risk the `pipeline-pause-after-sub-skill` error class: the parent may not reliably resume.

### 23. Heavy machinery for trivial skills
- **Pattern**: Multi-stage scoring loops, plan modes, or sub-agent chains attached to a skill that performs a one-shot, low-stakes action.
- **Fix**: Match quality machinery to output type (see plugin CLAUDE.md). Ephemeral, user-judged output does not need iteration loops.
