#!/usr/bin/env python3
"""
Salford — English section builder (/en/)

Source of truth for every English page. Edit the PAGES content below and run:
    python3 scripts/build_en.py
It writes /en/*.html. It does NOT touch Arabic pages, sitemap.xml or hreflang
on Arabic pages — that is done once by scripts/link_en.py.

Rules baked in (do not remove):
- lang="en" dir="ltr", self-referencing canonical, hreflang ar-KW / en-KW / x-default (Arabic)
- no Google Tag; Firebase analytics loads deferred via /analytics.js
- images: -small variants, width/height set, only the hero is eager
- no physical address anywhere (Service Area Business)
- prices always carry their unit (per linear metre / per square metre)
"""
import html
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://salfordkw.shop"
PHONE = "+96555943343"
PHONE_DISPLAY = "+965 5594 3343"
WA = "96555943343"
IMG = f"{SITE}/products/"

AREAS = ["Salmiya", "Hawally", "Kuwait City", "Farwaniya", "Jleeb Al-Shuyoukh", "Khaitan",
         "Mahboula", "Fahaheel", "Ahmadi", "Jahra", "Mubarak Al-Kabeer", "Salwa", "Rumaithiya",
         "Bayan", "Sabah Al-Salem", "Qurain", "Adan", "Sabahiya", "Riggae", "Shuwaikh",
         "Kaifan", "Abdullah Al-Mubarak", "Sulaibiya"]

e = html.escape


def img_size(name):
    with Image.open(os.path.join(ROOT, "products", name)) as im:
        return im.size


def picture(name, alt, eager=False):
    w, h = img_size(name)
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{IMG}{name}" alt="{e(alt)}" width="{w}" height="{h}" '
            f'{load} decoding="async">')


def wa_link(text):
    from urllib.parse import quote
    return f"https://wa.me/{WA}?text={quote(text)}"


LOGO = """<svg class="logo" viewBox="0 0 300 130" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Salford Furniture &amp; Furnishings">
<g stroke="#C8A96E" stroke-linecap="round" stroke-linejoin="round">
<path d="M 112 38 C 112 28, 188 28, 188 38 V 48 H 112 Z" stroke-width="3"/>
<path d="M 100 42 C 95 42, 95 56, 100 56 H 112 V 42 Z" stroke-width="2.5"/>
<path d="M 200 42 C 205 42, 205 56, 200 56 H 188 V 42 Z" stroke-width="2.5"/>
<path d="M 100 48 H 200 C 203 48, 205 51, 205 54 V 58 C 205 61, 203 63, 200 63 H 100 C 97 63, 95 61, 95 58 V 54 C 95 51, 97 48, 100 48 Z" stroke-width="3"/>
<path d="M 103 63 L 98 72" stroke-width="3"/><path d="M 197 63 L 202 72" stroke-width="3"/>
</g>
<text x="150" y="99" fill="#C8A96E" font-family="system-ui,-apple-system,'Segoe UI',Arial,sans-serif" font-size="30" font-weight="900" text-anchor="middle" letter-spacing="3">SALFORD</text>
<text x="150" y="119" fill="#E8D5A3" font-family="system-ui,-apple-system,'Segoe UI',Arial,sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1">FURNITURE &amp; FURNISHINGS</text>
</svg>"""

CSS = """:root{--gold:#C8A96E;--gold-light:#E8D5A3;--glow:rgba(200,169,110,.25);--bg:#090D16;--card:#0F172A;--sub:#1E293B;--text:#F8FAFC;--muted:#94A3B8;--green:#10B981}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;padding-bottom:72px;overflow-x:hidden}
a{color:var(--gold)}
.wrap{max-width:860px;margin:0 auto;padding:0 18px}
header{background:linear-gradient(180deg,var(--card),var(--bg));border-bottom:1px solid var(--glow);padding:14px 0 16px;text-align:center}
.top{display:flex;justify-content:space-between;align-items:center;max-width:860px;margin:0 auto;padding:0 18px;font-size:13px}
.top a{text-decoration:none;color:var(--gold-light);font-weight:700}
.lang{border:1px solid var(--glow);border-radius:16px;padding:3px 12px}
.logo{width:220px;max-width:70vw;height:auto;display:block;margin:6px auto 0}
.badges{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:10px}
.badge{background:rgba(200,169,110,.08);border:1px solid rgba(200,169,110,.2);color:var(--gold-light);font-size:12px;padding:4px 12px;border-radius:20px;font-weight:600}
.badge a{text-decoration:none;font-weight:800}
.crumbs{font-size:12px;color:var(--muted);padding:12px 0 0}
.crumbs a{color:var(--muted)}
.hero{padding:22px 0 8px}
h1{font-size:26px;line-height:1.25;color:var(--gold-light);margin-bottom:10px}
.lead{color:var(--text);font-size:16px;margin-bottom:14px}
.hero-img img,.grid img{width:100%;height:auto;border-radius:12px;display:block;background:var(--sub)}
.hero-img{margin:16px 0 4px}
.hero-img img{max-height:440px;object-fit:cover}
.grid img{aspect-ratio:3/4;object-fit:cover}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0}
.stat{background:var(--card);border:1px solid var(--glow);border-radius:12px;padding:12px 6px;text-align:center}
.stat b{display:block;color:var(--gold);font-size:20px}
.stat span{font-size:12px;color:var(--muted)}
section{padding:18px 0;border-top:1px solid rgba(200,169,110,.1)}
h2{font-size:21px;color:var(--gold);margin-bottom:10px;line-height:1.3}
h3{font-size:16px;color:var(--gold-light);margin:12px 0 4px}
p{margin-bottom:10px}
ul,ol{margin:0 0 10px 20px}
li{margin-bottom:6px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--glow);border-radius:12px;padding:14px}
.card h3{margin-top:0}
.card a{text-decoration:none}
.price{color:var(--green);font-weight:800}
table{width:100%;border-collapse:collapse;margin:6px 0 12px;font-size:14px}
th,td{border:1px solid rgba(200,169,110,.2);padding:9px;text-align:left;vertical-align:top}
th{background:var(--card);color:var(--gold-light)}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.grid figure figcaption{font-size:12px;color:var(--muted);padding:4px 2px 0}
details{background:var(--card);border:1px solid var(--glow);border-radius:10px;padding:12px 14px;margin-bottom:8px}
summary{cursor:pointer;font-weight:700;color:var(--gold-light)}
details p{margin:8px 0 0}
.areas{font-size:14px;color:var(--muted)}
.cta{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.btn{display:flex;align-items:center;justify-content:center;padding:14px 10px;border-radius:10px;font-weight:800;text-decoration:none;font-size:15px}
.wa{background:#25D366;color:#06210f}
.call{background:var(--gold);color:#1a1405}
footer{border-top:1px solid var(--glow);padding:20px 0 10px;text-align:center;font-size:13px;color:var(--muted)}
footer a{color:var(--gold-light)}
.sticky{position:fixed;left:0;right:0;bottom:0;display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:8px;background:rgba(9,13,22,.96);border-top:1px solid var(--glow);z-index:50}
.sticky .btn{padding:12px 8px;font-size:14px}
@media(min-width:700px){h1{font-size:32px}.grid{grid-template-columns:repeat(4,1fr)}}"""


def nav_links():
    return [("/en/", "Home"), ("/en/curtains-kuwait.html", "Curtains"), ("/en/custom-sofas-kuwait.html", "Sofas"), ("/en/carpets-kuwait.html", "Carpets"),
            ("/en/about.html", "About"), ("/en/faq.html", "FAQ"), ("/en/contact.html", "Contact")]


def business_ld(url):
    return {
        "@context": "https://schema.org",
        "@type": ["FurnitureStore", "LocalBusiness"],
        "@id": f"{SITE}/#business",
        "name": "Salford Furniture & Furnishings",
        "alternateName": "سالفورد للأثاث والمفروشات",
        "url": url,
        "logo": f"{SITE}/favicon-192.png",
        "telephone": PHONE,
        "foundingDate": "2016",
        "priceRange": "$$",
        "currenciesAccepted": "KWD",
        "paymentAccepted": "Cash, KNET, Wamd, Bank Transfer",
        "areaServed": {"@type": "Country", "name": "Kuwait"},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "10:00", "closes": "21:00"}],
        "sameAs": ["https://www.instagram.com/salforad/", "https://www.tiktok.com/@salford_kuwait"],
        "inLanguage": "en",
    }


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "en",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


def faq_html(faqs):
    return "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faqs)


