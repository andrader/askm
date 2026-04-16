# CHANGELOG


## v0.9.1 (2026-04-16)

### Bug Fixes

- Prioritize standard skill path and add recursive search fallback
  ([`c755bef`](https://github.com/andrader/jup/commit/c755bef5834eef8ea3d7c4258629ad7ce3af57d9))


## v0.9.0 (2026-04-16)

### Features

- Update jup list command with improved formatting and filtering
  ([`0ef6f2d`](https://github.com/andrader/jup/commit/0ef6f2d6fa067c39960ecfce6cff385c6d0215d5))


## v0.8.0 (2026-04-15)

### Documentation

- Clarify skill path structure and update project guidelines
  ([`008bb7b`](https://github.com/andrader/jup/commit/008bb7b32b2618584b7cd74fe0228ebd8e008135))

### Features

- Cleanup managed skills from inactive agent directories in sync
  ([`811bc23`](https://github.com/andrader/jup/commit/811bc2356bec12cc9b0ceb9a96ed2726f8591b15))


## v0.7.1 (2026-04-15)

### Bug Fixes

- **cli**: Remove redundant 'skills/' nesting in skill target paths
  ([`d8220c5`](https://github.com/andrader/jup/commit/d8220c5231e251e9176ffaef25376361de51b4ee))


## v0.7.0 (2026-04-14)

### Features

- **cli**: Add interactive TUI for find and new show command
  ([`67ca644`](https://github.com/andrader/jup/commit/67ca644e52ec3f4a629d10092c448d6cec4d41e6))


## v0.6.0 (2026-04-14)

### Features

- **agent**: Add custom agent provider management
  ([`8cb3526`](https://github.com/andrader/jup/commit/8cb3526e6dad3935211ae5a9072cf59a62e43e16))


## v0.5.0 (2026-04-14)

### Documentation

- Add screenshots of the CLI output to the readme
  ([`282007a`](https://github.com/andrader/jup/commit/282007ac40f17f5e1d1ccb703e2d79993f1107bd))

### Features

- **cli**: Make find command non-interactive by default and add filtering options
  ([`28a5bcc`](https://github.com/andrader/jup/commit/28a5bcc36ec96dc7cb0c942dcbfa402d221d40bb))


## v0.4.2 (2026-04-14)

### Bug Fixes

- **cli**: Improve version callback documentation
  ([`ce89279`](https://github.com/andrader/jup/commit/ce892798163c72fbd2ca0b6aea63a0f474a499a1))

### Continuous Integration

- Add workflow_dispatch to release workflow
  ([`f0dcc6e`](https://github.com/andrader/jup/commit/f0dcc6e53a293196b44a8dc3fc520d01e09edd95))

### Documentation

- Update README with features
  ([`e6d376d`](https://github.com/andrader/jup/commit/e6d376d30056b95b6cbc021c7b762a53ff74abe0))


## v0.4.1 (2026-04-14)

### Bug Fixes

- **ci**: Fix permissions for dist directory in release workflow
  ([`aa8a94a`](https://github.com/andrader/jup/commit/aa8a94af796416b59c08e330f0f0114bb3a62194))


## v0.4.0 (2026-04-14)

### Bug Fixes

- **ci**: Ensure uv is available for build in release workflow
  ([`d65a03b`](https://github.com/andrader/jup/commit/d65a03bfe3053d7dcd267e42ed32c5b585f7f841))

- **ci**: Fix setup-uv version in release workflow
  ([`0cf0926`](https://github.com/andrader/jup/commit/0cf0926ef0aef6a380f1b3fdce5a4ca52266b030))

### Documentation

- Add comparison with npx skills
  ([`fd28afa`](https://github.com/andrader/jup/commit/fd28afa5a09f6a5b46c267fbc3e6ac4f960602ee))

- Update comparison with npx skills to include new 'find' command
  ([`231828c`](https://github.com/andrader/jup/commit/231828c4e2e143970a14629d47a7773791d24ee4))

### Features

- Add 'find' command to search skills.sh registry interactively
  ([`bb27173`](https://github.com/andrader/jup/commit/bb27173ca20bb8d9659b98597199766fc4bebe92))

- Add banner and --version flag to cli
  ([`5f3d544`](https://github.com/andrader/jup/commit/5f3d5446a64ed002c58f7dc5e4cb17be188de4f1))


## v0.3.3 (2026-04-14)

### Chores

- Update dependencies for ruff, ty, commitizen, and semantic-release
  ([`e55c5df`](https://github.com/andrader/jup/commit/e55c5df93761ba05e5f1a1fd90650ecb998b9ad4))

### Code Style

- Fix linting errors across codebase
  ([`da7ce54`](https://github.com/andrader/jup/commit/da7ce54efbe1f58cc7a2863fb1047b6a6b4f7c74))

### Continuous Integration

- Add modern tooling and automated release workflow
  ([`00e47f0`](https://github.com/andrader/jup/commit/00e47f041f4e740b78de969b6aac8aac7a844510))

### Documentation

- Update contribution guidelines and tooling documentation
  ([`cf693f6`](https://github.com/andrader/jup/commit/cf693f682f2daddc4d422d4966cce5acfb0472a2))


## v0.3.2 (2026-04-14)

### Bug Fixes

- **cli**: Improve list output and track skill source updates
  ([`f16ae05`](https://github.com/andrader/jup/commit/f16ae052557aa8fe2f126c7475c99970920a8468))

### Documentation

- Refresh AGENTS guidance and README update flow
  ([`6f1721a`](https://github.com/andrader/jup/commit/6f1721a67e9a923ec3b442752645a81fcc625f1c))


## v0.3.1 (2026-04-14)

### Features

- Fallback to .claude/skills/ if skills/ missing; update docs and tests\n\nCo-authored-by: Copilot
  <223556219+Copilot@users.noreply.github.com>
  ([`c745abb`](https://github.com/andrader/jup/commit/c745abb0dcb5c0d037849766ab0f8db1421f467d))


## v0.3.0 (2026-04-13)

### Bug Fixes

- Move command registrations to maintain app structure
  ([`2003a14`](https://github.com/andrader/jup/commit/2003a14d66b0b8792e9c7ded98d7afd6411ae42d))

### Documentation

- Update command execution instructions for consistency and clarity
  ([`1e0d6b1`](https://github.com/andrader/jup/commit/1e0d6b1afc36b603fbfaa023742fdf9497a51621))

### Features

- Support --path and --skills for GitHub sources in add command; update help, README, and tests
  ([`e72af98`](https://github.com/andrader/jup/commit/e72af98a2782ef7b82a0a7bd3bf32778feb1d837))

- Add --path and --skills options to add command for GitHub sources - Allow installing skills from a
  subdirectory and selecting specific skills - Update help text and README with usage and caveats -
  Add integration tests for new options

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.2.0 (2026-04-08)

### Features

- Add local directory skill sources
  ([`20ca153`](https://github.com/andrader/jup/commit/20ca15340400e91d942ed8b866b58bb53bbe5be1))


## v0.1.0 (2026-04-08)
