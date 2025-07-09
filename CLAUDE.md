# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a Claude Code playground repository for exploring and understanding Claude Code's advanced capabilities, workflow features, and best practices. The repository contains documentation and examples for experimenting with Claude Code's functionality.

## Repository Structure

- `claude_code_docs/` - Documentation and tutorials about Claude Code features
  - `claude_code_plan_mode.txt` - Detailed guide on using Claude Code's plan mode
  - `github_claude_code.txt` - Workflow guide for GitHub integration with Claude Code
  - `debuggin_git_actions.txt` - Debugging information for GitHub Actions
  - `pro-tips-for-claude-code-by-gred.txt` - Advanced tips and best practices
  - `voice_to_claude_tutorial.txt` - Voice interaction tutorial
  - `my_claude-AUTH-token.txt` - Authentication token information
- `readme.md` - Basic project description
- `sushi.txt` - Example file content

## Development Commands

This repository does not contain a traditional software project with build/test commands. It's primarily a documentation and experimentation repository.

## Claude Code Features Documented

### Plan Mode
- Use `shift+tab+tab` to enter plan mode
- Plan mode allows research and analysis before code execution
- Restricted from making file edits, running commands, or commits in plan mode
- Use `exit_plan_mode` tool to transition from planning to execution

### GitHub Integration
- Use GitHub CLI (`gh`) for repository interactions
- Workflow: Plan → Create → Test → Deploy
- Custom slash commands for processing GitHub issues
- Continuous integration with GitHub Actions
- Pull request reviews and automated testing

### Workflow Best Practices
- Break down large issues into atomic tasks
- Use scratchpads for planning and context
- Implement proper testing before deployment
- Use `/clear` to wipe context between issues
- Consider work trees for parallel development

## Key Principles

1. **Great planning is great prompting** - Thorough planning leads to better results
2. **Atomic issues** - Break down complex tasks into small, manageable pieces
3. **Context management** - Use `/clear` between different tasks to maintain focus
4. **Testing first** - Set up comprehensive testing before feature development
5. **Iterative development** - Work in small cycles of plan-create-test-deploy