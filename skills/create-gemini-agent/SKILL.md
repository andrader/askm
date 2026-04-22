---
name: create-gemini-agent
description: Create a custom Gemini agent by defining its system prompt, tools, and configuration in a markdown file.
---

# Subagents

Subagents are specialized agents that operate within your main Gemini CLI
session. They are designed to handle specific, complex tasks—like deep codebase
analysis, documentation lookup, or domain-specific reasoning—without cluttering
the main agent's context or toolset.

## What are subagents?

Subagents are "specialists" that the main Gemini agent can hire for a specific
job.

- **Focused context:** Each subagent has its own system prompt and persona.
- **Specialized tools:** Subagents can have a restricted or specialized set of
  tools.
- **Independent context window:** Interactions with a subagent happen in a
  separate context loop, which saves tokens in your main conversation history.

Subagents are exposed to the main agent as a tool of the same name. When the
main agent calls the tool, it delegates the task to the subagent. Once the
subagent completes its task, it reports back to the main agent with its
findings.

## How to use subagents

You can use subagents through automatic delegation or by explicitly forcing them
in your prompt.

### Automatic delegation

Gemini CLI's main agent is instructed to use specialized subagents when a task
matches their expertise. For example, if you ask "How does the auth system
work?", the main agent may decide to call the `codebase_investigator` subagent
to perform the research.

### Forcing a subagent (@ syntax)

You can explicitly direct a task to a specific subagent by using the `@` symbol
followed by the subagent's name at the beginning of your prompt. This is useful
when you want to bypass the main agent's decision-making and go straight to a
specialist.

**Example:**

```bash
@codebase_investigator Map out the relationship between the AgentRegistry and the LocalAgentExecutor.
```

When you use the `@` syntax, the CLI injects a system note that nudges the
primary model to use that specific subagent tool immediately.

## Creating custom subagents

You can create your own subagents to automate specific workflows or enforce
specific personas.

### Agent definition files

Custom agents are defined as Markdown files (`.md`) with YAML frontmatter. You
can place them in:

1.  **Project-level:** `.gemini/agents/*.md` (Shared with your team)
2.  **User-level:** `~/.gemini/agents/*.md` (Personal agents)

### File format

The file **MUST** start with YAML frontmatter enclosed in triple-dashes `---`.
The body of the markdown file becomes the agent's **System Prompt**.

**Example: `.gemini/agents/security-auditor.md`**

```markdown
---
name: security-auditor
description: Specialized in finding security vulnerabilities in code.
kind: local
tools:
  - read_file
  - grep_search
model: gemini-3-flash-preview
temperature: 0.2
max_turns: 10
---

You are a ruthless Security Auditor. Your job is to analyze code for potential
vulnerabilities.

Focus on:

1.  SQL Injection
2.  XSS (Cross-Site Scripting)
3.  Hardcoded credentials
4.  Unsafe file operations

When you find a vulnerability, explain it clearly and suggest a fix. Do not fix
it yourself; just report it.
```

### Configuration schema

| Field          | Type   | Required | Description                                                                                                                                                                                                   |
| :------------- | :----- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`         | string | Yes      | Unique identifier (slug) used as the tool name for the agent. Only lowercase letters, numbers, hyphens, and underscores.                                                                                      |
| `description`  | string | Yes      | Short description of what the agent does. This is visible to the main agent to help it decide when to call this subagent.                                                                                     |
| `kind`         | string | No       | `local` (default) or `remote`.                                                                                                                                                                                |
| `tools`        | array  | No       | List of tool names this agent can use. Supports wildcards: `*` (all tools), `mcp_*` (all MCP tools), `mcp_server_*` (all tools from a server). **If omitted, it inherits all tools from the parent session.** |
| `mcpServers`   | object | No       | Configuration for inline Model Context Protocol (MCP) servers isolated to this specific agent.                                                                                                                |
| `model`        | string | No       | Specific model to use (for example, `gemini-3-preview`). Defaults to `inherit` (uses the main session model).                                                                                                 |
| `temperature`  | number | No       | Model temperature (0.0 - 2.0). Defaults to `1`.                                                                                                                                                               |
| `max_turns`    | number | No       | Maximum number of conversation turns allowed for this agent before it must return. Defaults to `30`.                                                                                                          |
| `timeout_mins` | number | No       | Maximum execution time in minutes. Defaults to `10`.                                                                                                                                                          |

### Tool wildcards

When defining `tools` for a subagent, you can use wildcards to quickly grant
access to groups of tools:

- `*`: Grant access to all available built-in and discovered tools.
- `mcp_*`: Grant access to all tools from all connected MCP servers.
- `mcp_my-server_*`: Grant access to all tools from a specific MCP server named
  `my-server`.

### Isolation and recursion protection

Each subagent runs in its own isolated context loop. This means:

- **Independent history:** The subagent's conversation history does not bloat
  the main agent's context.
- **Isolated tools:** The subagent only has access to the tools you explicitly
  grant it.
- **Recursion protection:** To prevent infinite loops and excessive token usage,
  subagents **cannot** call other subagents. If a subagent is granted the `*`
  tool wildcard, it will still be unable to see or invoke other agents.

## Subagent tool isolation

Subagent tool isolation moves Gemini CLI away from a single global tool
registry. By providing isolated execution environments, you can ensure that
subagents only interact with the parts of the system they are designed for. This
prevents unintended side effects, improves reliability by avoiding state
contamination, and enables fine-grained permission control.

With this feature, you can:

- **Specify tool access:** Define exactly which tools an agent can access using
  a `tools` list in the agent definition.
- **Define inline MCP servers:** Configure Model Context Protocol (MCP) servers
  (which provide a standardized way to connect AI models to external tools and
  data sources) directly in the subagent's markdown frontmatter, isolating them
  to that specific agent.
- **Maintain state isolation:** Ensure that subagents only interact with their
  own set of tools and servers, preventing side effects and state contamination.
- **Apply subagent-specific policies:** Enforce granular rules in your
  [Policy Engine](/docs/reference/policy-engine) TOML configuration based on the
  executing subagent's name.

### Configuring isolated tools and servers

You can configure tool isolation for a subagent by updating its markdown
frontmatter. This lets you explicitly state which tools the subagent can use,
rather than relying on the global registry.

Add an `mcpServers` object to define inline MCP servers that are unique to the
agent.

**Example:**

```yaml
---
name: my-isolated-agent
tools:
  - grep_search
  - read_file
