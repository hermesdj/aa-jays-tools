# AGENTS.md

## Scope and mental model
- This repository is a **single Alliance Auth plugin** (`aa-jays-tools`), not a full runnable AA instance.
- The plugin currently provides two feature areas: Discord cogs and Secure Groups smart filters (see `README.md`).
- Runtime wiring (enabled apps, Celery, services) is defined by the host AA instance (typically `working/myauth/` in this workspace), not by this repo itself.

## Where to look first
- Start with `README.md` for the feature intent.
- For extension entry points, read `jaystools/auth_hooks.py` first.
- For install-time optional dependency checks, read `jaystools/app_settings.py`.
- For business logic, read `jaystools/models/smart_filters.py` and `jaystools/cogs/me_recruter.py`.
- For admin exposure and model evolution, read `jaystools/admin.py` and `jaystools/migrations/`.

## Cross-project patterns you should preserve
- This plugin follows the AA app-config pattern with short label and versioned `verbose_name` in `jaystools/apps.py` (`JaysToolsConfig`, version from `jaystools.__version__`).
- Optional AA integrations are guarded with `apps.is_installed(...)` checks in `jaystools/app_settings.py`; keep imports/registrations conditional (see `jaystools/auth_hooks.py` and `jaystools/admin.py`).
- Hook registration is the main integration surface:
  - `@hooks.register('discord_cogs_hook')` returns the cog module path list.
  - `@hooks.register("secure_group_filters")` returns filter classes when `securegroups` is installed.
- Secure Groups filters share a small contract via `BaseFilter` in `jaystools/models/smart_filters.py`: implement both `process_filter(user)` and `audit_filter(users)`.
- This plugin currently has **no Celery tasks** (`tasks.py` absent); existing behavior is synchronous in model/filter logic and Discord cog handlers.

## Testing and developer workflow
- This repo currently does **not** ship `tox.ini`, `runtests.py`, or `testauth/`; validate behavior through host-instance integration (e.g., `working/myauth/`) and focused Django checks/migrations.
- Packaging/build metadata is in `pyproject.toml` and uses `flit_core` (`[build-system]` and `[tool.flit.module]`).
- Pre-commit is configured in `.pre-commit-config.yaml` (notably `pyupgrade`, `django-upgrade`, `isort`, `flake8`, `pyproject-fmt`, `validate-pyproject`). Keep edits compatible with these hooks.
- When changing models in `jaystools/models/smart_filters.py`, keep matching schema changes in `jaystools/migrations/`.

## Agent execution guardrails
- Never create a git commit unless the user explicitly asks for a commit in the current conversation turn.

## Plugin-specific guidance
When working in this plugin, prioritize these repo-specific constraints:
- Keep `securegroups` and `memberaudit` optional. Do not add unconditional imports from those apps in module top-level code.
- If you add a new Secure Groups smart filter, update all three places together:
  - model class in `jaystools/models/smart_filters.py`
  - conditional hook export in `jaystools/auth_hooks.py`
  - conditional admin registration in `jaystools/admin.py`
- If you add a new Discord cog, place it under `jaystools/cogs/` and expose it through `register_cogs()` in `jaystools/auth_hooks.py`.
- Discord command scoping is driven by `get_all_servers()` in `jaystools/app_settings.py` (`DISCORD_GUILD_IDS` and `DISCORD_GUILD_ID`). Preserve this fallback/merge behavior.

## Frontend / Bootstrap conventions
- This plugin currently ships no Django templates/static frontend assets; Bootstrap component conventions from other AA plugins generally do not apply here unless frontend files are introduced.

## Integrations and edge cases
- `RecruitmentFilter` depends on AA HR Applications data (`allianceauth.hrapplications.models.Application`) and evaluates reviewer approvals over a configurable time window.
- `CharacterSkillPointFilter` depends on `memberaudit.models.Character`; keep it behind `memberaudit_installed()` checks.
- The Discord cog in `jaystools/cogs/me_recruter.py` expects host settings like `RECRUIT_CHANNEL_ID` and `RECRUITER_GROUP_ID`; changes touching this flow should verify host settings compatibility.
- Some user-facing strings are localized (`gettext_lazy`), and some are French literals in the cog; preserve existing language intent unless a translation update is explicitly requested.

