# CHANGELOG


## v0.19.0 (2026-04-25)


## v0.19.0-beta.1 (2026-04-25)

### Features

- **cli**: Enhance jup list with categories, banner and better isolation
  ([`2daf122`](https://github.com/andrader/jup/commit/2daf122a77f66080669171d1e683b560e3d23d64))

- Surface git clone errors in jup add to prevent silent exits - Add Category column and jup banner
  to list output - Fix duplicated unmanaged skills by deduplicating harnesses by path - Add
  JUP_CONFIG_DIR environment variable support for isolated testing - Add automated screenshot
  generation script and just recipe - Update documentation screenshots


## v0.18.0 (2026-04-24)


## v0.18.0-beta.1 (2026-04-24)

### Features

- **cli**: Add move, update and harness aliases to help output
  ([`c1d3298`](https://github.com/andrader/jup/commit/c1d32988757b588aaa0778618bec442aa64e2b76))


## v0.17.0 (2026-04-24)


## v0.17.0-beta.1 (2026-04-24)

### Features

- **cli**: Show command aliases in help output
  ([`7253a06`](https://github.com/andrader/jup/commit/7253a066ff579bca44a8bd4ea8f2418a5cea22f1))


## v0.16.1 (2026-04-24)


## v0.16.1-beta.1 (2026-04-24)

### Bug Fixes

- **sync**: Improve path validation, deduplicate targets, and add verbose logging
  ([`4bdf49a`](https://github.com/andrader/jup/commit/4bdf49ad3203d404dd4fbd7f22b225577802a369))

### Documentation

- Regenerate changelog to consolidate beta entries into v0.16.0
  ([`e872fc9`](https://github.com/andrader/jup/commit/e872fc99c73658ba77dec0cadce0c52e5a121277))


## v0.16.0 (2026-04-23)

### Features

- Ensure minor bump to 0.16.0 for command decoupling release
  ([`61972bd`](https://github.com/andrader/jup/commit/61972bd109d20ac0963742f7331bb1b582461b28))


## v0.15.0 (2026-04-22)


## v0.15.0-beta.3 (2026-04-22)

### Bug Fixes

- Address security vulnerabilities, logical flaws, and performance bottlenecks
  ([`77aea70`](https://github.com/andrader/jup/commit/77aea70c1beab6eafe4c78f2437b791178e06bd0))

- Harden path validation, implement atomic writes and improve input normalization
  ([`0cb1ab6`](https://github.com/andrader/jup/commit/0cb1ab65201f2bf3abe9282329ff29e0eedda129))

- Harden repository arg parsing and address normalization edge cases
  ([`895e63f`](https://github.com/andrader/jup/commit/895e63f04bbaeff0a6e954b70176ecf7c64d50ae))

### Features

- Decouple CLI commands and extract shared state
  ([`1b82219`](https://github.com/andrader/jup/commit/1b82219462005ff473553e4fdf577107822abb49))


## v0.15.0-beta.2 (2026-04-22)

### Bug Fixes

- Update jup version in uv.lock
  ([`cb24268`](https://github.com/andrader/jup/commit/cb24268508f972767d2dc055bb8203b1b12c380c))


## v0.15.0-beta.1 (2026-04-22)

### Bug Fixes

- Bump main version to 0.15.0, enable beta tags, and fix back-sync logic
  ([`15fac1b`](https://github.com/andrader/jup/commit/15fac1b51266c7ddbbb0ffee50f599f1135b8bb8))


## v0.14.0-beta.2 (2026-04-22)

### Bug Fixes

- Add scope backward compatibility and improve list output robustness
  ([`64ef36d`](https://github.com/andrader/jup/commit/64ef36d3795e5a218bb9c9da1a82c61500add9db))

### Documentation

- Add lockfile specification and update backlog
  ([`4f92552`](https://github.com/andrader/jup/commit/4f92552071c1b4f04639d589f6d6747e8787d5d6))

- Finalize lockfile specification with limitations analysis
  ([`a2ecea5`](https://github.com/andrader/jup/commit/a2ecea58c36c71aee5ae36b2eac89abc80990103))

- Update documentation, skill and mandates for new features
  ([`01f00ab`](https://github.com/andrader/jup/commit/01f00abdbb214f93170569370e8db87451cd4ba7))

- Update project mandates and roadmap backlog
  ([`507c664`](https://github.com/andrader/jup/commit/507c6644e8032838ab4ba380b0e9535fa220a7f6))

### Features

- Add CLI aliases for list, add, remove and config commands
  ([`33c8734`](https://github.com/andrader/jup/commit/33c8734053189d1d46c6ee4150a148475f99d3d6))

- Add smart URL parsing, exact path resolution, target selection flags, versioning, and metadata
  injection
  ([`9d46c61`](https://github.com/andrader/jup/commit/9d46c6165231bf24f0474f5241d95dcb68b83647))

- Enhance list command to show version and source metadata
  ([`fb611e7`](https://github.com/andrader/jup/commit/fb611e79ea893240d4dd001d0d717d8cd8da098c))

- Rename global scope to user, add agent defaults and metadata fields
  ([`8f5294a`](https://github.com/andrader/jup/commit/8f5294a84056749ed8daea7cdd4502a5d7a3d3d7))


## v0.14.0 (2026-04-21)


## v0.14.0-beta.1 (2026-04-21)

### Features

- Differentiate global and local skills in jup list and improve config isolation
  ([`43d8bd0`](https://github.com/andrader/jup/commit/43d8bd0adfd171b5a066249ae8e0cf523bc6c526))


## v0.13.0-beta.3 (2026-04-20)


## v0.13.1 (2026-04-20)

### Bug Fixes

- Handle git clone failure gracefully when repo is not found
  ([`1ceb65a`](https://github.com/andrader/jup/commit/1ceb65a5ddfdb966f398d8453d705bee39ba9e0d))


## v0.13.0 (2026-04-20)


## v0.13.0-beta.2 (2026-04-20)

### Features

- Explicitly mention codex support in harness registry
  ([`b0f4d9b`](https://github.com/andrader/jup/commit/b0f4d9b8a659d13902f7542df1a1c24a593c2576))


## v0.13.0-beta.1 (2026-04-20)


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
