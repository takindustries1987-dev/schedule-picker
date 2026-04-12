# index.html - スケジュールピッカー

## 概要
Googleカレンダーの予定を表示し、空き時間をタップして候補日を選択・コピーできるWebアプリ。

## 主要関数

### buildEvMap(evs)
- 入力: Google Calendar APIから取得したイベント配列
- 出力: `evMap`（スロット判定用）と `evBlocks`（描画用）を更新
- 説明: 終日予定（`ev.start.date`）と時間指定予定（`ev.start.dateTime`）の両方を処理。終日予定は表示時間帯全体をブロックする。

### renderGrid()
- 入力: なし（グローバル状態 `weekStart`, `evMap`, `evBlocks`, `blocks` を参照）
- 出力: `#cal-grid` のDOM を再描画
- 説明: 既存予定は `evBlocks` を使って実際の時間幅で1枠表示。先頭スロットにタイトルとバーを描画し、後続スロットは空のblocked扱い。

### tapSlot(dateStr, mins)
- 入力: 日付文字列（YYYY-MM-DD）、分（0〜）
- 出力: `blocks` 配列を更新し再描画
- 説明: タップごとに30分スロットをトグル。選択時は隣接ブロックと自動マージ。解除時はブロックを分割して該当スロットのみ除去。

### blockLabel(b)
- 入力: ブロックオブジェクト `{ date, start, end }`
- 出力: `"4/3(木)10:00~11:30"` 形式の文字列
