# Contributing to askm

Thank you for your interest in contributing to `askm`!

## Development Setup

To set up a local development environment:

```bash
# Clone the repository
git clone https://github.com/andrader/askm
cd askm

# Install dependencies and create a virtual environment
uv sync

# Install the tool in editable mode
uv pip install -e .
```

## Specialized Agents

This project uses specialized agents to assist with development. Please refer to [AGENTS.md](AGENTS.md) for details on the different agents and how they collaborate.

## Project Structure

- `skills/`: Contains the definitions for agent skills.
- `src/askm/`: Contains the Python source code for the CLI tool.

## Guidelines

- Follow existing coding styles and conventions.
- Ensure any new skills are documented in their respective `SKILL.md` files.
- Update `AGENTS.md` if you add or modify specialized agents.
- For bug fixes, please include a reproduction script or test case if possible.

## Publishing to PyPI

### Automated (GitHub Actions)

A GitHub Action is configured to publish to PyPI whenever a new tag starting with `v` is pushed:

```bash
git tag v0.1.0
git push origin v0.1.0
```

*Note: Ensure you have set up [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) on PyPI for this repository.*

### Manual Publishing

To publish manually using `uv`:

```bash
# Build the package
uv build

# Publish to PyPI
uv publish
```
