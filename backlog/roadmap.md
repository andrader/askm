# jup Roadmap & Backlog 🚀

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories.

## Current Backlog

- [ ] **Remote Update Checks**: Check for remote skill updates (via git hash/date) once a day and show in `jup list` table.
- [ ] **Registry Integration**: Deeper integration with `skills.sh` for better discovery and versioning.
- [x] **Beta/Prerelease Workflow**: Configure beta/prerelease workflows with `python-semantic-release`. (Branch configured)

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
- [x] Extract Python package template and moved to `~/projects/python-pkg-template`.
- [x] Add `jup-architect` and `jup-roadmap` skills.
