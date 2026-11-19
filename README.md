# git-recap

**English** | [日本語](README.ja.md)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Generate clean daily/weekly standup recaps and ASCII commit activity charts from one or more local git repositories.

## Features

- **Single or Multi-Repo**: Point at one or more repositories with `--dir`, or auto-discover repositories under a parent folder with `--scan`.
- **Standup-Ready Output**: Groups commits by repository and date in Markdown (`--format md`) or plain text (`--format text`).
- **ASCII Activity Chart**: Visualizes daily commit volume over the selected window.
- **Flexible Filtering**: Filter by timeframe (`--days 7`) and author (`--author`).

## Installation

```bash
uv tool install .
```

Or run directly with `uv`:

```bash
uv run git-recap
```

## Usage

```bash
# Recap the current repository for the last 7 days
git-recap

# Recap the last 14 days for a specific author
git-recap --days 14 --author "Jane"

# Scan a parent directory for all git repos and output plain text
git-recap --scan ~/projects --days 7 --format text

# Combine specific repositories
git-recap --dir ~/projects/api --dir ~/projects/web
```

## Example Output

```markdown
# Git Recap (Last 3 days)

**Total commits:** 4 across **2** repositories

## Activity

```text
2026-01-13 | ·                        (0)
2026-01-14 | ████████████             (1)
2026-01-15 | ████████████████████████ (3)
```

## api

### 2026-01-15
- `a1b2c3d` feat: add rate limiting middleware _(Jane Doe)_
- `f9e8d7c` test: cover token bucket edge cases _(Jane Doe)_

## web

### 2026-01-15
- `b2c3d4e` feat: render standup preview card _(Jane Doe)_

### 2026-01-14
- `e4f5g6h` fix: handle empty date range _(Jane Doe)_
```

## Requirements

- Python >= 3.11
- `git`

## License

MIT