def render(p):
    url = f"{SITE}{p['path']}"
    ar = f"{SITE}{p['ar']}"
    hero = p.get("hero")
    ld = [business_ld(url)]
    crumbs = [("Home", f"{SITE}/en/")]
    if p.get("parent"):
        crumbs.append((p["parent"][0], f"{SITE}{p['parent'][1]}"))
    if p.get("crumb"):
        crumbs.append((p["crumb"], url))
    if len(crumbs) > 1:
        ld.append(crumbs_ld(crumbs))
    if p.get("faqs"):
        ld.append(faq_ld(p["faqs"]))
    ld += p.get("extra_ld", [])
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    wa = wa_link(p["wa"])
    preload = (f'<link rel="preload" as="image" fetchpriority="high" href="{IMG}{hero[0]}">' if hero else "")
    crumb_html = ""
    if p.get("crumb"):
        mid = f' › <a href="{p['parent'][1]}">{e(p['parent'][0])}</a>' if p.get("parent") else ""
        crumb_html = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/en/">Home</a>{mid} › {e(p["crumb"])}</nav>'
    nav = " · ".join(f'<a href="{u}">{t}</a>' for u, t in nav_links())
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-KW" href="{url}">
<link rel="alternate" hreflang="ar-KW" href="{ar}">
<link rel="alternate" hreflang="x-default" href="{ar}">
<meta name="theme-color" content="#C8A96E">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_KW">
<meta property="og:locale:alternate" content="ar_KW">
<meta property="og:site_name" content="Salford Furniture &amp; Furnishings">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p['desc'])}">
<meta property="og:url" content="{url}">
{f'<meta property="og:image" content="{IMG}{hero[0]}">' if hero else ''}
<meta name="twitter:card" content="summary_large_image">
{preload}
{ld_html}
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="top"><a href="/en/">Salford</a><a class="lang" href="{p['ar']}" hreflang="ar" lang="ar">عربي</a></div>
  <a href="/en/" aria-label="Salford home">{LOGO}</a>
  <div class="badges"><span class="badge">Delivery &amp; installation across Kuwait</span><span class="badge">Daily 10 am – 9 pm</span><span class="badge"><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span></div>
</header>
<main class="wrap">
{crumb_html}
<div class="hero">
<h1>{e(p['h1'])}</h1>
<p class="lead">{p['lead']}</p>
<div class="cta"><a class="btn wa" href="{wa}" target="_blank" rel="noopener">WhatsApp us</a><a class="btn call" href="tel:{PHONE}">Call {PHONE_DISPLAY}</a></div>
{f'<div class="hero-img">{picture(hero[0], hero[1], eager=True)}</div>' if hero else ''}
</div>
{p['body']}
{f'<section><h2>Frequently asked questions</h2>{faq_html(p["faqs"])}</section>' if p.get('faqs') else ''}
<section>
<h2>Areas we serve</h2>
<p class="areas">We deliver and install across all of Kuwait, including {", ".join(AREAS)} and every other area.</p>
<div class="cta"><a class="btn wa" href="{wa}" target="_blank" rel="noopener">Get a free quote on WhatsApp</a><a class="btn call" href="tel:{PHONE}">Call now</a></div>
</section>
</main>
<footer class="wrap">
<p><strong style="color:var(--gold)">Salford Furniture &amp; Furnishings</strong> — Kuwait, since 2016</p>
<p>{nav}</p>
<p><a href="https://www.instagram.com/salforad/" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.tiktok.com/@salford_kuwait" target="_blank" rel="noopener">TikTok</a> · <a href="{p['ar']}" hreflang="ar" lang="ar">النسخة العربية</a></p>
<p style="opacity:.6;font-size:11px;margin-top:6px">© 2026 Salford. All rights reserved.</p>
</footer>
<div class="sticky"><a class="btn wa" href="{wa}" target="_blank" rel="noopener">WhatsApp</a><a class="btn call" href="tel:{PHONE}">Call</a></div>
<script src="/analytics.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- content
STATS = """<div class="stats"><div class="stat"><b>2016</b><span>Founded</span></div><div class="stat"><b>790+</b><span>Projects completed</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>"""

CURTAIN_PHOTOS = [
    ("product_1786197567265_jz8bl-small.webp", "Gold velvet drapes over a white swag sheer, living room in Khaitan"),
    ("product_1786197651322_1zw0r-small.webp", "Floor-to-ceiling beige wave curtains under a carved cornice"),
    ("product_1786197817583_avoyf-small.webp", "Grey drapes with tiebacks over a white sheer, Hawally"),
    ("product_1786197982498_ekn0c-small.webp", "Day-and-night roller blind on a bathroom window, Hawally"),
    ("product_1786198170852_7o0ir-small.webp", "Sun-blocking roller blind in a bedroom, Mahboula"),
    ("product_1786198315153_52wc7-small.webp", "Grey roller blinds in an office, Capital Governorate"),
    ("product_1786220577670_dz6ih-small.webp", "White sheer wave curtain in a bedroom, Sabah Al-Salem"),
    ("product_1786198933149_374vc-small.webp", "Patterned grey drapes with a lace-edged sheer, Mangaf"),
]


def gallery(photos):
    items = "\n".join(f"<figure>{picture(n, a)}<figcaption>{e(a)}</figcaption></figure>" for n, a in photos)
    return f'<div class="grid">{items}</div>'


PAGES = []

# ---- Home
PAGES.append(dict(
    path="/en/", file="en/index.html", ar="/",
    title="Custom Furniture & Furnishings in Kuwait | Salford",
    desc="Custom curtains, roller blinds, sofas, upholstery, Arabic majlis seating and Turkish carpets in Kuwait. Free home measuring, delivery and installation since 2016.",
    h1="Furniture and furnishings in Kuwait, made to measure",
    lead="Salford makes curtains, blinds, sofas, majlis seating and carpets to fit your home or office — then delivers and installs them anywhere in Kuwait. We have been doing this since 2016.",
    hero=("product_1786197567265_jz8bl-small.webp", "Gold velvet drapes over a white swag sheer, made by Salford in Kuwait"),
    wa="Hello Salford, I'd like a quote (from salfordkw.shop/en/)",
    body=STATS + """
<section>
<h2>What we make</h2>
<div class="cards">
<div class="card"><h3><a href="/en/curtains-kuwait.html">Curtains and blinds →</a></h3><p>Wave, <a href="/en/blackout-curtains-kuwait.html">blackout</a>, <a href="/en/sheer-curtains-kuwait.html">sheer</a> and <a href="/en/roller-blinds-kuwait.html">roller blinds</a>, made to the size of each window. Roller blinds <span class="price">5 KD per square metre</span>.</p></div>
<div class="card"><h3><a href="/en/custom-sofas-kuwait.html">Sofas and upholstery →</a></h3><p><a href="/en/custom-sofas-kuwait.html">New sofas</a> built to your measurements, plus <a href="/en/sofa-upholstery-kuwait.html">re-upholstery</a> and <a href="/en/sofa-slipcovers-kuwait.html">slipcovers</a> for the sofas you already own.</p></div>
<div class="card"><h3>Arabic majlis seating</h3><p>Floor seating, back cushions and wooden majlis frames for diwaniyas and living rooms.</p></div>
<div class="card"><h3><a href="/en/carpets-kuwait.html">Carpets →</a></h3><p>Turkish carpet from Bursa mills, cut to size or by the metre, from <span class="price">11 KD per metre</span>, plus <a href="/en/mosque-carpet-kuwait.html">mosque carpet</a> and office carpet.</p></div>
<div class="card"><h3>Artificial grass and flooring</h3><p>Artificial grass for gardens and roofs, and parquet flooring, supplied and installed.</p></div>
</div>
</section>
<section>
<h2>How it works</h2>
<ol>
<li><strong>Message or call us</strong> — tell us what you need and where you are in Kuwait.</li>
<li><strong>Free home visit</strong> — we come to measure and bring fabric and material samples.</li>
<li><strong>Clear written price</strong> — you get the final price before anything is made, with no obligation.</li>
<li><strong>Made in our workshop</strong> — every order is produced by the Salford workshop.</li>
<li><strong>Delivery and installation</strong> — our team installs it and hands it over finished.</li>
</ol>
</section>
<section>
<h2>Why people choose Salford</h2>
<ul>
<li>Over 790 completed projects across Kuwait since 2016.</li>
<li>Everything is made to measure, so it fits your space instead of a showroom size.</li>
<li>Prices are always quoted with their unit — per linear metre or per square metre — so there are no surprises.</li>
<li>Pay by KNET, Wamd, cash or bank transfer, in Kuwaiti dinars.</li>
</ul>
</section>""",
    faqs=[
        ("Do you deliver and install everywhere in Kuwait?", "Yes. We deliver and install in every area of Kuwait, including Salmiya, Hawally, Mahboula, Fahaheel, Farwaniya, Jahra and Kuwait City."),
        ("Is the home visit really free?", "Yes. We visit to measure and show samples at no cost, and you get the final price in writing with no obligation to order."),
        ("How do I pay?", "You can pay by KNET, Wamd, cash or bank transfer. All prices are in Kuwaiti dinars."),
        ("What are your working hours?", "We work every day from 10 am to 9 pm. You can reach us by WhatsApp or phone on +965 5594 3343."),
    ],
))

