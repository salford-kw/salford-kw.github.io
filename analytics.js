/* ============================================================
   سالفورد — مراقبة زيارات الموقع ونقرات الاتصال/واتساب (Firebase)
   يُضاف بإضافة السطور الثلاثة التالية قبل إغلاق </body> بأي صفحة:

   <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
   <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-firestore.js"></script>
   <script src="/analytics.js"></script>

   (إذا كانت الصفحة تحمّل reviews-widget.js أصلاً — Firebase محمّل مسبقاً،
   فقط أضف سطر analytics.js وحده)

   يسجّل: زيارات الصفحة/الموقع، نقرات الاتصال وواتساب (إجمالي + لكل صفحة/منتج
   + حسب الجهاز جوال/كمبيوتر)، وبيانات يومية لحساب الاتجاه الأسبوعي/الشهري
   وتنبيه الصفحات بدون زيارات.
   ============================================================ */
(function () {
  if (typeof firebase === 'undefined') return;

  var firebaseConfig = {
    apiKey: "AIzaSyB6imGpaY05BQYPvC9ObNTKR8aHz9u5u0I",
    authDomain: "salford-reviews.firebaseapp.com",
    projectId: "salford-reviews",
    storageBucket: "salford-reviews.firebasestorage.app",
    messagingSenderId: "126143260748",
    appId: "1:126143260748:web:431de7abe3b952420aece9",
    measurementId: "G-714VYZ0K2L"
  };

  try {
    if (!firebase.apps.length) firebase.initializeApp(firebaseConfig);
  } catch (e) { return; }

  var db = firebase.firestore();
  var inc = firebase.firestore.FieldValue.increment(1);
  var counterRef = db.collection('analytics').doc('counters');

  function getPageName() {
    var p = location.pathname.replace(/^\/|\/$/g, '');
    if (p === '' || p === 'index.html') return 'home';
    p = p.replace(/\.html$/, '').replace(/\//g, '_');
    return p || 'other';
  }
  function getDateStr() {
    try { return new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kuwait' }); }
    catch (e) { return new Date().toISOString().slice(0, 10); }
  }
  function isMobile() {
    return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent || '');
  }

  var page = getPageName();
  var today = getDateStr();
  var dailyRef = db.collection('analytics_daily').doc(today);

  function safeSet(ref, data) { ref.set(data, { merge: true }).catch(function () {}); }

  // 1) زيارة صفحة — إجمالي دائم + سجل يومي
  var pageField = {}; pageField[page] = inc;
  safeSet(counterRef, { pages: pageField });
  safeSet(dailyRef, { pages: pageField });

  // 2) زيارة موقع (جلسة متصفح) — تُحتسب مرة واحدة لكل جلسة، وأيضاً مرة لكل يوم
  try {
    if (!sessionStorage.getItem('salford_visited')) {
      sessionStorage.setItem('salford_visited', '1');
      safeSet(counterRef, { site_visits: inc });
    }
    var visitedTodayKey = 'salford_visited_' + today;
    if (!sessionStorage.getItem(visitedTodayKey)) {
      sessionStorage.setItem(visitedTodayKey, '1');
      safeSet(dailyRef, { site_visits: inc });
    }
  } catch (e) {}

  // 3) نقرات الاتصال وواتساب — تُلتقط تلقائياً من أي رابط tel: أو wa.me
  //    بدون الحاجة لتعديل أي زر موجود بالصفحة — تُسجَّل إجمالي + لكل صفحة/منتج + حسب الجهاز
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a || !a.href) return;
    var type = null;
    if (a.href.indexOf('tel:') === 0) type = 'call';
    else if (a.href.indexOf('wa.me') !== -1 || a.href.indexOf('whatsapp') !== -1) type = 'whatsapp';
    if (!type) return;

    var device = isMobile() ? 'mobile' : 'desktop';
    var clicksField = {}; clicksField[type] = inc;
    var byPageField = {}; byPageField[page] = clicksField;
    var deviceField = {}; deviceField[type] = {}; deviceField[type][device] = inc;

    safeSet(counterRef, { clicks: clicksField });
    safeSet(counterRef, { clicks_by_page: byPageField });
    safeSet(counterRef, { device: deviceField });
    safeSet(dailyRef, { clicks: clicksField });
  }, true);

  // 4) نقرات أزرار "تصفّح أقسامنا" بالصفحة الرئيسية (class="cat-card")
  //    تُسجَّل بمفتاح ثابت مبني من رابط القسم (مو النص) — ما يتأثر لو
  //    تغيّر عنوان القسم لاحقاً. إجمالي + حسب الجهاز + سجل يومي.
  document.addEventListener('click', function (e) {
    var card = e.target.closest && e.target.closest('.cat-card');
    if (!card || !card.getAttribute) return;
    var href = card.getAttribute('href') || '';
    if (!href) return;

    var catKey = href.replace(/^\//, '').replace(/\.html$/, '') || 'other';
    var device = isMobile() ? 'mobile' : 'desktop';

    var catField = {}; catField[catKey] = inc;
    var catDeviceField = {}; catDeviceField[catKey] = {}; catDeviceField[catKey][device] = inc;

    safeSet(counterRef, { category_clicks: catField });
    safeSet(counterRef, { category_clicks_device: catDeviceField });
    safeSet(dailyRef, { category_clicks: catField });
  }, true);
})();
