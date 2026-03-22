# Specialized Agents: Agent Skills Manager (`askm`)

The `askm` project utilizes a variety of specialized agents, each defined within the `skills/` directory. These agents collaborate to streamline the lifecycle of agent skills.

## Agent Directory

| Agent Name | Skill Path | Role | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Skill Creator** | `skills/create-skill/` | Builder | Designing, scaffolding, and documenting new agent skills. |
| **Skill Evaluator** | `skills/eval-skill/` | Quality Assurance | Benchmarking and testing existing skills to ensure reliability. |
| **Gmail Productivity** | `skills/productivity/gmail/` | Automation | Managing Gmail-related tasks like cleanups and summaries. |

## Standard Workspace Agents

| Agent Name | Role | Responsibilities |
| :--- | :--- | :--- |
| **`codebase_investigator`** | Architect | In-depth analysis of the `askm` codebase and skill structures. |
| **`generalist`** | Assistant | Handling broad tasks, batch operations, and general research. |

## Collaboration Protocol

- **New Skill Creation:** Use the **Skill Creator** agent to generate boilerplate and initial documentation for any new capability.
- **Validation:** Always employ the **Skill Evaluator** to confirm a skill's behavior after updates.
- **Project Structure:** Adhere to the `askm` standards defined in `README.md` when modifying the `src/` directory.

## Maintenance

Agent definitions are stored in Markdown format (e.g., `SKILL.md`) within their respective `skills/` subdirectories. Updates to these definitions should be reflected here in `AGENTS.md` to maintain project clarity.
