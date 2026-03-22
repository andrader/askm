---
name: create-skill
description: The ultimate manual for creating, optimizing, and maintaining Agent Skills. Use when asked to build a new capability, define specialized workflows, or capture domain expertise for AI agents using the agentskills.io standard.
---

# The Ultimate Guide to Creating Agent Skills

An Agent Skill is a portable, version-controlled package that gives AI agents new capabilities, domain expertise, and repeatable workflows.

---

## 1. Anatomy of a Skill
A skill is a directory containing a mandatory `SKILL.md` and optional supporting resources. By convention, skills are often discovered in `.agents/skills/` at the project or user level.

```text
skill-name/
├── SKILL.md          # Required: Instructions + metadata
├── scripts/          # Optional: Self-contained executable code
├── references/       # Optional: Documentation loaded on demand
└── assets/           # Optional: Static templates, icons, or data
```

---

## 2. SKILL.md Specification
The `SKILL.md` file defines the skill's identity and core logic.

### Frontmatter (YAML)
| Field | Required | Constraints |
| :--- | :--- | :--- |
| **`name`** | Yes | 1-64 chars, lowercase `a-z`, `0-9`, and `-`. No leading/trailing hyphens. No consecutive hyphens (`--`). Must match folder name. |
| **`description`** | Yes | 1-1024 chars. Primary trigger for the agent. |
| **`license`** | No | Name or reference to a bundled license file. |
| **`compatibility`** | No | Max 500 chars. Environment/tool requirements. |
| **`metadata`** | No | Arbitrary key-value mapping (e.g., `author`, `version`). |
| **`allowed-tools`** | No | Space-delimited list of pre-approved tools (Experimental). |

### Progressive Disclosure
To manage context efficiently, skills load in tiers:
1. **Catalog**: `name` + `description` (Session start).
2. **Instructions**: Full `SKILL.md` body (On activation). **Limit to 500 lines / 5,000 tokens.**
3. **Resources**: Individual files in `scripts/`, `references/`, etc. (Loaded only when referenced).

---

## 3. Optimizing for Triggering
The `description` is the ONLY way an agent knows to use your skill.

- **Use Imperative Phrasing**: "Use this skill when..." rather than "This skill does..."
- **Focus on Intent**: Describe the user's goal, not the code's implementation.
- **Be Explicit**: List specific keywords and contexts (e.g., "even if the user doesn't mention 'CSV' or 'analysis'").
- **Avoid Over-Broadening**: Near-miss test cases help refine boundaries (e.g., distinguish "CSV Analysis" from "Excel formula editing").

---

## 4. Instruction Design Patterns
Choose the right pattern based on the task's complexity.

### Gotchas (High Value)
List environment-specific facts that defy reasonable assumptions.
> "The `/health` endpoint returns 200 even if the DB is down. Use `/ready` for full health."

### Checklists for Multi-Step Workflows
Help the agent track progress and avoid skipping validation gates.
> - [ ] Step 1: Analyze the form (`scripts/analyze_form.py`)
> - [ ] Step 2: Validate mapping (`scripts/validate_fields.py`)

### Output Templates
Agents pattern-match concrete structures better than prose descriptions. Store large templates in `assets/`.

### Validation Loops
Instruct the agent to "do the work, run a validator, fix errors, and repeat" until a success state is reached.

### Plan-Validate-Execute
For destructive or batch operations, require a structured plan (e.g., `plan.json`) to be validated against a source of truth before execution.

---

## 5. Using Scripts & Commands
Scripts ensure deterministic reliability for fragile tasks.

### One-Off Command Runners
Use tools that auto-resolve dependencies at runtime:
- **Python**: `uvx ruff check .` or `pipx run 'ruff==0.8.0' check .`
- **Node.js**: `npx eslint --fix .` or `bunx eslint@9 --fix .`
- **Go**: `go run golang.org/x/tools/cmd/goimports@latest .`
- **Deno**: `deno run npm:create-vite@6 my-app`

### Self-Contained Scripts (Inline Dependencies)
Bundle scripts in `scripts/` and use inline metadata to keep them portable.
- **Python (PEP 723)**: `uv run scripts/process.py`
- **Deno/Bun**: Use `npm:` or direct versioned imports (e.g., `import * as cheerio from "npm:cheerio@1.0.0"`).
- **Ruby**: Use `require 'bundler/inline'` with an inline `gemfile do ... end` block.

### Agentic Script Design
- **Non-Interactive**: Must NOT block on TTY prompts (use flags/env vars).
- **Documented**: Support `--help` so the agent can learn the interface.
- **Helpful Errors**: Clearly state what was expected vs. received.
- **Structured Output**: Output JSON/CSV to stdout; diagnostics to stderr.

---

## 6. Calibrating Control
- **Freedom**: Use when multiple approaches are valid. Explain the "why" to help the agent make context-dependent decisions.
- **Prescriptive**: Use when consistency is critical. "Run exactly this sequence... Do not modify the command."
- **Defaults over Menus**: Pick a standard tool/approach; mention alternatives only as escape hatches.

---

## 7. Iteration & Refinement
1. **Extract from hands-on tasks**: Complete a task manually, then capture the successful pattern.
2. **Synthesize from artifacts**: Use existing runbooks, schemas, and incident reports as source material.
3. **Execute-then-Revise**: Run the skill, identify where the agent wastes time or ignores instructions, and tighten the `SKILL.md`.

---

## 8. Best Practices
- **Relative Paths**: Always reference files relative to the skill root (e.g., `scripts/validate.sh`).
- **One Level Deep**: Keep file references direct; avoid deeply nested reference chains.
- **Omit Common Knowledge**: The agent already knows HTTP, JSON, and basic Python. Focus only on project-specific context.

---

## 9. Security & Trust
Project-level skills from untrusted repositories should be gated behind a trust check. This prevents malicious repositories from silently injecting instructions or executing untrusted code via the agent's context. Always review project-specific skills before use in high-stakes environments.
