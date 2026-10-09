// ============================================================
// سالفورد — حارس LCP (يشتغل داخل GitHub Actions)
//
// الجزء A: شبكة أمان للصور داخل products/
//   - أي WebP ضلعه الطويل > 1600px يُصغَّر إلى 1200px (جودة 75).
//   - أي WebP حجمه > 300KB يُعاد ترميزه بجودة أقل (يُحفظ فقط لو وفّر ≥15%).
//   - الصور القديمة بلا لاحقة (product_xxx.webp) تحصل على نسخة -small (640px)
//     لأن الصفحة الرئيسية تطلبها أولاً.
//   لوحة الإدارة تصغّر الصور أصلاً، فهذا الجزء يلتقط فقط ما يُرفع بغيرها
//   (رفع يدوي من GitHub، أو صور قديمة).
//
// الجزء B: مزامنة شريحة LCP في index.html
//   - تأخذ أحدث عمل في posts.json صورته وصفحته موجودتان فعلاً بالمستودع،
//     وتحدّث (preload + الشريحة الأولى + data-static-first-img) تلقائياً.
//   - لو حُذف المنتج الحالي أو انكسرت صورته، تختار التالي بدل ترك LCP مكسوراً.
//
// آمن للتكرار: لا يكتب شيئاً إن لم يتغير شيء.
// ============================================================
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const SITE = 'https://salfordkw.shop/';
const PRODUCTS_DIR = path.join(ROOT, 'products');

const LONG_SIDE_LIMIT = 1600;
const RESIZE_TO = 1200;
const RESIZE_QUALITY = 75;
const MAX_BYTES = 300 * 1024;
const MIN_SAVING = 0.15;
const LEGACY_SMALL_SIZE = 640;
const LEGACY_SMALL_QUALITY = 70;

// ---------- أدوات ----------
function webpInfo(buf) {
  if (!buf || buf.length < 30) return null;
  if (buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') return null;
  const fourcc = buf.toString('ascii', 12, 16);
  if (fourcc === 'VP8X') return { width: buf.readUIntLE(24, 3) + 1, height: buf.readUIntLE(27, 3) + 1 };
  if (fourcc === 'VP8 ') return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff };
  if (fourcc === 'VP8L') {
    const b = buf.readUInt32LE(21);
    return { width: (b & 0x3fff) + 1, height: ((b >> 14) & 0x3fff) + 1 };
  }
  return null;
}

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

function urlToLocalPath(url) {
  if (!url || !url.startsWith(SITE)) return null;
  let rel = url.slice(SITE.length).split('?')[0].split('#')[0];
  try { rel = decodeURIComponent(rel); } catch { /* اتركه كما هو */ }
  return path.join(ROOT, rel);
}

// ---------- الجزء A: الصور ----------
async function guardImages() {
  let sharp;
  try { sharp = (await import('sharp')).default; }
  catch { console.warn('⚠️ sharp غير متوفر — تخطي الجزء A'); return 0; }

  const files = walk(PRODUCTS_DIR).filter((f) => /\.webp$/i.test(f));
  let changed = 0;

  for (const file of files) {
    const rel = path.relative(ROOT, file);
    let buf;
    try { buf = fs.readFileSync(file); } catch { continue; }
    const info = webpInfo(buf);
    if (!info) {
      // JPEG/PNG مرفوع باسم .webp — يُحوَّل إلى WebP حقيقي بنفس الاسم
      try {
        const out = await sharp(buf).rotate().resize({ width: RESIZE_TO, height: RESIZE_TO, fit: 'inside', withoutEnlargement: true })
          .webp({ quality: RESIZE_QUALITY }).toBuffer();
        fs.writeFileSync(file, out);
        changed++;
        console.log(`🔁 حُوّلت إلى WebP حقيقي ${rel}: ${Math.round(buf.length / 1024)}KB → ${Math.round(out.length / 1024)}KB`);
      } catch { console.warn(`⚠️ تعذّر تحويل ${rel}`); }
      continue;
    }

    const long = Math.max(info.width, info.height);

    // 1) تصغير الأبعاد الضخمة
    if (long > LONG_SIDE_LIMIT) {
      const out = await sharp(buf).rotate().resize({
        width: info.width >= info.height ? RESIZE_TO : undefined,
        height: info.height > info.width ? RESIZE_TO : undefined,
        fit: 'inside', withoutEnlargement: true,
      }).webp({ quality: RESIZE_QUALITY }).toBuffer();
      if (out.length < buf.length) {
        fs.writeFileSync(file, out);
        buf = out;
        changed++;
        console.log(`📉 صُغّرت ${rel}: ${info.width}x${info.height} → ${Math.round(out.length / 1024)}KB`);
      }
    }
    // 2) ضغط الملفات الثقيلة
    else if (buf.length > MAX_BYTES) {
      const out = await sharp(buf).webp({ quality: 70 }).toBuffer();
      if (out.length <= buf.length * (1 - MIN_SAVING)) {
        fs.writeFileSync(file, out);
        buf = out;
        changed++;
        console.log(`🗜️ ضُغطت ${rel}: ${Math.round(out.length / 1024)}KB`);
      }
    }

    // 3) نسخة -small للصور القديمة بلا لاحقة
    const base = path.basename(file, '.webp');
    if (/^product_/.test(base) && !/-(small|large)$/.test(base)) {
      const smallPath = path.join(path.dirname(file), `${base}-small.webp`);
      const cur = webpInfo(buf);
      if (!fs.existsSync(smallPath) && cur && Math.max(cur.width, cur.height) > LEGACY_SMALL_SIZE) {
        const out = await sharp(buf).resize({
          width: cur.width >= cur.height ? LEGACY_SMALL_SIZE : undefined,
          height: cur.height > cur.width ? LEGACY_SMALL_SIZE : undefined,
          fit: 'inside', withoutEnlargement: true,
        }).webp({ quality: LEGACY_SMALL_QUALITY }).toBuffer();
        fs.writeFileSync(smallPath, out);
        changed++;
        console.log(`➕ أُنشئت ${path.relative(ROOT, smallPath)} (${Math.round(out.length / 1024)}KB)`);
      }
    }
  }
  return changed;
}

