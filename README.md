# lineage2-crow

## ディレクトリ構成

```text
lineage2-crow/
├── pages/                  # ページ原稿 (Markdown)
│   ├── home.md
│   ├── coupon.md
│   ├── faq.md
│   ├── invasion.md
│   ├── boss.md
│   ├── dimmension_boss.md
│   ├── crowpass.md
│   └── accessories.md
├── scripts/
│   └── build.py            # 公開ファイルを生成するビルドスクリプト
├── assets/
│   └── crow-cat.png        # サイトで使用する画像
├── template.html           # 共通HTMLテンプレート
├── requirements.txt        # Python依存パッケージ
├── sitemap.xml             # サイトマップ
├── dist/                   # ビルド出力先 (Git管理対象外)
│   ├── index.html
│   ├── assets/
│   └── sitemap.xml
└── README.md
```

`dist/` はビルド時に生成されるため、最初は存在しない場合があります。

## サイトの更新

ページの内容は `pages/` 内の Markdown ファイルを、サイトのレイアウトは `template.html` を編集してください。画像などの静的ファイルは `assets/` に置きます。生成される `dist/index.html` は直接編集しないでください。

`scripts/build.py` は各 Markdown ファイルをテンプレートに組み込み、`dist/index.html` を生成します。また `assets/` と `sitemap.xml` を `dist/` にコピーします。生成物は `.gitignore` により Git 管理対象外です。

## Cloudflare Pages の設定

Cloudflare Pages でこの GitHub リポジトリを接続し、次のように設定してください。

- **Framework preset:** None
- **Root directory:** 空欄（リポジトリのルート）
- **Build command:** `pip install -r requirements.txt && python scripts/build.py`
- **Build output directory:** `dist`

`main` にプッシュすると Cloudflare Pages が自動でビルドと公開を行います。ビルド成果物を Git にコミットしないため、公開後に生成されたファイルを `git pull` する必要はありません。
