# jup vs. npx skills

Both `jup` and `npx skills` are CLI tools designed to manage and install Open Agent Skills (`SKILL.md` files) for AI coding assistants like Gemini CLI, Claude Code, and Cursor. However, they take different architectural approaches and cater to different workflows.

## Feature Comparison

| Feature | `jup` | `npx skills` |
| :--- | :--- | :--- |
| **Language / Runtime** | Python (via `uv` or `pip`) | Node.js (via `npx`) |
| **State Management** | Central lockfile (`~/.jup/skills-lock.json`) | Global or per-project installation |
| **Multi-Agent Sync** | **Yes.** Symlinks/copies from a central cache to all configured agents via `jup sync` | **Yes.** Via `-a` flags during install (e.g., `-a gemini-cli -a cursor`) |
| **Search / Registry** | Direct repo/local path only | Built-in search (`npx skills find`) backed by `skills.sh` |
| **Local Development** | Excellent. Symlinks local directories directly into agent folders | Good. Includes an `init` command for scaffolding |
| **Updates** | `jup sync --update` | `npx skills update` / `npx skills check` |

## Command Reference

### `jup`
*   `jup add <repo|path>`: Installs a skill from a GitHub repo or a local directory. Supports `--path` and `--skills` for sub-selection.
*   `jup sync`: Syncs managed skills from the central storage into the configured agent directories (e.g., `.gemini/skills`, `.claude/skills`).
*   `jup list`: Shows all installed skills, locations, and last update times.
*   `jup remove <target>`: Uninstalls a skill or repository.
*   `jup config set agents gemini,claude`: Configures which agents receive the synced skills.

### `npx skills`
*   `npx skills find [query]`: Interactively searches for available skills in the community registry.
*   `npx skills add <package>`: Installs a skill. Supports `--global` and targeting specific agents via `-a`.
*   `npx skills list`: Lists installed skills.
*   `npx skills check` / `update`: Manages skill versioning.
*   `npx skills init`: Scaffolds a new skill template.

## Pros and Cons

### `jup`

**Pros:**
*   **Centralized Multi-Agent Sync:** You configure your target agents once (`jup config set agents ...`), and every `jup sync` ensures all agents have exactly the same skills via lightweight symlinks.
*   **Local-First Design:** It natively supports adding local skill directories (`jup add ./my-skills`). Because it uses symlinks by default, you can edit the source skill locally and the changes are immediately available to your agents without needing to re-run an update.
*   **Python Ecosystem:** Ideal for developers already using `uv` or Python toolchains.

**Cons:**
*   **No Central Registry:** You must know the exact GitHub repository (`owner/repo`) or local path to install a skill. There is no interactive `find` command.
*   **Requires Python:** Adds a dependency for users strictly in the Node.js ecosystem.

### `npx skills`

**Pros:**
*   **Interactive Search Registry:** Deep integration with `skills.sh` allows you to easily discover and install community skills via `npx skills find`.
*   **Zero-Install for JS Devs:** If you have Node.js installed, you can just run `npx skills` without any prior installation step.
*   **Skill Scaffolding:** The `init` command makes it very easy to start writing a new skill from scratch.

**Cons:**
*   **Requires Node.js:** Adds a dependency for users strictly in the Python/Rust/Go ecosystems.
*   **Less Transparent State:** Relies on direct installation into `.claude` or `.gemini` directories without a highly visible lockfile synchronization step, making local cross-agent iteration slightly more manual if not using global installation flags.
