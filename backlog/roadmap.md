# Current Backlog

- [ ] **Remote Update Checks**: Check for remote skill updates (via git hash/date) once a day and show in `jup list` table.
- [ ] **Registry Integration**: Deeper integration with `skills.sh` for better discovery and versioning.

- warn on skills with the same name duri8ng installation and also when running `jup list` to detect potential conflicts.
- fix jup find doesnt show the correct owner/repo. for example:
    ```bash
    jup find suggest
                                                        Search Results for 'suggest'                                                       
    ┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
    ┃ #    ┃ Skill / Name                                ┃ Source / Repo                                                          ┃ Installs ┃
    ┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
    │ 1    │ suggest-awesome-github-copilot-skills       │ awesome-copilot/suggest-awesome-github-copilot-skills                  │    8,412 │
    │ 2    │ suggest-awesome-github-copilot-agents       │ awesome-copilot/suggest-awesome-github-copilot-agents                  │    8,341 │
    ...
    ```
    but awesome-copilot/suggest-awesome-github-copilot-skills is not the correct owner/repo. It should be github/awesoeme-copilot and the skill is in the awesome-copilot/skills/suggest-awesome-github-copilot-agents directory.

## Future Ideas 💡

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
- [x] **Smart URL Parsing**: Support full GitHub URLs (e.g., `https://github.com/owner/repo/tree/main/skills/skill-name`).
- [x] **Exact Path Installation**: Support passing an exact path `owner/repo/skills/my-skill` to avoid full tree traversal.
- [x] **Target Selection Flags**: Add `--agent`, `--scope`, and `--dir` flags for fine-grained installation control.
- [x] **Skill Versioning**: Support `@version` resolution (tags, commit SHA, then HEAD) during installation.
- [x] **Metadata Injection**: Inject source tracking metadata (repo URL, version) into `SKILL.md` frontmatter upon installation.
- [x] **Agent Aliases**: Add global aliases (`jup ls`, `jup install`, `jup rm`) and `agent`/`agents` for `harness`.
- [x] **Updated Agents Registry**: Add defaults for Copilot, Cursor, Codex, and Antigravity.
- [x] **Scope Renaming**: Transition from "Global" scope terminology to "User" scope.
- [x] **Beta/Prerelease Workflow**: Configure beta/prerelease workflows with `python-semantic-release`. (Branch configured)