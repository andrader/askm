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
```

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
