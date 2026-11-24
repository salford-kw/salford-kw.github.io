#!/usr/bin/env python3
"""التواصل عبر واتساب فقط (طلب المالك 2026-11-25): يحذف أزرار الاتصال من كل الصفحات ويُبقي زر واتساب.

يحذف: زر الشريط السفلي (s-call)، وزر «اتصل بنا الآن» (btn-call)، وزر Call في الصفحات الإنجليزية (btn call)،
ويجعل الشريط السفلي وصفوف الأزرار عمودًا واحدًا حتى يأخذ زر واتساب العرض كاملًا.
لا يمس رقم الهاتف في بيانات Schema ولا رقم التذييل النصي.

يعمل على ملفات المستودع ويُستدعى أيضًا في deploy-pages.yml قبل النشر، فأي صفحة جديدة (من لوحة الإدارة مثلًا)
تُنشر بلا زر اتصال. آمن للتكرار.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATS = [
    re.compile(r'[ \t]*<a class="s-btn s-call"[^>]*>.*?</a>\n?', re.S),
    re.compile(r'[ \t]*<a class="btn btn-call"[^>]*>.*?</a>\n?', re.S),
    re.compile(r'<a class="btn call"[^>]*>.*?</a>', re.S),
]
# الشريط السفلي وصف الأزرار الإنجليزي: عمود واحد بدل عمودين
CSS = [
    (re.compile(r'(\.sticky\s*\{[^}]*?grid-template-columns\s*:\s*)1fr 1fr'), r'\g<1>1fr'),
    (re.compile(r'(\.cta\s*\{[^}]*?grid-template-columns\s*:\s*)1fr 1fr'), r'\g<1>1fr'),
]


def clean(t: str) -> str:
    for p in PATS:
        t = p.sub('', t)
    for p, r in CSS:
        t = p.sub(r, t)
    return t


def main():
    files = [p for p in ROOT.rglob('*.html') if '.git' not in p.parts and 'node_modules' not in p.parts]
    n = 0
    for f in files:
        t = f.read_text(encoding='utf-8')
        c = clean(t)
        if c != t:
            f.write_text(c, encoding='utf-8')
            n += 1
    print(f'whatsapp-only: {n} صفحة حُدّثت')
    if '--check' in sys.argv:
        left = [str(f.relative_to(ROOT)) for f in files if any(p.search(f.read_text(encoding="utf-8")) for p in PATS)]
        if left:
            raise SystemExit('ما زال زر اتصال في: ' + ', '.join(left[:10]))


if __name__ == '__main__':
    main()
