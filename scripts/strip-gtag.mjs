// ============================================================
// سالفورد — إزالة Google Tag (gtag / Google Ads / GA4) نهائياً
//
// يشتغل داخل GitHub Actions بعد كل نشر، فأي صفحة تُنشأ أو تُحدَّث
// من لوحة الإدارة وفيها كود Google Tag يُحذف منها تلقائياً.
// يحذف:
//   1) <script src="...googletagmanager...">
//   2) سكربتات dataLayer/gtag المضمّنة (المحمِّل المؤجَّل وغيره)
//   3) تعليقات HTML الخاصة بـ Google Ads / GA4 / Tag Manager
//   4) استدعاءات gtag(...) داخل onclick (ويحذف onclick إن أصبح فارغاً)
// آمن للتكرار: لا يكتب ملفاً إن لم يتغير.
// ============================================================
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const SKIP_DIRS = new Set(['.git', 'node_modules', 'backups', '.github']);

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name)) out.push(...walk(path.join(dir, e.name)));
    } else if (e.name.endsWith('.html')) {
      out.push(path.join(dir, e.name));
    }
  }
  return out;
}

const GTAG_CALL = /gtag\((?:[^()"]|\([^()"]*\))*\)\s*;?\s*/g;

function strip(html) {
  let out = html;

  // 1) سكربتات خارجية من googletagmanager
  out = out.replace(/[ \t]*<script\b[^>]*\bsrc=["'][^"']*googletagmanager\.com[^"']*["'][^>]*>\s*<\/script>[ \t]*\r?\n?/gi, '');

  // 2) سكربتات مضمّنة خاصة بـ gtag
  out = out.replace(/[ \t]*<script\b([^>]*)>([\s\S]*?)<\/script>[ \t]*\r?\n?/gi, (m, attrs, body) => {
    if (/\bsrc=/i.test(attrs) || /application\/ld\+json/i.test(attrs)) return m;
    const isGtag = /googletagmanager\.com/.test(body) || /gtag\(\s*['"]config['"]/.test(body);
    return isGtag ? '' : m;
  });

  // 3) تعليقات HTML المتعلقة بـ Google Tag
  out = out.replace(/[ \t]*<!--([\s\S]*?)-->[ \t]*\r?\n?/g, (m, body) =>
    /gtag|Google Ads|Google Analytics|Google Tag Manager|googletagmanager/i.test(body) ? '' : m);

  // 4) استدعاءات gtag داخل onclick
  out = out.replace(/\s+onclick="([^"]*)"/g, (m, val) => {
    if (!val.includes('gtag(')) return m;
    const cleaned = val.replace(GTAG_CALL, '').trim();
    return cleaned ? ` onclick="${cleaned}"` : '';
  });

  return out;
}

let changed = 0;
let leftovers = 0;
for (const file of walk(ROOT)) {
  const html = fs.readFileSync(file, 'utf8');
  if (!/gtag|googletagmanager/.test(html)) continue;
  const out = strip(html);
  if (out !== html) {
    fs.writeFileSync(file, out);
    changed++;
  }
  if (/gtag\(|googletagmanager/.test(out)) {
    leftovers++;
    console.warn(`⚠️ بقايا gtag في ${path.relative(ROOT, file)}`);
  }
}
console.log(`🧹 Google Tag: نُظّفت ${changed} صفحة، بقايا في ${leftovers} صفحة.`);
