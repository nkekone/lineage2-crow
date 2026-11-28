# lineage2-crow

## ディレクトリ構成

```text
lineage2-crow/
├── data/
│   ├── coupons.yaml        # クーポン情報と報酬
│   ├── items.yaml          # アイテムの説明
│   ├── schedules.yaml      # イベント・アイテム販売の期間
│   └── accessories.yaml    # レアアクセサリーの構造化データ
├── pages/                  # ページ原稿 (Markdown)
│   ├── home.md
│   ├── schedule.md         # イベント・販売スケジュール
│   ├── coupon.md
│   ├── faq.md               # Q&A本文 (質問は見出し、回答はMarkdown)
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

ページの本文は `pages/` 内の Markdown ファイルを、クーポン情報は `data/coupons.yaml` を、アイテムの説明は `data/items.yaml` を、レアアクセサリーの一覧データは `data/accessories.yaml` を、サイトのレイアウトは `template.html` を編集してください。画像などの静的ファイルは `assets/` に置きます。生成される `dist/index.html` は直接編集しないでください。

`scripts/build.py` は各 Markdown ファイル、`data/coupons.yaml`、`data/items.yaml`、`data/schedules.yaml`、`data/accessories.yaml` をテンプレートに組み込み、`dist/index.html` を生成します。また `assets/` と `sitemap.xml` を `dist/` にコピーします。生成物は `.gitignore` により Git 管理対象外です。

イベントとアイテム販売の期間は [data/schedules.yaml](data/schedules.yaml) の `schedules` に登録します。各項目に分類の `category`（`event` または `sale`）、`name`、`start`、`end` を設定してください。予定は開始日時順に並び、端末の現在日時を基準に過去7日から14日先までの日単位タイムラインに表示されます。イベントと販売は色で区別します。日時は日本時間で、日付のみ（`YYYY-MM-DD`）または時刻を含む ISO 8601 形式（`YYYY-MM-DDTHH:MM:SS+09:00`）を指定できます。日付のみの終了日は、その日の終わりまでとして扱います。予定がない場合は `schedules: []` にします。

```yaml
schedules:
  - category: event
    name: "イベント名"
    start: "2026-12-01"
    end: "2026-12-08"
  - category: sale
    name: "販売アイテム名"
    start: "2026-12-01T09:00:00+09:00"
    end: "2026-12-08T06:00:00+09:00"
```

終了日時は開始日時より後にしてください。

クーポンを追加・更新する場合は、[data/coupons.yaml](data/coupons.yaml) を編集してください。`name` と `items` を設定し、`code` と `target` は必要な場合だけ記載します。コードを省略すると「クーポンボックスで配布」と表示されます。有効期限は表示用の `expiration.display` と期限判定用の `expiration.at` を設定し、期限情報自体がない場合は `expiration` を省略します。報酬アイテムの `name`、`quantity`、`deletion_date` は未設定の項目が空欄で表示されます。

報酬アイテムの説明を表示する場合は、[data/items.yaml](data/items.yaml) にアイテム名と説明を追加してください。説明が登録されたアイテム名は、マウスオーバー、キーボードフォーカス、タップで説明を確認できます。`(期間限定)`、`(期間制)`、`[刻印]` の表記は説明を照合するときだけ無視し、クーポン表には元のアイテム名をそのまま表示します。

レアアクセサリーを追加・更新する場合は、[data/accessories.yaml](data/accessories.yaml) の `id`、`name`、`category`、`stats` を編集してください。強化値に表示する数値がない場合は、対応するキーを省略します。

## Cloudflare Pages の設定

Cloudflare Pages でこの GitHub リポジトリを接続し、次のように設定してください。

- **Framework preset:** None
- **Root directory:** 空欄（リポジトリのルート）
- **Build command:** `pip install -r requirements.txt && python scripts/build.py`
- **Build output directory:** `dist`

`main` にプッシュすると Cloudflare Pages が自動でビルドと公開を行います。ビルド成果物を Git にコミットしないため、公開後に生成されたファイルを `git pull` する必要はありません。
