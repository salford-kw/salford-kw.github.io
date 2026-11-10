#!/usr/bin/env python3
"""
توحيد هوية النشاط (NAP) وتنظيف الـSchema في كل صفحات الموقع — مصدر واحد للحقيقة.

ما يفعله (آمن لإعادة التشغيل، لا يغيّر Title/H1/النص المرئي):
1. كل كائن LocalBusiness معرّفه  https://salfordkw.shop/#business  يأخذ نفس الحقول
   الأساسية من BUSINESS أدناه (الاسم، الهاتف، عنوان فرع الضجيج، أوقات العمل، sameAs،
   url = الصفحة الرئيسية). الحقول الخاصة بالصفحة (makesOffer / hasOfferCatalog /
   description) تبقى كما هي.
2. أي Product بلا offers (عمل منفَّذ بلا سعر) يُحوَّل إلى Service مرتبط بكيان النشاط —
   Google يرفض Product بلا offers/review/aggregateRating ويظهره خطأً في Search Console.
3. يحذف aggregateRating من كائن النشاط، ويحذف حقن Schema من نوع Product باسم
   الشركة عبر JavaScript — جوجل لا يقبل تقييم النشاط لنفسه (self-serving reviews).
   التقييمات تبقى ظاهرة للزائر كما هي.

الاستخدام:  python3 scripts/seo-unify.py            (يعدّل الملفات)
            python3 scripts/seo-unify.py --check    (يفشل إن وُجد ملف غير موحّد)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://salfordkw.shop'
BIZ_ID = SITE + '/#business'

# ⚠️ المصدر الوحيد لبيانات النشاط. أي تغيير في العنوان/الهاتف/الأوقات يكون هنا فقط،
# ومطابقاً لـ BUSINESS في salford-admin/src/catalogTemplate.js.
BUSINESS = {
    'name': 'سالفورد للأثاث والمفروشات',
    'alternateName': 'Salford Furniture Kuwait',
    'url': SITE + '/',
    'telephone': '+96555943343',
    'logo': SITE + '/favicon-192.png',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'مجمع علي عبدالوهاب - السرداب',
        'addressLocality': 'الضجيج',
        'addressRegion': 'محافظة الفروانية',
        'addressCountry': 'KW',
    },
    'hasMap': 'https://www.google.com/maps?q=%D8%A7%D9%84%D9%83%D9%88%D9%8A%D8%AA+%D8%A7%D9%84%D8%B6%D8%AC%D9%8A%D8%AC+%D9%85%D8%AC%D9%85%D8%B9+%D8%B9%D9%84%D9%8A+%D8%B9%D8%A8%D8%AF%D8%A7%D9%84%D9%88%D9%87%D8%A7%D8%A8+%D8%A7%D9%84%D8%B3%D8%B1%D8%AF%D8%A7%D8%A8',
    'foundingDate': '2016',
    'priceRange': '$$',
    'currenciesAccepted': 'KWD',
    'paymentAccepted': 'Cash, KNET, Wamd, Bank Transfer',
    'openingHoursSpecification': {
        '@type': 'OpeningHoursSpecification',
        'dayOfWeek': ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'opens': '10:00',
        'closes': '21:00',
    },
    'areaServed': {'@type': 'Country', 'name': 'Kuwait'},
    'sameAs': ['https://www.instagram.com/salforad/', 'https://www.tiktok.com/@salford_kuwait'],
}
DROP_KEYS = ('aggregateRating', 'review', 'serviceArea')

LD_RE = re.compile(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.S)
# حقن Schema التقييم عبر JS (الصيغتان المستخدمتان في الصفحات)
JS_RATING_RE = re.compile(
    r"\n[ \t]*(?://[^\n]*\n[ \t]*)?const schemaEl = document\.getElementById\('(?:site-)?reviews-schema'\);"
    r".*?schemaEl\.textContent = JSON\.stringify\(schema\);[ \t]*", re.S)
EMPTY_HOLDER_RE = re.compile(r'[ \t]*<script id="(?:site-)?reviews-schema" type="application/ld\+json"></script>\n?')


def is_business(obj):
    if not isinstance(obj, dict) or obj.get('@id') != BIZ_ID:
        return False
    t = obj.get('@type')
    types = t if isinstance(t, list) else [t]
    return 'LocalBusiness' in types or 'FurnitureStore' in types


def unify_business(obj):
    new = {}
    for k in ('@context', '@type', '@id'):
        if k in obj:
            new[k] = obj[k]
    new.update(BUSINESS)
    for k, v in obj.items():
        if k in new or k in DROP_KEYS:
            continue
        new[k] = v
    return new


def product_to_service(obj):
    new = {'@context': obj.get('@context', 'https://schema.org'), '@type': 'Service'}
    for k in ('name', 'description'):
        if obj.get(k):
            new[k] = obj[k]
    if obj.get('category'):
        new['serviceType'] = obj['category']
    for k in ('image', 'url'):
        if obj.get(k):
            new[k] = obj[k]
    new['provider'] = {'@id': BIZ_ID}
    new['areaServed'] = obj.get('areaServed') or {'@type': 'Country', 'name': 'Kuwait'}
    return new


def process(text):
    def fix_ld(m):
        raw = m.group(2)
        if '#business' not in raw and '"Product"' not in raw:
            return m.group(0)
        try:
            data = json.loads(raw)
        except ValueError:
            return m.group(0)
        if isinstance(data, dict) and data.get('@type') == 'Product' and not (
                data.get('offers') or data.get('review') or data.get('aggregateRating')):
            return m.group(1) + json.dumps(product_to_service(data), ensure_ascii=False) + m.group(3)
        if not is_business(data):
            return m.group(0)
        new = unify_business(data)
        if new == data:
            return m.group(0)
        return m.group(1) + '\n' + json.dumps(new, ensure_ascii=False) + '\n' + m.group(3)

    text = LD_RE.sub(fix_ld, text)
    text = JS_RATING_RE.sub('', text)
    text = EMPTY_HOLDER_RE.sub('', text)
    return text


def main():
    check = '--check' in sys.argv
    dirty = []
    for p in sorted(ROOT.rglob('*.html')):
        rel = p.relative_to(ROOT).as_posix()
        # en/ يولّدها scripts/build_en.py بنفس البيانات (business_ld) فلا تُعدَّل هنا
        if rel.startswith(('backups/', 'node_modules/', '.git/', 'en/')):
            continue
        old = p.read_text(encoding='utf-8')
        new = process(old)
        if new != old:
            dirty.append(rel)
            if not check:
                p.write_text(new, encoding='utf-8')
    print(('غير موحّد: ' if check else 'تم توحيد: ') + str(len(dirty)) + ' ملف')
    for d in dirty[:15]:
        print(' -', d)
    if check and dirty:
        sys.exit(1)


if __name__ == '__main__':
    main()
