#!/usr/bin/env python3
"""
فهرس نصي ثابت لكل منتجات القسم في صفحة القسم نفسها.

المشكلة: صفحات الأقسام تعرض المنتجات عبر JavaScript من products.json، والروابط
الثابتة في HTML تغطي جزءاً قديماً فقط، فتبقى منتجات كثيرة بلا رابط داخلي ثابت.
الحل: قائمة روابط نصية خفيفة (بلا صور) لكل منتجات القسم، بين العلامتين
ALL_PRODUCTS:START / ALL_PRODUCTS:END قبل </main> مباشرة.

قواعد ثابتة (حماية الترتيب):
- لا يغيّر العنوان أو الوصف أو H1 أو النص أو الـSchema الموجود في الصفحة.
- إضافة فقط في آخر المحتوى؛ إعادة التشغيل تستبدل القسم القديم (لا تكرار).

شغّله بعد أي إضافة/حذف/تعديل اسم منتج:
    python3 scripts/category-index.py          (يعدّل)
    python3 scripts/category-index.py --check  (يفشل إن وُجدت صفحة غير محدّثة)
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# القسم في products.json -> (صفحة القسم، اسم القسم في العنوان)
PAGES = {
    'sajjad': ('sajjad.html', 'السجاد والموكيت'),
    'majalis': ('majalis.html', 'المجالس والمساند'),
    'athath': ('athath.html', 'الأثاث والكنب'),
    'sataer': ('sataer.html', 'الستائر'),
    'diwaniyat': ('tafseel-diwaniyat.html', 'الديوانيات'),
    'parquet': ('parquet-kuwait.html', 'الباركيه'),
    'theel': ('theel-sinaei-kuwait.html', 'الثيل الصناعي'),
    'mukhayyamat': ('mukhayyamat.html', 'سجاد ومساند المخيمات'),
}
BLOCK_RE = re.compile(r'<!-- ALL_PRODUCTS:START -->.*?<!-- ALL_PRODUCTS:END -->\n?', re.S)


def block(section, title, products):
    items = []
    for p in products:
        slug = p.get('slug')
        if not slug or not (ROOT / 'catalog' / f'{section}-{slug}.html').exists():
            continue
        name = html.escape(p.get('code') or slug.replace('-', ' '), quote=True)
        items.append(f'<li style="margin:0;"><a href="/catalog/{section}-{slug}.html" '
                     f'style="color:var(--gold-light);text-decoration:none;font-size:12.5px;line-height:1.9;">{name}</a></li>')
    if not items:
        return ''
    return ('<!-- ALL_PRODUCTS:START --><section aria-label="فهرس المنتجات والأعمال" style="padding:6px 16px 16px;">'
            f'<h2 style="font-size:14px;font-weight:800;color:var(--gold);margin:8px 0 10px;">فهرس {title}: كل المنتجات والأعمال ({len(items)})</h2>'
            '<ul style="list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:2px 14px;">'
            + ''.join(items) + '</ul></section><!-- ALL_PRODUCTS:END -->\n')


def main():
    check = '--check' in sys.argv
    data = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))
    stale = []
    for section, (page, title) in PAGES.items():
        path = ROOT / page
        old = path.read_text(encoding='utf-8')
        new = BLOCK_RE.sub('', old)
        b = block(section, title, data.get(section, []))
        if b:
            assert new.count('</main>') == 1, page
            new = new.replace('</main>', b + '</main>')
        if new != old:
            stale.append(page)
            if not check:
                path.write_text(new, encoding='utf-8', newline='')
    if check and stale:
        print('صفحات غير محدّثة:', ', '.join(stale))
        sys.exit(1)
    print(('يحتاج تحديث: ' if check else 'تم تحديث: ') + (', '.join(stale) or 'لا شيء'))


if __name__ == '__main__':
    main()
