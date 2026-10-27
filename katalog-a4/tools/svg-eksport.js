// Katalog sahifalarini SVG uchun tayyorlaydi: matn qatorlari va ikonkalar o'rni (JSON) + matnsiz fon rasmi (JPG).
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  // Ishlatish: node svg-eksport.js <chiqish-papka> [katalog-url]
  const out = process.argv[2];
  const url = process.argv[3] || 'http://localhost:8766/';
  const DPI = 200;
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 1200 }, deviceScaleFactor: DPI / 96 });
  p.on('pageerror', (e) => console.log('ERR', e.message));
  await p.goto(url);
  await p.emulateMedia({ media: 'print' });
  await p.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => (i.complete ? 1 : new Promise((r) => { i.onload = i.onerror = r; }))));
  });

  // ::before bilan chiqadigan qadam raqamlarini (01, 02 ...) haqiqiy matnga aylantirish
  await p.addStyleTag({ content: '.steps li::before{content:none!important}' });
  await p.evaluate(() => {
    document.querySelectorAll('.steps li').forEach((li, i) => {
      const s = document.createElement('span');
      s.textContent = '0' + (i + 1);
      s.style.cssText = 'position:absolute;right:5mm;top:5.5mm;font:600 9pt/1 var(--display);color:var(--gold-ink)';
      li.appendChild(s);
    });
  });

  const data = await p.evaluate(() => {
    const fam = (s) => s.split(',')[0].trim().replace(/["']/g, '');
    const ctx = document.createElement('canvas').getContext('2d');
    const cache = {};
    const ascent = (cs) => {
      const key = `${cs.fontWeight} ${cs.fontSize} ${fam(cs.fontFamily)}`;
      if (!(key in cache)) {
        ctx.font = `${cs.fontWeight} ${cs.fontSize} "${fam(cs.fontFamily)}"`;
        cache[key] = ctx.measureText('Hg').fontBoundingBoxAscent;
      }
      return cache[key];
    };
    const symbols = {};
    const pages = [...document.querySelectorAll('section.page')].map((pg) => {
      const P = pg.getBoundingClientRect();
      const runs = [];
      const tw = document.createTreeWalker(pg, NodeFilter.SHOW_TEXT);
      const r = document.createRange();
      let node;
      while ((node = tw.nextNode())) {
        if (!node.data.trim()) continue;
        const el = node.parentElement;
        if (el.closest('svg')) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden') continue;
        const lines = [];
        let cur = null;
        for (let i = 0; i < node.data.length; i++) {
          r.setStart(node, i);
          r.setEnd(node, i + 1);
          const rects = r.getClientRects();
          if (!rects.length) continue;
          const q = rects[0];
          const c = node.data[i];
          if (q.width === 0 && /\s/.test(c)) continue;
          if (!cur || Math.abs(q.top - cur.top) > 2 || q.left < cur.lastX - 1) {
            cur = { top: q.top, chars: [] };
            lines.push(cur);
          }
          cur.chars.push({ c, x: q.left - P.left, w: q.width });
          cur.lastX = q.left;
        }
        const a = ascent(cs);
        const out = [];
        for (const ln of lines) {
          while (ln.chars.length && /\s/.test(ln.chars[0].c)) ln.chars.shift();
          while (ln.chars.length && /\s/.test(ln.chars[ln.chars.length - 1].c)) ln.chars.pop();
          if (ln.chars.length) out.push({ baseline: ln.top - P.top + a, chars: ln.chars });
        }
        if (out.length) {
          runs.push({
            family: fam(cs.fontFamily), weight: +cs.fontWeight, size: parseFloat(cs.fontSize),
            color: cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing),
            upper: cs.textTransform === 'uppercase', lines: out,
          });
        }
      }
      const icons = [...pg.querySelectorAll('svg.ic')].map((svg) => {
        const q = svg.getBoundingClientRect();
        const id = svg.querySelector('use').getAttribute('href').slice(1);
        symbols[id] = document.getElementById(id).innerHTML;
        const cs = getComputedStyle(svg);
        // ikonka chizig'i padding va ramka ichida chiziladi (content box)
        const px = (k) => parseFloat(cs[k]) || 0;
        const l = px('paddingLeft') + px('borderLeftWidth'), t = px('paddingTop') + px('borderTopWidth');
        const w = q.width - l - px('paddingRight') - px('borderRightWidth');
        const h = q.height - t - px('paddingBottom') - px('borderBottomWidth');
        return { x: q.left - P.left + l, y: q.top - P.top + t, w, h, id, color: cs.color, sw: parseFloat(cs.strokeWidth) };
      });
      return { w: P.width, h: P.height, runs, icons };
    });
    return { pages, symbols };
  });
  fs.writeFileSync(`${out}/layout.json`, JSON.stringify(data));

  // Fon: matn va ikonkalar yashiriladi (joylashuv o'zgarmaydi), qolgani rasmga olinadi
  await p.addStyleTag({ content: '*{-webkit-text-fill-color:transparent!important;text-shadow:none!important} svg.ic use{visibility:hidden!important}' });
  const pages = await p.$$('section.page');
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: `${out}/bg-${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 86 });
  }
  console.log('sahifalar:', pages.length);
  await b.close();
})();
