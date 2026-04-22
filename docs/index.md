# jup ✨

`jup` is a small command-line tool for installing and syncing agent skills across the local skill directories used by supported AI assistants.

It helps you:

- install skills from GitHub repositories (via name, URL, or exact path)
- keep installed skills organized in a lockfile with version tracking
- copy or link skills into directories for Gemini, Copilot, Claude, Cursor, and more

## Features ✨

- **Multi-Agent Support**: Sync skills for Gemini, Copilot, Claude, Cursor, Codex, and Antigravity.
- **Smart Parsing**: Install via `owner/repo`, full GitHub URLs, or exact paths for faster setup.
- **Flexible Scope**: Manage skills at the `user` (formerly global) or `local` project level.
- **CLI Aliases**: Faster workflow with `ls`, `up`, `install`, and `agent` aliases.

## Quick Start 🚀

### 1. Install `jup` 📦

The preferred way to install `jup` is from PyPI with `uv`:

```bash
uv tool install jup
jup --help
```

### 2. Check the current configuration ⚙️

```bash
jup ls config
```

### 3. Choose which agent directories should receive synced skills 🤖

```bash
jup config set agents gemini,cursor,claude
```

### 4. Add skills ➕

```bash
# Via shorthand
jup add owner/repo --category productivity

# Via URL
jup add https://github.com/kepano/obsidian-skills/tree/main/skills/obsidian-cli

# Pin to a version
jup add owner/repo@v1.0.0
```

#### Search for skills 🔍

Search for skills in the `skills.sh` registry:

```bash
jup find instagram --interactive
```

### 5. Review and update skills 📋

```bash
jup ls
```

#### Check for updates and apply them

```bash
jup up
```

### 6. Push the managed skills into the configured agent directories 🔄

```bash
jup sync
```

## Comparison with `npx skills` ⚖️

While Vercel's `npx skills` is a fantastic package manager for AI skills, `jup` focuses heavily on **centralized lockfile management** and **local symlink synchronization** across multiple agents.

For a full breakdown, see the [jup vs. npx skills comparison](jup-vs-npx-skills.md).

## What It Does 🧭

`jup` works with repositories that follow a simple structure:

```text
repo/
  skills/
    skill-name/
      SKILL.md
```

When you run `jup add owner/repo`, it clones the repository, finds every nested skill directory under `skills/` (or `.claude/skills/` if present) that contains a `SKILL.md` file, stores those skills in `~/.jup`, and records them in a lockfile.

After that, `jup sync` installs the managed skills into the configured target locations. By default, `jup` uses symlinks, ensuring your local edits are immediately available.
