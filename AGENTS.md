# Project Guidelines

## Code Style
- Target Python 3.12+ and keep changes aligned with the existing `src/jup` layout.
- Prefer small, focused edits that preserve the current Typer CLI and Pydantic model patterns.
- Keep imports and formatting consistent with the surrounding file; `ruff` is available, but there is no separate repo-specific lint config beyond `pyproject.toml`.

## Architecture
- `src/jup/main.py` wires the Typer app and config subcommands.
- `src/jup/commands.py` contains the skill install, remove, sync, and list flows and lazily registers commands from `main.py`.
- `src/jup/config.py` handles `~/.jup` persistence, config files, and the skills lockfile.
- `src/jup/models.py` defines config models, enums, and the `DEFAULT_AGENTS` registry.
- Treat [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) as the primary docs; link to them instead of duplicating their content here.

## Build and Test
- Set up the environment with `uv sync` and `uv pip install -e .`.
- Run the test suite with `pytest`.
- Build distributions with `uv build`.
- Publish with `uv publish`.
- Use `jup --help` as the basic post-install smoke check.

## Conventions
- Keep the `sync-mode` alias behavior intact: it maps to `sync_mode` in the config model and CLI commands.
- `config set agents` accepts a comma-separated list, and `none` clears the list.
- `add` only accepts `owner/repo` and only installs nested skill directories that contain `SKILL.md` under a top-level `skills/` folder.
- `sync` only manages entries in the lockfile; do not assume it preserves arbitrary manual edits inside managed target directories.
- Tests patch `DEFAULT_AGENTS` in both `jup.config` and `jup.models`, so keep those imports stable when refactoring.
- When changing CLI behavior, update the relevant tests under [tests/integration](tests/integration) and [tests/e2e](tests/e2e).
