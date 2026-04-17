# jup Roadmap & Backlog 🚀

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories.

## Current Backlog

- [ ] **Manage Unmanaged Skills**: Add a way to start managing unmanaged skills discovered by `jup list` (e.g., `jup add <path>`).
- [ ] **Shortcut Improvements**: Add more intuitive shortcuts for common commands (e.g., `jup up` for `sync --update`).
- [ ] **Move Skill Location**: Enhance `jup mv` to handle edge cases like renaming skills or moving between local and remote sources.
- [ ] **Agent Skill Iteration**: Add an agent skill to help iterate on new ideas, roadmap, and specs.
- [ ] **Expert Engineer Skill**: Add a skill for an expert engineer to analyze the codebase, identify technical debt, and suggest architectural improvements.
- [ ] **MkDocs Documentation**: Set up MkDocs with automatic package reference generation.
- [ ] **Python Package Template**: Extract a reusable Python package template from the `jup` repository (using Copier).
- [ ] **Beta/Prerelease Workflow**: Configure beta/prerelease workflows with `python-semantic-release`.
- [ ] **Interactive `sync`**: Add an interactive mode for `jup sync` to selectively sync skills.
- [ ] **Registry Integration**: Deeper integration with `skills.sh` for better discovery and versioning.

## Future Ideas 💡

- **Plugin System**: Allow users to add custom commands via plugins.
- **GUI Dashboard**: A simple local web interface to manage skills visually.
- **Cross-Platform Support**: Improved support for Windows and Linux agent directories.
- **Skill Versioning**: Support for specific versions of skills from GitHub.
- **Security Scanning**: Scan `SKILL.md` for potential malicious scripts or instructions.

## Completed ✅

- [x] Modularize `commands.py` into `src/jup/commands/` package.
- [x] Enhance `jup list` with status flags and unmanaged skills detection.
- [x] Add `jup list --json` for machine-readable output.
- [x] Add `jup SKILL.md` to teach AI agents how to use `jup`.
- [x] Improve `jup find` search logic for better discovery.
- [x] Add `jup ls` and `jup rm` shortcuts.
- [x] Add `jup mv` to move skill category.