// ---------- الجزء B: شريحة LCP ----------
const AR_MONTHS = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];

function arabicDate(str) {
  const d = new Date(str);
  if (!str || isNaN(d)) return '';
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Kuwait', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(d);
  const o = {};
  parts.forEach((p) => { o[p.type] = p.value; });
  return `${Number(o.day)} ${AR_MONTHS[Number(o.month) - 1]} ${o.year}`;
}

function pickHeroPost(posts) {
  for (let i = posts.length - 1; i >= 0; i--) {
    const p = posts[i];
    if (!p || !p.img) continue;
    const imgPath = urlToLocalPath(p.img);
    if (!imgPath || !fs.existsSync(imgPath)) continue;
    const info = webpInfo(fs.readFileSync(imgPath));
    if (!info) continue;
    if (p.productUrl) {
      const pagePath = urlToLocalPath(p.productUrl);
      if (pagePath && !fs.existsSync(pagePath)) continue; // صفحة المنتج محذوفة
    }
    return { post: p, info };
  }
  return null;
}

function heroSlideHTML(p, info) {
  const target = p.productUrl || '/works.html';
  const safeTarget = String(target).replace(/\\/g, '').replace(/'/g, '%27').replace(/"/g, '%22');
  const price = p.price ? `\n            <div class="work-card-price">${esc(p.price)} د.ك / ${esc(p.unit || 'م')}</div>` : '';
  const date = arabicDate(p.date);
  const dateLine = date ? `\n            <div class="work-card-date">${date}</div>` : '';
  return `      <div class="slide-item">
        <div class="work-card" onclick="location.href='${safeTarget}'">
          <div class="work-card-img">
            <img src="${esc(p.img)}" alt="${esc(p.title)} - سالفورد للأثاث والمفروشات الكويت" loading="eager" fetchpriority="high" decoding="async" width="${info.width}" height="${info.height}" onerror="this.style.opacity='.2'">
          </div>
          <div class="work-card-info">
            <div class="work-card-title">${esc(p.title)}</div>${price}${dateLine}
          </div>
        </div>
      </div>`;
}

function syncHero() {
  const indexPath = path.join(ROOT, 'index.html');
  const postsPath = path.join(ROOT, 'posts.json');
  if (!fs.existsSync(indexPath) || !fs.existsSync(postsPath)) {
    console.warn('⚠️ index.html أو posts.json غير موجود — تخطي الجزء B');
    return 0;
  }
  let posts;
  try { posts = JSON.parse(fs.readFileSync(postsPath, 'utf8')); }
  catch (e) { console.warn('⚠️ posts.json غير صالح — تخطي الجزء B:', e.message); return 0; }
  if (!Array.isArray(posts)) return 0;

  const picked = pickHeroPost(posts);
  if (!picked) { console.warn('⚠️ لا يوجد عمل صالح لشريحة LCP — لم يُغيَّر شيء'); return 0; }

  const html = fs.readFileSync(indexPath, 'utf8');
  const startTag = '<!-- HERO:START -->';
  const endTag = '<!-- HERO:END -->';
  const s = html.indexOf(startTag);
  const e = html.indexOf(endTag);
  const preloadRe = /<link rel="preload" as="image" fetchpriority="high" href="[^"]*" id="lcp-preload-1">/;
  const dataRe = /data-static-first-img="[^"]*"/;
  if (s === -1 || e === -1 || e < s || !preloadRe.test(html) || !dataRe.test(html)) {
    console.warn('⚠️ علامات HERO أو preload غير موجودة في index.html — تخطي الجزء B');
    return 0;
  }

  const { post, info } = picked;
  let out = html.slice(0, s + startTag.length) + '\n' + heroSlideHTML(post, info) + '\n      ' + html.slice(e);
  out = out.replace(preloadRe, `<link rel="preload" as="image" fetchpriority="high" href="${esc(post.img)}" id="lcp-preload-1">`);
  out = out.replace(dataRe, `data-static-first-img="${esc(post.img)}"`);

  if (out === html) { console.log('✅ شريحة LCP محدّثة أصلاً'); return 0; }
  fs.writeFileSync(indexPath, out);
  console.log(`🖼️ شريحة LCP الآن: ${post.title} (${info.width}x${info.height})`);
  return 1;
}

