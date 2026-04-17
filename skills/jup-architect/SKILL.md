# jup Expert Architect Assistant 🏗️

This skill helps AI agents analyze the `jup` codebase, identify technical debt, suggest architectural improvements, and ensure high engineering standards.

## How to Use This Skill

- **Codebase Analysis**: Perform deep dives into `src/jup/` to understand current implementation patterns.
- **Technical Debt Audit**: Identify areas where the code is fragile, complex, or difficult to test.
- **Architectural Proposals**: Suggest structural changes to improve modularity, performance, or scalability.
- **Code Quality Review**: Evaluate existing code against best practices for Python, Typer, and Pydantic.

## Core Architectural Values

- **Modularity**: Ensure clear boundaries between CLI commands, configuration, and data models.
- **Testability**: Prioritize designs that are easy to unit test and integrate.
- **Performance**: Optimize for speed, especially in common operations like `list` and `sync`.
- **Maintainability**: Favor simple, explicit code over complex abstractions.
- **Type Safety**: Leverage Python type hints and Pydantic validation to prevent runtime errors.

## Key Areas of Focus

- **Command Orchestration**: Evaluate how commands are registered and executed.
- **Data Persistence**: Analyze how `~/.jup` and the lockfile are managed.
- **Dependency Management**: Review the use of `uv` and external libraries.
- **Error Handling**: Ensure robust error reporting across the entire application.
- **Testing Strategy**: Suggest improvements to the current `pytest` suite and coverage.
