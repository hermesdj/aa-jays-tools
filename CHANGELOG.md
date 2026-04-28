# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.4] - 2026-04-28

### Added
- New smart filter `FittingInHangarFilter` to validate if a user owns a matching ship fit in their hangar via `fittings` + `memberaudit`.
- New smart filter `CharacterCloneImplantsFilter` to validate jump clone implants from `memberaudit` data with `require_all` / `any` behavior.
- Admin UI for clone implant selection now uses a dual-list multiselect (`FilteredSelectMultiple`) populated from `EveType` records.

### Changed
- Excluded the `Booster` group from clone-implant admin choices, so only implant items are selectable.
- Smart filter registration now conditionally exposes fitting/clone implant filters based on installed dependencies.
- Release update to version `1.0.4`.

### Validated
- `DJANGO_SETTINGS_MODULE=testauth.settings_aa4.local python -u runtests.py jaystools -v 2` (**59 passed**).
- `DJANGO_SETTINGS_MODULE=testauth.settings_aa4.local pylint --load-plugins pylint_django jaystools` (**10.00/10**).
- `python -m build` generated `aa_jays_tools-1.0.4.tar.gz` and `aa_jays_tools-1.0.4-py3-none-any.whl`.

## [1.0.3] - 2026-04-27

### Added
- GitHub Actions workflows (`.github/workflows/main.yml` and `.github/workflows/publish.yml`) adapted from `aa-fitting-mastery` for this plugin's tox/test/build flow.
- Expanded `README.md` with installation, configuration, optional integrations, and development workflow.
- Initial plugin `AGENTS.md` and local test scaffold (`tox.ini`, `runtests.py`, `testauth/`, `jaystools/tests/`).

### Changed
- Improved internal code documentation and lint compatibility across plugin modules.
- Tox environments now install `django-eveuniverse` so `testauth.settings_aa4.local` resolves consistently in tests and pylint.
- Added explicit runtime dependency on `humanize`, which is required by `CharacterSkillPointFilter`.
- Release update to version `1.0.3`.

### Validated
- `DJANGO_SETTINGS_MODULE=testauth.settings_aa4.local python -u runtests.py jaystools -v 2` (**33 passed**).
- `DJANGO_SETTINGS_MODULE=testauth.settings_aa4.local pylint --load-plugins pylint_django jaystools` (**10.00/10**).
- `tox -e py312-django42` (**33 passed**, `coverage report` total **91%**).
- `tox -e pylint` (**10.00/10**).
- `python -m build` generated `aa_jays_tools-1.0.3.tar.gz` and `aa_jays_tools-1.0.3-py3-none-any.whl`.

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
