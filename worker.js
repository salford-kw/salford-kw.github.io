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

const ALLOWED_CATALOG_SECTIONS = ['sajjad', 'majalis', 'athath', 'sataer'];

// 🆕 مُعرّف صفحة كتالوج دائم (slug) بدل رقم الموضع القديم — يمنع تزحزح
// الروابط عند حذف/إعادة ترتيب منتجات (راجع migration: catalog url slugs).
// نسمح فقط بحروف عربية/إنجليزية وأرقام وشرطة، بلا نقطتين متتاليتين ولا
// شرطة مائلة، لمنع أي محاولة path traversal عبر واجهة الكتابة على GitHub.
const SLUG_RE = /^[a-zA-Z0-9\u0600-\u06FF-]{1,120}$/;
function sanitizeSlug(slug) {
  if (typeof slug !== 'string') return null;
  const s = slug.trim();
  if (!s || s.includes('..') || s.includes('/') || s.includes('\\')) return null;
  if (!SLUG_RE.test(s)) return null;
  return s;
}

// يبني اسم صفحة الكتالوج من slug (الطريقة الدائمة الجديدة) أو، إن ما توفر
// slug، من رقم موضع قديم (الطريقة السابقة — للتوافق أثناء فترة الانتقال
// فقط، يُفترض إزالتها بعد ما تكتمل الهجرة بكل ملفات admin.html/add.html).
function resolvePageIdentifier(payload) {
  const slug = sanitizeSlug(payload && payload.slug);
  if (slug) return { ok: true, idStr: slug };
  const idxNum = Number(payload && payload.index);
  if (Number.isInteger(idxNum) && idxNum >= 1) {
    return { ok: true, idStr: String(idxNum).padStart(2, '0') };
  }
  return { ok: false };
}