# ---- Curtains
PAGES.append(dict(
    path="/en/curtains-kuwait.html", file="en/curtains-kuwait.html", ar="/sataer.html", crumb="Curtains in Kuwait",
    title="Custom Curtains in Kuwait, Measured & Installed | Salford",
    desc="Made-to-measure curtains in Kuwait: roller blinds 5 KD per sq m, blackout from 14 KD per metre. Free home measuring, installed in 1–3 days.",
    h1="Custom curtains in Kuwait, measured and installed",
    lead="We make wave, blackout, sheer and roller curtains to the exact size of your windows, then install them with the tracks included. Most orders are made and installed within 1 to 3 days.",
    hero=("product_1786197651322_1zw0r-small.webp", "Floor-to-ceiling beige wave curtains made by Salford in Kuwait"),
    wa="Hello Salford, I'd like a quote for curtains (from salfordkw.shop/en/curtains-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>1–3 days</b><span>Made and installed</span></div><div class="stat"><b>790+</b><span>Projects since 2016</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>
<section>
<h2>Curtain prices in Kuwait</h2>
<p>These are our starting prices. You get the exact price in writing after the free home visit, before anything is made.</p>
<table>
<thead><tr><th>Type</th><th>Price</th><th>Unit</th></tr></thead>
<tbody>
<tr><td>Roller blinds — plain, silver heat-reflective or blackout fabric</td><td class="price">5 KD</td><td>per square metre</td></tr>
<tr><td>Blackout curtains</td><td class="price">from 14 KD</td><td>per metre</td></tr>
<tr><td>Wave and sheer curtains</td><td>depends on the fabric</td><td>quoted after the visit</td></tr>
</tbody>
</table>
<p>Roller blinds are priced by the square metre of the window. Other curtains are priced by the metre of fabric width. Tracks and installation are included in the service.</p>
</section>
<section>
<h2>Which curtain suits which room?</h2>
<h3><a href="/en/blackout-curtains-kuwait.html">Blackout curtains</a> — bedrooms and day sleepers</h3>
<p>A dense, opaque fabric that blocks almost all light and much of the sun's heat. It is the first choice for bedrooms through the Kuwaiti summer, and for anyone who sleeps during the day.</p>
<h3>Wave curtains — living rooms and majlis</h3>
<p>Fabric folded into even waves that hide the track completely. It gives a neat, hotel-style look in living rooms, reception rooms and large bedrooms.</p>
<h3><a href="/en/sheer-curtains-kuwait.html">Sheer curtains</a> — soft daylight</h3>
<p>A light, see-through fabric that lets in soft light instead of full darkness. It is often paired with a heavier curtain so you can switch between privacy and light.</p>
<h3><a href="/en/roller-blinds-kuwait.html">Roller blinds</a> — kitchens, offices and small windows</h3>
<p>A single panel that rolls up and down on one mechanism. It is practical, easy to clean, and suits kitchens, bathrooms, offices and shop fronts. Sun-blocking fabric works well on large glass windows.</p>
</section>
<section>
<h2>How we make and install your curtains</h2>
<ol>
<li><strong>Contact us</strong> by WhatsApp or phone and tell us about your windows.</li>
<li><strong>Free visit</strong> — we measure every window and opening on site.</li>
<li><strong>Choose your fabric</strong> from samples of wave, blackout, sheer and roller fabrics in the available colours and weights.</li>
<li><strong>Agree the timing</strong> — usually 1 to 3 days, depending on the number of windows and the fabric.</li>
<li><strong>Made and installed</strong> by the Salford workshop, tracks included, until the final handover.</li>
</ol>
</section>
<section>
<h2>Recent curtain work in Kuwait</h2>
""" + gallery(CURTAIN_PHOTOS) + """
</section>""",
    faqs=[
        ("What is the difference between wave, roller and blackout curtains?", "Wave curtains are folded fabric with an elegant look for living rooms and majlis. Roller blinds are a single panel that rolls on one mechanism, ideal for practical spaces. Blackout is a dense fabric that blocks light almost completely, ideal for bedrooms."),
        ("How long does it take to make and install curtains?", "Usually 1 to 3 days, depending on the sizes, the number of windows and the availability of the fabric you choose."),
        ("Are tracks and installation included?", "Yes. We supply and fit the tracks and install the curtains, all the way to the final handover."),
        ("Can you match a fabric sample I already have?", "Yes. Give us your fabric sample and we will match the colour and material as closely as possible."),
        ("How much do roller blinds cost in Kuwait?", "Our roller blinds are 5 KD per square metre for plain, silver heat-reflective and blackout fabrics."),
        ("How much do wave or sheer curtains cost?", "It depends on the fabric, its weight and the size. We give you the final price in writing after the free home visit, with no obligation."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Custom curtains and blinds",
        "name": "Made-to-measure curtains in Kuwait",
        "provider": {"@id": f"{SITE}/#business"},
        "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": [
            {"@type": "Offer", "name": "Roller blinds", "priceCurrency": "KWD",
             "priceSpecification": {"@type": "UnitPriceSpecification", "price": 5, "priceCurrency": "KWD", "unitText": "square metre"}},
            {"@type": "Offer", "name": "Blackout curtains", "priceCurrency": "KWD",
             "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 14, "priceCurrency": "KWD", "unitText": "metre"}},
        ]}],
))

# ---- Blackout curtains
PAGES.append(dict(
    path="/en/blackout-curtains-kuwait.html", file="en/blackout-curtains-kuwait.html", ar="/sataer-blackout-kuwait.html",
    crumb="Blackout curtains", parent=("Curtains in Kuwait", "/en/curtains-kuwait.html"),
    title="Blackout Curtains in Kuwait — From 14 KD per Metre | Salford",
    desc="Made-to-measure blackout curtains in Kuwait from 14 KD per metre. Block light and summer heat in bedrooms. Free home measuring, installed in 1–3 days.",
    h1="Blackout curtains in Kuwait",
    lead="A dense, layered fabric that blocks as much outside light and heat as possible — unlike ordinary curtains, which only soften the light. Made to the size of each window, from <span class='price'>14 KD per metre</span>.",
    hero=("product_1786197817583_avoyf-small.webp", "Grey sun-blocking drapes with tiebacks over a white sheer, Hawally"),
    wa="Hello Salford, I'd like a quote for blackout curtains (from salfordkw.shop/en/blackout-curtains-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>14 KD</b><span>From, per metre</span></div><div class="stat"><b>1–3 days</b><span>Made and installed</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>
<section>
<h2>Why blackout curtains matter in a Kuwaiti summer</h2>
<p>Direct summer sun makes east- and west-facing rooms very hot, even behind ordinary curtains. A dense blackout layer reflects much of that sunlight before it enters the room, which eases the load on your air conditioning and keeps the room cooler for longer, especially around midday.</p>
<p>They are most useful in children's bedrooms, for people who work night shifts and sleep during the day, and in media rooms. They also suit living rooms and diwaniyas that face the street, cutting glare on screens and furniture while blocking the view from outside.</p>
</section>
<section>
<h2>Blackout curtain prices</h2>
<table>
<thead><tr><th>Item</th><th>Price or time</th></tr></thead>
<tbody>
<tr><td>Blackout fabric, made to measure</td><td class="price">from 14 KD per metre</td></tr>
<tr><td>Home measuring visit</td><td>free</td></tr>
<tr><td>One or a few standard windows</td><td>1 to 2 days</td></tr>
<tr><td>A whole room or several rooms</td><td>up to 3 days</td></tr>
</tbody>
</table>
<p>You get the final price in writing after the free visit. Pay by KNET, Wamd or cash.</p>
</section>
<section>
<h2>Types of blackout curtain we make</h2>
<p>"Blackout" describes the fabric, not the style. You choose the final look for your room:</p>
<ul>
<li><strong>Wave blackout</strong> — the opaque fabric sewn in even waves on a track. The most requested style for bedrooms and living rooms, with a neat hotel look.</li>
<li><strong>Blackout with sheer</strong> — two layers on a double track: the sheer for soft daylight with privacy, the blackout for full darkness. Ideal for a room used day and night.</li>
<li><strong>Plain blackout</strong> — a single opaque layer, the economical choice for bedrooms, storerooms and staff rooms.</li>
<li><strong>Heavy royal blackout</strong> — a heavier, richer fabric for diwaniyas and formal living rooms.</li>
<li><strong>Sun-blocking roller blind</strong> — the opaque fabric on a <a href="/en/roller-blinds-kuwait.html">roller blind</a>, lighter and better for small windows and kitchens.</li>
</ul>
<p>Colour does not decide how much light is blocked — the weave and the inner lining do. So blackout curtains come in many colours and patterns, not only black.</p>
</section>
<section>
<h2>Blackout or sun-blocking: what is the difference?</h2>
<p>The two names are often used interchangeably in Kuwait, but they do different jobs. Sun-blocking or dimming curtains reduce strong light and block the view from outside, but some light still comes through, especially at the edges. Blackout curtains are thicker and have an inner insulating layer designed to stop the light itself.</p>
<p>The simple rule: if you want privacy, dimming is enough. If you want to sleep in full darkness, choose blackout.</p>
</section>
<section>
<h2>How to choose the right level of darkness</h2>
<ul>
<li><strong>Bedroom facing direct sun or street lights</strong> — the darkest fabric available, fitted on a track wider than the window to reduce light at the sides.</li>
<li><strong>Children's room or inner bedroom</strong> — a medium level is usually enough and keeps the curtain light to open every day.</li>
<li><strong>Living room or diwaniya</strong> — the aim is to cut glare, not to make the room dark, so blackout with a sheer layer works best.</li>
</ul>
<p>We bring real fabric samples to the visit so you can compare them in your own light before deciding.</p>
</section>
<section>
<h2>Recent blackout and sun-blocking work</h2>
""" + gallery([
        ("product_1786198170852_7o0ir-small.webp", "Sun-blocking roller blind in a bedroom, Mahboula"),
        ("product_1786198315153_52wc7-small.webp", "Sun-blocking roller blinds in an office, Capital Governorate"),
        ("product_1786197817583_avoyf-small.webp", "Grey sun-blocking drapes over a white sheer, Hawally"),
        ("product_1786220498508_suibg-small.webp", "Grey wave drapes layered with a white sheer"),
    ]) + """
</section>""",
    faqs=[
        ("How much do blackout curtains cost in Kuwait?", "Our made-to-measure blackout curtains start from 14 KD per metre. You get the final price in writing after the free home visit."),
        ("Do blackout curtains block heat as well as light?", "Yes. The dense blackout layer reflects much of the direct sunlight before it enters the room, which keeps the room cooler and eases the load on the air conditioning."),
        ("Are blackout curtains only available in black?", "No. The darkness comes from the weave and the inner lining, not the colour, so they come in many colours and patterns."),
        ("Can I have blackout and sheer together?", "Yes. We fit both on a double track: the sheer for soft daylight and privacy, the blackout for full darkness."),
        ("How long does it take?", "One or a few standard windows take 1 to 2 days. A whole room or several rooms take up to 3 days."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Blackout curtains", "name": "Made-to-measure blackout curtains in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 14, "priceCurrency": "KWD", "unitText": "metre"}}}],
))

