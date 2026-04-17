set shell := ["bash", "-c"]

# Setup development environment
setup:
    uv sync
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg

# Run all qa checks
qa: lint typecheck test

# Format code
format:
    uv run ruff format .

# Lint code
lint:
    uv run ruff check .

# Run type checker
typecheck:
    uv run ty check

# Run tests
test:
    uv run pytest

# Serve documentation
docs-serve:
    uv run mkdocs serve

# Build documentation
docs-build:
    uv run mkdocs build