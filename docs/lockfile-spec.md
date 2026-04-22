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

## Current Limitations & Known Problems

1. **Non-Portable Local Keys**: Absolute paths are used as dictionary keys for local sources. This makes the lockfile non-portable across different machines or environments where the project directory structure might differ.
2. **Ambiguous Versioning**: The `version` field does not distinguish between semantic tags, branch names, or commit SHAs. This makes it difficult to implement a robust "update" vs "upgrade" logic.
3. **No Content Integrity**: There are no checksums (e.g., SHA-256) of the installed skills. Jup cannot detect if a user has manually modified a skill's content without a full sync.
4. **Lack of Concurrency Control**: The specification does not define a mechanism for atomic writes or file locking, which could lead to data loss if multiple CLI instances (or agents) attempt to modify the lockfile simultaneously.
5. **Harness Dependency**: The lockfile doesn't explicitly track which harness an entry was originally intended for, which complicates cleanup when multiple harnesses share the same physical destination directory.

