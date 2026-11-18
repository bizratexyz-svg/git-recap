"""CLI for generating daily/weekly git standup recaps."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from git_recap import __version__

_FIELD_SEP = "\x1f"


@dataclass(frozen=True)
class Commit:
    """Represents a single git commit."""

    repo: str
    short_hash: str
    date_str: str
    author: str
    subject: str


def is_git_repo(path: Path) -> bool:
    """Return True if path is inside a git repository."""
    if not path.is_dir():
        return False
    res = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return res.returncode == 0 and res.stdout.strip() == "true"


def discover_repos(scan_dir: Path, max_depth: int = 3) -> list[Path]:
    """Find git repositories under scan_dir up to max_depth."""
    repos: list[Path] = []
    scan_dir = scan_dir.resolve()
    if not scan_dir.is_dir():
        return repos

    def _walk(current: Path, depth: int) -> None:
        if (current / ".git").exists():
            repos.append(current)
            return
        if depth >= max_depth:
            return
        try:
            children = sorted(current.iterdir())
        except PermissionError:
            return
        for child in children:
            if child.is_dir() and not child.name.startswith("."):
                _walk(child, depth + 1)

    _walk(scan_dir, 0)
    return repos


def collect_commits(repo_path: Path, days: int, author: str | None) -> list[Commit]:
    """Collect commits from a single git repository over the past N days."""
    since_date = (date.today() - timedelta(days=max(0, days - 1))).isoformat()
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "log",
        f"--since={since_date} 00:00:00",
        "--date=short",
        f"--pretty=format:%h{_FIELD_SEP}%ad{_FIELD_SEP}%an{_FIELD_SEP}%s",
    ]
    if author:
        cmd.append(f"--author={author}")

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return []

    repo_name = repo_path.resolve().name
    commits: list[Commit] = []
    for line in res.stdout.splitlines():
        parts = line.split(_FIELD_SEP, 3)
        if len(parts) != 4:
            continue
        short_hash, date_str, commit_author, subject = parts
        commits.append(
            Commit(
                repo=repo_name,
                short_hash=short_hash,
                date_str=date_str,
                author=commit_author,
                subject=subject,
            )
        )
    return commits


def render_activity_chart(commits: list[Commit], days: int, max_bar_width: int = 24) -> str:
    """Render an ASCII bar chart of commits per day."""
    today = date.today()
    day_list = [(today - timedelta(days=offset)).isoformat() for offset in range(days - 1, -1, -1)]
    counts = Counter(c.date_str for c in commits)
    peak = max((counts[d] for d in day_list), default=0)

    lines: list[str] = []
    for d in day_list:
        count = counts[d]
        if peak > 0 and count > 0:
            bar_len = max(1, round((count / peak) * max_bar_width))
            bar = "█" * bar_len
        else:
            bar = "·"
        lines.append(f"{d} | {bar:<{max_bar_width}} ({count})")
    return "\n".join(lines)


def format_recap(commits: list[Commit], days: int, fmt: str = "md") -> str:
    """Format commits grouped by repo and date, plus an ASCII activity chart."""
    chart = render_activity_chart(commits, days=days)
    total = len(commits)

    grouped: dict[str, dict[str, list[Commit]]] = defaultdict(lambda: defaultdict(list))
    for c in commits:
        grouped[c.repo][c.date_str].append(c)

    lines: list[str] = []
    if fmt == "md":
        lines.append(f"# Git Recap (Last {days} day{'s' if days != 1 else ''})")
        lines.append("")
        lines.append(f"**Total commits:** {total} across **{len(grouped)}** repositor{'y' if len(grouped) == 1 else 'ies'}")
        lines.append("")
        lines.append("## Activity")
        lines.append("")
        lines.append("```text")
        lines.append(chart)
        lines.append("```")

        if not commits:
            lines.append("")
            lines.append("_No commits found in the selected timeframe._")
            return "\n".join(lines)

        for repo in sorted(grouped):
            lines.append("")
            lines.append(f"## {repo}")
            for d in sorted(grouped[repo], reverse=True):
                lines.append("")
                lines.append(f"### {d}")
                for c in grouped[repo][d]:
                    lines.append(f"- `{c.short_hash}` {c.subject} _({c.author})_")
    else:
        lines.append(f"GIT RECAP (Last {days} day{'s' if days != 1 else ''})")
        lines.append("=" * 40)
        lines.append(f"Total commits: {total} across {len(grouped)} repo(s)")
        lines.append("")
        lines.append("Activity:")
        lines.append(chart)

        if not commits:
            lines.append("")
            lines.append("No commits found in the selected timeframe.")
            return "\n".join(lines)

        for repo in sorted(grouped):
            lines.append("")
            lines.append(f"[{repo}]")
            for d in sorted(grouped[repo], reverse=True):
                lines.append(f"  {d}")
                for c in grouped[repo][d]:
                    lines.append(f"    - {c.short_hash} {c.subject} ({c.author})")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="git-recap",
        description="Generate a daily/weekly standup recap from one or more local git repositories.",
    )
    parser.add_argument(
        "--dir",
        dest="dirs",
        action="append",
        help="Path to a git repository (can be specified multiple times; default: '.').",
    )
    parser.add_argument(
        "--scan",
        type=Path,
        metavar="PARENT_DIR",
        help="Scan PARENT_DIR recursively to discover local git repositories.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7).",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="Filter commits by author name or email.",
    )
    parser.add_argument(
        "--format",
        choices=("md", "text"),
        default="md",
        help="Output format: 'md' (Markdown) or 'text' (default: md).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for git-recap."""
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_paths: list[Path] = []
    if args.scan is not None:
        repo_paths.extend(discover_repos(args.scan))

    if args.dirs:
        for d in args.dirs:
            p = Path(d).resolve()
            if is_git_repo(p) and p not in repo_paths:
                repo_paths.append(p)
    elif args.scan is None:
        cwd = Path(".").resolve()
        if is_git_repo(cwd):
            repo_paths.append(cwd)

    if not repo_paths:
        print("No git repositories found.", file=sys.stderr)
        return 1

    all_commits: list[Commit] = []
    for repo in repo_paths:
        all_commits.extend(collect_commits(repo, days=max(1, args.days), author=args.author))

    print(format_recap(all_commits, days=max(1, args.days), fmt=args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
