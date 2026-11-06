# lineage2-crow

## サイトの更新

ページの内容は `pages/` 内の Markdown ファイルを、サイトのレイアウトは `template.html` を編集してください。生成される `index.html` は直接編集しないでください。

## Cloudflare Pages の設定

Cloudflare Pages でこの GitHub リポジトリを接続し、次のように設定してください。

- **Root directory:** 空欄（リポジトリのルート）
- **Build command:** `pip install -r requirements.txt && python scripts/build.py`
- **Build output directory:** `dist`

`main` にプッシュすると Cloudflare Pages がビルドと公開を行います。`scripts/build.py` は `pages/` と `template.html` から `dist/index.html` を生成し、`assets/` と `sitemap.xml` も出力先へコピーします。生成物は Git にコミットしません。
