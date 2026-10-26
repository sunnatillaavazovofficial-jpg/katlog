# Katalog

Rasmlardan avtomatik tuziladigan mahsulotlar katalogi (GitHub Pages uchun).

## Qanday ishlaydi

1. Rasmlarni `images/` papkasiga yuklang (qoidalar: [images/README.md](images/README.md)).
2. Do'kon nomi, Telegram, telefonni `catalog.json` faylida yozing.
3. Saytni yoqing: **Settings → Pages → Source: Deploy from a branch → Branch: shu branch, `/ (root)` → Save**.

Bir-ikki daqiqadan keyin sayt `https://sunnatillaavazovofficial-jpg.github.io/katlog/` manzilida ochiladi.

## catalog.json

| Maydon | Ma'nosi |
| --- | --- |
| `shop.name`, `shop.tagline` | Do'kon nomi va shiori |
| `shop.telegram` | Telegram username (`@`siz) |
| `shop.whatsapp`, `shop.phone` | Raqam, masalan `+998901234567` |
| `products` | Mahsulot nomi bo'yicha qo'shimcha: `description`, `oldPrice`, `badge`, `available` |
