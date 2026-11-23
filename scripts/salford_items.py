#!/usr/bin/env python3
"""مولّد صفحات منتجات/أعمال سالفورد من ملف وصف (JSON) — مصدر واحد للنشر الفوري والمجدول.

كل عنصر (item) يحوي: code (الاسم = الرابط)، sub، sub_page [ملف الصفحة، اسم القسم]، meta (وصف جوجل)،
desc (النص)، price، unit، unitCode (MTR للمتر الطولي، MTK للمتر المربع)، color، material، area (اختياري)،
specs [[العنوان، القيمة]]، images [[الاسم بلا -large/-small، النص البديل، العرض، الارتفاع]]،
post_title، post_desc، id، publishDate (YYYY-MM-DD).

يبني من scripts/templates/catalog-template.html صفحة catalog/sajjad-<slug>.html كاملة (العنوان، الوصف،
Product + Offer + UnitPriceSpecification + الإرجاع والتوصيل، المعرض، المواصفات، واتساب) ويضيف العنصر
إلى products.json و posts.json (آخر أعمالنا) و sitemap.xml. بعده تُشغَّل سكربتات الأقسام والمنتجات المشابهة.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

SITE = 'https://salfordkw.shop'
TPL_FILE = Path(__file__).resolve().parent / 'templates' / 'catalog-template.html'
OLD_TITLE = 'سجاد رمادي فاتح سادة سماكة 22 مم لغرفة اعمالنا في الدسمة'
OLD_SLUG = 'سجاد-رمادي-فاتح-سادة-سماكة-22-مم-لغرفة-اعمالنا-في-الدسمة'


def slug_of(item):
    return item['code'].replace(' ', '-')


def build_page(item, today):
    t = TPL_FILE.read_text(encoding='utf-8')
    e = html.escape
    slug = slug_of(item)
    url = f"{SITE}/catalog/sajjad-{slug}.html"
    imgs = item['images']
    L = [f"{SITE}/products/{b}-large.webp" for b, _, _, _ in imgs]
    S = [f"{SITE}/products/{b}-small.webp" for b, _, _, _ in imgs]

    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        t = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*', lambda m: m.group(1) + e(item['meta']), t)

    pj = re.search(r'<script type="application/ld\+json">(\{"@context":"https://schema.org","@type":"Product".*?)</script>', t, re.S)
    d = json.loads(pj.group(1))
    d.update(sku=item['id'], name=item['code'], description=item['desc'], image=L, url=url, dateModified=today)
    o = d['offers']
    o.update(url=url, price=item['price'], validFrom=today, priceValidUntil=str(int(today[:4]) + 5) + today[4:])
    if item.get('unitCode'):
        o['priceSpecification'] = {"@type": "UnitPriceSpecification", "price": item['price'], "priceCurrency": "KWD",
                                   "unitCode": item['unitCode'], "unitText": item['unit']}
    t = t.replace(pj.group(1), json.dumps(d, ensure_ascii=False, separators=(',', ':')))

    sub_page, sub_name = item['sub_page']
    t = t.replace('"name":"سجاد ساده","item":"https://salfordkw.shop/sajjad-saada-kuwait.html"',
                  f'"name":"{sub_name}","item":"https://salfordkw.shop/{sub_page}"')
    t = t.replace('<a href="/sajjad-saada-kuwait.html">سجاد ساده</a>', f'<a href="/{sub_page}">{sub_name}</a>')
    t = t.replace(f"{SITE}/products/{OLD_SLUG}-سالفورد-1-large.webp", L[0])

    g = '\n'.join(f'  <img src="{s}" alt="{e(a)}" loading="lazy" data-large="{l}" onclick="swapHero(this)">'
                  for s, l, (_, a, _, _) in zip(S, L, imgs))
    t = re.sub(r'<div class="gallery-strip">.*?</div>', lambda m: f'<div class="gallery-strip">\n{g}\n</div>', t, count=1, flags=re.S)
    _, a0, w0, h0 = imgs[0]
    t = re.sub(r'(<img class="hero-img" id="hero-img" src="[^"]*" alt=")[^"]*(" width=")\d+(" height=")\d+',
               lambda m: f'{m.group(1)}{e(a0)}{m.group(2)}{w0}{m.group(3)}{h0}', t)
    t = re.sub(r'<div class="p-desc">.*?</div>', lambda m: f'<div class="p-desc">{e(item["desc"])}</div>', t, count=1, flags=re.S)
    rows = '\n'.join(f'  <tr><td>{e(k)}</td><td>{v}</td></tr>' for k, v in item['specs'])
    t = re.sub(r'<table class="spec-table">.*?</table>', lambda m: f'<table class="spec-table">\n{rows}\n</table>', t, count=1, flags=re.S)
    t = (t.replace('<strong>سجاد ساده</strong>', f'<strong>{sub_name}</strong>')
          .replace('اطّلع على سجاد ساده:', f'اطّلع على {sub_name}:')
          .replace('<a href="/sajjad-saada-kuwait.html" style="display:inline-block', f'<a href="/{sub_page}" style="display:inline-block'))
    wa = urllib.parse.quote(f"مرحباً، أريد الاستفسار عن {item['code']}")
    t = re.sub(r'(https://wa\.me/96555943343\?text=)[^"]*', lambda m: m.group(1) + wa, t, count=1)
    t = t.replace(OLD_SLUG, slug).replace(OLD_TITLE, item['code'])
    leftover = [l for l in t.splitlines() if 'الدسمة' in l or 'رمادي فاتح' in l]
    if leftover and 'الدسمة' not in item['code'] and 'رمادي فاتح' not in item['code']:
        raise SystemExit(f'بقايا من القالب في {slug}: {leftover[:2]}')
    return slug, url, L, S, t, (w0, h0)


def apply_items(items, root: Path, today: str):
    """يضيف العناصر للموقع (صفحات + products.json + posts.json + sitemap). يُرجع الروابط الجديدة."""
    pj_path, po_path, sm_path = root / 'products.json', root / 'posts.json', root / 'sitemap.xml'
    pj = json.loads(pj_path.read_text(encoding='utf-8'))
    po = json.loads(po_path.read_text(encoding='utf-8'))
    sm = sm_path.read_text(encoding='utf-8')
    existing = {p.get('slug') for p in pj.get('sajjad', [])}
    urls = []
    for it in items:
        slug = slug_of(it)
        if slug in existing:
            continue  # نُشر سابقًا (أُضيف للفرع الرئيسي) — لا تكرار
        day = it.get('publishDate') or today
        slug, url, L, S, page, (w0, h0) = build_page(it, day)
        (root / 'catalog' / f'sajjad-{slug}.html').write_text(page, encoding='utf-8')
        pj['sajjad'].append({
            "code": it['code'], "sub": it['sub'], "desc": it['desc'], "price": it['price'], "unit": it['unit'],
            "area": it.get('area', ''), "availability": "https://schema.org/InStock", "stock": "", "color": it['color'],
            "material": it['material'], "dimensions": "", "mpn": "", "deliveryTime": "", "days": "",
            "img": S[0], "imgLarge": L[0], "imgLargeW": w0, "imgLargeH": h0, "images": S, "imagesLarge": L,
            "id": it['id'], "slug": slug})
        po.insert(0, {"id": it['id'].replace('prod_', 'post_'), "title": it['post_title'], "desc": it['post_desc'],
                      "img": S[0], "images": S, "imagesLarge": L, "imgLarge": L[0], "video": "", "date": day,
                      "price": it['price'], "unit": it['unit'], "productUrl": url})
        sm = sm.rstrip().removesuffix('</urlset>') + (
            f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{day}</lastmod>\n    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.6</priority>\n    <image:image>\n      <image:loc>{L[0]}</image:loc>\n    </image:image>\n  </url>\n</urlset>")
        urls.append(url)
    pj_path.write_text(json.dumps(pj, ensure_ascii=False, indent=2), encoding='utf-8')
    po_path.write_text(json.dumps(po, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sm_path.write_text(sm, encoding='utf-8')
    return urls
