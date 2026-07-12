---
name: dual-model-harness
description: >-
  Three-stage coding harness: DeepSeek designs + plans +
  implements multi-file work.  DeepSeek Pro handles delegation for parallel
  sub-tasks. Test and verify with DeepSeek. Use for any multi-step coding task.
---

# Dual-Model Development Harness

Design → Plan → Implement → Test → Verify

## Core Principles

### Evidence Before Assertion (from SOUL.md)
I verify before I claim. Every "it works," "it's done," "tests pass" is backed
by actual tool output. Don't paraphrase success — show the command that proves
it. The gap between "I think it works" and "I verified it works" is where
every bug lives.

### Self-Audit
When switching models, scaling up, or hitting repeated friction, audit own
instruction files (skills, memory, SOUL.md) for:
1. Contradictions — rules that pull in opposite directions
2. Legacy constraints — guardrails written for a weaker model
3. Bad examples — files that violate the patterns they prescribe
4. Dead weight — things that could be deleted

### No Placeholders
Never write TBD, TODO, "implement later," or "fill in details." Every code
block is complete. Every plan step has actual content. If uncertain, stop
and say so — guessing creates bugs.

## Core Principle — DeepSeek handles everything in-session

**DeepSeek handles everything in-session.** The main agent (DeepSeek V4 Flash
as default, Pro as fallback) does design, implementation, testing, and verification
directly — no delegation pipeline for sequential multi-file work. GLM 5.2 and
DeepSeek Pro are available as delegation targets for genuinely isolated sub-tasks
that benefit from parallel execution.

The "dual model" aspect is config-level: you can route delegation sub-tasks to
a different model via config, but the default workflow is single-model direct
implementation.

## How It Works

```
You request a coding task
      ↓
[DeepSeek — main agent] — DESIGN
  ├─ Clarify requirements
  ├─ Read existing patterns (batch-read 4-6 files)
  ├─ Design architecture
  └─ Get user approval
      ↓
[DeepSeek — main agent] — IMPLEMENT
  ├─ Create all new files in one batch
  └─ Patch existing files one at a time
      ↓
[DeepSeek — main agent] — VERIFY
  ├─ npx tsc --noEmit --pretty (zero errors = done)
  └─ Report summary to user
```

## Model Roles

| Stage | Model | Why |
|-------|-------|-----|
| Design | DeepSeek (main agent) | Big picture, architecture decisions |
| Planning | DeepSeek (main agent) | Breaking into independent sub-tasks needs context |
| Implementation | DeepSeek Pro (delegation) | Fast, no reasoning overhead, solid code quality |
| Large multi-file work | DeepSeek (self, in-session) | Avoiding delegation overhead for 5+ file changes |
| Review | DeepSeek (main agent) | Sees the full picture |
| Testing | DeepSeek (self) | Integration tests need codebase context |

## Delegation Model Config

```yaml
delegation:
  model: deepseek-v4-pro
  provider: deepseek
  child_timeout_seconds: 1200
```