# ---- Roller blinds
PAGES.append(dict(
    path="/en/roller-blinds-kuwait.html", file="en/roller-blinds-kuwait.html", ar="/tafseel-sataer-rol.html",
    crumb="Roller blinds", parent=("Curtains in Kuwait", "/en/curtains-kuwait.html"),
    title="Roller Blinds in Kuwait — 5 KD per Square Metre | Salford",
    desc="Made-to-measure roller blinds in Kuwait: 5 KD per square metre for every fabric — standard, silver heat-reflective or sun-blocking. Installation included.",
    h1="Roller blinds in Kuwait, made to your window",
    lead="We cut each roller blind to the exact size of your window, in the fabric and colour you choose from real samples. One price for every fabric: <span class='price'>5 KD per square metre</span>, installation included.",
    hero=("product_1786198230102_2d8yi-small.webp", "Dark grey roller blinds made to measure, Rumaithiya"),
    wa="Hello Salford, I'd like a quote for roller blinds (from salfordkw.shop/en/roller-blinds-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>5 KD</b><span>Per square metre</span></div><div class="stat"><b>1–3 days</b><span>Made and installed</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>
<section>
<h2>Roller blind fabrics — all at the same price</h2>
<p>Every fabric costs 5 KD per square metre, so you choose by what the room needs, not by budget.</p>
<table>
<thead><tr><th>Fabric</th><th>What it does</th><th>Best for</th></tr></thead>
<tbody>
<tr><td>Standard roller</td><td>Blocks the view and lets soft light through</td><td>Living rooms and family rooms where you want privacy and daylight</td></tr>
<tr><td>Silver heat-reflective</td><td>A silver back reflects direct sun, cutting heat and screen glare</td><td>South- and west-facing windows, offices</td></tr>
<tr><td>Sun-blocking</td><td>A denser fabric that stops almost all light</td><td>Bedrooms and day sleepers</td></tr>
<tr><td>Linen-look roller</td><td>A natural fabric texture, closer to traditional curtains</td><td>Rooms where you want a softer look</td></tr>
</tbody>
</table>
<p>We bring samples of each fabric to your window, because a fabric looks very different in your own light than on a screen.</p>
</section>
<section>
<h2>Manual chain or electric motor</h2>
<p>We fit manual roller blinds with a side chain for simple daily use, and motorised blinds for remote control or a smart-home system. A motor makes most sense for high windows, large glass fronts, or a row of windows you want to open together. At the visit we check whether power can reach the window without building work, and explain the price difference before you decide.</p>
</section>
<section>
<h2>Roller blinds for offices and companies</h2>
<p>Roller blinds are one of the most requested options for offices: they take little space at the window, do not clash with desks against the wall, and give a uniform look across a whole facade. Silver heat-reflective fabric suits offices facing direct sun, cutting glare on computer screens while keeping natural light. For multi-window orders we measure every window separately, because a few centimetres of difference between windows is common.</p>
</section>
<section>
<h2>How it works</h2>
<ol>
<li><strong>Free visit</strong> — we measure each window or opening precisely.</li>
<li><strong>Choose fabric and colour</strong> from real samples.</li>
<li><strong>Made in our workshop</strong> to the exact measurement — non-standard and very wide windows are fine.</li>
<li><strong>Installed</strong> — usually about an hour per window, and several windows on the same visit. Offices and shops with many units take 1 to 2 days.</li>
</ol>
<p>The same team measures, makes and installs your blinds, which keeps measuring mistakes to a minimum.</p>
</section>
<section>
<h2>Recent roller blind work in Kuwait</h2>
""" + gallery([
        ("product_1786198230102_2d8yi-small.webp", "Dark grey roller blinds in a bedroom, Rumaithiya"),
        ("product_1786198365428_vaf21-small.webp", "Taupe roller blinds on corner windows in an office"),
        ("product_1786198038983_l25ke-small.webp", "Day-and-night blind on a sliding door, Salwa"),
        ("product_1786198082795_c7oqu-small.webp", "Grey day-and-night blind in a home office"),
        ("product_1786197982498_ekn0c-small.webp", "Day-and-night blind on a bathroom window, Hawally"),
        ("product_1786198170852_7o0ir-small.webp", "Sun-blocking roller blind in a bedroom, Mahboula"),
        ("product_1786198315153_52wc7-small.webp", "Grey roller blinds in an office, Capital Governorate"),
    ]) + """
</section>""",
    faqs=[
        ("How much do roller blinds cost in Kuwait?", "5 KD per square metre for every fabric — standard, silver heat-reflective, sun-blocking or linen-look. Installation is included."),
        ("How is the square metre calculated?", "We multiply the width by the height of the blind in metres. For example, a blind 2 m wide and 1.5 m high is 3 square metres. The exact price is confirmed in writing after the free visit."),
        ("Do you make motorised roller blinds?", "Yes. We fit manual chain blinds and electric motorised blinds, which can work with a remote or a smart-home system. We explain the price difference at the visit."),
        ("Can you install a roller blind I bought somewhere else?", "We mainly install blinds we make, so the track and size match exactly. For ready-made blinds, contact us first so we can check whether they can be installed to the same standard."),
        ("How long does it take?", "Making and installing usually takes 1 to 3 days depending on the number of windows. Fitting itself takes about an hour per window."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Roller blinds", "name": "Made-to-measure roller blinds in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "price": 5, "priceCurrency": "KWD", "unitText": "square metre"}}}],
))

# ---- Sheer curtains
PAGES.append(dict(
    path="/en/sheer-curtains-kuwait.html", file="en/sheer-curtains-kuwait.html", ar="/sataer-shifon-kuwait.html",
    crumb="Sheer curtains", parent=("Curtains in Kuwait", "/en/curtains-kuwait.html"),
    title="Sheer Curtains in Kuwait — Made to Measure | Salford",
    desc="Made-to-measure sheer (chiffon) curtains in Kuwait in soft silky Turkish fabric. Soft daylight with privacy for living rooms. Free measuring, tracks included.",
    h1="Sheer curtains in Kuwait",
    lead="A light, semi-transparent fabric that lets daylight in softly instead of blocking it — the right choice for living and reception rooms. Made to the size of your window, with tracks and installation included.",
    hero=("product_1786220577670_dz6ih-small.webp", "White sheer wave curtain made by Salford, Sabah Al-Salem"),
    wa="Hello Salford, I'd like a quote for sheer curtains (from salfordkw.shop/en/sheer-curtains-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>2–3 days</b><span>One window</span></div><div class="stat"><b>3–4 days</b><span>A whole room</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>
<section>
<h2>Soft light instead of full darkness</h2>
<p>Sheer curtains do the opposite job to <a href="/en/blackout-curtains-kuwait.html">blackout curtains</a>. Blackout is made for bedrooms that need full darkness; sheer is made for living and reception rooms that want soft natural light with a little privacy, without darkening the room during the day.</p>
</section>
<section>
<h2>Where sheer curtains work best</h2>
<p>Most often in living and reception rooms, where they soften the decor while keeping the room bright. They also work as a front layer over a heavier curtain — a <a href="/en/roller-blinds-kuwait.html">roller blind</a> or blackout. Open the heavy layer in the day and the sheer alone gives light privacy; close it at night.</p>
</section>
<section>
<h2>Our sheer fabric</h2>
<p>We use a silky, soft-touch Turkish fabric that reflects light gently rather than glaring. It usually comes in light and neutral colours that suit most interiors. It is lighter than wave or roller fabric, so it moves easily and makes the room feel lighter.</p>
<p>Do sheer curtains need a lining? Usually not, because their job is soft light. But if the window faces the street, or you want more privacy at night with the lights on, we recommend pairing it with a second layer that you close in the evening.</p>
</section>
<section>
<h2>Timing and payment</h2>
<table>
<thead><tr><th>Order</th><th>Made and installed in</th></tr></thead>
<tbody>
<tr><td>Sheer curtain for one window</td><td>2 to 3 days</td></tr>
<tr><td>Sheer curtains for a whole living room</td><td>3 to 4 days</td></tr>
</tbody>
</table>
<p>The price depends on the fabric and the size; you get it in writing after the free visit. Pay by KNET, Wamd or cash.</p>
</section>
<section>
<h2>Recent sheer curtain work in Kuwait</h2>
""" + gallery([
        ("product_1786220577670_dz6ih-small.webp", "White sheer wave curtain in a bedroom, Sabah Al-Salem"),
        ("product_1786220974971_4z3av-small.webp", "White sheer with lace edging on a double track, Jahra"),
        ("product_1786199839154_hqlc9-small.webp", "Beige drapes with a full-width sheer in a living room, Fahad Al-Ahmad"),
        ("product_1786198933149_374vc-small.webp", "Patterned grey drapes over a lace-edged sheer, Mangaf"),
        ("product_1786382432376_ijsgz-small.webp", "Brown drape with a tasselled tieback over a sheer, Sulaibikhat"),
        ("product_1786197567265_jz8bl-small.webp", "Gold velvet drapes over a white swag sheer, Khaitan"),
    ]) + """
</section>""",
    faqs=[
        ("What is the difference between sheer and blackout curtains?", "Sheer is a light, see-through fabric that lets soft light in. Blackout is a dense, opaque fabric that blocks light almost completely and suits bedrooms."),
        ("Do sheer curtains block the view from outside during the day?", "They give light privacy during the day but are not opaque. For more privacy with natural light, pair them with a roller or wave curtain."),
        ("Can I use sheer curtains in a bedroom?", "Yes, as a decorative extra layer, but not on their own — they do not give enough darkness for sleeping compared with blackout."),
        ("What colours are available?", "Light and neutral colours are the most available and popular because they suit most interiors. We bring the real samples to the visit."),
        ("How long does it take to make and install sheer curtains?", "Usually 2 to 3 days for one window and up to 4 days for a whole living room."),
    ],
))