mcpServers:
  my-custom-server:
    command: 'node'
    args: ['path/to/server.js']
---
```

### Subagent-specific policies

You can enforce fine-grained control over subagents using the
[Policy Engine's](/docs/reference/policy-engine) TOML configuration. This allows
you to grant or restrict permissions specifically for an agent, without
affecting the rest of your CLI session.

To restrict a policy rule to a specific subagent, add the `subagent` property to
the `[[rules]]` block in your `policy.toml` file.

**Example:**

```toml
[[rules]]
name = "Allow pr-creator to push code"
subagent = "pr-creator"
description = "Permit pr-creator to push branches automatically."
action = "allow"
toolName = "run_shell_command"
commandPrefix = "git push"
```

In this configuration, the policy rule only triggers if the executing subagent's
name matches `pr-creator`. Rules without the `subagent` property apply
universally to all agents.

## Managing subagents

You can manage subagents interactively using the `/agents` command or
persistently via `settings.json`.

### Interactive management (/agents)

If you are in an interactive CLI session, you can use the `/agents` command to
manage subagents without editing configuration files manually. This is the
recommended way to quickly enable, disable, or re-configure agents on the fly.

For a full list of sub-commands and usage, see the
[`/agents` command reference](/docs/reference/commands#agents).

### Persistent configuration (settings.json)

While the `/agents` command and agent definition files provide a starting point,
you can use `settings.json` for global, persistent overrides. This is useful for
enforcing specific models or execution limits across all sessions.

#### `agents.overrides`

Use this to enable or disable specific agents or override their run
configurations.

```json
{
  "agents": {
    "overrides": {
      "security-auditor": {
        "enabled": false,
        "runConfig": {
          "maxTurns": 20,
          "maxTimeMinutes": 10
        }
      }
    }
  }
}
```

#### `modelConfigs.overrides`

You can target specific subagents with custom model settings (like system
instruction prefixes or specific safety settings) using the `overrideScope`
field.

```json
{
  "modelConfigs": {
    "overrides": [
      {
        "match": { "overrideScope": "security-auditor" },
        "modelConfig": {
          "generateContentConfig": {
            "temperature": 0.1
          }
        }
      }
    ]
  }
}
```

#### Safety policies (TOML)

You can restrict access to specific subagents using the CLI's **Policy Engine**.
Subagents are treated as virtual tool names for policy matching purposes.

To govern access to a subagent, create a `.toml` file in your policy directory
(e.g., `~/.gemini/policies/`):

```toml
[[rule]]
toolName = "codebase_investigator"
decision = "deny"
deny_message = "Deep codebase analysis is restricted for this session."
```

For more information on setting up fine-grained safety guardrails, see the
[Policy Engine reference](/docs/reference/policy-engine#special-syntax-for-subagents).

### Optimizing your subagent

The main agent's system prompt encourages it to use an expert subagent when one
is available. It decides whether an agent is a relevant expert based on the
agent's description. You can improve the reliability with which an agent is used
by updating the description to more clearly indicate:

- Its area of expertise.
- When it should be used.
- Some example scenarios.

For example, the following subagent description should be called fairly
consistently for Git operations.

> Git expert agent which should be used for all local and remote git operations.
> For example:
>
> - Making commits
> - Searching for regressions with bisect
> - Interacting with source control and issues providers such as GitHub.

If you need to further tune your subagent, you can do so by selecting the model
to optimize for with `/model` and then asking the model why it does not think
that your subagent was called with a specific prompt and the given description.

## Remote subagents (Agent2Agent)

Gemini CLI can also delegate tasks to remote subagents using the Agent-to-Agent
(A2A) protocol.

See the [Remote Subagents documentation](/docs/core/remote-agents) for detailed
configuration, authentication, and usage instructions.

## Extension subagents

Extensions can bundle and distribute subagents. See the
[Extensions documentation](/docs/extensions#subagents) for details on how
to package agents within an extension.

## Disabling subagents

Subagents are enabled by default. To disable them, set `enableAgents` to `false`
in your `settings.json`:

```json
{
  "experimental": { "enableAgents": false }
}
```