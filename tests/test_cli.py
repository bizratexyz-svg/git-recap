"""Unit tests for git-recap CLI discovery, parsing, and formatting."""

from __future__ import annotations

import subprocess
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from git_recap.cli import (
    _FIELD_SEP,
    Commit,
    build_parser,
    collect_commits,
    discover_repos,
    format_recap,
    main,
    render_activity_chart,
)


def test_discover_repos_finds_nested_and_skips_hidden(tmp_path: Path) -> None:
    repo_a = tmp_path / "api"
    (repo_a / ".git").mkdir(parents=True)

    repo_b = tmp_path / "group" / "web"
    (repo_b / ".git").mkdir(parents=True)

    hidden_repo = tmp_path / ".hidden" / "secret"
    (hidden_repo / ".git").mkdir(parents=True)

    too_deep = tmp_path / "a" / "b" / "c" / "d"
    (too_deep / ".git").mkdir(parents=True)

    found = discover_repos(tmp_path, max_depth=3)
    assert found == [repo_a.resolve(), repo_b.resolve()]


def test_collect_commits_parses_git_log_output(tmp_path: Path) -> None:
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    stdout = "\n".join(
        [
            f"a1b2c3d{_FIELD_SEP}2026-01-15{_FIELD_SEP}Jane Doe{_FIELD_SEP}feat: add search",
            f"e4f5g6h{_FIELD_SEP}2026-01-14{_FIELD_SEP}Jane Doe{_FIELD_SEP}fix: handle empty query",
            "malformed-line-without-separators",
        ]
    )
    completed = subprocess.CompletedProcess(args=["git"], returncode=0, stdout=stdout, stderr="")
    with patch("git_recap.cli.subprocess.run", return_value=completed):
        commits = collect_commits(repo, days=7, author="Jane")

    assert commits == [
        Commit(
            repo="demo-repo",
            short_hash="a1b2c3d",
            date_str="2026-01-15",
            author="Jane Doe",
            subject="feat: add search",
        ),
        Commit(
            repo="demo-repo",
            short_hash="e4f5g6h",
            date_str="2026-01-14",
            author="Jane Doe",
            subject="fix: handle empty query",
        ),
    ]


def test_collect_commits_returns_empty_on_git_error(tmp_path: Path) -> None:
    completed = subprocess.CompletedProcess(args=["git"], returncode=128, stdout="", stderr="err")
    with patch("git_recap.cli.subprocess.run", return_value=completed):
        assert collect_commits(tmp_path, days=7, author=None) == []


def test_render_activity_chart_bars_and_empty() -> None:
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    commits = [
        Commit("app", "111", today, "Dev", "c1"),
        Commit("app", "222", today, "Dev", "c2"),
        Commit("app", "333", yesterday, "Dev", "c3"),
    ]
    chart = render_activity_chart(commits, days=3, max_bar_width=10)
    lines = chart.splitlines()
    assert len(lines) == 3
    assert "(0)" in lines[0] and "·" in lines[0]
    assert "(1)" in lines[1] and "█" in lines[1]
    assert "(2)" in lines[2] and "█" * 10 in lines[2]


def test_format_recap_markdown_and_text() -> None:
    today = date.today().isoformat()
    commits = [
        Commit("api", "abc1234", today, "Jane", "feat: add endpoint"),
        Commit("web", "def5678", today, "Jane", "chore: polish UI"),
    ]

    md = format_recap(commits, days=7, fmt="md")
    assert "# Git Recap (Last 7 days)" in md
    assert "**Total commits:** 2 across **2** repositories" in md
    assert "## api" in md and "## web" in md
    assert "- `abc1234` feat: add endpoint _(Jane)_" in md

    txt = format_recap(commits, days=1, fmt="text")
    assert "GIT RECAP (Last 1 day)" in txt
    assert "[api]" in txt and "[web]" in txt
    assert "- abc1234 feat: add endpoint (Jane)" in txt


def test_format_recap_empty() -> None:
    assert "_No commits found in the selected timeframe._" in format_recap([], days=7, fmt="md")
    assert "No commits found in the selected timeframe." in format_recap([], days=7, fmt="text")


def test_build_parser_and_main_no_repos(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(["--scan", str(tmp_path), "--days", "14", "--format", "text"])
    assert args.days == 14
    assert args.format == "text"

    rc = main(["--scan", str(tmp_path)])
    assert rc == 1
    assert "No git repositories found." in capsys.readouterr().err
