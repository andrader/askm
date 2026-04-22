# Lockfile Specification (`skills.lock`)

The `skills.lock` file is a JSON file located in the scope's skills directory. It manages the state and source tracking of installed skills, enabling Jup to synchronize changes efficiently without destroying user-modified directories unnecessarily.

## Schema Version
The top-level `version` field tracks the lockfile schema version (currently `0.0.0`).

## Sources
The `sources` object is a dictionary where each key is a unique identifier for a source (e.g., a GitHub repository path like `owner/repo/skills/name` or a local absolute path).

### Source Object Fields:
- `repo` (string, optional): Canonical repository reference (e.g., `owner/repo`). Omitted for purely local sources.
- `source_type` (string): Identifies the origin mechanism (`github` or `local`).
- `source_path` (string, optional): The original absolute path if it is a local directory source.
- `source_layout` (string): `single` or `collection`, depending on whether the root of the source path contained a single `SKILL.md` or multiple skill subdirectories.
- `category` (string): The organizational category for the skill within the central global storage directory.
- `skills` (array of strings): A list of the precise skill names installed from this specific source.
- `version` (string, optional): The resolved version (e.g., tag, commit SHA, or branch) used during installation.
- `source` (string, optional): The full git URL or local path to the original source location.
- `last_updated` (string): ISO 8601 formatted timestamp indicating when the source was last downloaded or updated via `jup sync`.
