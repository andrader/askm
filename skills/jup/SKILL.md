# jup: Agent Skills Manager ✨

`jup` is a lightweight Python-based command-line tool designed to manage and synchronize "agent skills" across various AI assistant directories (e.g., Gemini, Copilot, Claude). It allows users to install skills from GitHub repositories or local directories, keeping them organized via a lockfile and syncing them to target locations using symlinks or file copies.

## Core Concepts

- **Skills**: A directory containing a `SKILL.md` file.
- **Syncing**: Linking or copying skills from your local cache (`~/.jup/skills/`) to agent-specific directories (e.g., `~/.gemini/skills/`).
- **Lockfile**: A central record of all installed skill sources and their metadata.

## Usage Instructions

### Adding Skills
You can add skills from GitHub or local paths.

- **GitHub**: `jup add owner/repo --category category-name`
  - Fallback: If `skills/` is missing, it checks `.claude/skills/`.
  - Specific path: `jup add owner/repo --path custom/path`
  - Specific skills: `jup add owner/repo --skills skill-a,skill-b`
- **Local**: `jup add /path/to/local/skills` (Supports single skill or collection layouts).

### Listing Skills
Check the status of your skills:
- `jup list`: Shows installed skills, their origins, and whether they are present in configured agent directories.
- `jup list --json`: Outputs the status in machine-readable format.
- `jup list --only-local` / `--remote`: Filters the list.

### Syncing
Push your managed skills to agents:
- `jup sync`: Updates all links/copies in configured agent directories.
- `jup sync --update`: Checks GitHub for updates to your installed skills.

### Searching Registry
- `jup find query`: Search the `skills.sh` registry.
- `jup find query -it`: Interactive mode to preview and install skills.

### Configuration
Manage which agents receive skills:
- `jup config show`: View current settings.
- `jup config set agents gemini,copilot`: Choose target agents.
- `jup config set sync-mode copy`: Switch from symlinks to file copies.

## Agent Specifics
`jup` has built-in paths for:
- `gemini`: `~/.gemini/skills`
- `copilot`: `~/.copilot/skills`
- `claude`: `~/.claude/skills`
- `default`: `~/.agents/skills`

You can add custom agents with `jup agent add`.
