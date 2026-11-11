// 捲到先彈出：自動幫標題、卡、步驟、表、FAQ 加 .rv；同一組嘅卡逐個遲少少出。
// 冇 JS 或者揀咗「減少動態」嘅人，全部照常顯示。
(function () {
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!("IntersectionObserver" in window) || reduce) { document.documentElement.classList.remove("js"); runChat(true); return; }
  document.documentElement.classList.add("js");

  var sel = "main h1, main .lead, main .cta, main .meta, main .kicker, main h2, main section > h3, main section > p, " +
    ".stat, .card, .stepcard, .callout, .tablewrap, ol.steps li, details.faq, .magnet, .sources, .chatdemo, footer";
  var els = [].slice.call(document.querySelectorAll(sel));
  var set = new Set(els);
  els.forEach(function (el) {
    el.classList.add(el.matches(".stat") ? "rv-pop" : "rv");
    var p = el.parentNode;
    if (p && p.matches(".cards, .stats, .toc-hub, ol.steps, #faq")) {
      var i = [].filter.call(p.children, function (c) { return set.has(c); }).indexOf(el);
      if (i > 0) el.style.setProperty("--d", Math.min(i, 6) * 0.08 + "s");
    }
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); if (e.target.classList.contains("chatdemo")) runChat(false); }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  els.forEach(function (el) { io.observe(el); });
  // 保險：萬一觀察器冇反應（舊瀏覽器、嵌入頁），3 秒後全部顯示，唔好令內容消失
  setTimeout(function () {
    if (!document.querySelector(".rv.in, .rv-pop.in")) { els.forEach(function (el) { el.classList.add("in"); }); runChat(true); }
  }, 3000);

  // 開頭對話：逐句彈出，中間有「打緊字」
  function runChat(instant) {
    var box = document.querySelector(".chatdemo");
    if (!box || box.dataset.ran) return;
    box.dataset.ran = "1";
    var bubs = [].slice.call(box.querySelectorAll(".bub")), typing = box.querySelector(".typing");
    if (instant) { bubs.forEach(function (b) { b.classList.add("show"); }); return; }
    var t = 300;
    bubs.forEach(function (b) {
      var bot = b.classList.contains("bot");
      if (bot) {
        setTimeout(function () { box.insertBefore(typing, b); typing.classList.add("on"); }, t);
        t += 900;
      }
      setTimeout(function () { if (bot) typing.classList.remove("on"); b.classList.add("show"); }, t);
      t += bot ? 700 : 600;
    });
  }
})();
