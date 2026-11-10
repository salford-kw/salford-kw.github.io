#!/usr/bin/env python3
"""يضيف وسم مصدر واتساب لكل صفحات HTML (يُشغَّل تلقائياً من .github/workflows/wa-source.yml).
كل رسالة واتساب من الموقع تبدأ بسطر: 📍 سالفورد — <عنوان الصفحة> — <اسم المنتج إن وُجد>
المصدر الوحيد للكود: scripts/wa-src.js"""
import pathlib, re, sys
SITE = 'سالفورد'
ROOT = pathlib.Path(__file__).resolve().parent.parent
JS = (ROOT / 'scripts/wa-src.js').read_text(encoding='utf-8').strip().replace('__SITE__', SITE)
TAG = '<script>/*wa-src*/' + JS + '</script>'
def snippet(): return TAG
if __name__ == '__main__':
    n = 0
    for p in ROOT.rglob('*.html'):
        if any(x in p.parts for x in ('.git', 'node_modules')): continue
        h = p.read_text(encoding='utf-8', errors='surrogateescape')
        if '/*wa-src*/' in h:
            h2 = re.sub(r'<script>/\*wa-src\*/.*?</script>', lambda m: TAG, h, flags=re.S)
        else:
            i = h.lower().rfind('</body>')
            if i < 0: continue
            h2 = h[:i] + TAG + '\n' + h[i:]
        if h2 != h:
            p.write_text(h2, encoding='utf-8', errors='surrogateescape'); n += 1
    print(f'wa-src: {n} صفحة حُدّثت')
