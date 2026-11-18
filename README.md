# git-recap

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

## Requirements

- Python >= 3.11
- `git`

## License

MIT
