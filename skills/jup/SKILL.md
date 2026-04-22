# jup: Agent Skills Manager ✨

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories (e.g., Gemini, Copilot, Claude). It allows users to install skills from GitHub repositories or local directories, keeping them organized via a lockfile and syncing them to target locations using symlinks or file copies.

## Core Concepts

- **Skills**: A directory containing a `SKILL.md` file.
- **Syncing**: Linking or copying skills from your local cache (`~/.jup/skills/`) to agent-specific directories (e.g., `~/.gemini/skills/`).
- **Lockfile**: A central record of all installed skill sources and their metadata.

## Usage Instructions

### Adding Skills
You can add skills from GitHub repositories, URLs, or local paths.

- **GitHub Repository**: `jup add owner/repo`
- **GitHub URL**: `jup add https://github.com/owner/repo/tree/branch/path`
- **Versioning**: `jup add owner/repo@v1.0.0` (Supports tags, SHAs, or branches).
- **Exact Path**: `jup add owner/repo/path/to/skill` (Faster installation for large repos).
- **Targeting**:
  - `--agent (-a) name`: Install to specific agent(s).
  - `--scope user|local`: Set target scope.
  - `--dir path`: Install to a custom directory (overrides agent/scope).
- **Options**:
  - `--category (-c) name`: Category (default: `misc`).
  - `--skills name1,name2`: Select specific skills from a collection.

### Listing Skills
Check the status of your skills with flexible aliases:
- `jup list` or `jup ls`: Shows installed skills, versions, and origins.
- `jup ls skills`: Alias for `jup list`.
- `jup ls agents` or `jup ls agent`: Lists configured harness providers.
- `jup ls config`: Shows current configuration.
- `jup list --json`: Outputs status in clean, machine-readable format.

### Syncing
Push your managed skills to agents:
- `jup sync`: Updates all links/copies in configured agent directories.
- `jup sync --update` (or `jup up`): Checks GitHub for updates.

### Searching Registry
- `jup find query`: Search the `skills.sh` registry.
- `jup find query -it`: Interactive mode to preview and install skills.

### Configuration
Manage your environment:
- `jup config show`: View current settings (renamed `global` scope to `user`).
- `jup config set sync-mode copy`: Switch from symlinks to file copies.

## Agent Specifics
`jup` supports built-in paths for:
- `gemini`: `~/.gemini/skills`
- `copilot`: `~/.copilot/skills`
- `claude`: `~/.claude/skills`
- `cursor`: `~/.cursor/skills`
- `codex`: `~/.codex/skills`
- `antigravity`: `~/.gemini/antigravity/skills`
- `default`: `~/.agents/skills`

You can add custom agents with `jup agent add`.

