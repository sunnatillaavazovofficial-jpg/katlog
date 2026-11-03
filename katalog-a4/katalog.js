/* SINO TIB katalog muharriri: matn va rasmlarni brauzerning o'zida o'zgartirish. */
(() => {
  "use strict";

  const VERSION = 8; // shablon o'zgarsa oshiriladi — eski saqlangan nusxa e'tiborga olinmaydi
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

  book.addEventListener("input", (e) => {
    if (e.target.closest(".pp__title, .pp__sub, .inf__body")) fitText();
    save();
  });

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
    // Keng ekranda rasm va ma'lumot sahifalari yonma-yon, telefonda bittadan
    const mm = 96 / 25.4;
    const spread = window.innerWidth >= 900;
    book.classList.toggle("book--spread", spread);
    const scale = Math.min(1, (window.innerWidth - 24) / ((spread ? 420 : 210) * mm));
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

  /* Uzun nom va tavsif bir qatorga sig'guncha shrift kichraytiriladi */
  function fitText() {
    book.querySelectorAll(".pp__title, .pp__sub").forEach((el) => {
      el.style.fontSize = "";
      let size = parseFloat(getComputedStyle(el).fontSize);
      const min = size * 0.55;
      while (el.scrollWidth > el.clientWidth + 1 && size > min) {
        size -= 0.5;
        el.style.fontSize = `${size}px`;
      }
    });
    // Ma'lumot sahifasi: matn imkon qadar katta, lekin sahifaga sig'adigan qilib tanlanadi
    book.querySelectorAll(".inf__body").forEach((body) => {
      let s = 1.08;
      body.style.setProperty("--s", s);
      while (body.scrollHeight > body.clientHeight + 1 && s > 0.8) {
        s = Math.round((s - 0.02) * 100) / 100;
        body.style.setProperty("--s", s);
      }
    });
  }

  restore();
  fit();
  // Eksport skriptlari shu belgini kutadi (tools/svg-eksport.js)
  document.fonts.ready.then(() => {
    fitText();
    document.documentElement.dataset.ready = "1";
  });
})();
