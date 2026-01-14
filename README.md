# Claude Code Plugins

A collection of Claude Code plugins for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add jvelez79/claude-code-plugins
```

Then install individual plugins:

```bash
/plugin install ui-improve-loop
```

## Available Plugins

### ui-improve-loop

**Iterative UI improvement loop using AI evaluation and Chrome automation.**

Automatically evaluates web application UI quality, generates improvement recommendations, implements CSS/component changes, and re-evaluates until reaching a target quality score.

**Commands:**
- `/ui-improve-loop:ui-improve-loop` - Start iterative improvement loop
- `/ui-improve-loop:ui-review` - Single UI review without loop
- `/ui-improve-loop:cancel-ui-loop` - Cancel active loop
- `/ui-improve-loop:help` - Show help

**Requirements:**
- Chrome browser with Claude in Chrome extension
- MCP server `claude-in-chrome` configured

[View plugin documentation](./plugins/ui-improve-loop/README.md)

### dev-workflow

**Feature development workflow with specialized agents.**

Orchestrates a complete feature development pipeline from idea to implementation, using specialized agents for each phase: requirements gathering, technical specification, task planning, implementation, E2E testing, and code review.

**Commands:**
- `/dev-workflow:feature` - Start feature development workflow

**Agents:**
- `idea-refiner` - Clarifies requirements through dialogue
- `spec-writer` - Creates technical specifications
- `task-planner` - Breaks down into atomic tasks
- `implementer` - Writes code and tests
- `e2e-tester` - Tests in live browser
- `reviewer` - Code review and approval

**Options:**
- `--from <agent>` - Resume from specific agent
- `--auto` - No confirmations between agents
- `--skip-e2e` - Skip browser testing
- `--skip-review` - Skip code review
- `--linear` - Create Linear tasks

[View plugin documentation](./plugins/dev-workflow/README.md)

## Adding New Plugins

To add a new plugin to this marketplace:

1. Create a new directory under `plugins/`:
   ```
   plugins/your-plugin-name/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── commands/
   ├── agents/
   └── README.md
   ```

2. Add the plugin entry to `.claude-plugin/marketplace.json`

3. Commit and push changes

## License

MIT
