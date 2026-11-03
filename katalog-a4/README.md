# SINO TIB — A4 katalog

41 sahifali, chop etishga tayyor A4 katalog. Tayyor PDF: [SINO-TIB-katalog.pdf](SINO-TIB-katalog.pdf).

| Sahifa | Mazmuni |
| --- | --- |
| 1–38 | Har bir mahsulot ikki sahifada: chapda (toq) asl rasm, ustida katta logotip, nomi va ikonkalar (3 ustun), pastda qisqa tavsif; o‘ngda (juft) xuddi shu fonda 4 tilda (UZ, RU, EN, KZ): tavsif, tarkibi, qo‘llash usuli, saqlash, qarshi ko‘rsatmalar |
| 39 | Buyurtma berish va tavsiyalar |
| 40 | Narxlar ro‘yxati |
| 41 | Orqa muqova: aloqa, QR kod |

`img/mahsulot/` — GitHub'ga yuklangan asl rasmlar, o‘zgartirilmagan.
`img/fon/` — o‘sha rasmlardan mahsulot olib tashlangan fon (ma’lumot sahifalari uchun).

Shriftlar statik TTF (`fonts/`): Montserrat, Inter (qozoq kirilini to‘liq qo‘llaydi), Great Vibes.

## CorelDRAW uchun SVG

[SINO-TIB-katalog-SVG.zip](SINO-TIB-katalog-SVG.zip) — har bir sahifa alohida SVG (A4):

- `1-matnli` — matn tahrirlanadi (har bir paragraf bitta matn obyekti); avval `shriftlar/` dagi 8 ta TTF ni o‘rnating. Matn soyasi yo‘q.
- `2-egri chiziqli` — matn egri chiziqlarga aylantirilgan, shriftsiz ham bir xil ko‘rinadi; soyalar bilan, PDF bilan bir xil.

Uzun mahsulot nomi va tavsifi bir qatorga sig‘guncha avtomatik kichraytiriladi (`katalog.js`, `fitText`).

Katalog o‘zgargach sahifalar va SVG’ni qayta yasash (`katalog-a4` papkasida):

```
python3 tools/sahifalar.py index.html               # mahsulot sahifalari (matnlar shu faylda)
python3 -m http.server 8766 &
node tools/svg-eksport.js /tmp/svg-xom              # matn o‘rni + fon rasmlari
python3 tools/svg-yasash.py /tmp/svg-xom fonts svg  # svg/matn va svg/egri
```

## Matn va rasmlarni o‘zgartirish

1. `index.html` faylini brauzerda oching (Chrome tavsiya etiladi).
2. **Tahrirlash** tugmasini bosing.
   - Istalgan matnni bosib, o‘zgartiring.
   - Rasmni bosib, kompyuterdan boshqa rasm tanlang.
3. O‘zgarishlar shu brauzerda avtomatik saqlanadi.
4. **PDF / Chop etish** → *Saqlash PDF sifatida* (Save as PDF). Qog‘oz: A4, chekka maydonlar (margins): *Yo‘q*, *Fon grafikasi* (Background graphics) yoqilgan bo‘lsin.
5. O‘zgarishlarni GitHub'da saqlash uchun **HTML saqlash** tugmasi bilan `index.html` ni yuklab oling va shu papkadagi faylning o‘rniga yuklang.

## To‘ldirilishi kerak bo‘lgan joylar

Ekranda sariq punktir chiziq bilan belgilangan (bosmaga chiqmaydi). Matnda `[kvadrat qavs]` ichida yozilgan — Corel’da ham shu yozuvni topib almashtirasiz.

| Nima | Qayerda |
| --- | --- |
| Mahsulot nomi va tavsifi (5 ta: kulrang idish, qora shisha, 3 ta to‘q sariq banka) | 29–38-sahifalar |
| Tavsifi umumiy yozilgan: Giyohli damlama (ko‘k), Sinomum, Tabon, Rosebud Tibet | 19–20, 23–28 |
| Tekshirish: “Buyrak damlamasi” va “Bo‘g‘im moyi” nomlari yorliqdan o‘qilgan | 17–18, 21–22 |
| **Tarkibi** — har bir mahsulotda, 4 tilda | barcha juft sahifalar |
| **Qo‘llash usuli** (dozasi) — Bo‘g‘im moyidan tashqari hammasida, 4 tilda | barcha juft sahifalar |
| Hajmi (noma’lum bo‘lganlarida) va **Narxi** | 40-sahifa (narxlar ro‘yxati) |
| Telefon, Telegram, Instagram | 39, 41 |

Saqlash va qarshi ko‘rsatmalar — biologik faol qo‘shimchalar uchun standart yozuv; o‘z yorlig‘ingizdagidan farq qilsa, almashtiring.

Matnlar `tools/sahifalar.py` boshidagi ro‘yxatlarda: shu yerda o‘zgartirib, buyruqni qayta ishga tushirsangiz, hamma sahifa birdaniga yangilanadi.
