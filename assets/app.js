/* Katalog — rasmlarni images/ papkasidan o'zi topib, katalog qilib ko'rsatadi.
   Papka = bo'lim, fayl nomi = "Mahsulot nomi_150000.jpg" (pastki chiziqdan keyin narx). */
(() => {
  "use strict";

  const IMAGE_EXT = /\.(jpe?g|png|webp|gif|avif)$/i;
  const $ = (sel) => document.querySelector(sel);
  const state = { settings: {}, products: [], category: "all", query: "", sort: "default", current: null, index: 0 };

  /* ---------- Yordamchilar ---------- */

  const norm = (s) => String(s || "").toLowerCase().replace(/[ʻʼ‘’`´]/g, "'").trim();
  const slug = (s) => norm(s).replace(/'/g, "").replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "");
  const money = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  const currency = () => state.settings.shop?.currency || "so'm";
  const fmt = (n) => `${money(n)} ${currency()}`;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const naturalCompare = new Intl.Collator("uz", { numeric: true, sensitivity: "base" }).compare;
  const encodePath = (p) => p.split("/").map(encodeURIComponent).join("/");
  const stripOrder = (s) => s.replace(/^\d+[\s._-]+(?=\S)/, "");

  function parseTitle(base) {
    let name = base;
    let price = null;
    const m = base.match(/^(.*?)_\s*([\d][\d\s.,]*)\s*(?:so'?m|sum|som)?\s*$/i);
    if (m && m[1].trim()) {
      name = m[1];
      price = parseInt(m[2].replace(/\D/g, ""), 10) || null;
    }
    name = name.trim();
    name = /\s/.test(name) ? name.replace(/_+/g, " ") : name.replace(/[-_]+/g, " ");
    name = name.charAt(0).toUpperCase() + name.slice(1);
    return { name, price };
  }

  /* images/ ichidagi fayl yo'llaridan mahsulotlar ro'yxatini tuzadi */
  function buildProducts(files, dates = {}) {
    const groups = new Map();
    const texts = new Map();
    for (const path of files) {
      const rel = path.replace(/^images\//, "");
      const parts = rel.split("/");
      if (parts.some((p) => p.startsWith("."))) continue;
      const file = parts[parts.length - 1];
      const base = file.replace(/\.[^.]+$/, "");
      let category = "";
      let key;
      if (parts.length === 1) key = base;
      else if (parts.length === 2) { category = parts[0]; key = `${parts[0]}/${base}`; }
      else { category = parts[0]; key = `${parts[0]}/${parts[1]}`; }

      if (/\.(txt|md)$/i.test(file)) {
        if (!/^readme\.md$/i.test(file)) texts.set(key, path);
        continue;
      }
      if (!IMAGE_EXT.test(file)) continue;
      if (!groups.has(key)) {
        const titleBase = parts.length >= 3 ? parts[1] : base;
        groups.set(key, { key, category, titleBase, images: [], date: 0 });
      }
      const g = groups.get(key);
      g.images.push(path);
      g.date = Math.max(g.date, dates[path] || 0);
    }

    return [...groups.values()].map((g) => {
      const { name, price } = parseTitle(g.titleBase);
      g.images.sort(naturalCompare);
      return {
        id: slug(g.key),
        name,
        price,
        category: g.category ? stripOrder(g.category) : "",
        categoryKey: g.category,
        images: g.images.map((p) => ({ thumb: encodePath(p), full: encodePath(p) })),
        descFile: texts.get(g.key) ? encodePath(texts.get(g.key)) : null,
        date: g.date,
        base: g.titleBase,
      };
    });
  }

  /* catalog.json dagi "products" bo'limidan qo'shimcha ma'lumotlar (tavsif, eski narx, belgi) */
  function applyExtras(products) {
    const extras = state.settings.products || {};
    const map = new Map(Object.entries(extras).map(([k, v]) => [norm(k), v]));
    for (const p of products) {
      const e = map.get(norm(p.name)) || map.get(norm(p.base));
      if (e) Object.assign(p, e);
    }
    const newDays = state.settings.newDays ?? 14;
    const cutoff = Date.now() / 1000 - newDays * 86400;
    for (const p of products) {
      if (!p.badge && p.available !== false && p.oldPrice && p.price && p.oldPrice > p.price) p.badge = "Chegirma";
      if (!p.badge && p.available !== false && newDays > 0 && p.date && p.date > cutoff) p.badge = "Yangi";
    }
    return products;
  }

  /* ---------- Ma'lumotlarni yuklash ---------- */

  async function getJSON(url, opts) {
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`${url}: ${res.status}`);
    return res.json();
  }

  function repoInfo() {
    const gh = state.settings.github || {};
    let { owner, repo } = gh;
    const host = location.hostname;
    if (host.endsWith(".github.io")) {
      owner = owner || host.replace(/\.github\.io$/, "");
      const first = location.pathname.split("/").filter(Boolean)[0];
      repo = repo || (first && !first.includes(".") ? first : host);
    }
    return owner && repo ? { owner, repo, branch: gh.branch || "HEAD" } : null;
  }

  async function loadFromGitHub() {
    const info = repoInfo();
    if (!info) return [];
    const cacheKey = `katalog:${info.owner}/${info.repo}`;
    try {
      const cached = JSON.parse(sessionStorage.getItem(cacheKey) || "null");
      if (cached && Date.now() - cached.t < 5 * 60 * 1000) return cached.files;
    } catch { /* sessionStorage yopiq bo'lishi mumkin */ }

    const url = `https://api.github.com/repos/${info.owner}/${info.repo}/git/trees/${info.branch}?recursive=1`;
    const data = await getJSON(url, { headers: { Accept: "application/vnd.github+json" } });
    const files = data.tree.filter((n) => n.type === "blob" && n.path.startsWith("images/")).map((n) => n.path);
    try { sessionStorage.setItem(cacheKey, JSON.stringify({ t: Date.now(), files })); } catch { /* */ }
    return files;
  }

  async function loadProducts() {
    // 1) build skripti yaratgan tayyor ro'yxat (kichraytirilgan rasmlar bilan)
    try {
      const data = await getJSON("data.json", { cache: "no-cache" });
      if (Array.isArray(data.products)) return data.products;
    } catch { /* yo'q bo'lsa — GitHub'dan o'qiymiz */ }
    // 2) GitHub repodagi images/ papkasi
    return buildProducts(await loadFromGitHub());
  }

  /* ---------- Sozlamalar (do'kon nomi, kontaktlar) ---------- */

  function applySettings() {
    const shop = state.settings.shop || {};
    if (shop.name) document.title = shop.tagline ? `${shop.name} — ${shop.tagline}` : shop.name;
    document.querySelectorAll("[data-shop]").forEach((el) => {
      const v = shop[el.dataset.shop];
      if (v) el.textContent = v;
    });
    $("[data-hero='eyebrow']").textContent = shop.eyebrow || `${shop.name || "Katalog"} · ${new Date().getFullYear()}`;
    if (shop.logo) {
      const mark = $(".brand__mark");
      mark.classList.add("has-logo");
      mark.style.backgroundImage = `url("${shop.logo}")`;
    }
    $("#year").textContent = new Date().getFullYear();

    const links = contactLinks();
    $("#footer-links").innerHTML = links
      .map((l) => `<li><a class="btn btn--ghost" href="${esc(l.href)}" target="_blank" rel="noopener">${l.icon}<span>${esc(l.label)}</span></a></li>`)
      .join("");
    const main = links[0];
    if (main) {
      const btn = $("#contact-btn");
      btn.href = main.href;
      btn.target = "_blank";
      btn.rel = "noopener";
      btn.hidden = false;
    }
  }

  const ICONS = {
    telegram: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.5 4.5 2.8 11.7c-.9.4-.9 1.6.1 1.9l4.6 1.4 1.8 5.6c.3.8 1.3 1 1.9.4l2.6-2.5 4.9 3.6c.7.5 1.7.1 1.9-.7l3-15.5c.2-1-.8-1.8-1.6-1.4Z"/><path d="m7.6 15 10-7.2"/></svg>',
    whatsapp: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 20.5 5 16a8.5 8.5 0 1 1 3.2 3.1Z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-2-2l.8-1-1-2Z"/></svg>',
    phone: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    instagram: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/></svg>',
    photos: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="14" height="14" rx="2"/><path d="M7 3h12a2 2 0 0 1 2 2v12"/></svg>',
    box: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5Z"/><path d="m3 7.5 9 4.5 9-4.5M12 12v9"/></svg>',
    search: '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  };

  function contactLinks(message) {
    const shop = state.settings.shop || {};
    const text = message ? `?text=${encodeURIComponent(message)}` : "";
    const links = [];
    if (shop.telegram) links.push({ type: "telegram", label: "Telegram", href: `https://t.me/${shop.telegram.replace(/^@|^https?:\/\/t\.me\//, "")}${text}`, icon: ICONS.telegram });
    if (shop.whatsapp) links.push({ type: "whatsapp", label: "WhatsApp", href: `https://wa.me/${shop.whatsapp.replace(/\D/g, "")}${text}`, icon: ICONS.whatsapp });
    if (shop.phone) links.push({ type: "phone", label: shop.phone, href: `tel:${shop.phone.replace(/[^\d+]/g, "")}`, icon: ICONS.phone });
    if (shop.instagram && !message) links.push({ type: "instagram", label: "Instagram", href: `https://instagram.com/${shop.instagram.replace(/^@/, "")}`, icon: ICONS.instagram });
    return links;
  }

  /* ---------- Chizish ---------- */

  function priceHTML(p) {
    if (!p.price) return `<span class="price__ask">Narxini so'rang</span>`;
    const sale = p.oldPrice && p.oldPrice > p.price;
    return `<span class="price ${sale ? "price--sale" : ""}"><span class="price__now">${fmt(p.price)}</span>${sale ? `<span class="price__old">${fmt(p.oldPrice)}</span>` : ""}</span>`;
  }

  function badgeHTML(p) {
    if (p.available === false) return `<span class="badge badge--out">Sotuvda yo'q</span>`;
    if (!p.badge) return "";
    const cls = /chegirma|aksiya|sale|-%/i.test(p.badge) ? "badge--sale" : /yangi|new/i.test(p.badge) ? "badge--new" : "";
    return `<span class="badge ${cls}">${esc(p.badge)}</span>`;
  }

  function renderChips() {
    const counts = new Map();
    for (const p of state.products) if (p.category) counts.set(p.categoryKey || p.category, { label: p.category, n: (counts.get(p.categoryKey || p.category)?.n || 0) + 1 });
    const chips = $("#chips");
    if (!counts.size) { chips.innerHTML = ""; return; }
    const keys = [...counts.keys()].sort(naturalCompare);
    const chip = (key, label, n) => `<button class="chip" type="button" data-cat="${esc(key)}" aria-pressed="${state.category === key}">${esc(label)}<span class="chip__count">${n}</span></button>`;
    chips.innerHTML = chip("all", "Hammasi", state.products.length) + keys.map((k) => chip(k, counts.get(k).label, counts.get(k).n)).join("");
  }

  function visibleProducts() {
    const q = norm(state.query);
    let list = state.products.filter((p) => {
      if (state.category !== "all" && (p.categoryKey || p.category) !== state.category) return false;
      if (!q) return true;
      return norm(`${p.name} ${p.category} ${p.description || ""}`).includes(q);
    });
    const byPrice = (dir) => (a, b) => (a.price ? 0 : 1) - (b.price ? 0 : 1) || dir * ((a.price || 0) - (b.price || 0));
    const sorters = {
      new: (a, b) => (b.date || 0) - (a.date || 0),
      cheap: byPrice(1),
      expensive: byPrice(-1),
      name: (a, b) => naturalCompare(a.name, b.name),
    };
    if (sorters[state.sort]) list = [...list].sort(sorters[state.sort]);
    return list;
  }

  function renderGrid() {
    const list = visibleProducts();
    const grid = $("#grid");
    const box = $("#state");
    grid.innerHTML = list.map((p, i) => `
      <button class="card ${p.available === false ? "is-out" : ""}" type="button" data-id="${esc(p.id)}" style="--i:${Math.min(i, 12)}">
        <div class="card__media">
          ${badgeHTML(p)}
          <img src="${esc(p.images[0]?.thumb)}" alt="${esc(p.name)}" loading="${i < 8 ? "eager" : "lazy"}" decoding="async">
          ${p.images.length > 1 ? `<span class="card__photos">${ICONS.photos}${p.images.length}</span>` : ""}
        </div>
        <div class="card__body">
          ${p.category ? `<span class="card__cat">${esc(p.category)}</span>` : ""}
          <h3 class="card__name">${esc(p.name)}</h3>
          ${priceHTML(p)}
        </div>
      </button>`).join("");

    grid.querySelectorAll("img").forEach((img) => {
      const done = () => img.classList.add("is-loaded");
      if (img.complete) done(); else { img.addEventListener("load", done); img.addEventListener("error", done); }
    });

    if (!state.products.length) {
      box.innerHTML = `
        <div class="state__icon">${ICONS.box}</div>
        <h2>Hozircha mahsulotlar yo'q</h2>
        <p>Katalog GitHub'dagi <code>images</code> papkasidan o'zi to'ladi.</p>
        <ol>
          <li><span>GitHub'da <code>images</code> papkasini oching → <b>Add file → Upload files</b>.</span></li>
          <li><span>Har bir bo'lim uchun alohida papka: <code>images/Ko'ylaklar/</code></span></li>
          <li><span>Fayl nomi — nomi va narxi: <code>Qizil ko'ylak_150000.jpg</code></span></li>
        </ol>`;
      box.hidden = false;
    } else if (!list.length) {
      box.innerHTML = `
        <div class="state__icon">${ICONS.search}</div>
        <h2>Hech narsa topilmadi</h2>
        <p>Boshqa so'z bilan qidirib ko'ring yoki barcha mahsulotlarni ko'ring.</p>
        <button class="btn btn--primary" type="button" data-reset>Hammasini ko'rsatish</button>`;
      box.hidden = false;
    } else {
      box.hidden = true;
    }

    const cats = new Set(state.products.map((p) => p.category).filter(Boolean)).size;
    $("#hero-meta").textContent = state.products.length
      ? `${state.products.length} ta mahsulot${cats ? ` · ${cats} ta bo'lim` : ""}`
      : " ";
  }

  function renderSkeleton() {
    $("#grid").innerHTML = Array.from({ length: 8 }, () => `
      <div class="card card--skeleton" aria-hidden="true">
        <div class="card__media"></div>
        <div class="card__body"><div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="width:80%;margin-top:6px"></div></div>
      </div>`).join("");
  }

  /* ---------- Mahsulot oynasi ---------- */

  const modal = $("#modal");

  function showImage(i) {
    const p = state.current;
    const n = p.images.length;
    state.index = (i + n) % n;
    const img = $("#gallery-img");
    img.classList.add("is-fading");
    const src = p.images[state.index].full;
    const swap = () => { img.src = src; img.alt = p.name; img.classList.remove("is-fading"); };
    img.src ? setTimeout(swap, 120) : swap();
    $("#gallery-count").textContent = n > 1 ? `${state.index + 1} / ${n}` : "";
    document.querySelectorAll(".thumb").forEach((t, k) => t.setAttribute("aria-current", k === state.index));
  }

  function openProduct(id, push = true) {
    const p = state.products.find((x) => x.id === id);
    if (!p) return;
    state.current = p;
    $("#gallery-img").removeAttribute("src");
    $("#modal-cat").textContent = p.category || "";
    $("#modal-title").textContent = p.name;

    const sale = p.price && p.oldPrice > p.price;
    $("#modal-price").innerHTML = priceHTML(p)
      + (sale ? `<span class="discount">−${Math.round((1 - p.price / p.oldPrice) * 100)}%</span>` : "")
      + (p.available === false ? `<span class="stock stock--out">Sotuvda yo'q</span>` : "");

    const desc = $("#modal-desc");
    desc.textContent = p.description || "";
    if (!p.description && p.descFile) {
      fetch(p.descFile).then((r) => (r.ok ? r.text() : "")).then((t) => {
        p.description = t.trim();
        if (state.current === p) desc.textContent = p.description;
      }).catch(() => {});
    }

    const priceText = p.price ? ` (${fmt(p.price)})` : "";
    const msg = `Assalomu alaykum! "${p.name}"${priceText} mahsuloti bo'yicha murojaat qilyapman.\n${productUrl(p)}`;
    $("#modal-actions").innerHTML = contactLinks(msg).map((l, i) => `
      <a class="btn ${i === 0 ? "btn--primary" : "btn--ghost"} btn--block" href="${esc(l.href)}" target="_blank" rel="noopener">${l.icon}<span>${
        l.type === "phone" ? `Qo'ng'iroq: ${esc(l.label)}` : `${esc(l.label)} orqali buyurtma`
      }</span></a>`).join("");

    $("#gallery-thumbs").innerHTML = p.images.length > 1
      ? p.images.map((im, k) => `<button class="thumb" type="button" data-thumb="${k}" aria-label="Rasm ${k + 1}"><img src="${esc(im.thumb)}" alt="" loading="lazy"></button>`).join("")
      : "";
    document.querySelectorAll(".gallery__nav").forEach((b) => (b.hidden = p.images.length < 2));
    showImage(0);

    if (!modal.open) modal.showModal();
    modal.querySelector(".modal__panel").scrollTop = 0;
    if (push) history.pushState({ product: id }, "", `#${id}`);
  }

  function closeProduct(fromHistory = false) {
    if (!modal.open) return;
    modal.close();
    state.current = null;
    if (!fromHistory) {
      if (history.state?.product) history.back();
      else history.replaceState(null, "", location.pathname + location.search);
    }
  }

  const productUrl = (p) => `${location.origin}${location.pathname}#${p.id}`;

  let toastTimer;
  function toast(text) {
    const el = $("#toast");
    el.textContent = text;
    el.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-visible"), 2200);
  }

  /* ---------- Hodisalar ---------- */

  function bindEvents() {
    $("#grid").addEventListener("click", (e) => {
      const card = e.target.closest(".card[data-id]");
      if (card) openProduct(card.dataset.id);
    });

    $("#chips").addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      state.category = chip.dataset.cat;
      document.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c === chip));
      renderGrid();
    });

    $("#state").addEventListener("click", (e) => {
      if (!e.target.closest("[data-reset]")) return;
      state.query = "";
      state.category = "all";
      $("#search").value = "";
      renderChips();
      renderGrid();
    });

    let t;
    $("#search").addEventListener("input", (e) => {
      clearTimeout(t);
      t = setTimeout(() => { state.query = e.target.value; renderGrid(); }, 120);
    });

    $("#sort").addEventListener("change", (e) => { state.sort = e.target.value; renderGrid(); });

    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && !modal.open && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        $("#search").focus();
      }
      if (modal.open && state.current?.images.length > 1) {
        if (e.key === "ArrowLeft") showImage(state.index - 1);
        if (e.key === "ArrowRight") showImage(state.index + 1);
      }
    });

    modal.addEventListener("cancel", (e) => { e.preventDefault(); closeProduct(); });
    modal.addEventListener("click", (e) => {
      if (e.target === modal || e.target.closest("[data-close]")) closeProduct();
      const step = e.target.closest("[data-step]");
      if (step) showImage(state.index + Number(step.dataset.step));
      const thumb = e.target.closest("[data-thumb]");
      if (thumb) showImage(Number(thumb.dataset.thumb));
    });

    // Rasmni barmoq bilan surish
    const stage = $("#gallery-stage");
    let startX = null;
    stage.addEventListener("pointerdown", (e) => { startX = e.clientX; });
    stage.addEventListener("pointerup", (e) => {
      if (startX === null || !state.current || state.current.images.length < 2) return;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 40) showImage(state.index + (dx < 0 ? 1 : -1));
      startX = null;
    });

    $("#share-btn").addEventListener("click", async () => {
      const p = state.current;
      if (!p) return;
      const url = productUrl(p);
      try {
        if (navigator.share) await navigator.share({ title: p.name, url });
        else { await navigator.clipboard.writeText(url); toast("Havola nusxalandi"); }
      } catch { /* foydalanuvchi bekor qildi */ }
    });

    window.addEventListener("popstate", () => {
      const id = decodeURIComponent(location.hash.slice(1));
      if (id && state.products.some((p) => p.id === id)) openProduct(id, false);
      else closeProduct(true);
    });
  }

  /* ---------- Ishga tushirish ---------- */

  async function init() {
    renderSkeleton();
    bindEvents();
    try { state.settings = await getJSON("catalog.json", { cache: "no-cache" }); } catch { state.settings = {}; }
    applySettings();

    try {
      state.products = applyExtras(await loadProducts());
    } catch (err) {
      console.error(err);
      state.products = [];
    }
    renderChips();
    renderGrid();

    const id = decodeURIComponent(location.hash.slice(1));
    if (id && state.products.some((p) => p.id === id)) openProduct(id, false);
  }

  init();
})();
