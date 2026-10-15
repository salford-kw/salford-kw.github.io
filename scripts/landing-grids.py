#!/usr/bin/env python3
"""
قسم «نماذج من مخزننا وأعمالنا» في الصفحات المختصة (*-kuwait.html).

يقرأ products.json ويعرض في كل صفحة مختصة منتجات قسمها الفرعي فقط (sub)،
بين العلامتين LANDING_GRID:START / LANDING_GRID:END، قبل قسم الروابط ذات الصلة.
إعادة التشغيل تستبدل القسم القديم بالجديد (لا تكرار)، فالصفحة تبقى مطابقة للمنتجات.

قواعد ثابتة (حماية الترتيب):
- لا يغيّر العنوان أو الوصف أو H1 أو النص أو الـSchema الموجود في الصفحة.
- لا يضيف Product schema (يبقى في صفحة كل منتج فقط).
- صور صغيرة (img) بـ loading=lazy وأبعاد محددة، تحت المحتوى؛ لا تنافس صورة LCP.
- حد أقصى MAX_CARDS بطاقة، الأحدث أولاً.

الاستخدام:  python3 scripts/landing-grids.py          (صفحات ENABLED فقط)
            python3 scripts/landing-grids.py --check  (يفشل إذا القسم غير محدّث)
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://salfordkw.shop'
MAX_CARDS = 8

# نفس ربط SUBSECTION_PAGES في salford-admin/src/catalogTemplate.js
SUB_PAGES = {
    ('sajjad', 'saada'): ('sajjad-saada-kuwait.html', 'سجاد ساده'),
    ('sajjad', 'mashjar'): ('sajjad-mashjar-kuwait.html', 'سجاد مشجر'),
    ('sajjad', 'hafr'): ('sajjad-hafr-yadawi-kuwait.html', 'سجاد حفر يدوي'),
    ('sajjad', 'mokeet'): ('afdal-mokeet-kuwait.html', 'موكيت تركي'),
    ('sajjad', 'masjid'): ('sajjad-masjid-kuwait.html', 'سجاد مساجد ومصليات'),
    ('majalis', 'diwaniyat-modern'): ('diwaniyat-modern-kuwait.html', 'ديوانيات مودرن'),
    ('majalis', 'diwaniyat-kharjiya'): ('diwaniyat-kharjiya-kuwait.html', 'ديوانيات خارجية'),
    ('majalis', 'jalsat-ardiya'): ('jalsat-ardiya-jahza-kuwait.html', 'جلسات أرضية جاهزة'),
    ('majalis', 'masanid-khashab'): ('masanid-khashab-dekor-kuwait.html', 'مساند ظهر خشب ديكور'),
    ('majalis', 'masanid-tafseel'): ('tafseel-masanid-kuwait.html', 'تفصيل وتنجيد مساند'),
    ('athath', 'tanjeed-ganafat'): ('tanjeed-ganafat-kuwait.html', 'تنجيد قنفات'),
    ('athath', 'talbees-kanab'): ('talbees-kanab-kuwait.html', 'تلبيس كنب'),
    ('athath', 'tafseel-kanab'): ('tafseel-kanab-kuwait.html', 'تفصيل كنب وأطقم صالات'),
    ('athath', 'console-tawlat'): ('tawlat-istiqbal-console-kuwait.html', 'كونسول وطاولات استقبال'),
    ('sataer', 'shifon'): ('sataer-shifon-kuwait.html', 'ستائر شيفون'),
}

# المرحلة الأولى (2026-10-15): أربع صفحات ضعيفة الظهور فقط، ثم المقارنة في Search Console قبل التعميم.
# الصفحات القوية (من أعلى 10 صفحات بالنقرات في Search Console) تُترك للمرحلة الأخيرة:
# jalsat-ardiya-jahza, sajjad-al-dajeej, sajjad-bel-meter, sajjad-masjid, tafseel-kanab,
# tafseel-sajjad, afdal-mokeet, wajar.
# خط الأساس (آخر 3 أشهر حتى 2026-10-15): 685 نقرة، 19.9 ألف ظهور، CTR 3.4%، متوسط الترتيب 8.2.
ENABLED = {
    ('sajjad', 'saada'),
    ('sajjad', 'hafr'),
    ('majalis', 'masanid-khashab'),
    ('majalis', 'masanid-tafseel'),
}

START = '<!-- LANDING_GRID:START -->'
END = '<!-- LANDING_GRID:END -->'
ANCHOR = '<section class="related-links"'


def esc(s):
    return html.escape(str(s or '').replace('​', '').strip(), quote=True)


def price_text(p):
    price = str(p.get('price') or '').strip()
    if not price:
        return 'السعر حسب المقاس'
    unit = str(p.get('unit') or '').strip()
    unit = {'م': 'المتر'}.get(unit, unit)
    return f'{price} د.ك / {unit}' if unit else f'{price} د.ك'


def card(section, p):
    name = esc(p.get('code') or p.get('name'))
    href = f"/catalog/{section}-{p['slug']}.html"
    return (
        f'    <a href="{href}" style="display:block;text-decoration:none;border:1px solid rgba(200,169,110,.25);border-radius:12px;overflow:hidden;background:rgba(200,169,110,.04);">\n'
        f'      <img src="{esc(p["img"])}" alt="{name} — سالفورد الكويت" loading="lazy" decoding="async" width="400" height="400" style="width:100%;aspect-ratio:1/1;object-fit:cover;display:block;">\n'
        f'      <span style="display:block;padding:8px 10px 2px;color:var(--gold);font-size:13px;font-weight:700;line-height:1.6;">{name}</span>\n'
        f'      <span style="display:block;padding:0 10px 10px;color:var(--text-muted);font-size:12px;">{esc(price_text(p))}</span>\n'
        f'    </a>'
    )


def block(section, label, products):
    cards = '\n'.join(card(section, p) for p in products)
    return (
        f'{START}\n'
        f'<section class="content-section" aria-label="نماذج {esc(label)} من مخزننا وأعمالنا">\n'
        f'  <h2>نماذج {esc(label)} من مخزننا وأعمالنا</h2>\n'
        f'  <p style="font-size:14px;line-height:1.9;color:var(--text-muted);margin:0 0 12px;">نماذج حقيقية من مخزن سالفورد بالضجيج ومن أعمالنا في مناطق الكويت — اضغط على النموذج لمشاهدة الصور والسعر والتفاصيل.</p>\n'
        f'  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;">\n'
        f'{cards}\n'
        f'  </div>\n'
        f'</section>\n'
        f'{END}\n'
    )


def main():
    check = '--check' in sys.argv
    data = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))
    stale = []
    for key in sorted(ENABLED):
        section, sub = key
        page, label = SUB_PAGES[key]
        path = ROOT / page
        src = path.read_text(encoding='utf-8')
        items = [
            p for p in data.get(section, [])
            if p.get('sub') == sub and p.get('slug') and p.get('img')
            and (ROOT / 'catalog' / f"{section}-{p['slug']}.html").exists()
        ]
        items = list(reversed(items))[:MAX_CARDS]  # الأحدث أولاً
        if not items:
            continue
        new_block = block(section, label, items)
        if START in src:
            out = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', lambda _m: new_block, src, count=1, flags=re.S)
        else:
            if ANCHOR not in src:
                raise SystemExit(f'❌ {page}: لا يوجد قسم related-links لوضع النماذج قبله')
            out = src.replace(ANCHOR, new_block + '\n' + ANCHOR, 1)
        if out != src:
            stale.append(page)
            if not check:
                path.write_text(out, encoding='utf-8')
        print(f'{page}: {len(items)} بطاقة')
    if check and stale:
        raise SystemExit('❌ قسم النماذج غير محدّث في: ' + '، '.join(stale) + ' — شغّل python3 scripts/landing-grids.py')
    print('✅ تم' if not check else '✅ أقسام النماذج محدّثة')


if __name__ == '__main__':
    main()
