/* SINO TIB katalog muharriri: matn va rasmlarni brauzerning o'zida o'zgartirish. */
(() => {
  "use strict";

  const VERSION = 4; // shablon o'zgarsa oshiriladi — eski saqlangan nusxa e'tiborga olinmaydi
  const KEY = `sinotib-katalog-v${VERSION}`;
  const TEXT = ".page :is(h1, h2, h3, h4, p, li > span, dt, dd, b, small, figcaption, td:not(:has(*)), .e)";

  const $ = (s) => document.querySelector(s);
  const book = $("#book");
  const editBtn = $("#btn-edit");
  const fileInput = $("#file");
  let editing = false;
  let targetImg = null;

  /* ---------- Saqlash ---------- */

  function restore() {
    try {
      const saved = localStorage.getItem(KEY);
      if (saved) book.innerHTML = saved;
    } catch { /* localStorage yopiq bo'lishi mumkin */ }
  }

  let saveTimer;
  function save() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      try {
        localStorage.setItem(KEY, cleanHTML(book));
        toast("Saqlandi");
      } catch {
        toast("Brauzerda joy yetmadi — «HTML saqlash» orqali faylga yuklab oling");
      }
    }, 600);
  }

  function cleanHTML(root) {
    const clone = root.cloneNode(true);
    clone.querySelectorAll("[contenteditable]").forEach((el) => el.removeAttribute("contenteditable"));
    clone.querySelectorAll("[spellcheck]").forEach((el) => el.removeAttribute("spellcheck"));
    return clone.innerHTML;
  }

  /* ---------- Tahrirlash rejimi ---------- */

  function setEditing(on) {
    editing = on;
    document.body.classList.toggle("editing", on);
    editBtn.setAttribute("aria-pressed", on);
    editBtn.querySelector("span").textContent = on ? "Tayyor" : "Tahrirlash";
    book.querySelectorAll(TEXT).forEach((el) => {
      if (on) { el.contentEditable = "true"; el.spellcheck = false; }
      else el.removeAttribute("contenteditable");
    });
  }

  editBtn.addEventListener("click", () => setEditing(!editing));

  book.addEventListener("input", save);

  // Formatlangan matn emas, oddiy matn qo'yiladi
  book.addEventListener("paste", (e) => {
    if (!editing) return;
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData("text/plain");
    document.execCommand("insertText", false, text);
  });

  // Rasmni almashtirish
  book.addEventListener("click", (e) => {
    if (!editing) return;
    const img = e.target.closest("img[data-img]");
    if (!img) return;
    targetImg = img;
    fileInput.value = "";
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file || !targetImg) return;
    const reader = new FileReader();
    reader.onload = () => {
      targetImg.src = reader.result;
      save();
    };
    reader.readAsDataURL(file);
  });

  /* ---------- Tugmalar ---------- */

  $("#btn-print").addEventListener("click", () => {
    setEditing(false);
    window.print();
  });

  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("Barcha o'zgarishlar o'chib, katalog asl holiga qaytadi. Davom etilsinmi?")) return;
    try { localStorage.removeItem(KEY); } catch { /* */ }
    location.reload();
  });

  $("#btn-download").addEventListener("click", () => {
    const doc = document.documentElement.cloneNode(true);
    doc.querySelector("#book").innerHTML = cleanHTML(book);
    doc.querySelector("body").classList.remove("editing");
    doc.querySelector("#btn-edit")?.setAttribute("aria-pressed", "false");
    const html = "<!doctype html>\n" + doc.outerHTML;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([html], { type: "text/html" }));
    a.download = "index.html";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast("index.html yuklab olindi — uni katalog-a4 papkasidagi faylning o'rniga qo'ying");
  });

  /* ---------- Ekranga moslash ---------- */

  function fit() {
    const pageWidth = 210 * 96 / 25.4; // 210mm pikselda
    const scale = Math.min(1, (window.innerWidth - 24) / pageWidth);
    book.style.setProperty("--fit", scale.toFixed(3));
  }

  window.addEventListener("resize", fit);

  let toastTimer;
  function toast(text) {
    const el = $("#toast");
    el.textContent = text;
    el.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-visible"), 2400);
  }

  restore();
  fit();
})();
