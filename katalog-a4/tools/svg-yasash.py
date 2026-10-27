"""layout.json + fon rasmlaridan CorelDRAW uchun SVG sahifalar yasaydi.

matn/  — matn tahrirlanadi (shriftlar o'rnatilgan bo'lishi kerak)
egri/  — matn egri chiziqlarga aylantirilgan (shriftsiz ham bir xil ko'rinadi)
"""
import base64
import json
import os
import re
import sys
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

SRC, FONTS, OUT = sys.argv[1:4]

# (CSS oila, og'irlik) -> TTF fayl va Windows/Corel ko'radigan nom (name ID 1) + og'irlik
FACES = {
    ("Montserrat", 500): ("Montserrat-500.ttf", "Montserrat Medium", "normal"),
    ("Montserrat", 600): ("Montserrat-600.ttf", "Montserrat SemiBold", "normal"),
    ("Montserrat", 700): ("Montserrat-700.ttf", "Montserrat", "bold"),
    ("Manrope", 400): ("Manrope-400.ttf", "Manrope", "normal"),
    ("Manrope", 500): ("Manrope-500.ttf", "Manrope Medium", "normal"),
    ("Manrope", 600): ("Manrope-600.ttf", "Manrope SemiBold", "normal"),
    ("Manrope", 700): ("Manrope-700.ttf", "Manrope", "bold"),
    ("Great Vibes", 400): ("GreatVibes-400.ttf", "Great Vibes", "normal"),
}
fonts = {}


def face(run):
    key = (run["family"], run["weight"])
    if key not in FACES:  # eng yaqin og'irlik
        key = min((k for k in FACES if k[0] == run["family"]), key=lambda k: abs(k[1] - run["weight"]))
    return key, FACES[key]


def color(css):
    m = re.match(r"rgba?\(([\d.]+),?\s*([\d.]+),?\s*([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\)", css)
    r, g, b = (round(float(v)) for v in m.group(1, 2, 3))
    a = m.group(4)
    a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
    return f"#{r:02x}{g:02x}{b:02x}", a


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def line_text(run, ln):
    t = "".join(c["c"] for c in ln["chars"])
    return t.upper() if run["upper"] else t


def text_svg(run, ln):
    (_, _), (_, name, weight) = face(run)
    fill, a = color(run["color"])
    attrs = [f'x="{num(ln["chars"][0]["x"])}"', f'y="{num(ln["baseline"])}"',
             f'font-family="{name}"', f'font-weight="{weight}"', f'font-size="{num(run["size"])}"', f'fill="{fill}"']
    if a < 1:
        attrs.append(f'fill-opacity="{num(a)}"')
    if run["ls"]:
        attrs.append(f'letter-spacing="{num(run["ls"])}"')
    return f'  <text {" ".join(attrs)} xml:space="preserve">{escape(line_text(run, ln))}</text>'


def curves_svg(run, ln):
    (_, _), (file, _, _) = face(run)
    if file not in fonts:
        f = TTFont(os.path.join(FONTS, file))
        fonts[file] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    gs, cmap, upm = fonts[file]
    s = run["size"] / upm
    pen = SVGPathPen(gs, ntos=lambda v: num(v))
    for c in ln["chars"]:
        ch = c["c"].upper() if run["upper"] else c["c"]
        g = cmap.get(ord(ch))
        if g and not ch.isspace():
            gs[g].draw(TransformPen(pen, (s, 0, 0, -s, c["x"], ln["baseline"])))
    d = pen.getCommands()
    if not d:
        return ""
    fill, a = color(run["color"])
    op = f' fill-opacity="{num(a)}"' if a < 1 else ""
    return f'  <path d="{d}" fill="{fill}"{op}/>'


def icon_svg(ic, symbols):
    stroke, a = color(ic["color"])
    k = ic["w"] / 24
    body = re.sub(r"\s+", " ", symbols[ic["id"]]).strip()
    op = f' stroke-opacity="{num(a)}"' if a < 1 else ""
    return (f'  <g transform="translate({num(ic["x"])} {num(ic["y"])}) scale({k:.4f})" fill="none" stroke="{stroke}"{op} '
            f'stroke-width="{num(ic["sw"])}" stroke-linecap="round" stroke-linejoin="round">{body}</g>')


data = json.load(open(os.path.join(SRC, "layout.json"), encoding="utf-8"))
for variant in ("matn", "egri"):
    os.makedirs(os.path.join(OUT, variant), exist_ok=True)

for i, pg in enumerate(data["pages"], 1):
    bg = base64.b64encode(open(os.path.join(SRC, f"bg-{i:02d}.jpg"), "rb").read()).decode()
    w, h = num(pg["w"]), num(pg["h"])
    head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" '
            f'width="210mm" height="297mm" viewBox="0 0 {w} {h}">\n'
            f'  <title>SINO TIB katalog — {i:02d}</title>\n'
            f'  <image x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="none" '
            f'xlink:href="data:image/jpeg;base64,{bg}"/>\n')
    icons = "\n".join(icon_svg(ic, data["symbols"]) for ic in pg["icons"])
    for variant, fn in (("matn", text_svg), ("egri", curves_svg)):
        body = "\n".join(filter(None, (fn(r, ln) for r in pg["runs"] for ln in r["lines"])))
        with open(os.path.join(OUT, variant, f"{i:02d}.svg"), "w", encoding="utf-8") as f:
            f.write(head + icons + "\n" + body + "\n</svg>\n")
print("sahifalar:", len(data["pages"]))
