# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflows (`.github/workflows/main.yml` and `.github/workflows/publish.yml`) adapted from `aa-fitting-mastery` for this plugin's tox/test/build flow.
- Expanded `README.md` with installation, configuration, optional integrations, and development workflow.
- Initial plugin `AGENTS.md` and local test scaffold (`tox.ini`, `runtests.py`, `testauth/`, `jaystools/tests/`).

### Changed
- Improved internal code documentation and lint compatibility across plugin modules.

## [1.0.2] - 2025-09-24

### Added
- New smart filter `CharacterSkillPointFilter` for low-skillpoint detection.
- Integration with `memberaudit` for character skillpoint-based filtering.
- `ignore_alts` support for `CharacterSkillPointFilter` to evaluate mains only.

### Changed
- Release update to version `1.0.2`.

## [1.0.1] - 2025-09-05

### Added
- Translation updates.
- New recruitment-oriented smart filter.

## [1.0.0] - 2025-09-03

### Added
- First public release of `aa-jays-tools`.
- Initial Python package metadata and project structure.
- Initial licensing setup.
