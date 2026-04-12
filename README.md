# AI仙人テンプレート

最小構成のプロダクト用テンプレートです。

## 含めているもの

- `src`: 実装本体
- `docs`: `src` に対応する説明
- `config`: 設定まわり
- `scripts`: 実行補助
- `e2e`: E2Eの骨組み
- `02_claude`: AI作業用の出力先
- `old`: 廃止ファイルの退避先

## 使い方

1. `.env.example` を見て必要な環境変数を追加する
2. `src` にコードを書く
3. 対応する `docs` を更新する
4. 必要なら `e2e` にテストを追加する
5. 設計や使い方が変わったらこの `README.md` を更新する

## 初期ファイル

- [`src/main.py`](/Users/takumiyoshikawa/Desktop/Tools/AI仙人テンプレート/src/main.py)
- [`docs/main.md`](/Users/takumiyoshikawa/Desktop/Tools/AI仙人テンプレート/docs/main.md)
- [`e2e/e2e_test_runner.py`](/Users/takumiyoshikawa/Desktop/Tools/AI仙人テンプレート/e2e/e2e_test_runner.py)

