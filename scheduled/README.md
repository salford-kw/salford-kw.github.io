# المنتجات المجدولة

كل ملف `*.json` هنا منتج/عمل مجهّز مسبقًا بصيغة `scripts/salford_items.py` وفيه `publishDate` (YYYY-MM-DD).
صوره في `images/` بالاسمين `<الاسم>-large.webp` و`<الاسم>-small.webp`.

لا يُنشر هذا المجلد على الموقع. كل صباح (6:00 بتوقيت الكويت) ومع كل push يطبّق
`.github/workflows/deploy-pages.yml` العناصر التي حان موعدها عبر `scripts/release-scheduled.py`.

لعرض الجدول: `python3 scripts/release-scheduled.py --list`


