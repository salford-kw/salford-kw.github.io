// ============================================================
// Salford — Secure Publish Worker
// يستقبل الطلبات من admin.html / add.html / add-work.html
// يتحقق من كلمة المرور، ثم يكتب على GitHub باستخدام GH_TOKEN
// المخزّن كـ Secret على Cloudflare — لا يصل التوكن للمتصفح أبداً
// ============================================================

const ALLOWED_ORIGINS = [
  'https://salfordkw.shop',
  'https://salford-kw.github.io'
];

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) }
  });
}

async function ghRequest(env, path, options = {}) {
  const url = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/contents/${path}`;
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `token ${env.GH_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'salford-worker',
      ...(options.headers || {})
    }
  });
}

async function getSha(env, path) {
  try {
    const r = await ghRequest(env, path);
    if (r.ok) { const d = await r.json(); return d.sha; }
  } catch (e) {}
  return null;
}

async function putJSONFile(env, path, dataObj, commitMessage) {
  const sha = await getSha(env, path);
  const content = btoa(unescape(encodeURIComponent(JSON.stringify(dataObj, null, 2))));
  const body = { message: commitMessage, content, branch: env.GH_BRANCH };
  if (sha) body.sha = sha;
  const res = await ghRequest(env, path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || 'فشل الكتابة على GitHub');
  return data;
}

// حد بسيط لمنع محاولات تخمين كلمة المرور المتكررة (في الذاكرة، لكل نسخة worker)
const attempts = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const rec = attempts.get(ip) || { count: 0, reset: now + 60000 };
  if (now > rec.reset) { rec.count = 0; rec.reset = now + 60000; }
  rec.count++;
  attempts.set(ip, rec);
  return rec.count > 10; // أكثر من 10 محاولات بالدقيقة = حظر مؤقت
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(origin) });
    }

    if (request.method !== 'POST') {
      return json({ error: 'Method not allowed' }, 405, origin);
    }

    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (rateLimited(ip)) {
      return json({ error: 'محاولات كثيرة، حاول بعد قليل' }, 429, origin);
    }

    const url = new URL(request.url);
    let payload;
    try {
      payload = await request.json();
    } catch (e) {
      return json({ error: 'بيانات غير صالحة' }, 400, origin);
    }

    // تحقق كلمة المرور لكل الأنواع (constant-time بسيط)
    const passOk = typeof payload.password === 'string' &&
      payload.password.length === env.ADMIN_PASSWORD.length &&
      payload.password === env.ADMIN_PASSWORD;

    if (!passOk) {
      return json({ error: 'كلمة المرور غير صحيحة' }, 401, origin);
    }

    try {
      if (url.pathname === '/api/publish-products') {
        if (!Array.isArray(payload.products)) return json({ error: 'بيانات المنتجات غير صالحة' }, 400, origin);
        await putJSONFile(env, 'products.json', payload.products, 'تحديث المنتجات من لوحة التحكم');
        return json({ ok: true }, 200, origin);
      }

      if (url.pathname === '/api/publish-posts') {
        if (!Array.isArray(payload.posts)) return json({ error: 'بيانات المقالات غير صالحة' }, 400, origin);
        await putJSONFile(env, 'posts.json', payload.posts, 'تحديث posts.json');
        return json({ ok: true }, 200, origin);
      }

      if (url.pathname === '/api/upload-image') {
        const { filename, base64 } = payload;
        if (!filename || !base64) return json({ error: 'بيانات الصورة ناقصة' }, 400, origin);

        // سماح فقط بامتدادات صور آمنة، ومنع مسارات خطرة (../)
        const safeExt = /\.(jpg|jpeg|png|webp|gif)$/i.test(filename);
        const safeName = /^[a-zA-Z0-9_\-.]+$/.test(filename);
        if (!safeExt || !safeName) return json({ error: 'اسم أو نوع ملف غير مسموح' }, 400, origin);

        const ts = Date.now();
        const ext = filename.split('.').pop().toLowerCase();
        const finalName = `work_${ts}.${ext}`;
        const path = `works/${finalName}`;

        const res = await ghRequest(env, path, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `إضافة صورة عمل: ${finalName}`,
            content: base64,
            branch: env.GH_BRANCH
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || 'فشل رفع الصورة');

        return json({ ok: true, url: `https://salfordkw.shop/${path}` }, 200, origin);
      }

      // رفع ملف عام (صور/فيديوهات منتجات) — يحافظ على اسم الملف المُرسل بعد التحقق منه
      if (url.pathname === '/api/upload-file') {
        const { folder, filename, base64 } = payload;
        const allowedFolders = ['works', 'products'];
        if (!folder || !allowedFolders.includes(folder)) return json({ error: 'مجلد غير مسموح' }, 400, origin);
        if (!filename || !base64) return json({ error: 'بيانات الملف ناقصة' }, 400, origin);

        const safeExt = /\.(jpg|jpeg|png|webp|gif|mp4|mov|webm|m4v)$/i.test(filename);
        const safeName = /^[a-zA-Z0-9_\-.]+$/.test(filename);
        if (!safeExt || !safeName) return json({ error: 'اسم أو نوع ملف غير مسموح' }, 400, origin);

        const path = `${folder}/${filename}`;
        const res2 = await ghRequest(env, path, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `رفع ملف: ${filename}`,
            content: base64,
            branch: env.GH_BRANCH
          })
        });
        const data2 = await res2.json();
        if (!res2.ok) throw new Error(data2.message || 'فشل رفع الملف');

        return json({ ok: true, url: `https://salfordkw.shop/${path}` }, 200, origin);
      }

      // تحديث sitemap.xml (النص الكامل يُرسل جاهزاً من المتصفح بعد التعديل محلياً)
      if (url.pathname === '/api/write-sitemap') {
        const { xml } = payload;
        if (!xml || typeof xml !== 'string' || !xml.includes('<urlset')) {
          return json({ error: 'محتوى sitemap غير صالح' }, 400, origin);
        }
        const path = 'sitemap.xml';
        const sha = await getSha(env, path);
        const content = btoa(unescape(encodeURIComponent(xml)));
        const body = { message: 'تحديث sitemap.xml', content, branch: env.GH_BRANCH };
        if (sha) body.sha = sha;
        const res3 = await ghRequest(env, path, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data3 = await res3.json();
        if (!res3.ok) throw new Error(data3.message || 'فشل تحديث sitemap.xml');
        return json({ ok: true }, 200, origin);
      }

      return json({ error: 'مسار غير معروف' }, 404, origin);
    } catch (e) {
      return json({ error: e.message || 'خطأ بالسيرفر' }, 500, origin);
    }
  }
};