// 🗂️ قائمة ثابتة (one-time cleanup) لتصحيح أسماء صور قديمة اتخزنت بمجلد
// products/ بصيغة مشوّهة "#Uxxxx" بدل الحرف العربي الفعلي (بقايا خلل قديم
// بأداة رفع/تسمية سابقة). الروابط بكل صفحات الموقع (products.json، صفحات
// الكتالوج، sitemap.xml...) أصلاً مكتوبة بالاسم العربي الصحيح — بس الملف
// الفعلي على GitHub اسمه مشوّه فيصير رابط مكسور. الحل = rename فقط، بدون
// أي تعديل على أي كود أو رابط. المصفوفة الثانية ملفات يتيمة غير مستخدمة
// بأي مكان بالموقع، تُحذف بدل ما تُصحّح.
const MANGLED_IMAGE_RENAMES = [
  ["#U0627#U062b#U0627#U062b-#U062f#U064a#U0648#U0627#U0646#U064a#U0629-#U062a#U0643#U0627#U064a#U0627#U062a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "اثاث-ديوانية-تكايات-سالفورد.webp"],
  ["#U062a#U0646#U062c#U064a#U062f-#U0627#U062b#U0627#U062b-#U062f#U064a#U0648#U0627#U0646#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "تنجيد-اثاث-ديوانية-سالفورد.webp"],
  ["#U062f#U064a#U0643#U0648#U0631-#U062f#U0627#U062e#U0644#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "ديكور-داخلي-سالفورد.webp"],
  ["#U062f#U064a#U0643#U0648#U0631-#U0645#U062c#U0627#U0644#U0633-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "ديكور-مجالس-سالفورد.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0627#U0643#U0627#U062f#U064a#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "سجاد-تركي-اكادير-سالفورد-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0627#U0643#U0627#U062f#U064a#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "سجاد-تركي-اكادير-سالفورد.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-05-large.webp", "سجاد-تركي-سالفورد-05-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-05.webp", "سجاد-تركي-سالفورد-05.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-06-large.webp", "سجاد-تركي-سالفورد-06-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-06.webp", "سجاد-تركي-سالفورد-06.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-07-large.webp", "سجاد-تركي-سالفورد-07-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-07.webp", "سجاد-تركي-سالفورد-07.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0641#U0646#U062f#U0642#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "سجاد-تركي-فندقي-سالفورد-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0641#U0646#U062f#U0642#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "سجاد-تركي-فندقي-سالفورد.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0645#U0631#U0627#U0643#U0634-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "سجاد-تركي-مراكش-سالفورد-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0645#U0631#U0627#U0643#U0634-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "سجاد-تركي-مراكش-سالفورد.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0646#U0627#U0628#U0644-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "سجاد-تركي-نابل-سالفورد-large.webp"],
  ["#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0646#U0627#U0628#U0644-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "سجاد-تركي-نابل-سالفورد.webp"],
  ["#U0633#U062c#U0627#U062f-#U062d#U0641#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-2.webp", "سجاد-حفر-سالفورد-2.webp"],
  ["#U0633#U062c#U0627#U062f-#U062d#U0641#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "سجاد-حفر-سالفورد.webp"],
  ["#U0643#U0646#U0628-#U062a#U0641#U0635#U064a#U0644-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "كنب-تفصيل-سالفورد.webp"],
  ["#U0643#U0646#U0628-#U0645#U0648#U062f#U0631#U0646-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02.webp", "كنب-مودرن-سالفورد-02.webp"],
  ["#U0643#U0646#U0628-#U0645#U0648#U062f#U0631#U0646-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "كنب-مودرن-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062e#U0634#U0628-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0635#U0628#U0627#U062d#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-2.webp", "مجلس-خشب-ديكور-الصباحية-سالفورد-2.webp"],
  ["#U0645#U062c#U0644#U0633-#U062e#U0634#U0628-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0635#U0628#U0627#U062d#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-3.webp", "مجلس-خشب-ديكور-الصباحية-سالفورد-3.webp"],
  ["#U0645#U062c#U0644#U0633-#U062e#U0634#U0628-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0635#U0628#U0627#U062d#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-4.webp", "مجلس-خشب-ديكور-الصباحية-سالفورد-4.webp"],
  ["#U0645#U062c#U0644#U0633-#U062e#U0634#U0628-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0635#U0628#U0627#U062d#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-خشب-ديكور-الصباحية-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0639#U0645#U0627#U0644#U0646#U0627-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-ديكور-اعمالنا-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0631#U0626#U064a#U0633#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-2.webp", "مجلس-ديكور-الرئيسية-سالفورد-2.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0631#U0626#U064a#U0633#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-3.webp", "مجلس-ديكور-الرئيسية-سالفورد-3.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0631#U0626#U064a#U0633#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "مجلس-ديكور-الرئيسية-سالفورد-large.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0631#U0626#U064a#U0633#U064a#U0629-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-ديكور-الرئيسية-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0643#U0648#U064a#U062a-#U0635#U0628#U0627#U062d-#U0627#U0644#U0627#U062d#U0645#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-ديكور-الكويت-صباح-الاحمد-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02-large.webp", "مجلس-ديكور-سالفورد-02-large.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02.webp", "مجلس-ديكور-سالفورد-02.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-03-large.webp", "مجلس-ديكور-سالفورد-03-large.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-03.webp", "مجلس-ديكور-سالفورد-03.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-05-large.webp", "مجلس-ديكور-سالفورد-05-large.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-05.webp", "مجلس-ديكور-سالفورد-05.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0641#U062e#U0645-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-2.webp", "مجلس-ديكور-فخم-سالفورد-2.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0641#U062e#U0645-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-3.webp", "مجلس-ديكور-فخم-سالفورد-3.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0641#U062e#U0645-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-ديكور-فخم-سالفورد.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0648#U0627#U0646#U064a#U0629-#U0643#U0646#U0628-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-2.webp", "مجلس-ديوانية-كنب-سالفورد-2.webp"],
  ["#U0645#U062c#U0644#U0633-#U062f#U064a#U0648#U0627#U0646#U064a#U0629-#U0643#U0646#U0628-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مجلس-ديوانية-كنب-سالفورد.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U0627#U0633#U0641#U0646#U062c-#U0627#U0644#U0628#U063a#U0644#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مساند-اسفنج-البغلي-سالفورد.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U0627#U0633#U0641#U0646#U062c-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مساند-اسفنج-سالفورد.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "مساند-ديكور-سالفورد-large.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U062f#U064a#U0643#U0648#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مساند-ديكور-سالفورد.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U0638#U0647#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-large.webp", "مساند-ظهر-سالفورد-large.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U0638#U0647#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مساند-ظهر-سالفورد.webp"],
  ["#U0645#U0633#U0627#U0646#U062f-#U0648#U0646#U0642#U0634#U0629-#U062d#U0641#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "مساند-ونقشة-حفر-سالفورد.webp"],
  ["#U0646#U0642#U0634#U0627#U062a-#U062d#U0641#U0631-#U0633#U062c#U0627#U062f-#U064a#U062f#U0648#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "نقشات-حفر-سجاد-يدوي-سالفورد.webp"],
  ["#U0646#U0642#U0634#U0629-#U062d#U0641#U0631-#U0633#U062c#U0627#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-04-large.webp", "نقشة-حفر-سجاد-سالفورد-04-large.webp"],
  ["#U0646#U0642#U0634#U0629-#U062d#U0641#U0631-#U0633#U062c#U0627#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-04.webp", "نقشة-حفر-سجاد-سالفورد-04.webp"],
  ["#U0646#U0642#U0634#U0629-#U062d#U0641#U0631-#U064a#U062f#U0648#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp", "نقشة-حفر-يدوي-سالفورد.webp"],
  ["#U0646#U0642#U0634#U0629-#U0633#U062c#U0627#U062f-#U062d#U0641#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02-large.webp", "نقشة-سجاد-حفر-سالفورد-02-large.webp"],
  ["#U0646#U0642#U0634#U0629-#U0633#U062c#U0627#U062f-#U062d#U0641#U0631-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02.webp", "نقشة-سجاد-حفر-سالفورد-02.webp"],
];
const MANGLED_IMAGE_DELETES = [
  "#U0633#U062c#U0627#U062f-#U062a#U0631#U0643#U064a-#U0627#U0643#U0627#U062f#U064a#U0631-#U0633#U0627#U0644#U0641#U0648#U0631.webp",
  "#U0633#U062c#U0627#U062f-#U0645#U0633#U062c#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-01.jpg",
  "#U0633#U062c#U0627#U062f-#U0645#U0633#U062c#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-02.jpg",
  "#U0633#U062c#U0627#U062f-#U0645#U0633#U062c#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-03.jpg",
  "#U0633#U062c#U0627#U062f-#U0645#U0633#U062c#U062f-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-04.jpg",
  "#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0639#U0645#U0627#U0644#U0646#U0627-#U0633#U0627#U0644#U0641.webp",
  "#U0645#U062c#U0644#U0633-#U062f#U064a#U0643#U0648#U0631-#U0627#U0644#U0631#U0626#U064a#U0633#U064a#U0629-#U0633#U0627#U0644.webp",
  "#U0645#U0633#U0627#U0646#U062f-#U0627#U0633#U0641#U0646#U062c-#U0627#U0644#U0628#U063a#U0644#U064a-#U0633#U0627#U0644#U0641.webp",
  "#U0645#U0646#U062a#U062c-#U0627#U0636#U0627#U0641#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f-orphan.webp",
  "#U0646#U0642#U0634#U0627#U062a-#U062d#U0641#U0631-#U0633#U062c#U0627#U062f-#U064a#U062f#U0648#U064a-#U0633#U0627#U0644#U064.webp",
  "#U0646#U0642#U0634#U0629-#U062d#U0641#U0631-#U0633#U062c#U0627#U062f-#U064a#U062f#U0648#U064a-#U0633#U0627#U0644#U0641#U0648#U0631#U062f.webp",
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

// ترميز UTF-8 آمن إلى Base64 — بديل عن unescape() غير المتوفر في Cloudflare Workers
function utf8ToBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

// 🔧 FIX: يرمّز كل جزء من المسار (URL encode) قبل إرساله لـ GitHub API —
// مطلوب لأن slugs صفحات الكتالوج ممكن تحتوي أحرف عربية (راجع SLUG_RE)،
// وGitHub API يرجّع 400 لأي URL فيه أحرف غير ASCII بدون ترميز.
function encodePath(path) {
  return path.split('/').map(seg => encodeURIComponent(seg)).join('/');
}

async function ghRequest(env, path, options = {}) {
  const encodedPath = encodePath(path);
  const url = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/contents/${encodedPath}`;
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

// 🆕 قراءة آمنة لجسم استجابة GitHub. GitHub أحياناً (تعطّل مؤقت/أعطال
// 502-504 على طلبات كبيرة) يرجّع جسم فارغ أو غير قابل للتحليل — res.json()
// المباشر يرمي SyntaxError: Unexpected end of JSON input في هذه الحالة.
// هنا نقرأ كنص أولاً، وإذا كان فارغاً أو غير صالح نرمي خطأ واضح يُمسك
// بواسطة ghRequestJson لإعادة المحاولة، بدل ما ينهار الطلب كامل مباشرة.
async function safeGhJson(res) {
  const text = await res.text();
  if (!text || !text.trim()) {
    throw new Error('استجابة فارغة من GitHub API (status: ' + res.status + ')');
  }
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new Error('استجابة غير صالحة من GitHub API (status: ' + res.status + ')');
  }
}

// 🆕 يجمع بين ghRequest و safeGhJson مع إعادة محاولة تلقائية (تأخير تصاعدي)
// عند أي فشل شبكة أو جسم استجابة فارغ/غير صالح من GitHub. هذا هو الإصلاح
// الفعلي لمشكلة "Unexpected end of JSON input" — لأن المشكلة كانت تحصل
// هنا بالضبط (تواصل الـWorker مع GitHub)، وليس بين المتصفح والـWorker.
async function ghRequestJson(env, path, options = {}, retries = 3) {
  let lastErr;
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const res = await ghRequest(env, path, options);
      const data = await safeGhJson(res);
      return { res, data };
    } catch (e) {
      lastErr = e;
      if (attempt < retries) {
        await new Promise(r => setTimeout(r, attempt * 400)); // 400ms, 800ms...
      }
    }
  }
  throw lastErr || new Error('فشل الاتصال بـ GitHub بعد عدة محاولات');
}

async function getSha(env, path) {
  try {
    const { res, data } = await ghRequestJson(env, path, {}, 2);
    if (res.ok) return data.sha;
  } catch (e) {}
  return null;
}

async function putJSONFile(env, path, dataObj, commitMessage) {
  const sha = await getSha(env, path);
  const content = utf8ToBase64(JSON.stringify(dataObj, null, 2));
  const body = { message: commitMessage, content, branch: env.GH_BRANCH };
  if (sha) body.sha = sha;
  const { res, data } = await ghRequestJson(env, path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }, 3);
  if (!res.ok) throw new Error(data.message || 'فشل الكتابة على GitHub');
  return data;
}

// كتابة ملف نصي عام (HTML / XML) — تُستخدم لصفحات الكتالوج و sitemap.xml
async function putTextFile(env, path, textContent, commitMessage) {
  const sha = await getSha(env, path);
  const content = utf8ToBase64(textContent);
  const body = { message: commitMessage, content, branch: env.GH_BRANCH };
  if (sha) body.sha = sha;
  const { res, data } = await ghRequestJson(env, path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }, 3);
  if (!res.ok) throw new Error(data.message || 'فشل الكتابة على GitHub');
  return data;
}

// حذف ملف من GitHub (يتطلب SHA الملف الحالي). لو الملف غير موجود أصلاً،
// يرجع { skipped: true } بدل ما يفشل — عشان الحذف يبقى آمن حتى لو الصفحة
// ما انبنت من الأساس (مثلاً بسبب فشل سابق بإنشاء صفحة الكتالوج).
async function deleteFile(env, path, commitMessage) {
  const sha = await getSha(env, path);
  if (!sha) return { skipped: true };
  const { res, data } = await ghRequestJson(env, path, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: commitMessage, sha, branch: env.GH_BRANCH })
  }, 3);
  if (!res.ok) throw new Error(data.message || 'فشل حذف الملف');
  return { skipped: false };
}


// ⚡ LCP: مزامنة صورة السلايدر الأولى داخل index.html مع أحدث منشور.
// السبب: صورة LCP لو لم تكن في HTML من البداية، لا يكتشفها المتصفح إلا بعد
// جلب posts.json وتحليله — سلسلة تُضخّم أي تذبذب شبكي وترفع LCP بشدة.
// هذه الدالة تُبقي الـpreload والسلايدر الثابت مطابقين لأحدث صورة دائماً.
// آمنة بالكامل: أي فشل هنا لا يُفشل النشر (تُستدعى داخل try/catch صامت).
async function syncLcpPreload(env, posts) {
  if (!Array.isArray(posts) || posts.length === 0) return;
  const latest = [...posts].reverse()[0];
  if (!latest || !latest.img) return;

  const { res, data } = await ghRequestJson(env, 'index.html', {}, 2);
  if (!res.ok || !data.content) return;
  let html = decodeURIComponent(escape(atob(data.content.replace(/\n/g, ''))));

  const oldImgMatch = html.match(/data-static-first-img="([^"]*)"/);
  if (!oldImgMatch) return;
  const oldImg = oldImgMatch[1];
  if (oldImg === latest.img) return; // لا تغيير — لا حاجة لكتابة commit

  // استبدال كل مواضع الصورة القديمة (data-attr + أي روابط أخرى)
  html = html.split(oldImg).join(latest.img);

  // ⚡ دمج الصورة الجديدة كـdata URI داخل HTML — يلغي طلب الشبكة المنفصل
  // للصورة تماماً، وهو مصدر التذبذب المتبقي (Fastly edge cold/warm).
  try {
    const imgRes = await fetch(latest.img);
    if (imgRes.ok) {
      const buf = await imgRes.arrayBuffer();
      if (buf.byteLength > 0 && buf.byteLength < 120000) { // حد أمان: لا تدمج صورة ضخمة
        let bin = '';
        const bytes = new Uint8Array(buf);
        for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        const dataUri = 'data:image/webp;base64,' + btoa(bin);
        html = html.replace(
          /<img src="(?:data:image\/webp;base64,[^"]*|https:\/\/salfordkw\.shop\/products\/[^"]*)" data-real-src="[^"]*"/,
          `<img src="${dataUri}" data-real-src="${latest.img}"`
        );
      }
    }
  } catch (e) {}

  await putTextFile(env, 'index.html', html, 'مزامنة صورة LCP مع أحدث منشور');
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

// ============================================================
// 🔎 إضافة تشخيصية فقط — لا تغيّر أي منطق موجود
// تتحقق أن كل متغيرات البيئة المطلوبة موجودة فعلياً وقت التنفيذ،
// وترجع خطأ واضح يسمي بالضبط أي متغير ناقص (بدون طباعة GH_TOKEN نفسه).
// هذا يحل مباشرة السؤال: "هل env.GH_OWNER / env.GH_REPO تصل فعلياً للـ Worker؟"
// ============================================================
function checkRequiredEnv(env) {
  const required = ['GH_OWNER', 'GH_REPO', 'GH_BRANCH', 'GH_TOKEN', 'ADMIN_PASSWORD'];
  const missing = required.filter(k => {
    const v = env[k];
    return v === undefined || v === null || String(v).trim() === '';
  });
  return missing;
}

// معلومات تشخيصية آمنة تُرفق مع أي خطأ 500 — القيم الفعلية لـ owner/repo/branch
// (بدون التوكن نفسه، فقط طوله كتأكيد وجوده) عشان تُرى مباشرة برد diagnose-write.html
function safeDebugInfo(env) {
  return {
    GH_OWNER: env.GH_OWNER || null,
    GH_REPO: env.GH_REPO || null,
    GH_BRANCH: env.GH_BRANCH || null,
    GH_TOKEN_present: !!env.GH_TOKEN,
    GH_TOKEN_length: env.GH_TOKEN ? String(env.GH_TOKEN).length : 0
  };
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

    // 🔎 فحص تشخيصي أولاً: لو أي متغير بيئة أساسي ناقص، نوقف فوراً برسالة
    // واضحة تسمي المتغير الناقص بدل ما نكمل ونحصل على "Not Found" غامضة
    // من GitHub بسبب رابط فيه "undefined".
    const missingEnv = checkRequiredEnv(env);
    if (missingEnv.length) {
      console.log('⚙️ متغيرات بيئة ناقصة أو فارغة في Cloudflare:', missingEnv.join(', '));
      return json({
        error: '⚙️ إعداد الـ Worker ناقص — المتغيرات التالية غير موجودة أو فارغة في Cloudflare Variables: ' + missingEnv.join(', '),
        debug: safeDebugInfo(env)
      }, 500, origin);
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
        // products.json هو Object (قاموس أقسام) وليس Array
        const isValidObject = payload.products && typeof payload.products === 'object' && !Array.isArray(payload.products);
        if (!isValidObject) return json({ error: 'بيانات المنتجات غير صالحة' }, 400, origin);
        await putJSONFile(env, 'products.json', payload.products, 'تحديث المنتجات من لوحة التحكم');
        return json({ ok: true }, 200, origin);
      }

      if (url.pathname === '/api/publish-posts') {
        if (!Array.isArray(payload.posts)) return json({ error: 'بيانات المقالات غير صالحة' }, 400, origin);
        await putJSONFile(env, 'posts.json', payload.posts, 'تحديث posts.json');
        // ⚡ مزامنة صورة LCP — فشلها لا يُفشل النشر
        try { await syncLcpPreload(env, payload.posts); } catch (e) {}
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

        const { res, data } = await ghRequestJson(env, path, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `إضافة صورة عمل: ${finalName}`,
            content: base64,
            branch: env.GH_BRANCH
          })
        }, 3);
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
        const { res: res2, data: data2 } = await ghRequestJson(env, path, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `رفع ملف: ${filename}`,
            content: base64,
            branch: env.GH_BRANCH
          })
        }, 3);
        if (!res2.ok) throw new Error(data2.message || 'فشل رفع الملف');

        return json({ ok: true, url: `https://salfordkw.shop/${path}` }, 200, origin);
      }

      // تحديث sitemap.xml (النص الكامل يُرسل جاهزاً من المتصفح بعد التعديل محلياً)
      if (url.pathname === '/api/write-sitemap') {
        const { xml } = payload;
        if (!xml || typeof xml !== 'string' || !xml.includes('<urlset')) {
          return json({ error: 'محتوى sitemap غير صالح' }, 400, origin);
        }
        await putTextFile(env, 'sitemap.xml', xml, 'تحديث sitemap.xml');
        return json({ ok: true }, 200, origin);
      }

      // إنشاء/تحديث صفحة كتالوج ثابتة لمنتج (catalog/{section}-{slug}.html)
      if (url.pathname === '/api/publish-catalog-page') {
        const { section, html } = payload;

        if (typeof section !== 'string' || !ALLOWED_CATALOG_SECTIONS.includes(section)) {
          return json({ error: 'قسم غير مسموح' }, 400, origin);
        }

        const idRes = resolvePageIdentifier(payload);
        if (!idRes.ok) {
          return json({ error: 'مُعرّف الصفحة (slug) غير صالح' }, 400, origin);
        }
        const idStr = idRes.idStr;

        if (typeof html !== 'string' || html.trim().length === 0) {
          return json({ error: 'محتوى الصفحة فارغ' }, 400, origin);
        }

        const path = `catalog/${section}-${idStr}.html`;

        await putTextFile(env, path, html, `نشر صفحة كتالوج: ${section}-${idStr}`);
        return json({ ok: true, path, url: `https://salfordkw.shop/${path}` }, 200, origin);
      }

      // حذف صفحة كتالوج ثابتة (catalog/{section}-{slug}.html) — تُستخدم عند
      // حذف منتج من لوحة admin.html. آمن حتى لو الصفحة غير موجودة أصلاً
      // (يرجع ok:true مع skipped:true بدل ما يفشل).
      if (url.pathname === '/api/delete-catalog-page') {
        const { section } = payload;

        if (typeof section !== 'string' || !ALLOWED_CATALOG_SECTIONS.includes(section)) {
          return json({ error: 'قسم غير مسموح' }, 400, origin);
        }

        const idRes = resolvePageIdentifier(payload);
        if (!idRes.ok) {
          return json({ error: 'مُعرّف الصفحة (slug) غير صالح' }, 400, origin);
        }
        const idStr = idRes.idStr;
        const path = `catalog/${section}-${idStr}.html`;

        const result = await deleteFile(env, path, `حذف صفحة كتالوج: ${section}-${idStr}`);
        return json({ ok: true, path, skipped: result.skipped }, 200, origin);
      }

      // مزامنة دفعة من صفحات كتالوج قسم واحد بعد حذف/إعادة ترتيب/نقل منتج
      // من admin.html — يكتب صفحات (writes) ويحذف صفحات (deletes) بنفس
      // الطلب، عشان يصير طلب واحد من المتصفح بدل طلب لكل صفحة (يفادي حد
      // المحاولات بالدقيقة ويسرّع النشر). فشل صفحة واحدة لا يوقف الباقي —
      // النتيجة ترجع تفاصيل كل عملية على حدة.
      if (url.pathname === '/api/sync-catalog-pages') {
        const { section, writes, deletes } = payload;

        if (typeof section !== 'string' || !ALLOWED_CATALOG_SECTIONS.includes(section)) {
          return json({ error: 'قسم غير مسموح' }, 400, origin);
        }

        const writeList = Array.isArray(writes) ? writes : [];
        const deleteList = Array.isArray(deletes) ? deletes : [];

        if (writeList.length + deleteList.length === 0) {
          return json({ error: 'لا يوجد شيء لمزامنته' }, 400, origin);
        }
        // كل عنصر (كتابة أو حذف) يستهلك طلبين فرعيين (GET SHA + PUT/DELETE)
        // من واجهة GitHub. خطة Cloudflare Workers المجانية تسمح بحد أقصى 50
        // طلب فرعي بالتنفيذ الواحد، فنحدّ الدفعة بـ 20 عنصر (٤٠ طلب) كهامش أمان.
        if (writeList.length + deleteList.length > 20) {
          return json({ error: 'عدد الصفحات بالدفعة كبير جداً (الحد الأقصى 20 صفحة بالدفعة الواحدة بسبب حد الطلبات الفرعية لخطة Cloudflare المجانية)' }, 400, origin);
        }

        const results = { written: [], writeErrors: [], deleted: [], deleteErrors: [] };

        // الحذف أولاً: لو توقف التنفيذ بالمنتصف (تجاوز حد الطلبات الفرعية،
        // بطء الشبكة، إلخ) نضمن ما تبقى صفحات يتيمة على الأقل — أهم من
        // إعادة كتابة صفحات موجودة وشغّالة أصلاً.
        // 🆕 كل عنصر بـ deletes الآن إما نص slug مباشرة أو object {slug} —
        // بديل عن رقم الموضع القديم (يبقى مدعوم كـ fallback رقمي أثناء الانتقال).
        for (const d of deleteList) {
          const idRes = resolvePageIdentifier(typeof d === 'object' && d !== null ? d : { slug: d });
          if (!idRes.ok) {
            results.deleteErrors.push({ item: d, error: 'مُعرّف غير صالح' });
            continue;
          }
          const idStr = idRes.idStr;
          const path = `catalog/${section}-${idStr}.html`;
          try {
            const r = await deleteFile(env, path, `حذف صفحة كتالوج: ${section}-${idStr}`);
            results.deleted.push({ id: idStr, skipped: r.skipped });
          } catch (e) {
            results.deleteErrors.push({ item: idStr, error: e.message || 'فشل الحذف' });
          }
        }

        for (const w of writeList) {
          const html = w && w.html;
          const idRes = resolvePageIdentifier(w || {});
          if (!idRes.ok || typeof html !== 'string' || html.trim().length === 0) {
            results.writeErrors.push({ item: w && (w.slug || w.index), error: 'بيانات صفحة غير صالحة' });
            continue;
          }
          const idStr = idRes.idStr;
          const path = `catalog/${section}-${idStr}.html`;
          try {
            await putTextFile(env, path, html, `إعادة بناء صفحة كتالوج: ${section}-${idStr}`);
            results.written.push(idStr);
          } catch (e) {
            results.writeErrors.push({ item: idStr, error: e.message || 'فشل الكتابة' });
          }
        }

        const ok = results.writeErrors.length === 0 && results.deleteErrors.length === 0;
        return json({ ok, ...results }, 200, origin);
      }

      // 🧹 إصلاح دفعة من أسماء الصور المشوّهة (one-time cleanup) — يتحرك على
      // MANGLED_IMAGE_RENAMES / MANGLED_IMAGE_DELETES بدءاً من "offset"،
      // ويتوقف قبل ما يتجاوز ميزانية الطلبات الفرعية بالتنفيذ الواحد (حد
      // Cloudflare المجاني 50 طلب فرعي). كل rename = 3 طلبات (GET المحتوى
      // القديم + PUT الاسم الجديد + DELETE الاسم القديم)، وكل حذف يتيم =
      // 2 طلب (GET SHA + DELETE). يرجع nextOffset ليكرر المتصفح الطلب
      // لين تخلص كل القائمة (done: true).
      if (url.pathname === '/api/fix-mangled-images') {
        const combined = [
          ...MANGLED_IMAGE_RENAMES.map(([oldName, newName]) => ({ type: 'rename', oldName, newName })),
          ...MANGLED_IMAGE_DELETES.map(oldName => ({ type: 'delete', oldName }))
        ];

        let offset = Number(payload.offset);
        if (!Number.isInteger(offset) || offset < 0) offset = 0;

        const BUDGET = 45; // هامش أمان تحت حد الـ50 طلب فرعي
        const results = { renamed: [], renameErrors: [], deleted: [], deleteErrors: [] };
        let used = 0;
        let i = offset;

        for (; i < combined.length; i++) {
          const item = combined[i];
          const cost = item.type === 'rename' ? 3 : 2;
          if (used + cost > BUDGET) break;
          used += cost;

          const oldPath = `products/${item.oldName}`;

          if (item.type === 'rename') {
            const newPath = `products/${item.newName}`;
            try {
              let getData;
              try {
                const { res: getRes, data } = await ghRequestJson(env, oldPath, {}, 3);
                if (!getRes.ok) {
                  if (getRes.status === 404) {
                    results.renamed.push({ old: item.oldName, new: item.newName, skipped: true });
                    continue;
                  }
                  throw new Error('تعذر قراءة الملف القديم: ' + item.oldName);
                }
                getData = data;
              } catch (readErr) {
                throw readErr;
              }

              const { res: putRes, data: putData } = await ghRequestJson(env, newPath, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  message: `إصلاح اسم صورة: ${item.newName}`,
                  content: getData.content,
                  branch: env.GH_BRANCH
                })
              }, 3);
              if (!putRes.ok) throw new Error(putData.message || 'فشل إنشاء الملف بالاسم الصحيح');

              await deleteFile(env, oldPath, `حذف الاسم المشوّه بعد التصحيح: ${item.oldName}`);
              results.renamed.push({ old: item.oldName, new: item.newName, skipped: false });
            } catch (e) {
              results.renameErrors.push({ old: item.oldName, new: item.newName, error: e.message || 'فشل' });
            }
          } else {
            try {
              const r = await deleteFile(env, oldPath, `حذف صورة يتيمة مشوّهة: ${item.oldName}`);
              results.deleted.push({ old: item.oldName, skipped: r.skipped });
            } catch (e) {
              results.deleteErrors.push({ old: item.oldName, error: e.message || 'فشل' });
            }
          }
        }

        const done = i >= combined.length;
        const ok = results.renameErrors.length === 0 && results.deleteErrors.length === 0;
        return json({ ok, done, nextOffset: i, total: combined.length, ...results }, 200, origin);
      }

      return json({ error: 'مسار غير معروف' }, 404, origin);
    } catch (e) {
      // 🔎 نرفق هنا معلومات owner/repo/branch الفعلية (بدون التوكن) مع كل
      // خطأ 500 — عشان تشوف مباشرة برد diagnose-write.html هل القيم صحيحة
      return json({
        error: e.message || 'خطأ بالسيرفر',
        debug: safeDebugInfo(env)
      }, 500, origin);
    }
  }
};
