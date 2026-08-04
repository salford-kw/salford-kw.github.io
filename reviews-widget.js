/* ============================================================
   سالفورد — نظام التقييمات والتعليقات (Firebase Firestore)
   ملف مشترك يُستخدم في: majalis.html, sajjad.html, athath.html
   ============================================================ */

const firebaseConfig = {
  apiKey: "AIzaSyB6imGpaY05BQYPvC9ObNTKR8aHz9u5u0I",
  authDomain: "salford-reviews.firebaseapp.com",
  projectId: "salford-reviews",
  storageBucket: "salford-reviews.firebasestorage.app",
  messagingSenderId: "126143260748",
  appId: "1:126143260748:web:431de7abe3b952420aece9",
  measurementId: "G-714VYZ0K2L"
};

if (!window.firebase.apps.length) {
  window.firebase.initializeApp(firebaseConfig);
}
const srDb = window.firebase.firestore();

const srCache = {}; // productId -> unsubscribe function
const srListeners = {}; // productId -> [callback,...]

function srEscape(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function srRelativeDate(ts) {
  if (!ts) return '';
  const d = ts.toDate ? ts.toDate() : new Date(ts);
  const diff = Math.round((Date.now() - d.getTime()) / 86400000);
  if (diff <= 0) return 'اليوم';
  if (diff === 1) return 'أمس';
  if (diff < 7) return `منذ ${diff} أيام`;
  if (diff < 30) return `منذ ${Math.floor(diff / 7)} أسبوع`;
  if (diff < 365) return `منذ ${Math.floor(diff / 30)} شهر`;
  return `منذ ${Math.floor(diff / 365)} سنة`;
}

function srStarsHtml(rating, size) {
  size = size || 14;
  let html = '';
  for (let i = 1; i <= 5; i++) {
    html += `<span style="color:${i <= rating ? '#FFD700' : 'rgba(255,255,255,.15)'};font-size:${size}px;">★</span>`;
  }
  return html;
}

/* ============================================================
   تحميل التقييمات لمنتج معيّن (Real-time)
   ============================================================ */
function srSubscribe(productId, cb) {
  if (!srListeners[productId]) srListeners[productId] = [];
  srListeners[productId].push(cb);

  if (srCache[productId]) {
    // مشترك مسبقاً — استدعِ الكولباك بآخر بيانات إذا متوفرة
    return;
  }

  const unsub = srDb.collection('reviews')
    .where('productId', '==', productId)
    .onSnapshot(snap => {
      const reviews = [];
      snap.forEach(doc => reviews.push({ id: doc.id, ...doc.data() }));
      reviews.sort((a, b) => {
        const ta = a.createdAt && a.createdAt.toMillis ? a.createdAt.toMillis() : 0;
        const tb = b.createdAt && b.createdAt.toMillis ? b.createdAt.toMillis() : 0;
        return tb - ta;
      });
      (srListeners[productId] || []).forEach(fn => fn(reviews));
    }, err => {
      console.error('Reviews load error:', err);
      (srListeners[productId] || []).forEach(fn => fn([]));
    });

  srCache[productId] = unsub;
}

/* ============================================================
   الودجت الكامل: ملخص النجوم + قائمة التقييمات + نموذج الإضافة
   ============================================================ */
function initProductReviews(productId, mountEl) {
  if (typeof mountEl === 'string') mountEl = document.getElementById(mountEl);
  if (!mountEl) return;

  mountEl.innerHTML = `
    <div class="sr-summary" id="sr-summary-${productId}">
      <span class="sr-loading">⏳ جاري تحميل التقييمات...</span>
    </div>
    <div class="sr-list" id="sr-list-${productId}"></div>
    <div class="sr-form-box">
      <div class="sr-form-title">✍️ شاركنا رأيك بهذا المنتج</div>
      <div class="sr-star-picker" id="sr-picker-${productId}"></div>
      <input type="text" class="sr-input" id="sr-name-${productId}" placeholder="اسمك" maxlength="60">
      <textarea class="sr-input sr-textarea" id="sr-comment-${productId}" placeholder="اكتب تعليقك (اختياري)" maxlength="500"></textarea>
      <input type="text" class="sr-honeypot" id="sr-hp-${productId}" tabindex="-1" autocomplete="off">
      <button class="sr-submit-btn" id="sr-submit-${productId}" onclick="srSubmitReview('${productId}')">إرسال التقييم</button>
      <div class="sr-status" id="sr-status-${productId}"></div>
    </div>
  `;

  renderStarPicker(productId);

  srSubscribe(productId, reviews => renderReviews(productId, reviews));
}

let srSelectedRating = {};

function renderStarPicker(productId) {
  const wrap = document.getElementById(`sr-picker-${productId}`);
  srSelectedRating[productId] = 0;
  const draw = () => {
    wrap.innerHTML = [1,2,3,4,5].map(i => `
      <span class="sr-pick-star" data-i="${i}" onclick="srSetRating('${productId}',${i})"
        style="color:${i <= srSelectedRating[productId] ? '#FFD700' : 'rgba(255,255,255,.2)'};">★</span>
    `).join('');
  };
  wrap._draw = draw;
  draw();
}

function srSetRating(productId, i) {
  srSelectedRating[productId] = i;
  const wrap = document.getElementById(`sr-picker-${productId}`);
  if (wrap && wrap._draw) wrap._draw();
}

function renderReviews(productId, reviews) {
  const summaryEl = document.getElementById(`sr-summary-${productId}`);
  const listEl = document.getElementById(`sr-list-${productId}`);
  if (!summaryEl || !listEl) return;

  if (reviews.length === 0) {
    summaryEl.innerHTML = `<span class="sr-empty">🆕 كن أول من يقيّم هذا المنتج</span>`;
    listEl.innerHTML = '';
    return;
  }

  const avg = reviews.reduce((s, r) => s + (r.rating || 0), 0) / reviews.length;
  summaryEl.innerHTML = `
    <span class="sr-avg">${avg.toFixed(1)}</span>
    <span class="sr-avg-stars">${srStarsHtml(Math.round(avg), 16)}</span>
    <span class="sr-count">(${reviews.length} تقييم)</span>
  `;

  listEl.innerHTML = reviews.slice(0, 20).map(r => `
    <div class="sr-review-card">
      <div class="sr-review-head">
        <span class="sr-review-name">${srEscape(r.name || 'عميل')}</span>
        <span class="sr-review-stars">${srStarsHtml(r.rating || 0, 12)}</span>
      </div>
      ${r.comment ? `<p class="sr-review-body">${srEscape(r.comment)}</p>` : ''}
      <span class="sr-review-date">${srRelativeDate(r.createdAt)}</span>
    </div>
  `).join('');
}

async function srSubmitReview(productId) {
  const btn = document.getElementById(`sr-submit-${productId}`);
  const statusEl = document.getElementById(`sr-status-${productId}`);
  const rating = srSelectedRating[productId] || 0;
  const name = document.getElementById(`sr-name-${productId}`).value.trim();
  const comment = document.getElementById(`sr-comment-${productId}`).value.trim();
  const honeypot = document.getElementById(`sr-hp-${productId}`).value;

  if (honeypot) return; // بوت
  if (rating < 1 || rating > 5) { statusEl.textContent = '⚠️ اختر تقييم بالنجوم أولاً'; statusEl.style.color = '#ff6b6b'; return; }
  if (!name) { statusEl.textContent = '⚠️ أدخل اسمك'; statusEl.style.color = '#ff6b6b'; return; }

  btn.disabled = true;
  statusEl.textContent = '📤 جاري الإرسال...';
  statusEl.style.color = '';

  try {
    await srDb.collection('reviews').add({
      productId,
      name: name.slice(0, 60),
      rating,
      comment: comment.slice(0, 500),
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    });
    statusEl.textContent = '✅ شكراً لك! تم نشر تقييمك';
    statusEl.style.color = '#1ebe52';
    document.getElementById(`sr-name-${productId}`).value = '';
    document.getElementById(`sr-comment-${productId}`).value = '';
    srSetRating(productId, 0);
  } catch (e) {
    statusEl.textContent = '❌ حدث خطأ، حاول مرة أخرى';
    statusEl.style.color = '#ff6b6b';
    console.error(e);
  } finally {
    btn.disabled = false;
  }
}

/* ============================================================
   دالة مساعدة: جلب متوسط التقييم فقط (لعرض النجوم على كارد المنتج
   بدون فتح الودجت الكامل) — تُستخدم بقوائم المنتجات
   ============================================================ */
function srAttachMiniRating(productId, mountEl) {
  if (typeof mountEl === 'string') mountEl = document.getElementById(mountEl);
  if (!mountEl) return;
  srSubscribe(productId, reviews => {
    if (reviews.length === 0) { mountEl.innerHTML = ''; return; }
    const avg = reviews.reduce((s, r) => s + (r.rating || 0), 0) / reviews.length;
    mountEl.innerHTML = `${srStarsHtml(Math.round(avg), 11)} <span style="font-size:10px;color:rgba(200,169,110,.6);">(${reviews.length})</span>`;
  });
}
