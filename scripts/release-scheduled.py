#!/usr/bin/env python3
"""النشر المجدول لسالفورد (طلب المالك 2026-11-23، قبل سفره شهرين).

المنتجات والأعمال المجهّزة مسبقًا تُحفظ في scheduled/*.json (عنصر لكل ملف، بصيغة scripts/salford_items.py)
وصورها في scheduled/images/. لا تُنشر هذه المجلدات على الموقع (deploy-pages.yml يستبعدها)، فلا يصل إليها
أحد قبل موعدها.

وقت النشر (deploy-pages.yml: كل push وكل صباح 6:00 بتوقيت الكويت) يُطبَّق كل عنصر حان publishDate له:
تُنسخ صوره إلى products/، وتُبنى صفحته، ويُضاف إلى products.json و posts.json و sitemap.xml، ثم تُحدَّث
أقسام النماذج والمنتجات المشابهة وفهرس السجاد ووسم واتساب. الفرع الرئيسي لا يتغير؛ التطبيق يتم في نسخة النشر.
يكتب الروابط الجديدة في .released-urls.txt لإرسالها إلى IndexNow.

الاستخدام: python3 scripts/release-scheduled.py [--today YYYY-MM-DD] [--list]
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from salford_items import apply_items, slug_of  # noqa: E402

KUWAIT = timezone(timedelta(hours=3))


def main():
    args = sys.argv[1:]
    today = args[args.index('--today') + 1] if '--today' in args else datetime.now(KUWAIT).strftime('%Y-%m-%d')
    files = sorted((ROOT / 'scheduled').glob('*.json'))
    items = [json.loads(f.read_text(encoding='utf-8')) for f in files]
    due = sorted([it for it in items if it.get('publishDate', today) <= today], key=lambda it: it.get('publishDate', ''))
    if '--list' in args:
        for it in sorted(items, key=lambda it: it.get('publishDate', '')):
            print(it.get('publishDate'), '✅' if it in due else '⏳', it['code'])
        return
    print(f'اليوم (الكويت): {today} — مجدول: {len(items)}، حان موعده: {len(due)}')
    if not due:
        (ROOT / '.released-urls.txt').write_text('', encoding='utf-8')
        return
    for it in due:
        for base, *_ in it['images']:
            for size in ('large', 'small'):
                src = ROOT / 'scheduled' / 'images' / f'{base}-{size}.webp'
                dst = ROOT / 'products' / src.name
                if not src.exists() and not dst.exists():
                    raise SystemExit(f'صورة مفقودة: {src}')
                if src.exists():
                    shutil.copy2(src, dst)
    urls = apply_items(due, ROOT, today)
    for script in ('landing-grids.py', 'catalog-related.py', 'category-index.py', 'inject-wa-src.py'):
        subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], cwd=ROOT, check=True)
    (ROOT / '.released-urls.txt').write_text('\n'.join(urls), encoding='utf-8')
    for it in due:
        print('نُشر:', it['publishDate'], slug_of(it))


if __name__ == '__main__':
    main()
