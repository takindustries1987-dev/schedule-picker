# Claude Code 仙人テンプレート

AI仙人の教えを組み込んだ Claude Code プロジェクトテンプレート。

[logimania/clade_code_project](https://github.com/logimania/clade_code_project) をベースに、AI仙人の壁打ち哲学・行動原則・エラー学習サイクルをマージ。

## 特徴

- **セッション継続性** — `CLAUDE_PROGRESS.md` で前回の状態を確実に復元
- **エラー学習サイクル** — `CLAUDE_ISSUE.md` で失敗を構造化蓄積。同じ失敗を繰り返さない
- **即実行・忖度排除** — 確認するな、褒めるな、手順を説明するな。結果だけ報告
- **壁打ちモード** — コーディング以外の相談時も構造化された対話（売り方/作り方/時間 → ToDoで終わる）
- **抽象化蓄積** — 成功/失敗を法則化してMDに保存。再利用可能な資産に変える

## 使い方

```bash
# 新しいプロジェクトにコピー
gh repo create my-project --clone
cp -r claude-sennin-template/{CLAUDE.md,CLAUDE_PROGRESS.md,CLAUDE_ISSUE.md,.claude} my-project/
cd my-project && claude
```

## ファイル構成

```
.
├── CLAUDE.md              # 北極星（200行以内）
├── CLAUDE_PROGRESS.md     # セッション継続用の進捗ログ
├── CLAUDE_ISSUE.md        # エラー学習ログ
├── .claude/
│   └── rules/
│       ├── context-management.md  # コンテキスト管理詳細
│       └── security.md           # セキュリティルール
└── docs/                  # プロジェクト固有ドキュメント置き場
```

## 根本原則（仙人の教え）

| 原則 | 内容 |
|------|------|
| 量 > 質 | 雑でいい。完璧を目指すな。動くものを出せ |
| 即実行 | やれることは黙ってやれ。結果だけ報告 |
| 部品を先に作れ | 最小単位で作って組み合わせろ |
| 中断するな | 止まる場合は CLAUDE_PROGRESS.md を更新してから |
| 抽象化して蓄積 | 同じ失敗を二度繰り返すな |
| 忖度するな | 問題があれば指摘しろ |

## クレジット

- [AI仙人](https://x.com/logimania) — 壁打ち哲学・指示パターン
- [logimania/clade_code_project](https://github.com/logimania/clade_code_project) — ベーステンプレート
