

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project-name>"
  exit 1
fi

# stack
# git for version control
# uv for packaging and dependency management
# ruff for linting and formatting
# pyright for type checking
# pytest for testing
# pycov for test coverage
# pre-commit for git hooks
# github actions for CI/CD
# commitizen for commit message standardization and changelog generation
# python-semantic-release for automated releases based on commit messages

# The project will have the following structure:
# README.md for project documentation
# AGENTS.md for documenting the specialized agents used in the project
# CONTRIBUTING.md for contribution guidelines
# .github/workflows/publish.yml for GitHub Actions workflow to automate testing and publishing to PyPI
# src/{}/


PROJECT_SLUG=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

mkdir "$PROJECT_SLUG"
cd "$PROJECT_SLUG"

# Initialize git repository
git init

# Create .gitignore
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore


# Initialize uv package
uv init --package 

uv add --dev ruff pyright pytest pycov pre-commit commitizen python-semantic-release