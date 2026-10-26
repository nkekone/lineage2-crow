import os
import re
import markdown

PAGES_DIR = 'pages'
TEMPLATE_FILE = 'template.html'
OUTPUT_FILE = 'index.html'

PAGE_ORDER = ['home', 'coupon', 'faq', 'invasion', 'boss', 'crowpass']

def build():
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    sections_html = []

    for page_id in PAGE_ORDER:
        file_path = os.path.join(PAGES_DIR, f"{page_id}.md")
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content_md = f.read()

        html_content = md.convert(content_md)
        md.reset()

        hidden_attr = ' hidden' if page_id != 'home' else ''
        section_code = f"""<section id="page-{page_id}" class="page"{hidden_attr}>
  <div class="content-card">
    {html_content}
  </div>
</section>"""
        sections_html.append(section_code)

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_html = f.read()

    full_content = "\n\n".join(sections_html)
    final_html = template_html.replace('<!-- PAGE_CONTENT_PLACEHOLDER -->', full_content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("index.html の生成が正常に完了しました！")

if __name__ == '__main__':
    build()
