#!/usr/bin/env python3
"""مقالات سالفورد المجدولة (طلب المالك 2026-11-24): مقال كل سبت.

كل مقال ملف scheduled/blog/<slug>.json فيه publishDate (YYYY-MM-DD) والعنوان والوصف والنص (HTML لأقسام
art-section) والأسئلة الشائعة والروابط ذات الصلة. لا يُنشر مجلد scheduled على الموقع.

وقت النشر (scripts/release-scheduled.py داخل deploy-pages.yml) يُبنى كل مقال حان موعده إلى blog/<slug>.html
من قالب مقال قائم (blog/tanjeed-vs-new-sofa.html: نفس الرأس والتنسيق والتذييل)، ويُضاف إلى blog.html
(بطاقة + hasPart) و sitemap.xml و llms.txt. المقال المنشور سابقًا (موجود في blog/) لا يُعاد بناؤه.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

SITE = 'https://salfordkw.shop'
TEMPLATE = 'blog/tanjeed-vs-new-sofa.html'
WA = 'https://wa.me/96555943343?text='


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def render(a, tpl):
    e = html.escape
    url = f"{SITE}/blog/{a['slug']}.html"
    full_title = f"{a['seoTitle']} | سالفورد"
    t = tpl
    t = re.sub(r'<title>.*?</title>', lambda m: f'<title>{e(full_title)}</title>', t, count=1)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        t = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*', lambda m: m.group(1) + e(a['description']), t)
    for attr in ('property="og:title"', 'name="twitter:title"'):
        t = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*', lambda m: m.group(1) + e(full_title), t)
    for attr in ('property="og:image"', 'name="twitter:image"'):
        t = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*', lambda m: m.group(1) + a['image'], t)
    t = re.sub(r'(<meta name="keywords" content=")[^"]*', lambda m: m.group(1) + e(', '.join(a['keywords'])), t)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, t)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, t)
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "مركز المعرفة", "item": f"{SITE}/blog.html"},
        {"@type": "ListItem", "position": 3, "name": a['title'], "item": url}]}
    t = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "BreadcrumbList".*?</script>',
               lambda m: ld(crumbs), t, count=1, flags=re.S)
    article = {"@context": "https://schema.org", "@type": "Article", "headline": a['title'], "description": a['description'],
               "image": a['image'], "author": {"@type": "Organization", "name": "فريق سالفورد"},
               "publisher": {"@type": "Organization", "name": "سالفورد للأثاث والمفروشات",
                             "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}},
               "datePublished": a['publishDate'], "dateModified": a['publishDate'], "mainEntityOfPage": url, "inLanguage": "ar-KW"}
    t = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "Article".*?</script>',
               lambda m: ld(article), t, count=1, flags=re.S)
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a['faqs']]}
    t = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
               lambda m: ld(faq), t, count=1, flags=re.S)
    t = re.sub(r'<img class="art-hero" src="[^"]*" alt="[^"]*"',
               lambda m: f'<img class="art-hero" src="{a["image"]}" alt="{e(a["imageAlt"])}"', t, count=1)
    t = re.sub(r'(<div class="page-title">\s*<h1>).*?(</h1>)', lambda m: m.group(1) + e(a['title']) + m.group(2), t, count=1, flags=re.S)
    wa = WA + urllib.parse.quote(a.get('waText') or f"مرحبا، عندي سؤال بخصوص {a['title']}")
    faqs = '\n'.join(f'  <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">{e(q)}<span class="faq-icon">+</span></button>'
                     f'<div class="faq-a"><p>{e(ans)}</p></div></div>' for q, ans in a['faqs'])
    rel = '\n'.join(f'<a href="{h}"><b>{e(n)}</b></a>' for h, n in a['related'])
    cta = re.search(r'<div class="cta">.*?</div>\n', tpl, re.S).group(0)
    cta = re.sub(r'(<a class="btn btn-wa" href=")[^"]*', lambda m: m.group(1) + wa, cta, count=1)
    main = (f'<main>\n<div class="direct-answer">{e(a["answer"])}</div>\n\n{a["body"].strip()}\n\n'
            f'<a class="cta-inline" href="{wa}" target="_blank" rel="noopener">💬 عندك سؤال؟ راسلنا على واتساب</a>\n'
            f'<p class="author-note">بقلم فريق سالفورد — خبرة في المفروشات والأرضيات والنجارة في الكويت منذ 2016</p>\n\n'
            f'<section class="faq" aria-label="أسئلة شائعة">\n  <h2 class="sec-title">أسئلة شائعة</h2>\n{faqs}\n</section>\n\n'
            f'<div class="related"><h2 class="sec-title">مواضيع ذات صلة</h2>\n{rel}\n</div>\n{cta}</main>')
    t = re.sub(r'<main>.*?</main>', lambda m: main, t, count=1, flags=re.S)
    for bad in ('tanjeed-vs-new-sofa', 'تنجيد القنفات والغنفات أم شراء'):
        if bad in t and bad not in json.dumps(a, ensure_ascii=False):
            raise SystemExit(f'بقايا من القالب في {a["slug"]}: {bad}')
    return url, t


def apply_posts(root: Path, today: str, listing=False):
    files = sorted((root / 'scheduled' / 'blog').glob('*.json'))
    posts = [json.loads(f.read_text(encoding='utf-8')) for f in files]
    if listing:
        for p in sorted(posts, key=lambda p: p['publishDate']):
            print(p['publishDate'], '✅' if p['publishDate'] <= today else '⏳', 'blog/' + p['slug'])
        return []
    due = sorted([p for p in posts if p['publishDate'] <= today and not (root / 'blog' / f"{p['slug']}.html").exists()],
                 key=lambda p: p['publishDate'])
    if not due:
        return []
    tpl = (root / TEMPLATE).read_text(encoding='utf-8')
    bl_path, sm_path, llms_path = root / 'blog.html', root / 'sitemap.xml', root / 'llms.txt'
    bl, sm, llms = (p.read_text(encoding='utf-8') for p in (bl_path, sm_path, llms_path))
    urls = []
    for a in due:
        url, page = render(a, tpl)
        (root / 'blog' / f"{a['slug']}.html").write_text(page, encoding='utf-8')
        e = html.escape
        card = (f'<a class="blog-card" href="/blog/{a["slug"]}.html"><img src="{a["image"]}" alt="{e(a["title"])}" loading="lazy">'
                f'<div class="blog-card-body"><b>{e(a["title"])}</b><p>{e(a["description"])}</p></div></a>')
        bl = bl.replace('<div class="blog-list">\n', '<div class="blog-list">\n' + card + '\n', 1)
        m = re.search(r'("@type": "CollectionPage".*?"hasPart": \[)(.*?)(\]\}</script>)', bl, re.S)
        if m:
            part = json.dumps({"@type": "Article", "headline": a['title'], "url": url}, ensure_ascii=False)
            bl = bl[:m.start(2)] + part + (', ' if m.group(2).strip() else '') + m.group(2) + bl[m.end(2):]
        sm = sm.rstrip().removesuffix('</urlset>') + (
            f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{a['publishDate']}</lastmod>\n    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.6</priority>\n  </url>\n</urlset>\n")
        line = f"- [{a['title']}]({url}): {a['description']}"
        anchor = '- [مركز المعرفة](https://salfordkw.shop/blog.html)'
        llms = re.sub(re.escape(anchor) + r'[^\n]*\n', lambda m: m.group(0) + line + '\n', llms, count=1)
        urls.append(url)
    bl = re.sub(r'(<loc>https://salfordkw\.shop/blog\.html</loc>\s*<lastmod>)[^<]*', lambda m: m.group(1) + due[-1]['publishDate'], bl)
    sm = re.sub(r'(<loc>https://salfordkw\.shop/blog\.html</loc>\s*<lastmod>)[^<]*', lambda m: m.group(1) + due[-1]['publishDate'], sm)
    bl_path.write_text(bl, encoding='utf-8')
    sm_path.write_text(sm, encoding='utf-8')
    llms_path.write_text(llms, encoding='utf-8')
    return urls
