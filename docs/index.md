# jup ✨

`jup` is a small command-line tool for installing and syncing agent skills across the local skill directories used by supported AI assistants.

It helps you:

- install skills from GitHub repositories that expose a top-level `skills/` folder (or `.claude/skills/` as a fallback)
- keep installed skills organized in a lockfile so they can be synced again later
- copy or link skills into the directories used by agents like Gemini, Copilot, and Claude

## Features ✨

- **Multi-Agent Support**: Sync skills for Gemini, Copilot, and Claude.
- **Local-First**: Works with local skill directories and global configurations.
- **Git Integration**: Install and update skills directly from GitHub.

## Quick Start 🚀

### 1. Install `jup` 📦

The preferred way to install `jup` is from PyPI with `uv`:

```bash
uv tool install jup
jup --help
```

If you do not want to install it, you can run it on demand:

```bash
uvx jup --help
```

`pip` also works if you prefer a traditional install:

```bash
pip install jup
jup --help
```

### 2. Check the current configuration ⚙️

```bash
jup config show
```

### 3. Choose which agent directories should receive synced skills 🤖

```bash
jup config set agents gemini,copilot,claude
```

### 4. Add skills ➕

```bash
jup add owner/repo --category productivity
```

#### Search for skills 🔍

Search for skills in the `skills.sh` registry:

```bash
jup find instagram --interactive
```

### 5. Review and update skills 📋

```bash
jup list
```

#### Check for updates and apply them

```bash
jup sync --update
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
