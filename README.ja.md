# git-recap

[English](README.md) | **日本語**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

1つ以上のローカル Git リポジトリから、日次・週次のスタンドアップ用サマリーと ASCII コミットアクティビティチャートを生成する CLI ツールです。

## 特徴

- **単一・複数リポジトリ対応**: `--dir` で1つ以上のリポジトリを指定できるほか、`--scan` で親ディレクトリ配下のリポジトリを自動検出できます。
- **スタンドアップ向け出力**: コミットをリポジトリ別・日付別に整理し、Markdown（`--format md`）またはプレーンテキスト（`--format text`）で出力します。
- **ASCII アクティビティチャート**: 指定期間内の日別コミット数を視覚的に表示します。
- **柔軟なフィルタリング**: 対象期間（`--days 7`）や作成者（`--author`）で絞り込み可能です。

## インストール

```bash
uv tool install .
```

または、`uv` で直接実行することもできます：

```bash
uv run git-recap
```

## 使い方

```bash
# 現在のリポジトリの直近7日間を集計
git-recap

# 特定の作成者の直近14日間を集計
git-recap --days 14 --author "Jane"

# 親ディレクトリ配下の全 Git リポジトリをスキャンし、プレーンテキストで出力
git-recap --scan ~/projects --days 7 --format text

# 複数のリポジトリを指定して集計
git-recap --dir ~/projects/api --dir ~/projects/web
```

## 出力例

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

## 動作要件

- Python >= 3.11
- `git`

## ライセンス

MIT
