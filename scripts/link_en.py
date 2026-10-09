#!/usr/bin/env python3
"""
Salford — link Arabic pages to their English twins (idempotent).

Reads en/pairs.json (written by build_en.py) and, for every pair:
  1. Arabic page <head>: hreflang ar-KW / en-KW / x-default (between HREFLANG markers)
  2. Arabic page: a small "English" link (between LANG-EN markers), absolutely
     positioned so it never shifts layout (no CLS) and never changes Title/H1/content
  3. sitemap.xml: xhtml:link alternates on the Arabic <url>, and an <url> for the
     English page with the same alternates (between EN markers)
Run after build_en.py:  python3 scripts/link_en.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://salfordkw.shop"


def ar_file(path):
    return "index.html" if path == "/" else path.lstrip("/")


def alt_links_html(ar, en):
    return ("<!-- HREFLANG:START -->\n"
            f'<link rel="alternate" hreflang="ar-KW" href="{SITE}{ar}">\n'
            f'<link rel="alternate" hreflang="en-KW" href="{SITE}{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE}{ar}">\n'
            "<!-- HREFLANG:END -->")


def lang_link_html(en):
    return ("<!-- LANG-EN:START -->"
            f'<a href="{en}" hreflang="en" lang="en" style="position:absolute;top:10px;left:12px;z-index:60;'
            'font:700 12px/1 system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:#E8D5A3;text-decoration:none;'
            'border:1px solid rgba(200,169,110,.35);border-radius:14px;padding:6px 11px;background:rgba(9,13,22,.6)">English</a>'
            "<!-- LANG-EN:END -->")


def put_block(s, start, end, block, anchor_re, where="after"):
    s = re.sub(r"\n?" + re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"\n?", "", s)
    m = re.search(anchor_re, s)
    if not m:
        raise SystemExit(f"anchor not found: {anchor_re}")
    i = m.end() if where == "after" else m.start()
    return s[:i] + "\n" + block + "\n" + s[i:]


def sitemap_alts(ar, en):
    return (f'    <xhtml:link rel="alternate" hreflang="ar-KW" href="{SITE}{ar}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en-KW" href="{SITE}{en}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{ar}"/>')


def main():
    pairs = json.load(open(os.path.join(ROOT, "en", "pairs.json"), encoding="utf-8"))

    for p in pairs:
        f = os.path.join(ROOT, ar_file(p["ar"]))
        s = open(f, encoding="utf-8").read()
        s = put_block(s, "<!-- HREFLANG:START -->", "<!-- HREFLANG:END -->",
                      alt_links_html(p["ar"], p["en"]), r'<link rel="canonical"[^>]*>')
        s = put_block(s, "<!-- LANG-EN:START -->", "<!-- LANG-EN:END -->",
                      lang_link_html(p["en"]), r"<body[^>]*>")
        open(f, "w", encoding="utf-8").write(s)
        print("linked", ar_file(p["ar"]))

    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = open(sm_path, encoding="utf-8").read()
    if "xmlns:xhtml" not in sm:
        sm = sm.replace("<urlset ", '<urlset xmlns:xhtml="http://www.w3.org/1999/xhtml" ', 1)
    # remove previous generated blocks
    sm = re.sub(r"\n?\s*<!-- EN-ALT -->[\s\S]*?<!-- /EN-ALT -->", "", sm)
    had_block = "<!-- EN:START -->" in sm
    en_urls = []
    for p in pairs:
        loc = f"{SITE}{p['ar']}"
        m = re.search(r"<loc>" + re.escape(loc) + r"</loc>", sm)
        if not m:
            raise SystemExit(f"Arabic URL not in sitemap: {loc}")
        sm = sm[:m.end()] + "\n    <!-- EN-ALT -->\n" + sitemap_alts(p["ar"], p["en"]) + "\n    <!-- /EN-ALT -->" + sm[m.end():]
        en_urls.append(f"  <url>\n    <loc>{SITE}{p['en']}</loc>\n{sitemap_alts(p['ar'], p['en'])}\n"
                       f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>")
    block = "  <!-- EN:START -->\n" + "\n".join(en_urls) + "\n  <!-- EN:END -->"
    if had_block:
        # keep the block where it already is, so pages the admin panel appends later
        # do not move it (stable output = the Site Guard check stays green)
        sm = re.sub(r"  <!-- EN:START -->[\s\S]*?<!-- EN:END -->", lambda _: block, sm, count=1)
    else:
        sm = re.sub(r"</urlset\s*>", lambda _: block + "\n</urlset>", sm, count=1)
    open(sm_path, "w", encoding="utf-8").write(sm)
    print("sitemap: +", len(en_urls), "English URLs")


if __name__ == "__main__":
    main()
