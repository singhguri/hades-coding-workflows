# Hermes Coding Workflows

A collection of Hermes Agent coding workflow skills — structured patterns for
planning, delegating, and implementing software tasks through subagents.

These skills encode patterns inspired by Fable's fan-out delegation approach,
adapted for Hermes Agent's `delegate_task` system. Originally iterated between
DeepSeek and Sol to arrive at the current structure.

## Skills

### [dual-model-harness](./dual-model-harness/SKILL.md)
Three-stage coding harness: design → implement → verify. Routes design and
verification to the main agent (DeepSeek V4 Flash) while delegating isolated
implementation tasks to a faster coding model (DeepSeek V4 Pro). Documents the
practical lesson that delegation overhead often outweighs its benefit for
serial multi-file work — use it only for genuinely parallel sub-tasks.

Includes a reference on [GLM 5.2 / Z.AI provider quirks](./dual-model-harness/references/glm-provider-quirks.md)
— specifically the thinking-mode default bug that caused 35s response times
until patched.

### [subagent-driven-development](./subagent-driven-development/SKILL.md)
Execute implementation plans by dispatching fresh `delegate_task` subagents per
task with systematic two-stage review: spec compliance first, code quality
second. Each subagent gets clean context. Reviews catch issues before they
compound across tasks.

Includes references on [context budget discipline](./subagent-driven-development/references/context-budget-discipline.md)
and [gates taxonomy](./subagent-driven-development/references/gates-taxonomy.md),
both adapted from the GSD project by Lex Christopherson.

### [writing-plans](./writing-plans/SKILL.md)
Write comprehensive implementation plans with bite-sized tasks (2-5 minutes
each), exact file paths, complete code examples, verification commands, and
expected output. Designed to pair with subagent-driven-development for
execution. DRY, YAGNI, TDD, frequent commits.

Includes a reference on the [server action result pattern](./writing-plans/references/server-action-result-pattern.md)
for Next.js — a discriminated union approach to distinguish "empty results"
from "database error."

## Usage

Clone into your Hermes skills directory or symlink individual skills:

```bash
# Clone the whole collection
git clone https://github.com/singhguri/hermes-coding-workflows ~/hermes-coding-workflows

# Symlink individual skills into Hermes
ln -s ~/hermes-coding-workflows/writing-plans ~/.hermes/skills/writing-plans
```

Or copy individual `SKILL.md` files into your Hermes skills folder.

## Related

- [FloorIsGround/skills](https://github.com/FloorIsGround/skills) — the
  fan-out-delegation and ai-coding-agent-workflows skills that inspired parts
  of this collection
- [obra/superpowers](https://github.com/obra/superpowers) — original
  superpowers skill format that subagent-driven-development and writing-plans
  are adapted from
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) —
  context budget and gates references (MIT © 2025 Lex Christopherson)

## License

MIT
