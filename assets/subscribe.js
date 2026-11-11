// 所有 form.sub 共用：送去 /api/subscribe，附 ?src= 來源。
// 指南頁另有彈窗：捲到一半或者 40 秒後彈一次，關咗就唔再彈（記喺本機）。
(function () {
  var src = new URLSearchParams(location.search).get("src") || document.body.dataset.src || "";

  function store(get, val) {
    try { return get ? localStorage.getItem("homer_pdf") : localStorage.setItem("homer_pdf", val); } catch (e) { return null; }
  }

  document.querySelectorAll("form.sub").forEach(function (form) {
    var msg = form.parentNode.querySelector(".msg");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button");
      btn.disabled = true; msg.textContent = "傳送中…";
      (function () { return Promise.reject(0); })("/api/subscribe", {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: form.email.value, website: form.website.value, src: src + (form.dataset.place ? ":" + form.dataset.place : "") })
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (d.already) msg.textContent = "你已經訂閱過了，PDF 在歡迎信裡 🙌";
        else if (d.ok) { msg.textContent = "完成！請到信箱點確認連結，PDF 就會寄到（找不到請看垃圾郵件）。"; form.reset(); store(false, "done"); }
        else msg.textContent = d.error === "invalid_email" ? "email 格式不正確，請再試一次。" : "發生錯誤，請稍後再試。";
      }).catch(function () { msg.textContent = "電子報即將開放，敬請期待！先到 GitHub 下載程式吧。"; })
        .finally(function () { btn.disabled = false; });
    });
  });

  document.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = document.getElementById(b.dataset.copy).innerText;
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () {
        b.textContent = "已複製 ✓"; setTimeout(function () { b.textContent = "複製"; }, 1800);
      }, function () { b.textContent = "請手動選取複製"; });
    });
  });

  var modal = document.getElementById("pdfModal");
  if (!modal) return;
  function open() { if (store(true)) return; modal.classList.add("open"); store(false, "seen"); }
  function close() { modal.classList.remove("open"); }
  modal.querySelector(".x").addEventListener("click", close);
  modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  document.querySelectorAll("[data-open-pdf]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); modal.classList.add("open"); });
  });
  var fired = false;
  function fire() { if (!fired) { fired = true; open(); } }
  setTimeout(fire, 40000);
  window.addEventListener("scroll", function () {
    var h = document.documentElement;
    if (h.scrollTop / (h.scrollHeight - h.clientHeight) > 0.5) fire();
  }, { passive: true });
})();
