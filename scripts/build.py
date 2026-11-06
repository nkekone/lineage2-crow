import shutil
from pathlib import Path

import markdown

ROOT_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT_DIR / 'pages'
TEMPLATE_FILE = ROOT_DIR / 'template.html'
OUTPUT_DIR = ROOT_DIR / 'dist'
OUTPUT_FILE = OUTPUT_DIR / 'index.html'
STATIC_DIRS = ['assets']
STATIC_FILES = ['sitemap.xml']

PAGE_ORDER = ['home', 'coupon', 'faq', 'invasion', 'boss', 'crowpass', 'accessories']

def build():
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    sections_html = []

    for page_id in PAGE_ORDER:
        file_path = PAGES_DIR / f'{page_id}.md'
        if not file_path.is_file():
            print(f"Warning: {file_path} not found!")
            continue

        content_md = file_path.read_text(encoding='utf-8')

        html_content = md.convert(content_md)
        md.reset()

        hidden_attr = ' hidden' if page_id != 'home' else ''
        section_code = f'<section id="page-{page_id}" class="page"{hidden_attr}>\n  <div class="content-card">\n    {html_content}\n  </div>\n</section>'
        sections_html.append(section_code)

    if not TEMPLATE_FILE.is_file():
        raise FileNotFoundError(f'{TEMPLATE_FILE} not found')
    template_html = TEMPLATE_FILE.read_text(encoding='utf-8')
    if '<!-- PAGE_CONTENT_PLACEHOLDER -->' not in template_html:
        raise ValueError(f'{TEMPLATE_FILE} is missing the page content placeholder')

    full_content = "\n\n".join(sections_html)
    final_html = template_html.replace('<!-- PAGE_CONTENT_PLACEHOLDER -->', full_content)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(final_html, encoding='utf-8')

    for static_dir in STATIC_DIRS:
        source = ROOT_DIR / static_dir
        if not source.is_dir():
            raise FileNotFoundError(f'{source} not found')
        shutil.copytree(source, OUTPUT_DIR / static_dir, dirs_exist_ok=True)

    for static_file in STATIC_FILES:
        source = ROOT_DIR / static_file
        if not source.is_file():
            raise FileNotFoundError(f'{source} not found')
        shutil.copy2(source, OUTPUT_DIR / static_file)

    print(f'{OUTPUT_FILE} の生成が正常に完了しました！')

if __name__ == '__main__':
    build()