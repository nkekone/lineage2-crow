import shutil
from html import escape
from pathlib import Path

import markdown
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT_DIR / 'pages'
TEMPLATE_FILE = ROOT_DIR / 'template.html'
OUTPUT_DIR = ROOT_DIR / 'dist'
OUTPUT_FILE = OUTPUT_DIR / 'index.html'
STATIC_DIRS = ['assets']
STATIC_FILES = ['sitemap.xml']
DATA_DIR = ROOT_DIR / 'data'

PAGE_ORDER = [
    'home', 
    'coupon', 
    'faq', 
    'invasion', 
    'boss', 
    'dimension_boss',
    'crowpass', 
    'accessories'
    ]

ENCHANTMENT_LABELS = [f'+{level}' for level in range(7)]
CATEGORY_LABELS = {
    'ring': ('💍 リング', 'badge-ring'),
    'earring': ('🦻 イヤリング', 'badge-earring'),
    'necklace': ('📿 ネックレス', 'badge-necklace'),
}

def render_accessories():
    yaml_file = DATA_DIR / 'accessories.yaml'
    if not yaml_file.is_file():
        raise FileNotFoundError(f'{yaml_file} not found')

    with yaml_file.open('r', encoding='utf-8') as file:
        accessories = yaml.safe_load(file) or []

    counts = {
        'all': len(accessories),
        'ring': sum(item['category'] == 'ring' for item in accessories),
        'earring': sum(item['category'] == 'earring' for item in accessories),
        'necklace': sum(item['category'] == 'necklace' for item in accessories),
    }

    parts = ['<div class="accessory-nav">']
    filters = [
        ('all', f'すべて ({counts["all"]})'),
        ('ring', f'💍 リング ({counts["ring"]})'),
        ('earring', f'🦻 イヤリング ({counts["earring"]})'),
        ('necklace', f'📿 ネックレス ({counts["necklace"]})'),
    ]
    for index, (category, label) in enumerate(filters):
        active = ' is-active' if index == 0 else ''
        parts.append(
            f'<button type="button" class="filter-btn{active}" '
            f'data-filter="{category}">{escape(label)}</button>'
        )
    parts.append('</div>')

    parts.append('<div class="accessory-quick-jump">')
    parts.append('<span class="quick-jump-label">目次ジャンプ:</span>')
    for accessory in accessories:
        accessory_id = escape(str(accessory['id']), quote=True)
        name = escape(str(accessory['name']))
        parts.append(
            f'<a href="#{accessory_id}" class="quick-jump-chip">{name}</a>'
        )
    parts.append('</div>')

    for accessory in accessories:
        accessory_id = escape(str(accessory['id']), quote=True)
        name = escape(str(accessory['name']))
        category = accessory['category']
        badge_label, badge_class = CATEGORY_LABELS[category]

        parts.append(
            f'<div id="{accessory_id}" class="accessory-item-card" '
            f'data-category="{category}">'
        )
        parts.append('<div class="accessory-header">')
        parts.append(f'<h2 class="accessory-name">{name}</h2>')
        parts.append(
            f'<span class="accessory-badge {badge_class}">'
            f'{escape(badge_label)}</span>'
        )
        parts.append('</div>')
        parts.append('<div class="table-responsive">')
        parts.append('<table class="accessory-table">')
        parts.append('<thead><tr>')
        parts.append('<th class="col-name">項目</th>')
        for enchantment in ENCHANTMENT_LABELS:
            parts.append(
                f'<th class="col-enchant">{escape(enchantment)}</th>'
            )
        parts.append('</tr></thead><tbody>')

        for stat in accessory['stats']:
            stat_name = escape(str(stat['name']))
            is_special_effect = stat['name'] == '特殊効果'
            values = stat.get('values') or {}
            parts.append('<tr>')
            parts.append(f'<td class="cell-name">{stat_name}</td>')
            for enchantment in ENCHANTMENT_LABELS:
                value = values.get(enchantment)
                if value is None:
                    parts.append('<td class="cell-empty">-</td>')
                else:
                    safe_value = escape(str(value))
                    if is_special_effect:
                        safe_value = (
                            f'<span class="special-effect-text">'
                            f'{safe_value}</span>'
                        )
                    parts.append(
                        f'<td class="cell-val">{safe_value}</td>'
                    )
            parts.append('</tr>')

        parts.append('</tbody></table>')
        parts.append('</div>')
        parts.append('</div>')

    return '\n'.join(parts)


