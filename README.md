# Jay's Army Tools for Alliance Auth

`aa-jays-tools` is an [Alliance Auth](https://allianceauth.readthedocs.io/) plugin that currently provides:

- Discord recruiter helper commands (via `allianceauth-discordbot` cogs)
- Secure Groups smart filters for recruitment activity and low skill points

[![release](https://img.shields.io/pypi/v/aa-jays-tools?label=release)](https://pypi.org/project/aa-jays-tools/)
[![python](https://img.shields.io/pypi/pyversions/aa-jays-tools)](https://pypi.org/project/aa-jays-tools/)
[![django](https://img.shields.io/pypi/djversions/aa-jays-tools?label=django)](https://pypi.org/project/aa-jays-tools/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Smart filters](#smart-filters)
- [Discord recruiter cog](#discord-recruiter-cog)
- [Development](#development)
- [Changelog](#changelog)

## Overview

This plugin extends Alliance Auth with small operational tools used by Jay's Army workflows.
It integrates through Alliance Auth hooks in `jaystools/auth_hooks.py` and keeps optional integrations guarded by install checks.

## Features

- Registers a Discord cog (`jaystools.cogs.me_recruter`) through the `discord_cogs_hook`
- Registers Secure Groups smart filters through `secure_group_filters` when `securegroups` is installed
- Provides a `RecruitmentFilter` based on approved HR applications in a configurable time window
- Provides a `CharacterSkillPointFilter` (when `memberaudit` is installed) to match users below a skillpoint threshold

## Requirements

- Alliance Auth 4.x
- `allianceauth-discordbot` (optional, required for Discord cog usage)
- `allianceauth-secure-groups` (optional, required for smart filters)
- `aa-memberaudit` (optional, required for `CharacterSkillPointFilter`)

## Installation

### 1 - Install the package

```bash
pip install aa-jays-tools
```

### 2 - Add app to Alliance Auth

Add `jaystools` to `INSTALLED_APPS` in your `local.py`:

```python
INSTALLED_APPS += [
    "jaystools",
]
```

### 3 - Run migrations and collect static files

```bash
python manage.py migrate
python manage.py collectstatic
```

### 4 - Restart services

Restart web and worker processes so hooks and app registration are loaded.

## Configuration

### Required settings for Discord recruiter cog

If you use the recruiter cog, define these settings in your host AA `local.py`:

```python
# Command scope (single guild or list)
DISCORD_GUILD_ID = "1234567890"
# DISCORD_GUILD_IDS = [1234567890, 9876543210]

# Recruiter workflow channels/roles
RECRUIT_CHANNEL_ID = 123456789012345678
RECRUITER_GROUP_ID = 987654321098765432
```

`jaystools.app_settings.get_all_servers()` merges `DISCORD_GUILD_IDS` and `DISCORD_GUILD_ID` for command registration.

### Optional integration behavior

- If `securegroups` is not installed, no smart filter hook is exported.
- If `memberaudit` is not installed, `CharacterSkillPointFilter` is not exported.

## Smart filters

### RecruitmentFilter

Model: `jaystools.models.smart_filters.RecruitmentFilter`

Checks whether a user approved at least `recruitments_needed` HR applications within the last `days`.

### CharacterSkillPointFilter

Model: `jaystools.models.smart_filters.CharacterSkillPointFilter`

Available only with `memberaudit` installed. Matches users with at least one character at or below `sp_threshold`.
Can optionally ignore alts (`ignore_alts=True`) and evaluate mains only.

## Discord recruiter cog

Cog module: `jaystools.cogs.me_recruter`

Registered commands include:

- slash command: `me_recruter`
- message context command: `Créer un fil de recrutement`
- user context command: `Me Recruter`

Each command creates a private recruitment thread in `RECRUIT_CHANNEL_ID` and pings `RECRUITER_GROUP_ID`.

## Development

This repository includes a standard Alliance Auth plugin test layout:

- `tox.ini`
- `runtests.py`
- `testauth/`
- `jaystools/tests/`

Run tests:

```powershell
python -u runtests.py jaystools.tests -v 2
```

Run lint:

```powershell
pylint jaystools
```

If `tox` is installed:

```powershell
tox -e py312-django42
tox -e pylint
```

## Changelog

See `CHANGELOG.md`.
