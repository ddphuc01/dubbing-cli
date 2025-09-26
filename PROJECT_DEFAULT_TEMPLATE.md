# Project Default Configuration Template

## Overview
This template provides default configurations that can be applied to new projects automatically.

## MCP Server Configuration
Default MCP servers for new projects:
```json
{
 "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
      },
      "alwaysAllow": [
        "resolve-library-id",
        "get-library-docs"
      ]
    },
    "python-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
      },
      "alwaysAllow": [
        "resolve-library-id",
        "get-library-docs"
      ]
    },
    "openai-api": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
      },
      "alwaysAllow": [
        "resolve-library-id",
        "get-library-docs"
      ]
    }
 }
}
```

## Mode Switching Configuration
Default mode switching rules for new projects:
```json
{
  "modeAutoSwitch": {
    "enabled": true,
    "rules": [
      {
        "keywords": ["plan", "design", "architecture", "structure", "overview", "strategy", "planning", "designing"],
        "mode": "architect",
        "description": "Switch to architect mode for planning and system design"
      },
      {
        "keywords": ["code", "implement", "function", "class", "module", "script", "development", "create", "write code", "programming"],
        "mode": "code",
        "description": "Switch to code mode for writing code and implementing features"
      },
      {
        "keywords": ["test", "testing", "unit test", "integration test", "pytest", "unittest", "verify", "validation"],
        "mode": "test-engineer",
        "description": "Switch to test mode for writing tests and quality assurance"
      },
      {
        "keywords": ["debug", "fix", "bug", "error", "issue", "troubleshoot", "problem", "error handling"],
        "mode": "debug",
        "description": "Switch to debug mode for fixing bugs and troubleshooting"
      }
    ]
  },
  "defaultMode": "code",
  "contextAwareSwitching": true
}
```

## Project Rules Template
```markdown
# Project Rules

## Project Management
- Break down work into smaller tasks and create checklists
- Check available tools before implementing new functionality
- Use automatic mode switching to optimize workflow

## File Operations
- Always create backup before changing important files
- Log important actions to logs/ directory
- Follow UTF-8 standard, CRLF for text files

## Code Quality
- Write clear, readable, and maintainable code
- Use appropriate mode (architect, code, test, debug) based on task
- Follow project-specific coding standards
```

## Setup Instructions
1. Copy MCP configuration to `.kilocode/mcp.json`
2. Copy mode switching config to `MODE_CONFIG.json`
3. Create `PROJECT_RULES.md` with project-specific rules
4. Create `PROJECT_TODO.md` for task tracking
5. Create `global.md` for project overview

## Automation Script
Use `scripts/mode_switcher.py` to automatically detect and switch modes based on user input.