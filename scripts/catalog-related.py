#!/usr/bin/env python3
"""
قسم «أعمال مشابهة» + سطر الفرع في كل صفحات المنتجات (catalog/*.html).

يقرأ products.json ويضع في كل صفحة منتج روابط لأربعة منتجات من نفس القسم الفرعي
(أو نفس القسم إن لم يكفِ) بين العلامتين RELATED_PRODUCTS:START / END، وسطر عنوان
فرع الضجيج بين BRANCH:START / END. إعادة التشغيل تستبدل القديم (لا تكرار).
الغرض: ربط داخلي بين صفحات المنتجات بدل أن تبقى كل صفحة معزولة برابط واحد للقسم.

شغّله بعد أي إضافة/حذف/تعديل اسم منتج:
    python3 scripts/catalog-related.py          (يعدّل)
    python3 scripts/catalog-related.py --check  (يفشل إن وُجدت صفحة غير محدّثة)
لا يغيّر Title أو H1 أو الوصف أو الـSchema.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N = 4
BRANCH = ('<!-- BRANCH:START --><p>📍 فرعنا ومعرض العينات: <a href="/sajjad-al-dajeej-kuwait.html" '
          'style="color:var(--gold-light);text-decoration:none;">الضجيج — مجمع علي عبدالوهاب (السرداب)</a>'
          ' — يومياً من 10 ص إلى 9 م، مع معاينة وقياس مجاني بالمنزل لجميع مناطق الكويت.</p><!-- BRANCH:END -->')
REL_RE = re.compile(r'<!-- RELATED_PRODUCTS:START -->.*?<!-- RELATED_PRODUCTS:END -->', re.S)
BR_RE = re.compile(r'<!-- BRANCH:START -->.*?<!-- BRANCH:END -->', re.S)


def card(section, p):
    name = html.escape(p['code'], quote=True)
    href = f"/catalog/{section}-{p['slug']}.html"
    img = html.escape(p.get('img') or '', quote=True)
    return (f'<a href="{href}" style="display:block;background:var(--bg-card);border:1px solid rgba(200,169,110,.15);'
            f'border-radius:10px;overflow:hidden;text-decoration:none;">'
            f'<img src="{img}" alt="{name}" loading="lazy" decoding="async" width="300" height="225" '
            f'style="width:100%;aspect-ratio:4/3;object-fit:cover;display:block;">'
            f'<span style="display:block;padding:7px 8px;font-size:12px;font-weight:700;color:var(--gold-light);line-height:1.5;">{name}</span></a>')


def related_block(section, items, idx):
    me = items[idx]
    visible = [(i, p) for i, p in enumerate(items) if not p.get('hidden') and p.get('slug')]
    same = [x for x in visible if x[1].get('sub', '') == me.get('sub', '') and x[0] != idx]
    pool = same if len(same) >= N else same + [x for x in visible if x[0] != idx and x not in same]
    if not pool:
        return '<!-- RELATED_PRODUCTS:START --><!-- RELATED_PRODUCTS:END -->'
    # تدوير حسب موضع المنتج حتى تتوزع الروابط على كل الصفحات لا على أول أربعة فقط
    start = idx % len(pool)
    pick = (pool[start:] + pool[:start])[:N]
    cards = ''.join(card(section, p) for _, p in pick)
    return ('<!-- RELATED_PRODUCTS:START --><section aria-label="أعمال مشابهة" style="padding:6px 16px 14px;">'
            '<h2 style="font-size:14px;font-weight:800;color:var(--gold);margin-bottom:10px;">أعمال مشابهة من سالفورد</h2>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{cards}</div></section>'
            '<!-- RELATED_PRODUCTS:END -->')


def process(text, block):
    if BR_RE.search(text):
        text = BR_RE.sub(lambda m: BRANCH, text, count=1)
    else:
        m = re.search(r'(<div class="about-mini">.*?</p>)', text, re.S)
        if m:
            text = text[:m.end()] + '\n  ' + BRANCH + text[m.end():]
    if REL_RE.search(text):
        text = REL_RE.sub(lambda m: block, text, count=1)
    else:
        i = text.find('<div class="related">')
        if i < 0:
            i = text.find('<main>')
        if i >= 0:
            text = text[:i] + block + '\n' + text[i:]
    return text


def main():
    check = '--check' in sys.argv
    products = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))
    dirty = []
    for section, items in products.items():
        for idx, p in enumerate(items):
            if p.get('hidden') or not p.get('slug'):
                continue
            f = ROOT / 'catalog' / f"{section}-{p['slug']}.html"
            if not f.exists():
                continue
            old = f.read_text(encoding='utf-8')
            if 'http-equiv="refresh"' in old:
                continue
            new = process(old, related_block(section, items, idx))
            if new != old:
                dirty.append(f.name)
                if not check:
                    f.write_text(new, encoding='utf-8')
    print(('غير محدّث: ' if check else 'تم تحديث: ') + f'{len(dirty)} صفحة منتج')
    if check and dirty:
        sys.exit(1)


if __name__ == '__main__':
    main()
