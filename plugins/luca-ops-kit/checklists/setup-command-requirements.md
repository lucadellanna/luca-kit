# Setup command requirements

How to use this checklist: when authoring a skill that installs third-party tools or configures the user's environment, every item below must be met before shipping. The skill is incomplete until each one is verified.

Consumers: `create-skill` (Step 5 conditional review for setup-classified skills), `audit-skill`, manual pre-PR review.

## Requirements

- **Live-tested before shipping.** Run the full skill flow on a clean machine (or simulate one) before merging. The gap between "should work" and "does work" hides native module builds, missing sync steps, and interactive prompts.
- **AskUserQuestion for every decision.** Never present choices as plain text. Use AskUserQuestion (or the platform equivalent) so the user gets a structured selection UI. This includes mode selection, package manager choice, directory paths, and confirmation gates.
- **Cross-platform.** Detect macOS vs Windows vs Linux and branch instructions where they diverge (package managers, paths, native dependencies, shell syntax). Stop and tell the user if their platform is unsupported rather than failing mid-flow.
- **Accessible language.** Explain technical concepts inline when first introduced (e.g., "npm is a package manager that comes with Node.js"). Detect what's already installed and recommend the simplest path. If the user doesn't know, pick a safe default.
- **Package manager edge cases.** When installing npm packages with native modules: (a) pnpm v10+ blocks build scripts interactively and can't be automated; warn before choosing, (b) npm is the safest default for native modules, (c) always verify the binary works after install.
- **Third-party attribution.** When installing tools not created by the plugin author, state clearly: who made it, that the plugin author assumes no liability, and that the user is responsible for the decision to install.
- **Verify each critical step before proceeding.** After install: check the binary runs. After collection/config creation: check it exists. After indexing: check file count > 0. Never assume success from exit code 0.
- **Atomic and resumable.** If the skill fails mid-flow, the user must be able to re-run it without side effects (idempotent). Write markers only after full success. Report clearly what succeeded and what didn't.