// ---------- الجزء C: صور البطاقات في الصفحة الرئيسية ----------
// أي صورة في index.html (خارج شريحة LCP) تُخدَم بنسختها -small (≤640px).
// إن لم تكن النسخة الصغيرة موجودة تُنشأ تلقائياً — حتى لا تتكرر مشكلة
// «تحسين عرض الصور» في PageSpeed مع كل منتج جديد.
async function smallCards() {
  const indexPath = path.join(ROOT, 'index.html');
  if (!fs.existsSync(indexPath)) return 0;
  let sharp = null;
  try { sharp = (await import('sharp')).default; } catch { /* بدون sharp: نستبدل الموجود فقط */ }

  const html = fs.readFileSync(indexPath, 'utf8');
  const hs = html.indexOf('<!-- HERO:START -->');
  const he = html.indexOf('<!-- HERO:END -->');
  const re = /(<img\b[^>]*?\b(?:src|data-src)=")(https:\/\/salfordkw\.shop\/products\/[^"]+?)(-large)?\.webp"/g;
  let count = 0;
  const parts = [];
  let last = 0;
  for (const m of html.matchAll(re)) {
    const at = m.index;
    if (hs !== -1 && he !== -1 && at > hs && at < he) continue; // شريحة LCP يديرها الجزء B
    const stem = m[2];
    if (/-small$/.test(stem)) continue;
    const smallUrl = `${stem}-small.webp`;
    const smallPath = urlToLocalPath(smallUrl);
    if (!smallPath) continue;
    if (!fs.existsSync(smallPath)) {
      const srcPath = urlToLocalPath(`${stem}${m[3] || ''}.webp`);
      if (!sharp || !srcPath || !fs.existsSync(srcPath)) continue;
      const buf = fs.readFileSync(srcPath);
      const info = webpInfo(buf);
      if (!info) continue;
      const out = await sharp(buf).resize({
        width: info.width >= info.height ? LEGACY_SMALL_SIZE : undefined,
        height: info.height > info.width ? LEGACY_SMALL_SIZE : undefined,
        fit: 'inside', withoutEnlargement: true,
      }).webp({ quality: LEGACY_SMALL_QUALITY }).toBuffer();
      if (out.length >= buf.length) continue; // الأصل صغير أصلاً
      fs.writeFileSync(smallPath, out);
      console.log(`➕ أُنشئت ${path.relative(ROOT, smallPath)} (${Math.round(out.length / 1024)}KB)`);
    }
    parts.push(html.slice(last, at), `${m[1]}${smallUrl}"`);
    last = at + m[0].length;
    count++;
  }
  if (!count) { console.log('✅ صور البطاقات صغيرة أصلاً'); return 0; }
  parts.push(html.slice(last));
  fs.writeFileSync(indexPath, parts.join(''));
  console.log(`🖼️ حُوّلت ${count} صورة بطاقة إلى -small`);
  return count;
}

// ---------- تشغيل ----------
const a = await guardImages();
// في وضع الفحص (GitHub Actions) لا نقارن شريحة LCP: تغيّرها بعد نشر عمل جديد
// أمر طبيعي وليس خللاً، والفرع الرئيسي محمي فلا يمكن رفع التحديث تلقائياً.
const b = process.env.SITE_GUARD_VERIFY === '1' ? 0 : syncHero();
const c = await smallCards();
console.log(`انتهى: ${a} تعديل صور، ${b} تعديل شريحة، ${c} صورة بطاقة.`);
