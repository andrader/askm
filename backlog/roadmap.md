# jup Roadmap & Backlog 🚀

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories.

## Current Backlog

- [x] **Manage Unmanaged Skills**: Add a way to start managing unmanaged skills discovered by `jup list` (e.g., `jup add <path>`).
- [x] **Shortcut Improvements**: Add more intuitive shortcuts for common commands (e.g., `jup up` for `sync --update`).
- [x] **Move Skill Location**: Enhance `jup mv` to handle edge cases like renaming skills or moving between local and remote sources.
- [x] **Agent Skill Iteration**: Add an agent skill to help iterate on new ideas, roadmap, and specs.
- [x] **Expert Engineer Skill**: Add a skill for an expert engineer to analyze the codebase, identify technical debt, and suggest architectural improvements.
- [x] **MkDocs Documentation**: Set up MkDocs with automatic package reference generation.
- [x] **Python Package Template**: Extract a reusable Python package template from the `jup` repository (using Copier).
- [ ] **Beta/Prerelease Workflow**: Configure beta/prerelease workflows with `python-semantic-release`. (Partially configured)
- [x] **Interactive `sync`**: Add an interactive mode for `jup sync` to selectively sync skills.
- [ ] **Registry Integration**: Deeper integration with `skills.sh` for better discovery and versioning.

## Future Ideas 💡

- **Plugin System**: Allow users to add custom commands via plugins.
- **GUI Dashboard**: A simple local web interface to manage skills visually.
- **Cross-Platform Support**: Improved support for Windows and Linux agent directories.
- **Skill Versioning**: Support for specific versions of skills from GitHub.
- **Security Scanning**: Scan `SKILL.md` for potential malicious scripts or instructions.

## Completed ✅

- [x] Manage Unmanaged Skills (detect and move/import).
- [x] Modularize `commands.py` into `src/jup/commands/` package.
- [x] Enhance `jup list` with status flags and unmanaged skills detection.
- [x] Add `jup list --json` for machine-readable output.
- [x] Add `jup SKILL.md` to teach AI agents how to use `jup`.
- [x] Improve `jup find` search logic for better discovery.
- [x] Add `jup ls` and `jup rm` shortcuts.
- [x] Add `jup mv` to move skill category.
- [x] Add `jup up` as alias for `jup sync --update`.
- [x] Add interactive mode to `jup sync`.
- [x] Add MkDocs documentation with auto-API reference.
- [x] Extract Python package template to `templates/python-pkg`.
- [x] Add `jup-architect` and `jup-roadmap` skills.