SOFA_PHOTOS = {
    "beige": ("product_1786196106227_tntws-small.webp", "Beige modern sofas with brown cushions in a formal living room"),
    "white_l": ("product_1786196266520_sd8ih-small.webp", "White L-shaped corner sofa made to fit the room"),
    "channel": ("product_1786196403904_3aq2d-small.webp", "Beige channel-stitched sofa set in a living room"),
    "cream": ("product_1786220875517_rmxk5-small.webp", "Cream tufted corner sofa, West Abdullah Al-Mubarak"),
    "navy": ("product_1786220770321_lknst-small.webp", "Navy blue L-shaped velvet sofa with gold legs"),
    "grey": ("product_1786196493883_huspb-small.webp", "Long grey reception sofa along the wall, Salwa"),
}
SOFA_COMPARE = """<section>
<h2>Upholstery, slipcovers or a new sofa?</h2>
<p>These are three different jobs with different prices. People often mix them up:</p>
<table>
<thead><tr><th>Service</th><th>What it involves</th><th>Price</th></tr></thead>
<tbody>
<tr><td><a href="/en/sofa-upholstery-kuwait.html">Re-upholstery</a></td><td>Strip the fabric and filling, replace the foam, re-cover</td><td class="price">18–28 KD per metre</td></tr>
<tr><td><a href="/en/sofa-slipcovers-kuwait.html">Slipcovers</a></td><td>New fabric fitted over the existing filling, without stripping it</td><td class="price">10–18 KD per metre</td></tr>
<tr><td><a href="/en/custom-sofas-kuwait.html">Custom sofa</a></td><td>A new sofa built from scratch to your measurements</td><td class="price">from 33 KD per metre</td></tr>
</tbody>
</table>
<p>The simple rule: sit on the sofa. If it is still comfortable and firm, slipcovers are enough. If you sink in or feel the wooden frame, the problem is inside and you need full re-upholstery. If the frame itself is damaged, or you want a different size or shape, a new custom sofa is the answer. At the visit we tell you honestly which one suits your sofa — even when it is the cheaper option.</p>
<p>Prices are per metre of fabric used. You get the full price in writing after the free visit, and it does not change during the work.</p>
</section>"""

# ---- Sofa upholstery
PAGES.append(dict(
    path="/en/sofa-upholstery-kuwait.html", file="en/sofa-upholstery-kuwait.html", ar="/tanjeed-kanab.html",
    crumb="Sofa upholstery",
    title="Sofa Upholstery in Kuwait — 18–28 KD per Metre | Salford",
    desc="Sofa re-upholstery in Kuwait from 18 to 28 KD per metre: new fabric and new foam on your existing frame. Free home visit, free pickup and return, 3–5 days.",
    h1="Sofa upholstery in Kuwait",
    lead="Renew the sofa you already have instead of buying a new set. If the wooden frame is sound but the fabric is worn or the foam has sagged, re-upholstery brings back the comfort of a new sofa for much less. From <span class='price'>18 to 28 KD per metre</span>, depending on the fabric.",
    hero=SOFA_PHOTOS["channel"],
    wa="Hello Salford, I'd like a quote for sofa upholstery (from salfordkw.shop/en/sofa-upholstery-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>18–28 KD</b><span>Per metre</span></div><div class="stat"><b>3–5 days</b><span>Full sofa set</span></div><div class="stat"><b>Free</b><span>Pickup and return</span></div></div>
<section>
<h2>What full re-upholstery includes</h2>
<p>We do not just change the outer cover. We take the sofa apart piece by piece, replace the old foam with first-grade Al-Baghli foam suited to each part — seat, back and arms — then cut and sew the new fabric onto the frame in our own workshop. The result is a sofa that is properly comfortable again, not only better looking.</p>
</section>
<section>
<h2>Every sofa shape</h2>
<p>We upholster standard sofas, L-shaped corner sofas, modular sofas and full reception sets of 3 or 4 pieces. Each piece of a corner set is measured and upholstered separately so the colour and filling match perfectly when it is put back together.</p>
<p>We also upholster gunfat (floor sofas), diwaniya seating, back cushions, chairs and fabric-covered tables. If you have several pieces in one home, do them in the same round: fabric batches vary slightly in colour when they are bought months apart.</p>
</section>
<section>
<h2>Fabrics</h2>
<p>We bring real fabric samples to your home: durable Turkish chenille for formal reception sofas, and stain- and wear-resistant fabrics for family living rooms, especially with children. You can also choose a colour close to the current one if you want to keep your room as it is.</p>
</section>
<section>
<h2>How long it takes</h2>
<table>
<thead><tr><th>Job</th><th>Time</th></tr></thead>
<tbody>
<tr><td>Single two-seater sofa</td><td>2 to 3 days</td></tr>
<tr><td>Full sofa set (3–4 pieces)</td><td>3 to 5 days</td></tr>
<tr><td>L-shaped corner sofa</td><td>4 to 6 days</td></tr>
</tbody>
</table>
<p>Full re-upholstery is done in our workshop, because the piece has to be taken apart. We collect and return your sofa free of charge and put it back in place. Measuring and choosing fabric happen at your home first. Pay by KNET, Wamd or cash.</p>
</section>
""" + SOFA_COMPARE + """
<section>
<h2>Sofas we have made and upholstered</h2>
""" + gallery([SOFA_PHOTOS[k] for k in ("channel", "beige", "white_l", "cream", "navy", "grey")]) + """
</section>""",
    faqs=[
        ("How much does sofa upholstery cost in Kuwait?", "From 18 to 28 KD per metre depending on the fabric, including new fabric and new foam. The total depends on the number of metres and the size of the sofa. We give you a fixed final price after the free home visit."),
        ("Can you re-upholster L-shaped corner sofas?", "Yes. We cover standard, L-shaped and modular sofas. Each piece of a corner set is measured and upholstered separately so the fabric and filling match."),
        ("Does upholstery include replacing the foam?", "Yes. Full upholstery always replaces the old foam with first-grade Al-Baghli foam, because sagging foam is the most common reason a sofa becomes uncomfortable."),
        ("Do you upholster at my home or in the workshop?", "In our workshop, because the sofa has to be taken apart. We collect and return it free of charge and set it back in place."),
        ("Should I re-upholster or buy a new sofa?", "If the wooden frame is sound, re-upholstery is cheaper and faster and feels almost like new. If the frame is damaged, a new custom sofa is the better choice."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Sofa upholstery", "name": "Sofa re-upholstery in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 18, "maxPrice": 28, "priceCurrency": "KWD", "unitText": "metre"}}}],
))

# ---- Custom sofas
PAGES.append(dict(
    path="/en/custom-sofas-kuwait.html", file="en/custom-sofas-kuwait.html", ar="/tafseel-kanab-kuwait.html",
    crumb="Custom sofas",
    title="Custom Sofas in Kuwait — Made to Measure | Salford",
    desc="Custom sofas and living room sets made to measure in Kuwait, from 33 KD per metre: modern, corner and reception sofas in beech or walnut frames. Ready in 12–15 days.",
    h1="Custom sofas in Kuwait, made to measure",
    lead="Ready-made sofas come in fixed sizes, so they are either too big for the room or leave awkward gaps. We measure your actual space and build the sofa to fit it, in the fabric, foam and wood you choose. From <span class='price'>33 KD per metre</span>.",
    hero=SOFA_PHOTOS["white_l"],
    wa="Hello Salford, I'd like a quote for a custom sofa (from salfordkw.shop/en/custom-sofas-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>33 KD</b><span>From, per metre</span></div><div class="stat"><b>12–15 days</b><span>Made and delivered</span></div><div class="stat"><b>Free</b><span>Home measuring</span></div></div>
<section>
<h2>What we make</h2>
<ul>
<li>Modern sofas and full sofa sets</li>
<li>L-shaped corner sofas, built to fit both walls of your corner</li>
<li>Gunfat-style low sofas</li>
<li>Reception sofas, and complete reception rooms with matching coffee tables</li>
</ul>
<p>Everything is built in the Salford workshop — no middleman — so we control the foam thickness, the stitching and the strength of the frame directly.</p>
</section>
<section>
<h2>The materials that make the difference</h2>
<table>
<thead><tr><th>Part</th><th>What we use</th></tr></thead>
<tbody>
<tr><td>Foam</td><td>Kuwaiti Al-Baghli foam, including the stamped pink grade where extra firmness is needed. Seat foam is denser than back foam, so the sofa does not sag after months of daily use.</td></tr>
<tr><td>Fabric</td><td>Turkish chenille is the most popular for its durability, with silky chenille for a richer look. Liquid-resistant fabrics are available for homes with children or frequent guests.</td></tr>
<tr><td>Frame</td><td>Beech or walnut wood, depending on the design. The frame decides how long the sofa really lasts — fabric can be changed later, a weak frame cannot be fixed.</td></tr>
</tbody>
</table>
</section>
<section>
<h2>Corner sofas and difficult spaces</h2>
<p>Corner sofas are among the most requested custom pieces, because ready-made ones rarely match the corner of a room exactly. We measure both walls and the right seat height, and build the sofa to sit in the corner with no gap and without blocking the way through. The same applies to long, narrow living rooms and irregular entrances.</p>
<p>Many customers order the whole room at once: reception sofas with matching coffee tables, or sofas that match an existing majlis or diwaniya. Give us a sample of the existing fabric and we will match the colour and texture as closely as possible.</p>
</section>
<section>
<h2>How it works</h2>
<ol>
<li><strong>Free visit</strong> — usually within a day or two of your request. We bring the tape measure and fabric and foam samples.</li>
<li><strong>Agreement</strong> — you choose the fabric and design, and get the full price and timing before we start.</li>
<li><strong>Made in our workshop</strong> — 12 to 15 days, including the wooden frame, foam, upholstery and sewing.</li>
<li><strong>Delivery and installation</strong> in place, anywhere in Kuwait.</li>
</ol>
</section>
""" + SOFA_COMPARE + """
<section>
<h2>Custom sofas we have made</h2>
""" + gallery([SOFA_PHOTOS[k] for k in ("white_l", "navy", "beige", "cream", "channel", "grey")]) + """
</section>""",
    faqs=[
        ("How much does a custom sofa cost in Kuwait?", "Our custom sofas start from 33 KD per metre, whether modern, corner, gunfat or reception sofas. The final price depends on the metres, fabric, foam and wood, and is confirmed after measuring with no obligation."),
        ("How long does it take to make a custom sofa?", "12 to 15 days from the agreement date, including the frame, foam, upholstery and installation in place. We confirm the exact time after measuring."),
        ("What foam, fabric and wood do you use?", "Kuwaiti Al-Baghli foam (including the stamped pink grade), Turkish chenille or silky chenille fabric, with liquid-resistant options, and beech or walnut frames."),
        ("Can you make a corner sofa for a specific space?", "Yes. We measure both walls and the seat height and build the sofa to fit the corner exactly, without gaps or blocking the walkway."),
        ("Can you make a sofa that matches my existing majlis?", "Yes. We take a sample of the existing fabric to match the colour and texture, and match the seat height so the pieces look consistent."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Custom sofas", "name": "Made-to-measure sofas in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 33, "priceCurrency": "KWD", "unitText": "metre"}}}],
))

