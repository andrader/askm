# jup

`jup` is a small command-line tool for installing and syncing agent skills across the local skill directories used by supported AI assistants.

It helps you:

- install skills from GitHub repositories that expose a top-level `skills/` folder
- keep installed skills organized in a lockfile so they can be synced again later
- copy or link skills into the directories used by agents like Gemini, Copilot, and Claude

## Install

The preferred way to install `jup` is from PyPI with `uv`:

```bash
uv tool install jup
jup --help
```

If you do not want to install it globally, you can run it on demand:

```bash
uvx jup --help
```

`pip` also works if you prefer a traditional install:

```bash
pip install jup
jup --help
```

## Quick Start

1. Check the current configuration:

```bash
jup config show
```

2. Choose which agent directories should receive synced skills:

```bash
jup config set agents gemini,copilot,claude
```

Use `none` to clear the list:

```bash
jup config set agents none
```

3. Add a skills repository:

```bash
jup add owner/repo --category productivity
```

4. Review what is installed:

```bash
jup list
```

5. Push the managed skills into the configured agent directories:

```bash
jup sync
```

## What It Does

`jup` works with repositories that follow a simple structure:

```text
repo/
	skills/
		skill-name/
			SKILL.md
```

When you run `jup add owner/repo`, it clones the repository, finds every nested skill directory under `skills/` that contains a `SKILL.md` file, stores those skills in `~/.jup`, and records them in a lockfile.

After that, `jup sync` installs the managed skills into the configured target locations. By default, `jup` uses symlinks, but you can switch to copying with:

```bash
jup config set sync-mode copy
```

The main configuration values are:

- `scope`: `global` or `local`
- `agents`: a comma-separated list of agent names
- `sync-mode`: `link` or `copy`

## Supported Agents

`jup` includes built-in locations for these agent names:

- `gemini`
- `copilot`
- `claude`
- `default`

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, workflow, and publishing details.
