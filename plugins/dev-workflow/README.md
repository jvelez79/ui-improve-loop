# Dev Workflow Plugin

A comprehensive feature development workflow plugin for Claude Code that orchestrates specialized agents to take features from idea to implementation.

## Overview

This plugin provides a structured approach to feature development by breaking down the process into specialized phases, each handled by a dedicated AI agent:

1. **Idea Refiner** - Clarifies requirements through interactive dialogue
2. **Spec Writer** - Creates technical specifications based on the codebase
3. **Task Planner** - Breaks down specs into atomic, actionable tasks
4. **Implementer** - Writes code and unit tests
5. **E2E Tester** - Tests in live browser using Chrome automation
6. **Reviewer** - Reviews code quality and completeness

## Installation

```bash
# Add the marketplace
/plugin marketplace add jvelez79/claude-code-plugins

# Install the plugin
/plugin install dev-workflow
```

## Usage

### Start a new feature

```bash
/feature Add user authentication with OAuth support for Google and GitHub
```

### Command Options

| Option | Description |
|--------|-------------|
| `--from <agent>` | Resume from a specific agent |
| `--auto` | Execute without confirmations between agents |
| `--skip-e2e` | Skip E2E testing (when Chrome unavailable) |
| `--skip-review` | Skip the code review phase |
| `--linear` | Create tasks in Linear after planning |

### Examples

```bash
# Basic usage
/feature Create a dark mode toggle in settings

# Resume from implementation
/feature --from implementer

# Skip E2E testing (no Chrome)
/feature --skip-e2e Add logout button

# Auto mode (no confirmations)
/feature --auto Add form validation
```

## Workflow Diagram

```
User describes feature idea
            |
            v
    +---------------+
    | Idea Refiner  |  <-- Interactive Q&A
    +---------------+
            |
            v
    +---------------+
    | Spec Writer   |  <-- Analyzes codebase
    +---------------+
            |
            v
    +---------------+
    | Task Planner  |  <-- Creates atomic tasks
    +---------------+
            |
            v
    +---------------+
    | Implementer   |  <-- Writes code + tests
    +---------------+
            |
            v
    +---------------+
    | E2E Tester    |  <-- Browser testing
    +---------------+
            |
       [Pass?] --No--> Back to Implementer
            |
           Yes
            |
            v
    +---------------+
    | Reviewer      |  <-- Code review
    +---------------+
            |
            v
    Feature complete!
```

## Output Files

The workflow creates a feature directory with documentation:

```
.claude/features/<feature-slug>/
├── concept.md    # Requirements and user stories
├── spec.md       # Technical specification
├── tasks.md      # Implementation tasks
└── review.md     # Code review results
```

## Agent Details

### Idea Refiner
- Uses interactive questions to clarify requirements
- Applies gap analysis to identify missing information
- Produces structured requirements document

### Spec Writer
- Explores existing codebase patterns
- Designs component architecture
- Defines API contracts and data schemas
- Identifies edge cases and risks

### Task Planner
- Creates atomic, verifiable tasks
- Estimates task sizes (S/M/L)
- Orders tasks by dependencies
- Formats tasks for Linear integration (optional)

### Implementer
- Follows project conventions
- Writes clean, tested code
- Reports progress per task
- Runs linter and type checks

### E2E Tester
- Tests in live Chrome browser
- Verifies acceptance criteria
- Reports detailed pass/fail results
- Loops with Implementer until passing (max 3 iterations)

### Reviewer
- Checks code quality and patterns
- Verifies test coverage
- Reviews for security issues
- Gives final approval or requests changes

## Requirements

- **Claude Code** - The CLI tool
- **Chrome + Claude in Chrome extension** - For E2E testing (optional)

### Chrome Setup (for E2E Testing)

1. Install the [Claude in Chrome extension](https://chromewebstore.google.com/detail/claude-in-chrome)
2. Start Claude with Chrome: `claude --chrome`

If Chrome is not available, use `--skip-e2e` to skip browser testing.

## License

MIT