# ---- Sofa slipcovers
PAGES.append(dict(
    path="/en/sofa-slipcovers-kuwait.html", file="en/sofa-slipcovers-kuwait.html", ar="/talbees-kanab-kuwait.html",
    crumb="Sofa slipcovers",
    title="Sofa Slipcovers in Kuwait — 10–18 KD per Metre | Salford",
    desc="Tailored sofa slipcovers in Kuwait from 10 to 18 KD per metre: new fabric over your existing filling. Faster and cheaper than re-upholstery, done in 2–3 days.",
    h1="Sofa slipcovers in Kuwait",
    lead="A new fabric cover fitted over your sofa's existing filling, without stripping it. It is faster and noticeably cheaper than full upholstery — the right choice when the foam is still good. From <span class='price'>10 to 18 KD per metre</span>.",
    hero=SOFA_PHOTOS["cream"],
    wa="Hello Salford, I'd like a quote for sofa slipcovers (from salfordkw.shop/en/sofa-slipcovers-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>10–18 KD</b><span>Per metre</span></div><div class="stat"><b>2–3 days</b><span>Full sofa set</span></div><div class="stat"><b>Free</b><span>Home visit</span></div></div>
<section>
<h2>When slipcovers are the right choice</h2>
<p>If the sofa is still comfortable and the foam has kept its shape, but the outer fabric is the problem — faded, lightly torn, or you are simply tired of the colour — a slipcover fixes it in the least time and at the lowest cost, without opening the sofa.</p>
<p>At the visit we check the filling under the current fabric. If the foam is damaged, we tell you honestly that <a href="/en/sofa-upholstery-kuwait.html">full upholstery</a> is the better long-term investment, rather than covering an internal problem.</p>
</section>
<section>
<h2>How it is done</h2>
<p>You choose the new fabric from real samples — a completely different colour and texture if you like. We cut it in our workshop to the exact dimensions of your sofa, so the new cover is tight and neat, never loose. If we notice small problems during the visit, such as a loose spring or a wobbly wooden corner, we can usually fix them in the same job without a large extra cost.</p>
<table>
<thead><tr><th>Job</th><th>Time</th></tr></thead>
<tbody>
<tr><td>A chair or a single piece</td><td>1 to 2 days</td></tr>
<tr><td>Full sofa set (3-2-1)</td><td>2 to 3 days</td></tr>
</tbody>
</table>
<p>Pay by KNET, Wamd or cash.</p>
</section>
""" + SOFA_COMPARE + """
<section>
<h2>Sofa work by Salford</h2>
""" + gallery([SOFA_PHOTOS[k] for k in ("cream", "grey", "beige", "navy")]) + """
</section>""",
    faqs=[
        ("What is the difference between slipcovers and upholstery?", "Slipcovers put new fabric over the existing filling without stripping it, from 10 to 18 KD per metre. Full upholstery strips the fabric and filling and replaces the foam, from 18 to 28 KD per metre."),
        ("Are slipcovers suitable for every sofa?", "Only when the filling and foam under the current fabric are still in good condition. If the foam is damaged or sagging, we recommend full upholstery."),
        ("How long does it take to slipcover a full sofa set?", "Usually 2 to 3 days for a full 3-2-1 set, and less for a single piece."),
        ("Can I choose a completely different fabric?", "Yes. You choose the new fabric from real samples, in a completely different colour and texture if you wish."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Sofa slipcovers", "name": "Tailored sofa slipcovers in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 10, "maxPrice": 18, "priceCurrency": "KWD", "unitText": "metre"}}}],
))

CARPET_PHOTOS = {
    "agadir": ("سجاد-تركي-اكادير-سالفورد-small.webp", "Agadir range of Turkish carpet samples in beige, brown and grey"),
    "marrakesh": ("سجاد-تركي-مراكش-سالفورد-small.webp", "Marrakesh range of soft Turkish carpet samples"),
    "nabel": ("سجاد-تركي-نابل-سالفورد-small.webp", "Nabel range of Turkish carpet samples"),
    "loop": ("سجاد-تركي-فندقي-سالفورد-small.webp", "Hotel-grade loop-pile carpet samples"),
    "geo05": ("سجاد-تركي-سالفورد-05-small.webp", "Patterned Turkish carpet samples with geometric designs"),
    "geo06": ("سجاد-تركي-سالفورد-06-small.webp", "Heavy-pile patterned carpet samples for majlis rooms"),
    "majlis_motif": ("سجاد-تركي-سالفورد-07-small.webp", "Blue-grey wall-to-wall carpet with a carved centre motif in a majlis"),
    "fit_majlis": ("tarkib-sajjad-1-small.webp", "Grey wall-to-wall carpet fitted in a majlis with floor seating"),
    "fit_room": ("tarkib-sajjad-2-small.webp", "Carpet fitted across a whole room"),
    "fit_edge": ("tarkib-sajjad-3-small.webp", "Clean carpet edge finished against a marble floor"),
    "carved_medallion": ("product_1786197423291_fvwuq-small.webp", "Hand-carved arabesque medallion carpet, Al-Rabiya"),
    "carved_border": ("product_1786199578906_qwb31-small.webp", "Hand-carved geometric border on a cream majlis carpet"),
    "mosque_blue": ("sajjad-masjid-01-small.webp", "Blue mosque carpet with gold prayer-row lines"),
    "mosque_red": ("sajjad-masjid-02-small.webp", "Red mosque carpet with gold prayer rows"),
    "mosque_roll": ("sajjad-masjid-03-small.webp", "Red mosque carpet roll with patterned row borders"),
    "prayer_rug": ("sajjad-musalla-02-small.webp", "Single prayer rug with a blue mihrab design"),
}

# ---- Carpets (hub)
PAGES.append(dict(
    path="/en/carpets-kuwait.html", file="en/carpets-kuwait.html", ar="/sajjad.html",
    crumb="Carpets in Kuwait",
    title="Carpets in Kuwait — Turkish Carpet, Cut & Fitted | Salford",
    desc="Turkish carpet and wall-to-wall moquette in Kuwait, imported from Bursa mills. From 11 KD per metre, cut to size and installed in one day. Free home measuring.",
    h1="Carpets in Kuwait — Turkish carpet, cut to size and fitted",
    lead="We import our carpet directly from mills in Bursa, Turkey, cut it to the exact shape of your room, majlis or office, and fit it — usually in a single day. Carpet starts from <span class='price'>11 KD per metre</span>, with free home measuring anywhere in Kuwait.",
    hero=CARPET_PHOTOS["fit_majlis"],
    wa="Hello Salford, I'd like a quote for carpet (from salfordkw.shop/en/carpets-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>11 KD</b><span>From, per metre</span></div><div class="stat"><b>1 day</b><span>Typical fitting</span></div><div class="stat"><b>790+</b><span>Projects since 2016</span></div></div>
<section>
<h2>Carpet prices in Kuwait</h2>
<p>Our carpet is priced per metre of roll, depending on the type and pile. Mosque carpet is the exception: it is priced per square metre. You get a written quote after the free visit.</p>
<table>
<thead><tr><th>Carpet</th><th>Price</th><th>Unit</th></tr></thead>
<tbody>
<tr><td>Turkish moquette (wall-to-wall carpet)</td><td class="price">from 11 KD</td><td>per metre</td></tr>
<tr><td>Medium-pile carpet for offices and corridors</td><td class="price">from about 13 KD</td><td>per metre</td></tr>
<tr><td>Standard Turkish carpet by the metre, straight from the roll</td><td class="price">from about 13 KD</td><td>per metre</td></tr>
<tr><td>High-pile luxury carpet for majlis rooms</td><td>depends on type and thickness</td><td>quoted after the visit</td></tr>
<tr><td><a href="/en/mosque-carpet-kuwait.html">Mosque and prayer-room carpet</a></td><td class="price">7.5–9 KD</td><td>per square metre, installed</td></tr>
<tr><td>Fitting only, for carpet bought elsewhere</td><td>10–35 KD</td><td>per job, by area and location</td></tr>
</tbody>
</table>
<p>When you buy and have the carpet cut by us, fitting is part of the order and is not charged as a separate job. Hand-carved patterns are priced separately from the carpet itself.</p>
</section>
<section>
<h2>Why Turkish carpet from Bursa</h2>
<p>We import exclusive carpet ranges that are not available elsewhere in Kuwait, made in the mills of Bursa, Turkey. Their denser weave and more stable colours mean a longer life before matting or fading — which matters most in majlis rooms and other heavily used spaces. Density (threads per centimetre) matters more than pile length alone in how long a carpet lasts.</p>
</section>
<section>
<h2>Choosing the right carpet for each space</h2>
<table>
<thead><tr><th>Space</th><th>What works best</th></tr></thead>
<tbody>
<tr><td>Majlis and diwaniya</td><td>High-pile, dense carpet — comfortable to sit on and good at absorbing sound</td></tr>
<tr><td>Bedrooms</td><td>Medium to high pile, balancing softness underfoot with easy care</td></tr>
<tr><td>Offices and shops</td><td>Medium to low pile that handles daily foot traffic and is quick to vacuum</td></tr>
<tr><td>Corridors and stairs</td><td>A hard-wearing carpet where durability matters more than softness</td></tr>
</tbody>
</table>
<p>Plain carpet in a single colour suits almost any interior. A large flowing pattern works as the centrepiece of a big living room. For something unique, a pattern can be hand-carved into the carpet after it is cut to your room.</p>
</section>
<section>
<h2>Cut to size, or bought by the metre?</h2>
<ul>
<li><strong>Cut to size and fitted</strong> — we measure the exact shape of your room or majlis, cut the carpet to it, finish the edges cleanly against the tiles or marble, and fit it. This is right for rooms where you want full, wall-to-wall coverage.</li>
<li><strong>By the metre from the roll</strong> — the length you need, cut straight from a standard roll with no final shaping. It is faster and suits stairs, long corridors, offices, exhibitions and short-term events. You can buy small amounts, such as 3 or 5 metres, without taking a whole roll.</li>
</ul>
</section>
<section>
<h2>How carpet fitting works</h2>
<ol>
<li><strong>Free visit</strong> — we measure your space and bring carpet samples in different piles and thicknesses.</li>
<li><strong>Floor preparation</strong> — we clean the floor and remove old adhesive or carpet, because any grit under the carpet shows as a bump after a few weeks.</li>
<li><strong>Laying</strong> — the carpet is unrolled and allowed to relax before it is fixed, especially if it was folded in storage.</li>
<li><strong>Fixing and finishing</strong> — edges are fixed and doorways are finished so nobody trips moving between rooms. On stairs every step is cut and fixed separately, with the pile running downwards.</li>
</ol>
<p>Fitting is usually done the same day or the next day after the visit.</p>
</section>
<section>
<h2>Commercial carpet projects</h2>
<p>We carry out carpet projects by the metre for large spaces, not only single rooms: hotels and serviced apartments, mosques, offices and companies, wedding halls and large diwaniyas. Hotel-grade carpet differs from home carpet in two ways: a denser weave for constant traffic, and colour that holds under strong lighting.</p>
<p>For a project we measure on site, then quote per metre including supply, cutting and fitting, with a better rate for larger areas. Fitting can be done outside working hours so your business is not interrupted. Send us the approximate area and type of building on WhatsApp for a first quote.</p>
</section>
<section>
<h2>See the samples in person</h2>
<p>Pile weight and softness are much easier to judge by touch than in photos. You can see our carpet samples at our carpet store in Al-Dajeej, or we bring them to your home on the free measuring visit.</p>
</section>
<section>
<h2>Our carpet ranges and recent fitting work</h2>
""" + gallery([CARPET_PHOTOS[k] for k in ("majlis_motif", "fit_room", "carved_medallion", "carved_border", "agadir", "marrakesh", "loop", "fit_edge")]) + """
</section>""",
    faqs=[
        ("How much does carpet cost per metre in Kuwait?", "Our Turkish moquette starts from 11 KD per metre, and standard carpet by the metre from about 13 KD, depending on type and pile. Mosque carpet is 7.5 to 9 KD per square metre. You get the exact price after the free visit."),
        ("What is the difference between a linear metre and a square metre of carpet?", "A linear metre is one metre of length cut from the roll, at the full width of that roll. A square metre is an area of one metre by one metre. Most of our carpet is priced per linear metre; mosque carpet is priced per square metre."),
        ("How long does carpet installation take?", "Usually one day. Fitting is normally done the same day or the day after the measuring visit, depending on the area."),
        ("Do you fit carpet I bought from another shop?", "Yes. Fitting only costs 10 to 35 KD depending on the area and location. If you buy and have the carpet cut by us, fitting is included in the order."),
        ("Can I buy a small amount of carpet, like 3 or 5 metres?", "Yes. Buying by the metre lets you take exactly what you need, without buying a whole roll, for example for a small staircase or a short corridor."),
        ("Do you supply carpet for hotels, offices and mosques?", "Yes. We supply and fit carpet by the metre for hotels, serviced apartments, offices, mosques, wedding halls and large diwaniyas, with on-site measuring and a per-metre project quote."),
        ("What is the difference between modern and classic carpet?", "Classic carpet has traditional patterns and warm colours for heritage-style interiors. Modern carpet has simple designs and neutral colours for contemporary interiors. We offer both in Turkish quality."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Carpet supply and installation", "name": "Turkish carpet cut to size and fitted in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": [
            {"@type": "Offer", "name": "Turkish moquette", "priceCurrency": "KWD",
             "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 11, "priceCurrency": "KWD", "unitText": "metre"}},
            {"@type": "Offer", "name": "Mosque carpet", "priceCurrency": "KWD",
             "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 7.5, "maxPrice": 9, "priceCurrency": "KWD", "unitText": "square metre"}}]}],
))

# ---- Mosque carpet
PAGES.append(dict(
    path="/en/mosque-carpet-kuwait.html", file="en/mosque-carpet-kuwait.html", ar="/sajjad-masjid-kuwait.html",
    crumb="Mosque carpet", parent=("Carpets in Kuwait", "/en/carpets-kuwait.html"),
    title="Mosque Carpet in Kuwait — 7.5–9 KD per Square Metre | Salford",
    desc="Mosque and prayer-room carpet in Kuwait with prayer-row designs, 7.5 to 9 KD per square metre installed. Qibla direction measured on site, free visit.",
    h1="Mosque and prayer-room carpet in Kuwait",
    lead="Carpet with prayer-row designs for mosques, home prayer rooms and office musallas, cut to your space and aligned to the qibla. From <span class='price'>7.5 to 9 KD per square metre</span>, installed, with a free measuring visit.",
    hero=CARPET_PHOTOS["mosque_red"],
    wa="Hello Salford, I'd like a quote for mosque carpet (from salfordkw.shop/en/mosque-carpet-kuwait.html)",
    body="""<div class="stats"><div class="stat"><b>7.5–9 KD</b><span>Per square metre</span></div><div class="stat"><b>Free</b><span>Measuring visit</span></div><div class="stat"><b>All Kuwait</b><span>Mosques and musallas</span></div></div>
<section>
<h2>The row pattern is not decoration — it organises the prayer</h2>
<p>Mosque carpet works differently from any other carpet. Its long running pattern marks the prayer rows, so worshippers line up neatly without extra lines or reminders. The row width gives each person comfortable room to prostrate, which is why the qibla direction is measured before anything is cut.</p>
</section>
<section>
<h2>Mosque, prayer room or single prayer rug</h2>
<ul>
<li><strong>Mosque carpet</strong> — wide rolls laid over large areas with a repeating row pattern, cut to the prayer hall.</li>
<li><strong>Prayer-room carpet</strong> — for smaller spaces such as a home musalla, a prayer room in an office or company, or a women's prayer area, cut to the exact room with finished edges.</li>
<li><strong>Single prayer rugs</strong> — one piece with or without a mihrab, for personal use, gifts or distribution.</li>
</ul>
<p>Carpet with printed mihrabs is the most requested for mosques, because each mihrab marks one worshipper's place. Plain carpet with printed row lines suits smaller prayer rooms in offices and schools, where the number of people changes.</p>
</section>
<section>
<h2>Colours and material</h2>
<p>Red and blue are the most requested colours for mosques: they hide heavy use and give the space dignity. The material has a dense pile to withstand repeated prostration and daily traffic, and resists crushing, so it keeps its shape in the front rows where it is used most.</p>
</section>
<section>
<h2>Qibla, measuring and installation</h2>
<p>The most important step is setting the qibla direction precisely, because the carpet is cut and fixed along it and cannot be turned afterwards. We measure on site, work out how many rows fit, and leave the right space at entrances and around any columns. In large mosques every piece is cut with the pile running the same way; otherwise the colour looks different from one piece to the next under the same light.</p>
<p>We recommend extra-dense, crush-resistant carpet at the entrances and in the first row, and place the joins between pieces away from direct foot traffic wherever possible. Installation includes fixing the edges and the transitions at doors and around the mihrab.</p>
</section>
<section>
<h2>Mosque carpet and prayer rugs we supply</h2>
""" + gallery([CARPET_PHOTOS[k] for k in ("mosque_red", "mosque_blue", "mosque_roll", "prayer_rug")]) + """
</section>""",
    faqs=[
        ("How much does mosque carpet cost in Kuwait?", "Our mosque carpet costs 7.5 to 9 KD per square metre, including installation. Measuring and the site visit are free."),
        ("Why is mosque carpet priced per square metre?", "Because it is laid across the whole prayer hall and cut to its area, so it is calculated on the area covered rather than the length of the roll."),
        ("How do you align the carpet with the qibla?", "We set the qibla direction on site before cutting. The carpet is cut and fixed along it, because it cannot be rotated once installed."),
        ("Do you supply prayer-room carpet for offices and homes?", "Yes. We cut carpet to the exact size of home musallas, office and company prayer rooms, and women's prayer areas, with finished edges."),
        ("Do you sell single prayer rugs?", "Yes, with or without a mihrab, for personal use, gifts or distribution."),
    ],
    extra_ld=[{
        "@context": "https://schema.org", "@type": "Service", "inLanguage": "en",
        "serviceType": "Mosque carpet", "name": "Mosque and prayer-room carpet in Kuwait",
        "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "Kuwait"},
        "offers": {"@type": "Offer", "priceCurrency": "KWD",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": 7.5, "maxPrice": 9, "priceCurrency": "KWD", "unitText": "square metre"}}}],
))

# ---- About
PAGES.append(dict(
    path="/en/about.html", file="en/about.html", ar="/about.html", crumb="About Salford",
    title="About Salford — Furnishings in Kuwait since 2016",
    desc="Salford is a Kuwait furnishings business founded in 2016, with over 790 completed projects: curtains, sofas, upholstery, majlis seating and Turkish carpets.",
    h1="About Salford Furniture & Furnishings",
    lead="Salford was founded in Kuwait in 2016. Since then we have completed more than 790 projects for homes and businesses across the country.",
    wa="Hello Salford, I'd like to ask about your services (from salfordkw.shop/en/about.html)",
    body=STATS + """
<section>
<h2>Who we are</h2>
<p>Salford is an online furnishings store with its own workshop. Every order — from carpet installation to majlis seating, upholstery and curtains — is handled by our team, from the first measuring visit to the final handover.</p>
<p>We import exclusive carpet ranges directly from mills in Bursa, Turkey. They are dense and soft, and last longer than many carpets found in the local market.</p>
</section>
<section>
<h2>Our services</h2>
<ul>
<li><a href="/en/curtains-kuwait.html">Curtains and blinds</a> — wave, blackout, sheer and roller.</li>
<li><a href="/en/custom-sofas-kuwait.html">Sofas made to measure</a>, <a href="/en/sofa-upholstery-kuwait.html">re-upholstery</a> and <a href="/en/sofa-slipcovers-kuwait.html">slipcovers</a>.</li>
<li>Arabic majlis seating and back cushions.</li>
<li><a href="/en/carpets-kuwait.html">Turkish carpets</a>, carpet by the metre and <a href="/en/mosque-carpet-kuwait.html">mosque carpet</a>.</li>
<li>Artificial grass for gardens and outdoor spaces.</li>
</ul>
</section>
<section>
<h2>Working with us</h2>
<ul>
<li><strong>Coverage:</strong> delivery and installation in every area of Kuwait.</li>
<li><strong>Hours:</strong> every day, 10 am to 9 pm.</li>
<li><strong>Phone and WhatsApp:</strong> <a href="tel:+96555943343">+965 5594 3343</a>.</li>
<li><strong>Payment:</strong> KNET, Wamd, cash or bank transfer.</li>
</ul>
</section>""",
))

# ---- FAQ
PAGES.append(dict(
    path="/en/faq.html", file="en/faq.html", ar="/faq.html", crumb="FAQ",
    title="FAQ — Payment, Delivery & Timing | Salford Kuwait",
    desc="Answers about ordering from Salford in Kuwait: payment methods, delivery areas, how long each service takes, warranty and free home measuring.",
    h1="Frequently asked questions",
    lead="General questions about ordering from Salford. Questions about a specific service are answered on that service's page.",
    wa="Hello Salford, I have a question (from salfordkw.shop/en/faq.html)",
    body="",
    faqs=[
        ("What payment methods do you accept?", "We accept KNET, Wamd, cash and bank transfer. All prices are in Kuwaiti dinars."),
        ("Do you cover all areas of Kuwait?", "Yes. We deliver and install in every area of Kuwait, including Hawally, Salmiya, Farwaniya, Ahmadi, Jahra, Mubarak Al-Kabeer and Kuwait City."),
        ("How long does an order take?", "It depends on the service: carpet installation takes one day, curtains 1 to 3 days, back cushions 3 days, and wooden majlis seating about 15 days. Upholstery depends on the size of the piece."),
        ("Is there a warranty?", "The warranty depends on the service and the materials used, and is agreed with you when you order."),
        ("How do I book a measuring visit or get a quote?", "Message us on WhatsApp or call +965 5594 3343. We visit to take measurements and inspect the space, free of charge."),
        ("How long has Salford been in business?", "Salford was founded in 2016 and has completed more than 790 projects in Kuwait since then."),
    ],
))

# ---- Contact
PAGES.append(dict(
    path="/en/contact.html", file="en/contact.html", ar="/contact.html", crumb="Contact",
    title="Contact Salford Kuwait — WhatsApp & Phone +965 5594 3343",
    desc="Contact Salford Furniture & Furnishings in Kuwait by WhatsApp or phone on +965 5594 3343. Open daily 10 am to 9 pm, free home measuring across Kuwait.",
    h1="Contact Salford",
    lead="The fastest way to reach us is WhatsApp. Send a photo of your space and we will reply with options and book a free measuring visit.",
    wa="Hello Salford, I'd like to book a free measuring visit (from salfordkw.shop/en/contact.html)",
    body="""<section>
<h2>Ways to reach us</h2>
<ul>
<li><strong>WhatsApp and phone:</strong> <a href="tel:+96555943343">+965 5594 3343</a></li>
<li><strong>Hours:</strong> every day, 10 am to 9 pm</li>
<li><strong>Instagram:</strong> <a href="https://www.instagram.com/salforad/" target="_blank" rel="noopener">@salforad</a></li>
<li><strong>TikTok:</strong> <a href="https://www.tiktok.com/@salford_kuwait" target="_blank" rel="noopener">@salford_kuwait</a></li>
</ul>
<p>We come to you: delivery, measuring and installation are available in every area of Kuwait.</p>
</section>""",
))


def main():
    os.makedirs(os.path.join(ROOT, "en"), exist_ok=True)
    for p in PAGES:
        out = os.path.join(ROOT, p["file"])
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(p))
        print("wrote", p["file"])
    # list for link_en.py
    pairs = [{"en": p["path"], "ar": p["ar"]} for p in PAGES]
    with open(os.path.join(ROOT, "en", "pairs.json"), "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
