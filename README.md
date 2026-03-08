# AutoInfoResearch

はてなブックマーク (IT) と Hacker News から毎日人気記事を収集し、Markdown ファイルにまとめる CLI ツール。

## セットアップ

```bash
pip install -r requirements.txt
```

## ローカル実行

```bash
python src/main.py
# → output/YYYY-MM-DD.md が生成されます
```

## 出力形式

`output/YYYY-MM-DD.md` に以下の形式で出力されます。

- はてなブックマーク IT ホットエントリ 上位20件
- Hacker News トップストーリー スコア順 上位20件

## GitHub Actions

リポジトリを GitHub にプッシュすると、毎日 JST 10:00 (UTC 01:00) に自動実行されます。

Actions タブの `workflow_dispatch` から手動実行も可能です。
