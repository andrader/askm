# CHANGELOG


## v0.13.0-beta.3 (2026-04-20)

### Bug Fixes

- Handle git clone failure gracefully when repo is not found
  ([`1ceb65a`](https://github.com/andrader/jup/commit/1ceb65a5ddfdb966f398d8453d705bee39ba9e0d))

### Chores

- Reconcile main and release branches
  ([`c52c3f1`](https://github.com/andrader/jup/commit/c52c3f1ec9489afb652438fd5ba1a276b933e20b))

### Continuous Integration

- Add actions:write permission to promotion workflow
  ([`c85e3e9`](https://github.com/andrader/jup/commit/c85e3e9280c65ec04910291a4557f003585418c9))

- Automate branch promotion and back-sync between main and release
  ([`8d2f64e`](https://github.com/andrader/jup/commit/8d2f64e30e18ebe1008d8b85ebfa76a8e33589d7))

- Change release promotion schedule to daily at 5am BRT
  ([`16dec81`](https://github.com/andrader/jup/commit/16dec813706951ebd6c86a105c509fa20c048c2e))

- Explicitly trigger release workflow in promotion job
  ([`700b82a`](https://github.com/andrader/jup/commit/700b82a392f42e297d7da300d838bf4e3e7256e8))


## v0.13.0-beta.2 (2026-04-20)

### Features

- Explicitly mention codex support in harness registry
  ([`b0f4d9b`](https://github.com/andrader/jup/commit/b0f4d9b8a659d13902f7542df1a1c24a593c2576))


## v0.13.0-beta.1 (2026-04-20)

### Chores

- Bump version to 0.13.0-beta.1 and sync with stable
  ([`6c9b842`](https://github.com/andrader/jup/commit/6c9b8425ed9f8676ed31e2409715cf12662e2f2e))


## v0.12.0-beta.4 (2026-04-20)

### Features

- Rename "agent" to "harness" and ".agents" terminology cleanup
  ([`9d60b06`](https://github.com/andrader/jup/commit/9d60b06d0d1928175b4f340b8cb47a1adff1e364))


## v0.12.1 (2026-04-20)


## v0.12.0-beta.3 (2026-04-20)

### Bug Fixes

- **ci**: Improve weekly release PR logic to fail on unexpected errors
  ([`57ac0f9`](https://github.com/andrader/jup/commit/57ac0f9063ac711057d311e8c2f733d48fd7c390))


## v0.12.0-beta.2 (2026-04-20)

### Bug Fixes

- **ci**: Ensure labels exist and update permissions for weekly release PR
  ([`b685ae9`](https://github.com/andrader/jup/commit/b685ae97494b6406c862abe11a7970af7663da1e))

### Chores

- Add mkdocs deployment workflow
  ([`5468348`](https://github.com/andrader/jup/commit/5468348baf9d1ca47216e02485a5d4952d9d7a66))

- Add mkdocs.yml to repository
  ([`0b18a4c`](https://github.com/andrader/jup/commit/0b18a4cd9e1225439a6eedc3eafb9b0e1f91dae9))

- Clean up docs workflow
  ([`f32e978`](https://github.com/andrader/jup/commit/f32e978bc8d53e9b57a4c34846f5afa7a2b8bb97))

- Debug docs deployment and trigger on main
  ([`de35e3e`](https://github.com/andrader/jup/commit/de35e3ee14565de85e79792186ee9f47f6a87ab0))

- Migrate documentation stack from mkdocs to zensical
  ([`016c975`](https://github.com/andrader/jup/commit/016c975df607522121ebf94358c62b05d6c00f03))

- Update jup package version to 0.12.0b1
  ([`85e672a`](https://github.com/andrader/jup/commit/85e672ac83336b686377a6d2c28fd3c70cc73655))

- Update setup-uv action to v8 and remove Python setup step
  ([`ef29e16`](https://github.com/andrader/jup/commit/ef29e1656b2f8df934b10a90458daed2ebfa252e))

- Use explicit config path for mkdocs deployment
  ([`25988f1`](https://github.com/andrader/jup/commit/25988f199044c61ae1696c92006ee9ff8adcff68))

- **ci**: Add --quiet and --frozen flags to uv commands
  ([`ba4d9ac`](https://github.com/andrader/jup/commit/ba4d9ac045f5058ad6133df13d7029a1b7928c7c))

- **ci**: Re-enable automated PyPI publishing
  ([`91d5c24`](https://github.com/andrader/jup/commit/91d5c241af772a2210cd54ab9b30439e2753d2a7))

- **ci**: Refactor release workflow to use local semantic-release and explicit build steps
  ([`5811f76`](https://github.com/andrader/jup/commit/5811f7628e09295a4d1bde6ef3389744e520e2f0))

- **ci**: Replace create-pull-request action with gh cli
  ([`a592366`](https://github.com/andrader/jup/commit/a59236656e82969980c94b18efbb11fbc035d7a7))

- **ci**: Split semantic-release version/publish and PyPI build/publish steps
  ([`6db5208`](https://github.com/andrader/jup/commit/6db5208ba3ba59d2b136a463813fb80c113f6f0d))

### Documentation

- Add site_url to mkdocs.yml
  ([`9a0b1a3`](https://github.com/andrader/jup/commit/9a0b1a3f53413eb7fbf56f5d26e387b4d40a9d1a))

- Explain name origin (The Matrix Jump Program)
  ([`b2ce842`](https://github.com/andrader/jup/commit/b2ce84289f0dbb4db831b84cd28d498312d37bde))

- Improve documentation structure, fix api reference, and update zensical theme
  ([`19ca883`](https://github.com/andrader/jup/commit/19ca883baf328813ca916666035f089b92578ba3))

- Restore essential documentation files and fix nav
  ([`58b9e8a`](https://github.com/andrader/jup/commit/58b9e8acafb28858d961a9fcc953efaaf4a5f9c9))

- Trigger build
  ([`2bafe73`](https://github.com/andrader/jup/commit/2bafe73f13f8b77628544ef53195fbb96e13f6c9))


## v0.12.0-beta.1 (2026-04-17)


## v0.12.0 (2026-04-17)

### Chores

- Enable multi-branch release support
  ([`c4b4f4a`](https://github.com/andrader/jup/commit/c4b4f4ab3bca22467c2171af7ae9de767974c852))

- Setup beta/stable branch workflow and weekly release PR
  ([`ef9705b`](https://github.com/andrader/jup/commit/ef9705b343879cadfa7e7a6beb70fe075d1a56f0))

### Features

- Trigger beta release for multi-branch support
  ([`6ea8c3d`](https://github.com/andrader/jup/commit/6ea8c3d8fc782cc4849d943532928cd2675a332d))


## v0.11.0 (2026-04-17)

### Bug Fixes

- **list**: Detect and flag missing sources and broken symlinks
  ([`0b13f61`](https://github.com/andrader/jup/commit/0b13f61000d2e26877b3a79751502e69ef9ae456))

- **list**: Improve table readability for multi-line entries
  ([`0626fe8`](https://github.com/andrader/jup/commit/0626fe85c28bc8e0a293ed3d14cbcb77a8e56771))

- **list**: Restore location paths and symlink symbols in table output
  ([`7f6d7aa`](https://github.com/andrader/jup/commit/7f6d7aa0dee3fae74b34bb56cfedea7a32b5efcf))

- **sync**: Prevent self-deletion when source is in target agent dir
  ([`3839040`](https://github.com/andrader/jup/commit/3839040a8b1d0c5f4bdde31a790fedc412261a73))

### Chores

- Add beta release config and update roadmap
  ([`3a2cb05`](https://github.com/andrader/jup/commit/3a2cb052b2ed07a03c023d037bc13d11cfaa298d))

- Ignore .worktrees directory
  ([`c301f13`](https://github.com/andrader/jup/commit/c301f136f347638615df923cc7569a02707e605f))

- Setup mkdocs, update ty config, and fix QA diagnostics
  ([`fb1851f`](https://github.com/andrader/jup/commit/fb1851f03e9f9ce82668a7989860d650137ba778))

### Code Style

- **list**: Color entire location red when broken or missing
  ([`a42ef9a`](https://github.com/andrader/jup/commit/a42ef9adfd64d13d68faad8ab45cda991aa78225))

- **list**: Revert to clean table style without horizontal lines
  ([`20577cd`](https://github.com/andrader/jup/commit/20577cd8ecc8e1476d27dd481c0574882d879068))

- **list**: Simplify output by removing redundant installed icon
  ([`8b0b370`](https://github.com/andrader/jup/commit/8b0b370dc41c1ba76c78980b3f631426b1ef21e5))

- **list**: Use ⛓️‍💥 as the primary symbol for broken links
  ([`088b48d`](https://github.com/andrader/jup/commit/088b48dd83e8a953c56a30c409261864270fa042))

- **list**: Use ⛓️‍💥 for broken links
  ([`26cf650`](https://github.com/andrader/jup/commit/26cf650e1ab94cff3a90e7ee0ff7abd48f389d06))

### Documentation

- Update roadmap with completed tasks
  ([`02e2b60`](https://github.com/andrader/jup/commit/02e2b60218c54022214c250a6c3b637c11b2c4ee))

### Features

- Sync shortcuts, interactive sync, enhanced move, and new agent skills
  ([`d6b49f8`](https://github.com/andrader/jup/commit/d6b49f80bfc6f32a0277b9f944132d475726e7f4))

This includes jup up, jup sync -i, jup mv --rename/--to-remote, and the new architect/roadmap
  skills.

- **add**: Detect and handle unmanaged skills in agent directories
  ([`ce3763b`](https://github.com/andrader/jup/commit/ce3763b89161f613854bdde2f7f3038ff1a4303a))

- **list**: Add symbols legend to table output
  ([`65685d0`](https://github.com/andrader/jup/commit/65685d021ce43a84b8ea77182b4f5e10746b924b))

- **list**: Add symbols to differentiate local and remote sources
  ([`bd0c9e0`](https://github.com/andrader/jup/commit/bd0c9e015d8b86913d55956d367a000e996f61e7))

- **list**: Add usage tips and update backlog
  ([`9a51765`](https://github.com/andrader/jup/commit/9a51765619c7ae162d1c598be728c4ca535c7d1d))

- **list**: Move source gone symbol and rename locations column
  ([`a4f1e4c`](https://github.com/andrader/jup/commit/a4f1e4c91ace5f608eb00d2f8cd249a76b92a7c0))

- **list**: Refine status symbols and placement
  ([`3ac551f`](https://github.com/andrader/jup/commit/3ac551f2c98d76122f168fd61e0d22c5232016cd))

- **mv**: Add --no-move flag and implement local source moving
  ([`d9f3a92`](https://github.com/andrader/jup/commit/d9f3a92250ddee0b93fe1f72de489630c3173448))

- **mv**: Rename --no-move to --ref-only and update list tips
  ([`741bf5b`](https://github.com/andrader/jup/commit/741bf5be7781c7b1669488b5ee939c144de6f02e))


## v0.10.0 (2026-04-17)

### Chores

- Ignore docs/superpowers and update gitignore
  ([`65b9517`](https://github.com/andrader/jup/commit/65b9517dc3b2e5318cfec72893c51c2ec306dbff))

### Documentation

- Add jup skill definition
  ([`43aabb2`](https://github.com/andrader/jup/commit/43aabb27add52268a96d2306d8362e596a87f8cd))

- Create roadmap, architect skill, and update backlog
  ([`ffba2a9`](https://github.com/andrader/jup/commit/ffba2a9e178792b2a60d16fce668bb06d9938d05))

- Implement jup-roadmap and jup-architect skills with TDD process
  ([`217e718`](https://github.com/andrader/jup/commit/217e718d6a58d327b524d4dcd1085830e3ff63ab))

### Features

- Add jup ls and rm shortcuts, and jup mv command
  ([`96f0dc1`](https://github.com/andrader/jup/commit/96f0dc1da9497c2c0b0adc005b43f4160491ab88))

- Improve remote skill search logic
  ([`2762fab`](https://github.com/andrader/jup/commit/2762faba885e40195d8c69378ee4ac2b2fe311f1))

- **mv**: Support moving skills to arbitrary filesystem paths
  ([`0e71707`](https://github.com/andrader/jup/commit/0e717072e57050dc4b5aad8ccc56a42df50b9ddd))

### Refactoring

- Modularize commands into jup.commands package
  ([`1256963`](https://github.com/andrader/jup/commit/125696361fb8ba442cf71d38a985c411d859dcbe))

### Testing

- Update test mocks for modularized commands package
  ([`2681379`](https://github.com/andrader/jup/commit/268137945d7e3c508a26703decb1392e69e793d8))


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
