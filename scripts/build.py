name: Build and Commit index.html

on:
  push:
    branches:
      - main
    paths:
      - 'pages/**'
      - 'template.html'
      - 'scripts/build.py'
      - '.github/workflows/deploy.yml'

jobs:
  build-and-commit:
    runs-on: ubuntu-latest
    permissions:
      contents: write # リポジトリへの自動書き込み権限を許可

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Run build script
        run: python scripts/build.py

      - name: Commit and push generated index.html
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add index.html
          # 変更がある場合のみコミットしてプッシュ
          git diff --quiet && git diff --staged --quiet || (git commit -m "auto: Build index.html from markdown update" && git push)