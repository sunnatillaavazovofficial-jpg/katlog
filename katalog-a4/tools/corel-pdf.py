"""layout.json + fon rasmlaridan CorelDRAW uchun bitta ko'p sahifali PDF yasaydi.

Har bir sahifa: bitta fon rasmi (JPEG), ustida vektor ikonkalar va haqiqiy matn (shriftlar ichiga
joylangan). Chrome PDF'idagi kabi minglab mayda soya rasmlari yo'q — Corel'ga ochish oson.

Ishlatish: python3 tools/corel-pdf.py <svg-eksport papkasi> fonts SINO-TIB-Corel.pdf
"""
import io
import json
import os
import re
import sys

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import STATE_DEFAULTS
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

SRC, FONTS, OUT = sys.argv[1:4]
PT = 0.75  # 1 CSS px (96 dpi) = 0.75 pt

# (CSS oila, og'irlik) -> TTF fayl va PDF'dagi shrift nomi (Corel shu nom bo'yicha o'rnatilgan shriftni topadi)
FACES = {
    ("Montserrat", 500): ("Montserrat-500.ttf", "Montserrat-Medium"),
    ("Montserrat", 600): ("Montserrat-600.ttf", "Montserrat-SemiBold"),
    ("Montserrat", 700): ("Montserrat-700.ttf", "Montserrat-Bold"),
    ("Inter", 400): ("Inter-400.ttf", "Inter-Regular"),
    ("Inter", 500): ("Inter-500.ttf", "Inter-Medium"),
    ("Inter", 600): ("Inter-600.ttf", "Inter-SemiBold"),
    ("Inter", 700): ("Inter-700.ttf", "Inter-Bold"),
    ("Great Vibes", 400): ("GreatVibes-400.ttf", "GreatVibes-Regular"),
}


def font(run):
    key = (run["family"], run["weight"])
    if key not in FACES:  # eng yaqin og'irlik
        key = min((k for k in FACES if k[0] == run["family"]), key=lambda k: abs(k[1] - run["weight"]))
    file, name = FACES[key]
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, file)))
    return name


def color(css):
    m = re.match(r"rgba?\(([\d.]+),?\s*([\d.]+),?\s*([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\)", css)
    r, g, b = (float(v) / 255 for v in m.group(1, 2, 3))
    a = m.group(4)
    a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
    return Color(r, g, b, alpha=a)


def draw_line(c, run, ln, page_h):
    text = "".join(ch["c"] for ch in ln["chars"])
    if run["upper"]:
        text = text.upper()
    name, size = font(run), run["size"] * PT
    cs = run["ls"] * PT
    # Brauzer kerning ishlatadi, PDF yo'q — qator kengligi brauzerdagidek bo'lishi uchun
    # harflar orasi ozgina to'g'rilanadi (matn tahrirlanadigan bo'lib qoladi)
    first, last = ln["chars"][0], ln["chars"][-1]
    want = (last["x"] + last["w"] - first["x"]) * PT
    have = pdfmetrics.stringWidth(text, name, size) + cs * len(text)
    if len(text) > 1 and abs(want - have) / len(text) < 0.6:
        cs += (want - have) / len(text)
    t = c.beginText(first["x"] * PT, page_h - ln["baseline"] * PT)
    t.setFont(name, size)
    t.setCharSpace(cs)
    t.setFillColor(color(run["color"]))
    t.textOut(text)
    c.drawText(t)


icons = {}


def draw_icon(c, ic, symbols, page_h):
    key = (ic["id"], ic["color"], ic["sw"])
    if key not in icons:
        col = color(ic["color"])
        hexc = "#%02x%02x%02x" % tuple(round(v * 255) for v in (col.red, col.green, col.blue))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
               f'<g fill="none" stroke="{hexc}" stroke-opacity="{col.alpha}" stroke-width="{ic["sw"]}" '
               f'stroke-linecap="round" stroke-linejoin="round">{symbols[ic["id"]]}</g></svg>')
        icons[key] = svg2rlg(io.BytesIO(svg.encode()))
    d = icons[key]
    k = ic["w"] * PT / d.width  # svglib o'lchamni o'zi pt ga aylantiradi (24px = 18pt)
    c.saveState()
    c.translate(ic["x"] * PT, page_h - (ic["y"] + ic["h"]) * PT)
    c.scale(k, k)
    renderPDF.draw(d, c, 0, 0)
    c.restoreState()


data = json.load(open(os.path.join(SRC, "layout.json"), encoding="utf-8"))
first = data["pages"][0]
# Boshlang'ich shrift ham o'zimizniki — aks holda ReportLab ichiga joylanmagan Helvetica'ni qo'shadi
base = font({"family": "Inter", "weight": 400})
STATE_DEFAULTS["fontName"] = base  # ikonkalarni chizishda ham
c = canvas.Canvas(OUT, pagesize=(first["w"] * PT, first["h"] * PT), pageCompression=1,
                  initialFontName=base, initialFontSize=10)
c.setTitle("SINO TIB — mahsulotlar katalogi")
c.setAuthor("SINO TIB")
c.setCreator("katalog-a4/tools/corel-pdf.py")

for i, pg in enumerate(data["pages"], 1):
    w, h = pg["w"] * PT, pg["h"] * PT
    c.setPageSize((w, h))
    c.drawImage(os.path.join(SRC, f"bg-{i:02d}.jpg"), 0, 0, width=w, height=h)
    for ic in pg["icons"]:
        draw_icon(c, ic, data["symbols"], h)
    for run in pg["runs"]:
        for ln in run["lines"]:
            draw_line(c, run, ln, h)
    c.showPage()

c.save()
print("sahifalar:", len(data["pages"]))
