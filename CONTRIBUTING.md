# Contributing to jup

Thank you for your interest in contributing to `jup`!

## Development Setup

To set up a local development environment:

```bash
# Clone the repository
git clone https://github.com/andrader/jup
cd jup

# Install dependencies and create a virtual environment
uv sync

# Install the tool in editable mode
uv pip install -e .

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## Tooling

This project uses the following tools for development:
- **[Ruff](https://docs.astral.sh/ruff/)**: For extremely fast linting and formatting.
- **[ty](https://ty.astral.sh/)**: A high-performance Python type checker.
- **[just](https://just.systems/)**: A command runner to automate tasks (run `just qa` to run all checks).
- **[Commitizen](https://commitizen-tools.github.io/commitizen/)**: To ensure standard conventional commits. Use `uv run cz commit` to commit changes.
- **[Pre-commit](https://pre-commit.com/)**: To run formatting, linting, type checking, and testing before commits.
- **[Python Semantic Release](https://python-semantic-release.readthedocs.io/)**: For automated versioning and changelog generation in CI.

## Task Runner Commands

Run tasks using `just`:

```bash
just format     # Format code with Ruff
just lint       # Lint code with Ruff
just typecheck  # Run type checking with ty
just test       # Run tests with pytest
just qa         # Run lint, typecheck, and test
```

## Committing

We use conventional commits. Please use `commitizen` to construct your commit messages:

```bash
uv run cz commit
```

The `commit-msg` pre-commit hook will validate the message format.

## Publishing to PyPI

### Automated (CI/CD)

A CI/CD pipeline (e.g., GitHub Actions) is set up to run `python-semantic-release` upon a merge to the `main` branch. This automatically bumps the version, creates a GitHub release, and publishes to PyPI.

### Manual Publishing

To publish manually using `uv`:

```bash
# Build the package
uv build

# Publish to PyPI
uv publish
```