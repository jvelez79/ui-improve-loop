# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Plugin** that implements a comprehensive feature development workflow. It orchestrates multiple specialized agents to take a feature idea from initial concept through implementation and review.

## Architecture

### Agent-based Workflow

The plugin uses a pipeline of specialized agents, each with isolated context and specific tool access:

```
/feature command
    |
Idea Refiner -> Clarify requirements (AskUserQuestion tool)
    |
Spec Writer -> Technical specification (file tools)
    |
Task Planner -> Atomic task breakdown (file tools)
    |
Implementer -> Write code and tests (file tools + Bash)
    |
E2E Tester -> Browser testing (Chrome MCP tools)
    |
    [Loop: Implementer <-> E2E Tester until passing]
    |
Reviewer -> Code review and approval (file tools + Bash)
```

### State Persistence

State is stored in `.claude/features/<feature-slug>/`:
- `mindmap.md` - Visual concept map (Mermaid)
- `validation.html` - Interactive validation page
- `concept.md` - Structured requirements from Idea Refiner
- `spec.md` - Technical specification from Spec Writer
- `tasks.md` - Task breakdown from Task Planner
- `review.md` - Code review from Reviewer

### Workflow Resumption

The workflow supports resumption from any agent using `--from <agent>`:
```bash
/feature --from implementer  # Resume from implementation phase
/feature --from e2e-tester   # Resume from E2E testing
```

## Key Files

| File | Purpose |
|------|---------|
| `commands/feature.md` | Main workflow orchestrator |
| `agents/idea-refiner.md` | Product analyst - clarifies requirements |
| `agents/spec-writer.md` | Technical architect - creates specifications |
| `agents/task-planner.md` | Tech lead - breaks down into tasks |
| `agents/implementer.md` | Developer - writes code and tests |
| `agents/e2e-tester.md` | QA engineer - tests in browser |
| `agents/reviewer.md` | Senior reviewer - code review |
| `templates/mindmap-validation.html` | Interactive validation page template |

## Plugin Commands

```bash
# Start new feature development
/feature "<idea description>"

# With options
/feature "<idea>" --auto            # No confirmations between agents
/feature "<idea>" --skip-e2e        # Skip E2E testing (no Chrome)
/feature "<idea>" --skip-review     # Skip code review
/feature "<idea>" --linear          # Create Linear tasks after planning

# Resume from specific agent
/feature --from spec-writer
/feature --from implementer
/feature --from e2e-tester
/feature --from reviewer
```

## Command Options

- `--from <agent>`: Resume from specific agent (idea-refiner, spec-writer, task-planner, implementer, e2e-tester, reviewer)
- `--auto`: Execute without confirmations between agents
- `--skip-e2e`: Skip E2E testing (useful when Chrome not available)
- `--skip-review`: Skip the Reviewer agent
- `--linear`: Create tasks in Linear after Task Planner

## Tool Access by Agent

| Agent | Tools |
|-------|-------|
| Idea Refiner | AskUserQuestion, Write, Read, Bash, Chrome MCP |
| Spec Writer | Read, Glob, Grep, Bash |
| Task Planner | Read, Glob, Grep |
| Implementer | Read, Write, Edit, Bash, Glob, Grep |
| E2E Tester | Read, Glob, Grep, Bash + Chrome MCP |
| Reviewer | Read, Glob, Grep, Bash |

## Agent Responsibilities

### Idea Refiner
- Interactive dialogue with user via AskUserQuestion
- Gap analysis on requirements using checklists
- **Visual validation with interactive mindmap:**
  1. Generates Mermaid mindmap when checklist is covered
  2. Opens validation page in Chrome (or system browser)
  3. User approves/adjusts/redoes directly from browser
  4. Agent monitors decision via Chrome tools
- Produces:
  - `mindmap.md` - Visual concept map
  - `validation.html` - Interactive validation page
  - `concept.md` - Structured requirements (after approval)

### Spec Writer
- Analyzes existing codebase patterns
- Designs technical architecture
- Produces spec.md with:
  - Components to create/modify
  - API contracts
  - Database schemas
  - Edge cases
  - Technical decisions

### Task Planner
- Dependency analysis
- Task decomposition
- Produces tasks.md with:
  - Atomic, verifiable tasks
  - Size estimates (S/M/L)
  - Execution order
  - Linear-compatible format

### Implementer
- Writes production code
- Creates unit tests
- Follows project conventions
- Reports progress per task

### E2E Tester
- Tests in live browser (Chrome)
- Verifies acceptance criteria
- Reports pass/fail with details
- Loops with Implementer on failures

### Reviewer
- Code quality assessment
- Security review
- Test coverage verification
- Final approval or change requests

## File Format Conventions

Commands and agents use Markdown with YAML frontmatter:
```yaml
---
name: "agent-name"
description: "Purpose"
tools:
  - Tool1
  - Tool2
model: sonnet
---
# Instructions here
```

## Error Handling

If any agent fails:
1. Error is reported to user
2. Partial state is preserved in feature directory
3. User can resume with: `/feature --from <failed-agent>`

## Chrome Integration

E2E Tester requires Chrome with Claude in Chrome extension:
- Install: https://chromewebstore.google.com/detail/claude-in-chrome
- Start Claude with: `claude --chrome`
- Or skip with: `--skip-e2e` flag