def render_coupons():
    yaml_file = DATA_DIR / 'coupons.yaml'
    if not yaml_file.is_file():
        raise FileNotFoundError(f'{yaml_file} not found')

    with yaml_file.open('r', encoding='utf-8') as file:
        coupons = yaml.safe_load(file) or []

    parts = []
    for coupon in coupons:
        coupon_id = escape(str(coupon['id']), quote=True)
        name = escape(str(coupon['name']))
        parts.append(f'<article id="{coupon_id}" class="coupon-item">')
        parts.append(f'<h2>{name}</h2>')

        code = coupon.get('code')
        if code:
            code_id = escape(f'{coupon_id}-code', quote=True)
            safe_code = escape(str(code), quote=True)
            parts.append('<div class="coupon-code-card">')
            parts.append('<div class="coupon-code-row">')
            parts.append(
                f'<input class="coupon-code-value" id="{code_id}" '
                f'type="text" value="{safe_code}" readonly '
                f'aria-label="{name} クーポンコード">'
            )
            parts.append(
                f'<button class="coupon-copy-button" type="button" '
                f'data-copy-target="{code_id}" '
                f'aria-label="{name} クーポンコードをコピー">'
                '<svg viewBox="0 0 24 24" aria-hidden="true" '
                'focusable="false">'
                '<rect x="8" y="8" width="13" height="13" rx="2"></rect>'
                '<path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 '
                '0 0 0 2 2h3"></path></svg></button>'
            )
            parts.append('</div>')
            parts.append(
                '<p class="coupon-copy-status" role="status" '
                'aria-live="polite"></p>'
            )
            parts.append('</div>')
        else:
            parts.append(
                '<p class="coupon-delivery-note">クーポンボックスで配布</p>'
            )

        expiration = coupon.get('expiration') or {}
        expiration_text = expiration.get('display')
        if expiration_text:
            expiration_at = expiration.get('at')
            data_expires_at = (
                f' data-expires-at="{escape(str(expiration_at), quote=True)}"'
                if expiration_at else ''
            )
            parts.append(
                '<p><span class="coupon-expiration"'
                f'{data_expires_at}><strong>有効期限:</strong> '
                f'{escape(str(expiration_text))}</span></p>'
            )

        targets = coupon.get('target') or []
        if targets:
            parts.append(
                '<div class="coupon-target"><strong>配布対象:</strong><ul>'
            )
            for target in targets:
                parts.append(f'<li>{escape(str(target))}</li>')
            parts.append('</ul></div>')

        parts.append('<div class="coupon-reward-table-wrap">')
        parts.append('<table class="coupon-reward-table">')
        parts.append(
            '<thead><tr><th>アイテム名</th><th>個数</th>'
            '<th>説明</th><th>削除日</th></tr></thead><tbody>'
        )
        for item in coupon.get('items') or []:
            parts.append('<tr>')
            for key in ('name', 'quantity', 'description', 'deletion_date'):
                parts.append(f'<td>{escape(str(item.get(key) or ""))}</td>')
            parts.append('</tr>')
        parts.append('</tbody></table></div></article>')

    return '\n'.join(parts)


def build():
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br', 'attr_list'])

    sections_html = []

    for page_id in PAGE_ORDER:
        file_path = PAGES_DIR / f'{page_id}.md'
        if not file_path.is_file():
            print(f"Warning: {file_path} not found!")
            continue

        content_md = file_path.read_text(encoding='utf-8')

        html_content = md.convert(content_md)
        md.reset()

        if page_id == 'coupon':
            html_content = f'{html_content}\n{render_coupons()}'
        elif page_id == 'accessories':
            html_content = f'{html_content}\n{render_accessories()}'

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