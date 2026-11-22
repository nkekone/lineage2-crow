# lineage2-crow

## ディレクトリ構成

```text
lineage2-crow/
├── data/
│   └── accessories.yaml    # レアアクセサリーの構造化データ
├── pages/                  # ページ原稿 (Markdown)
│   ├── home.md
│   ├── coupon.md
│   ├── faq.md
│   ├── invasion.md
│   ├── boss.md
│   ├── dimmension_boss.md
│   ├── crowpass.md
│   └── accessories.md      # 説明文のみ。アクセサリー一覧は data/ で管理
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

ページの本文は `pages/` 内の Markdown ファイルを、レアアクセサリーの一覧データは `data/accessories.yaml` を、サイトのレイアウトは `template.html` を編集してください。画像などの静的ファイルは `assets/` に置きます。生成される `dist/index.html` は直接編集しないでください。

`scripts/build.py` は各 Markdown ファイルと `data/accessories.yaml` をテンプレートに組み込み、`dist/index.html` を生成します。また `assets/` と `sitemap.xml` を `dist/` にコピーします。生成物は `.gitignore` により Git 管理対象外です。

レアアクセサリーを追加・更新する場合は、[data/accessories.yaml](data/accessories.yaml) の `id`、`name`、`category`、`stats` を編集してください。強化値に表示する数値がない場合は、対応するキーを省略します。

## Cloudflare Pages の設定

Cloudflare Pages でこの GitHub リポジトリを接続し、次のように設定してください。

- **Framework preset:** None
- **Root directory:** 空欄（リポジトリのルート）
- **Build command:** `pip install -r requirements.txt && python scripts/build.py`
- **Build output directory:** `dist`

`main` にプッシュすると Cloudflare Pages が自動でビルドと公開を行います。ビルド成果物を Git にコミットしないため、公開後に生成されたファイルを `git pull` する必要はありません。