DeepSeek Pro is the primary delegation model — fast API response (~0.5-1s),
no reasoning overhead, and capable of multi-file tasks in a single delegation.
Use it when a sub-task is truly independent (e.g., "write this Stripe webhook
handler in isolation while I work on the frontend").

GLM 5.2 via Z.AI is available as an alternative but has higher per-turn latency
(~2s vs ~0.5s). Use it only when DeepSeek is degraded or you specifically want
GLM's output characteristics.

## When to Delegate vs Do It Yourself

**Default to Do It Yourself.** The practical lesson from multiple sessions:
a focused coding task that DeepSeek can do in ~2 minutes takes a delegation
subagent 5-15 minutes (context transfer + tool call overhead + model latency).
Sequential delegation (dispatch → wait → review → next) is strictly worse
than direct implementation for anything involving 2+ files.

### Delegate (rare — genuinely independent sub-tasks only)
- Standalone utility lib with zero coupling to existing code
- "Look up X on the web and summarize" — parallel with your main work
- Truly fire-and-forget: one-shot research that doesn't need to integrate

### Do It Yourself (default)
- Anything that touches existing code (4+ files)
- Multi-file features where the design decisions cascade
- Debugging — full session context is essential
- Even single-file work: it's faster to write it than to spec it for a delegate

**Rule of thumb:** if explaining the context takes longer than writing the code,
do it yourself. Delegation's value is parallelism, not serial handoff.

## Task Granularity Rules

Each GLM implementation task MUST be:
- **1-3 files max** — creating or modifying
- **Self-contained** — doesn't depend on other GLM tasks in-flight
- **Clear definition of done** — "write X function that does Y, test passes"
- **Context-complete** — include relevant code snippets, not just file paths

**DO NOT** send GLM:
- Codebase-wide refactors (too many files)
- Research/exploration questions (too open-ended)
- Tasks needing 10+ reads of different files

## Pitfalls

### patch tool duplicating imports

When using `patch` in `replace` mode on a file that another session or tool
also modified, the patch may apply correctly but **duplicate the import line**.
This happens when the old_string appears more than once after concurrent edits.

**Fix**: After any patch that adds an import, re-read the file head. If a
duplicate import exists, patch again to remove it. Run `npx tsc --noEmit` to
catch duplicate identifier errors.

### GLM 5.2 Thinking Default — FIXED

Patched Z.AI provider to default thinking OFF. See `references/glm-provider-quirks.md`.

## Prompt Template for GLM Implementation Tasks

```
You are implementing a focused coding task.

## Task
{one-line summary}

## Files
- {path} — {what to do in this file}

## Context
{relevant code snippets or interfaces}

## Requirements
1. {specific requirement}
2. {specific requirement}

## Definition of Done
- {file} created/modified with {expected change}
- Tests pass: `{test command}`
- No unrelated changes
```

## Workflow Steps

### Step 1: Requirements & Design
- Clarify what the user wants
- Design the approach
- Get user approval before coding

### Step 2: Write the Plan
- Break into tasks (each 1-3 files, GLM-friendly)
- Save to `docs/plans/YYYY-MM-DD-<name>.md`
- Show the plan to the user

### Step 3: Implement via GLM Delegation
For each task in the plan:
```
delegate_task(
  goal="Implement X: ...",
  context="Files, code snippets, interfaces, test expectations"
)
```
- Dispatch ONE task at a time (sequential, not parallel)
- Review GLM's result before next task
- If GLM reports issues, adjust the task and retry

### Step 4: Test & Verify
- Run all tests
- Check edge cases
- Report summary to user

### Step 5: Commit
- Commit with descriptive message
- Push if appropriate

## GLM 5.2 Direct Implementation Workflow

When GLM is the main agent and the user gives explicit file specs:

### Step 1: Batch-Read Existing Patterns
Read 4-6 files in parallel to understand conventions:
- The nearest server action (e.g., `lib/actions/transactions.ts`)
- The page where the feature will live (e.g., `app/(app)/transactions/page.tsx`)
- A similar client component (e.g., `components/new-transaction-form.tsx`)
- UI primitives (e.g., `components/ui/button.tsx`, `components/ui/dialog.tsx`)
- Supporting libs (e.g., `lib/supabase/server.ts`, `lib/books.ts`)

### Step 2: Create All New Files in One Batch
Since new files are independent, create them all in a single tool-call block.
This avoids serial round-trips and is the most efficient path.

### Step 3: Patch Existing Files Sequentially
One at a time, re-reading if the patch tool reports a sibling-subagent warning.
After patching imports, run `npx tsc --noEmit` to verify no duplicate identifiers.

### Step 4: Verify
```bash
npx tsc --noEmit --pretty
```
Zero errors = done. This is the authoritative check — not lint, not build.
