# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Claude Code Plugin Marketplace** containing multiple plugins that extend Claude Code functionality. The repository serves as both a plugin collection and a template for creating new plugins.

## Architecture

### Marketplace Structure

```
.claude-plugin/
└── marketplace.json    # Registry of all plugins in this marketplace

plugins/
├── ui-improve-loop/    # UI quality automation
├── dev-workflow/       # Feature development pipeline
├── voice-notifications/# Audio feedback via TTS
└── business-advisor/   # Business consulting tools
```

### Plugin Anatomy

Each plugin follows this structure:
```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json     # Plugin metadata (name, version, author)
├── agents/             # Subagent definitions (markdown with YAML frontmatter)
├── commands/           # User-invokable commands
├── hooks/              # Event interceptors (hooks.json + bash scripts)
├── scripts/            # Supporting scripts (Python, Bash)
├── CLAUDE.md           # Plugin-specific guidance
└── README.md           # User documentation
```

### Key Patterns

**Agent Files** (`agents/*.md`):
```yaml
---
name: agent-name
description: "What this agent does"
tools:
  - Tool1
  - Tool2
model: inherit
---
# Instructions for the agent
```

**Command Files** (`commands/*.md`):
```yaml
---
description: "Command description"
argument-hint: "<args> [--flags]"
allowed-tools:
  - Read
  - Write
  - Task
---
# Command instructions with $ARGUMENTS placeholder
```

**Hooks** (`hooks/hooks.json`):
```json
{
  "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/script.sh"}]}]
}
```

### State Persistence

Plugins store state in `.claude/` directory of the target project:
- `ui-improve-loop`: `.claude/ui-loop.local.md`
- `dev-workflow`: `.claude/features/<slug>/`
- `business-advisor`: `.claude/biz/`

## Plugins

### ui-improve-loop
Iterative UI improvement using Chrome automation. Loop: Navigate → Screenshot → Review (score 1-10) → Implement fixes → Repeat until threshold reached. Uses stop hook to continue loop across sessions.

### dev-workflow
Feature development pipeline: Idea Refiner → Spec Writer → Task Planner → Implementer → E2E Tester → Reviewer. Each agent has isolated context and specific tools.

### voice-notifications
Audio feedback using Chatterbox TTS. Intercepts Stop and Notification events to speak task completion status in Spanish.

### business-advisor
Business consulting with 7 specialized agents: idea validation, feature prioritization (RICE/ICE), launch strategy, market research, financial analysis, pricing strategy, user personas. All outputs in Spanish.

## Adding a New Plugin

1. Create directory: `plugins/<name>/`
2. Create `.claude-plugin/plugin.json` with metadata
3. Add agents in `agents/` and commands in `commands/`
4. Create `CLAUDE.md` documenting the plugin architecture
5. Add entry to `.claude-plugin/marketplace.json`

## Plugin Installation

```bash
# Add marketplace
/plugin marketplace add jvelez79/claude-code-plugins

# Install specific plugin
/plugin install <plugin-name>
```

## Chrome Integration

Several plugins require Chrome with Claude in Chrome extension:
- Install: https://chromewebstore.google.com/detail/claude-in-chrome
- Start Claude with: `claude --chrome`
