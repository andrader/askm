# AGENTS.md - Project Context & Guidelines ✨

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories (e.g., Gemini, Copilot, Claude, Codex).
 It allows users to install skills from GitHub repositories or local directories, keeping them organized via a lockfile and syncing them to target locations using symlinks or file copies.

ALWAYS use subagents for independent steps.
ALWAYS follow the development workflow outlined below to ensure consistency, maintainability, and quality across the codebase. This workflow is designed to encourage thoughtful implementation, thorough testing, and clear documentation.

## Phase 0: Project Mandates & Core Workflows
To maintain high standards for the `jup` codebase and its evolution, the following mandates must be strictly followed:

- **Small, Clean Commits**: Each commit should address exactly one concern. Git history quality is a priority.
- **Verification Before Action**: Run `just qa` (linting, type checking, and tests) before each commit to ensure no regressions.
- **Confirm Before Pushing**: Always seek user confirmation before pushing any changes to remote branches.
- **Precise Git Staging**: Never use `git add .` or `git add -A`. Manually add specific files or hunks for each commit.
- **No Force Pushes**: Force pushing is prohibited unless explicitly requested by the user.
- **Conventional Commits**: All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification (e.g., `feat:`, `fix:`, `chore:`). Use `cz commit` when possible.
- **Patch Over Minor**: Prefer patch version updates (`0.x.y+1`) over minor version updates (`0.x+1.0`) whenever the change allows it.
- **Adversarial Testing**: For every significant feature or fix, launch 3 parallel adversarial subagents to find edge cases, implementation flaws, and bugs.
- **Maintain Documentation**: Keep this `AGENTS.md`, the implementation plan, and the `backlog/roadmap.md` updated throughout the development lifecycle.

## dev workflow (better rewrite this)
- ask clarifying questions
- propose 3 approaches with pros and cons
- ask the user choice
- create implementation plan
- break plan in small steps
- new branch, commit often with clear messages
- implement changes. use subagents whenever possible.
- adversarial testing: launch 3 parallel adversarial subagents to find implementation problems
- reflect: are there any edge cases?
- does it require new tests? add them, run them
- does it require docs updates? update docs: all jup readme+ screenshots
- update backlog/
- commit in new branch, push, make pr

jup backlog
- chores:
	- add mkdocs docs + auto doc pkg reference
	- extract a python pkg template from jup repo, cookiecutter/copier...? (maybe copier is better)
    - configure beta or prerealease workflow with python-semantic-release


## Project Overview

*   **Purpose:** Centralized management of AI agent skills/tools.
*   **Main Technologies:** Python 3.12+, `typer`, `pydantic` (v2), `rich`, and `uv`.
*   **Architecture:**
    *   `src/jup/main.py`: Main entry point and configuration sub-commands (`jup config ...`).
    *   `src/jup/commands/`: Package containing core CLI commands implementation (`add`, `remove`, `sync`, `list`, `show`, `find`).
    *   `src/jup/config.py`: Handles `~/.jup` persistence, config files, and the skills lockfile.
    *   `src/jup/models.py`: Defines Pydantic models for configuration, skill sources, and the `DEFAULT_HARNESSES` registry.
    *   **Internal Storage:** Skills are cached/stored in `~/.jup/skills/` before being synced.

## Mandates & Core Workflows

**ALWAYS** use `uv run ...` instead of `python -m ...` to run commands in the repo, as `uv` ensures the correct environment and dependencies are used.

### Build, Test, and Tooling
- **Environment Setup:** `uv sync` followed by `uv pip install -e .` and `uv run pre-commit install`. See [CONTRIBUTING.md](CONTRIBUTING.md) for full setup.
- **Task Runner:** We use `just`. Use `just qa` to run linting, type checking, and tests.
- **Testing:** Run the full suite with `just test`.
- **Formatting & Linting:** Handled by `ruff` (`just format` and `just lint`).
- **Type Checking:** Handled by `ty` (`just typecheck`).
- **Committing:** Use `uv run cz commit` for conventional commits.
- **Publishing:** Automated via GitHub Actions using `python-semantic-release`.

## Development Conventions

### Code Style
- Target Python 3.12+ and maintain alignment with the existing `src/jup` layout.
- Use `typer` for CLI commands and `pydantic` (v2) for all data models.
- Keep imports and formatting consistent; `ruff` is the primary tool for enforcement.

### Skill & Sync Logic
- **Skill Structure:** `jup` expects a directory containing a `SKILL.md` file. It supports single-skill directories or collections.
- **Sync Behavior:** `sync` only manages entries in the lockfile. It does not preserve arbitrary manual edits inside managed target directories.
- **Sync Mode:** The `sync-mode` alias in the CLI maps to `sync_mode` in the config model.
- **Harness Registry:** Supported harnesses and their default paths are defined in `src/jup/models.py`. The `get_scope_dir` function returns the exact path to a harness's skills directory (e.g., `~/.gemini/skills`). Tests frequently patch this registry.
- **Path Consistency:** Ensure that `list`, `sync`, and `remove` commands use `get_scope_dir` directly for the default target, avoiding redundant `/skills` nesting.

### Documentation
- Treat [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) as the primary user-facing and contributor documentation.
- When changing CLI behavior, **must** update the relevant tests under `tests/integration` and `tests/e2e`.
