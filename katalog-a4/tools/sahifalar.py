"""SINO TIB katalogi: mahsulot sahifalarini index.html ga yozadi.

Har bir mahsulot ikki sahifada: chapda asl rasm, nomi va ikonkalar; o'ngda 4 tilda (UZ, RU, EN, KZ)
tavsif, tarkibi, qo'llash usuli, saqlash va qarshi ko'rsatmalar.

Ishlatish (katalog-a4 papkasida):  python3 tools/sahifalar.py index.html
Matnlar shu faylning boshidagi ro'yxatlarda. [Kvadrat qavsdagi] joylar — to'ldirilishi kerak.
"""
import html
import re
import sys

PATH = sys.argv[1]

IMM = ("i-shield", "Immunitet", "Иммунитет", "Immunity")
NAT = ("i-leaf", "Tabiiy tarkib", "Натуральный состав", "Natural ingredients")
CAPS = ("i-capsule", "90 ta kapsula", "90 капсул", "90 capsules")
VIT = ("i-sun", "Tetiklik", "Бодрость", "Vitality")
ENERGY = ("i-bolt", "Energiya", "Энергия", "Energy")
STRENGTH = ("i-bolt", "Kuch-quvvat", "Сила и энергия", "Strength & energy")
HEALTH = ("i-heart", "Umumiy salomatlik", "Общее здоровье", "Overall health")
CARE = ("i-care", "Kundalik g‘amxo‘rlik", "Ежедневная забота", "Daily care")
LIFE = ("i-heart", "Sog‘lom hayot", "Здоровый образ жизни", "Healthy living")
QUALITY = ("i-star", "Yuqori sifat", "Высокое качество", "High quality")
GENERIC = [NAT, CARE, LIFE, QUALITY]

# ph=True — rasmda nomi/vazifasi yozilmagan: matnni egasi tekshirib to'ldirishi kerak
P = [
    dict(img="erkak-immun", eyebrow="SINO TIB · ±500 gr", title="Erkak Immun 999", spec="±500 gr",
         icons=[IMM, ("i-man", "Erkaklar salomatligi", "Мужское здоровье", "Men's health"), STRENGTH,
                ("i-dumbbell", "Chidamlilik", "Выносливость", "Endurance"), VIT, NAT],
         uz=("Erkaklar immuniteti va quvvati uchun",
             "Erkaklar organizmi uchun tabiiy giyohlar asosidagi aralashma. Immunitetni mustahkamlash, kuch-quvvat va tetiklikni qo‘llab-quvvatlashga yordam beradi."),
         ru=("Для мужского иммунитета и силы",
             "Натуральная смесь на основе трав для мужского организма. Помогает укрепить иммунитет, поддерживает силу и бодрость."),
         en=("Immunity and strength for men",
             "A natural herbal blend for men. Helps strengthen immunity and supports strength and vitality.")),
    dict(img="ayol-immun", eyebrow="SINO TIB · 500 gr", title="Ayol Immun", spec="500 gr",
         icons=[IMM, ("i-woman", "Ayollar salomatligi", "Женское здоровье", "Women's health"), VIT, ENERGY, HEALTH, NAT],
         uz=("Ayollar immuniteti va tetikligi uchun",
             "Ayollar organizmi uchun maxsus tabiiy aralashma. Immunitetni mustahkamlash, tetiklik va umumiy salomatlikni qo‘llab-quvvatlashga yordam beradi."),
         ru=("Для женского иммунитета и бодрости",
             "Специальная натуральная смесь для женского организма. Помогает укрепить иммунитет, поддерживает бодрость и общее здоровье."),
         en=("Immunity and vitality for women",
             "A special natural blend for women. Helps strengthen immunity and supports vitality and overall health.")),
    dict(img="bolajon-immun-555", eyebrow="SINO TIB · 100% tabiiy", title="Bolajon Immun 555", spec="100% tabiiy",
         icons=[IMM, ("i-child", "Bolalar salomatligi", "Здоровье детей", "Children's health"),
                ("i-sprout", "O‘sish va rivojlanish", "Рост и развитие", "Growth"), VIT, HEALTH, NAT],
         uz=("Bolalar immuniteti uchun",
             "Bolalar organizmi uchun tabiiy giyohlar asosidagi aralashma. Immunitetni mustahkamlash, tetiklik va sog‘lom o‘sishni qo‘llab-quvvatlashga yordam beradi."),
         ru=("Для детского иммунитета",
             "Натуральная смесь на основе трав для детского организма. Помогает укрепить иммунитет, поддерживает бодрость и здоровый рост."),
         en=("Immunity for children",
             "A natural herbal blend for children. Helps strengthen immunity and supports vitality and healthy growth.")),
    dict(img="universal-immun-707", eyebrow="SINO TIB · 100% tabiiy", title="Universal Immun 707", spec="100% tabiiy",
         icons=[IMM, ("i-people", "Butun oila uchun", "Для всей семьи", "For the whole family"), VIT, ENERGY, HEALTH, NAT],
         uz=("Butun oila immuniteti uchun",
             "Butun oila uchun universal tabiiy aralashma. Organizmning himoya kuchlarini mustahkamlash, tetiklik va energiyani qo‘llab-quvvatlashga yordam beradi."),
         ru=("Иммунитет для всей семьи",
             "Универсальная натуральная смесь для всей семьи. Помогает укрепить защитные силы организма, поддерживает бодрость и энергию."),
         en=("Immunity for the whole family",
             "A universal natural blend for the whole family. Helps strengthen the body's defences and supports vitality and energy.")),
    dict(img="super-aktiv-777", eyebrow="Super Aktiv 777 · ±75 gr", title="Tabiiy Kuvvalda", spec="±75 gr",
         icons=[IMM, ("i-man", "Erkaklar salomatligi", "Мужское здоровье", "Men's health"), STRENGTH,
                ("i-joint", "Bo‘g‘im va mushaklar", "Суставы и мышцы", "Joints & muscles"),
                ("i-hair", "Soch parvarishi", "Уход за волосами", "Hair care"), NAT],
         uz=("Erkaklar kuchini oshiruvchi vosita",
             "Tabiiy KUVVALDA — erkaklar quvvati, jismoniy kuch va jinsiy faollikni qo‘llab-quvvatlashga mo‘ljallangan tabiiy mahsulot. Charchoqni kamaytirish, organizmni tetiklashtirish va umumiy salomatlikni mustahkamlashga yordam beradi."),
         ru=("Средство для повышения мужской силы",
             "Натуральная «Кувалда» — натуральный продукт для поддержки мужской силы, физической выносливости и сексуальной активности. Помогает снизить усталость, взбодрить организм и укрепить общее здоровье."),
         en=("Natural strength support for men",
             "Natural KUVVALDA is a natural product designed to support male vitality, physical strength and sexual activity. It helps reduce fatigue, energise the body and strengthen overall health.")),
    dict(img="gemorroy-dorisi", eyebrow="SINO TIB · 100% tabiiy", title="Gemorroy dorisi", spec="90 ta kapsula",
         icons=[("i-pulse", "Qon tomirlari", "Сосуды", "Blood vessels"), ("i-drop", "Qon aylanishi", "Кровообращение", "Circulation"),
                ("i-gut", "Ichak faoliyati", "Работа кишечника", "Bowel function"), ("i-care", "Yengillik hissi", "Комфорт", "Comfort"), CAPS, NAT],
         uz=("Qon tomirlari va ichak salomatligi uchun",
             "Tabiiy giyohlar asosida tayyorlangan kapsulalar. Qon tomirlari va ichak faoliyatini qo‘llab-quvvatlashga, noqulaylik hissini kamaytirishga yordam beradi."),
         ru=("Для здоровья сосудов и кишечника",
             "Капсулы на основе натуральных трав. Помогают поддерживать здоровье сосудов и работу кишечника, уменьшают чувство дискомфорта."),
         en=("For healthy blood vessels and bowels",
             "Capsules made from natural herbs. Help support healthy blood vessels and bowel function and ease discomfort.")),
    dict(img="oshqozon-dorisi", eyebrow="SINO TIB · 100% tabiiy", title="Oshqozon dorisi", spec="90 ta kapsula",
         icons=[("i-gut", "Hazm tizimi", "Пищеварение", "Digestion"), ("i-care", "Oshqozon salomatligi", "Здоровье желудка", "Stomach health"),
                ("i-feather", "Yengillik", "Лёгкость", "Lightness"), ("i-pulse", "Modda almashinuvi", "Обмен веществ", "Metabolism"), CAPS, NAT],
         uz=("Oshqozon va hazm tizimi uchun",
             "Hazm tizimi uchun tabiiy giyohlar asosidagi kapsulalar. Hazm jarayonini yengillashtirish va oshqozon salomatligini qo‘llab-quvvatlashga yordam beradi."),
         ru=("Для желудка и пищеварения",
             "Капсулы на основе натуральных трав для пищеварительной системы. Облегчают пищеварение и помогают поддерживать здоровье желудка."),
         en=("For stomach and digestion",
             "Herbal capsules for the digestive system. Help ease digestion and support stomach health.")),
    dict(img="buqoq-dorisi", eyebrow="SINO TIB · 100% tabiiy", title="Buqoq dorisi", spec="90 ta kapsula",
         icons=[("i-butterfly", "Qalqonsimon bez", "Щитовидная железа", "Thyroid"), ("i-scale", "Gormonal muvozanat", "Гормональный баланс", "Hormonal balance"),
                ("i-pulse", "Modda almashinuvi", "Обмен веществ", "Metabolism"), ENERGY, CAPS, NAT],
         uz=("Qalqonsimon bez salomatligi uchun",
             "Qalqonsimon bez faoliyatini qo‘llab-quvvatlash uchun tabiiy giyohlar asosidagi kapsulalar. Organizmda modda almashinuvi muvozanatini saqlashga yordam beradi."),
         ru=("Для здоровья щитовидной железы",
             "Капсулы на основе натуральных трав для поддержки работы щитовидной железы. Помогают сохранять баланс обмена веществ в организме."),
         en=("For thyroid health",
             "Herbal capsules to support thyroid function. Help maintain a healthy metabolic balance in the body.")),
    dict(img="buyrak-damlamasi", eyebrow="SINO TIB · Giyohli damlama", title="Buyrak damlamasi", spec="100% tabiiy", ph_title=True,
         icons=[("i-kidney", "Buyraklar", "Почки", "Kidneys"), ("i-drop", "Siydik yo‘llari", "Мочевыводящие пути", "Urinary tract"),
                ("i-cup", "Giyohli choy", "Травяной чай", "Herbal tea"), CARE, NAT],
         uz=("Buyrak va siydik yo‘llari uchun",
             "Buyrak va siydik yo‘llari faoliyatini qo‘llab-quvvatlash uchun tabiiy giyohlardan tayyorlangan damlama (choy)."),
         ru=("Для почек и мочевыводящих путей",
             "Травяной сбор (чай) из натуральных растений для поддержки работы почек и мочевыводящих путей."),
         en=("For kidneys and urinary tract",
             "A natural herbal infusion (tea) to support kidney and urinary tract function.")),
    dict(img="damlama", eyebrow="SINO TIB · Giyohli damlama", title="Giyohli damlama", spec="100% tabiiy", ph=True,
         icons=[("i-cup", "Giyohli choy", "Травяной чай", "Herbal tea"), NAT, CARE, LIFE],
         uz=("Tabiiy giyohli damlama",
             "Tabiiy giyohlardan tayyorlangan damlama (choy) — salomatlikka kundalik g‘amxo‘rlik uchun."),
         ru=("Натуральный травяной сбор",
             "Травяной сбор (чай) из натуральных растений — для ежедневной заботы о здоровье."),
         en=("Natural herbal infusion",
             "A natural herbal infusion (tea) for everyday care of your health.")),
    dict(img="bogim-moyi", eyebrow="SINO TIB · Tashqi qo‘llash uchun", title="Bo‘g‘im moyi", spec="100% tabiiy", ph_title=True,
         icons=[("i-joint", "Bo‘g‘imlar", "Суставы", "Joints"), ("i-dumbbell", "Mushaklar", "Мышцы", "Muscles"),
                ("i-hand", "Surtib qo‘llanadi", "Наружное применение", "External use"),
                ("i-clock", "Kuniga 2 mahal", "2 раза в день", "Twice a day"), NAT],
         uz=("Bo‘g‘im va mushaklar uchun",
             "Sovuq ta’sirida yuzaga kelgan katta va kichik bo‘g‘imlardagi noqulayliklarda qo‘llaniladi. Kuniga 2 mahal — ertalab va kechqurun — og‘rigan joyga 3–4 daqiqa davomida surtib, uqalanadi."),
         ru=("Для суставов и мышц",
             "Применяется при дискомфорте в крупных и мелких суставах, вызванном переохлаждением. 2 раза в день — утром и вечером — втирать в болезненное место в течение 3–4 минут."),
         en=("For joints and muscles",
             "Used for discomfort in large and small joints caused by cold. Twice a day, morning and evening, rub into the affected area for 3–4 minutes.")),
    dict(img="sinomum", eyebrow="SINO TIB · 100% tabiiy", title="Sinomum", spec="100% tabiiy", ph=True, icons=GENERIC,
         uz=("Tabiiy giyohlar asosida",
             "SINO TIB tabiiy giyohlar asosidagi mahsuloti — salomatligingizga kundalik g‘amxo‘rlik uchun."),
         ru=("На основе натуральных трав",
             "Продукт SINO TIB на основе натуральных трав — для ежедневной заботы о вашем здоровье."),
         en=("Made from natural herbs",
             "A SINO TIB product made from natural herbs — for everyday care of your health.")),
    dict(img="tabon", eyebrow="SINO TIB · ±20 gr", title="Tabon", spec="±20 gr", ph=True,
         icons=[("i-woman", "Ayollar salomatligi", "Женское здоровье", "Women's health"), NAT, CARE, QUALITY],
         uz=("Ayollar salomatligi uchun",
             "Ayollar uchun tabiiy mahsulot — salomatlikka kundalik g‘amxo‘rlik uchun."),
         ru=("Для женского здоровья",
             "Натуральный продукт для женщин — для ежедневной заботы о здоровье."),
         en=("For women's health",
             "A natural product for women — for everyday care of your health.")),
    dict(img="rosebud-tibet", eyebrow="Shenju Health Products", title="Rosebud Tibet", spec="100% tabiiy", ph=True, icons=GENERIC,
         uz=("Tabiiy mahsulot", "Tabiiy mahsulot — salomatligingizga kundalik g‘amxo‘rlik uchun."),
         ru=("Натуральный продукт", "Натуральный продукт — для ежедневной заботы о вашем здоровье."),
         en=("Natural product", "A natural product for everyday care of your health.")),
]
for n in (1, 4, 9, 16, 19):
    P.append(dict(img=f"mahsulot-{n}", eyebrow="SINO TIB", title="Mahsulot nomi", spec="Hajmi", ph=True, ph_title=True, icons=GENERIC,
                  uz=("Qisqa tavsif", "Mahsulot haqida ma’lumot: tarkibi, foydasi va qo‘llash usuli."),
                  ru=("Краткое описание", "Информация о продукте: состав, польза и способ применения."),
                  en=("Short description", "Product information: ingredients, benefits and directions for use.")))

VOL = {"erkak-immun": "±500 gr", "ayol-immun": "500 gr", "super-aktiv-777": "±75 gr", "gemorroy-dorisi": "90 ta kapsula",
       "oshqozon-dorisi": "90 ta kapsula", "buqoq-dorisi": "90 ta kapsula", "tabon": "±20 gr"}

# Qozoqcha (kirill) — ikonka yozuvlari (o'zbekcha yozuv bo'yicha) va har bir mahsulot matni
KZ_ICON = {
    "Immunitet": "Иммунитет", "Erkaklar salomatligi": "Ер адамдар денсаулығы", "Kuch-quvvat": "Күш-қуат",
    "Chidamlilik": "Төзімділік", "Tetiklik": "Сергектік", "Tabiiy tarkib": "Табиғи құрам",
    "Ayollar salomatligi": "Әйелдер денсаулығы", "Energiya": "Энергия", "Umumiy salomatlik": "Жалпы денсаулық",
    "Bolalar salomatligi": "Балалар денсаулығы", "O‘sish va rivojlanish": "Өсу мен даму",
    "Butun oila uchun": "Бүкіл отбасыға", "Bo‘g‘im va mushaklar": "Буындар мен бұлшықеттер",
    "Soch parvarishi": "Шаш күтімі", "Qon tomirlari": "Қан тамырлары", "Qon aylanishi": "Қан айналымы",
    "Ichak faoliyati": "Ішек жұмысы", "Yengillik hissi": "Жайлылық", "90 ta kapsula": "90 капсула",
    "Hazm tizimi": "Ас қорыту", "Oshqozon salomatligi": "Асқазан денсаулығы", "Yengillik": "Жеңілдік",
    "Modda almashinuvi": "Зат алмасу", "Qalqonsimon bez": "Қалқанша без",
    "Gormonal muvozanat": "Гормондық тепе-теңдік", "Buyraklar": "Бүйректер",
    "Siydik yo‘llari": "Зәр шығару жолдары", "Giyohli choy": "Шөп шайы",
    "Kundalik g‘amxo‘rlik": "Күнделікті күтім", "Bo‘g‘imlar": "Буындар", "Mushaklar": "Бұлшықеттер",
    "Surtib qo‘llanadi": "Сыртқа қолдану", "Kuniga 2 mahal": "Күніне 2 рет",
    "Sog‘lom hayot": "Салауатты өмір", "Yuqori sifat": "Жоғары сапа",
}
KZ = {
    "erkak-immun": ("Ер адамдардың иммунитеті мен күш-қуаты үшін",
                    "Ер адам ағзасына арналған табиғи шөптер негізіндегі қоспа. Иммунитетті нығайтуға, күш-қуат пен сергектікті қолдауға көмектеседі."),
    "ayol-immun": ("Әйелдердің иммунитеті мен сергектігі үшін",
                   "Әйел ағзасына арналған арнайы табиғи қоспа. Иммунитетті нығайтуға, сергектік пен жалпы денсаулықты қолдауға көмектеседі."),
    "bolajon-immun-555": ("Балалар иммунитеті үшін",
                          "Бала ағзасына арналған табиғи шөптер негізіндегі қоспа. Иммунитетті нығайтуға, сергектік пен дені сау өсуді қолдауға көмектеседі."),
    "universal-immun-707": ("Бүкіл отбасының иммунитеті үшін",
                            "Бүкіл отбасыға арналған әмбебап табиғи қоспа. Ағзаның қорғаныс күштерін нығайтуға, сергектік пен энергияны қолдауға көмектеседі."),
    "super-aktiv-777": ("Ер адамдардың күшін арттыратын құрал",
                        "Табиғи «Кувалда» — ер адамның күш-қуатын, физикалық төзімділігін және жыныстық белсенділігін қолдауға арналған табиғи өнім. Шаршауды азайтуға, ағзаны сергітуге және жалпы денсаулықты нығайтуға көмектеседі."),
    "gemorroy-dorisi": ("Қан тамырлары мен ішек денсаулығы үшін",
                        "Табиғи шөптер негізіндегі капсулалар. Қан тамырлары мен ішек жұмысын қолдауға, жайсыздық сезімін азайтуға көмектеседі."),
    "oshqozon-dorisi": ("Асқазан мен ас қорыту үшін",
                        "Ас қорыту жүйесіне арналған табиғи шөптер негізіндегі капсулалар. Ас қорытуды жеңілдетуге және асқазан денсаулығын қолдауға көмектеседі."),
    "buqoq-dorisi": ("Қалқанша без денсаулығы үшін",
                     "Қалқанша бездің жұмысын қолдауға арналған табиғи шөптер негізіндегі капсулалар. Ағзадағы зат алмасу тепе-теңдігін сақтауға көмектеседі."),
    "buyrak-damlamasi": ("Бүйрек пен зәр шығару жолдары үшін",
                         "Бүйрек пен зәр шығару жолдарының жұмысын қолдауға арналған табиғи шөптерден жасалған тұндырма (шай)."),
    "damlama": ("Табиғи шөп тұндырмасы",
                "Табиғи шөптерден жасалған тұндырма (шай) — денсаулыққа күнделікті күтім үшін."),
    "bogim-moyi": ("Буындар мен бұлшықеттер үшін",
                   "Суықтың әсерінен пайда болған ірі және ұсақ буындардағы жайсыздық кезінде қолданылады. Күніне 2 рет — таңертең және кешке — ауыратын жерге 3–4 минут бойы сүртіп, уқалайды."),
    "sinomum": ("Табиғи шөптер негізінде",
                "Табиғи шөптер негізіндегі SINO TIB өнімі — денсаулығыңызға күнделікті күтім үшін."),
    "tabon": ("Әйелдер денсаулығы үшін",
              "Әйелдерге арналған табиғи өнім — денсаулыққа күнделікті күтім үшін."),
    "rosebud-tibet": ("Табиғи өнім",
                      "Табиғи өнім — денсаулығыңызға күнделікті күтім үшін."),
}
for p in P:
    p["kz"] = KZ.get(p["img"], ("Қысқаша сипаттама", "Өнім туралы ақпарат: құрамы, пайдасы және қолдану тәсілі."))
    p["icons"] = [(i, uz, ru, en, KZ_ICON[uz]) for i, uz, ru, en in p["icons"]]

# Bo'g'im moyi: yorliqdagi tavsif va qo'llash usuli alohida bo'limlarga ajratiladi
for p in P:
    if p["img"] == "bogim-moyi":
        p["uz"] = (p["uz"][0], "Sovuq ta’sirida yuzaga kelgan katta va kichik bo‘g‘imlardagi noqulayliklarda qo‘llaniladi.")
        p["ru"] = (p["ru"][0], "Применяется при дискомфорте в крупных и мелких суставах, вызванном переохлаждением.")
        p["en"] = (p["en"][0], "Used for discomfort in large and small joints caused by cold.")
        p["kz"] = (p["kz"][0], "Суықтың әсерінен пайда болған ірі және ұсақ буындардағы жайсыздық кезінде қолданылады.")

LANGS = (("uz", "UZ"), ("ru", "RU"), ("en", "EN"), ("kz", "KZ"))
LANG_I = {code: k for k, (code, _) in enumerate(LANGS)}

# O'ng sahifadagi bo'limlar: sarlavha (UZ, RU, EN, KZ)
SEC_TITLES = {
    "ing": ("Tarkibi", "Состав", "Ingredients", "Құрамы"),
    "use": ("Qo‘llash usuli", "Способ применения", "Directions for use", "Қолдану тәсілі"),
    "store": ("Saqlash", "Хранение", "Storage", "Сақтау"),
    "warn": ("Qarshi ko‘rsatmalar", "Противопоказания", "Contraindications", "Қарсы көрсетілімдер"),
}
# Bo'lim matnlari. True — to'ldirilishi kerak (ekranda sariq belgi)
ING_CAPS = (("100% tabiiy giyohlar. [To‘liq tarkibini yozing]", "100% натуральные травы. [Укажите полный состав]",
             "100% natural herbs. [Add full ingredients]", "100% табиғи шөптер. [Толық құрамын жазыңыз]"), True)
ING_HERB = (("Tabiiy giyohlar. [To‘liq tarkibini yozing]", "Натуральные травы. [Укажите полный состав]",
             "Natural herbs. [Add full ingredients]", "Табиғи шөптер. [Толық құрамын жазыңыз]"), True)
ING_NONE = (("[Tarkibini yozing]", "[Укажите состав]", "[Add ingredients]", "[Құрамын жазыңыз]"), True)
USE_DEFAULT = (("Mutaxassis tavsiyasiga ko‘ra. [Miqdori va qabul qilish tartibini yozing]",
                "По рекомендации специалиста. [Укажите дозировку и схему приёма]",
                "As recommended by a specialist. [Add dosage and schedule]",
                "Маман ұсынысы бойынша. [Мөлшері мен қабылдау тәртібін жазыңыз]"), True)
USE_BOGIM = (("Kuniga 2 mahal — ertalab va kechqurun — og‘rigan joyga 3–4 daqiqa davomida surtib, uqalanadi.",
              "2 раза в день — утром и вечером — втирать в болезненное место в течение 3–4 минут.",
              "Twice a day, morning and evening, rub into the affected area for 3–4 minutes.",
              "Күніне 2 рет — таңертең және кешке — ауыратын жерге 3–4 минут бойы сүртіп, уқалайды."), False)
STORE = (("Quruq, salqin, quyosh nuri tushmaydigan va bolalar ololmaydigan joyda saqlang.",
          "Хранить в сухом, прохладном, защищённом от солнечного света и недоступном для детей месте.",
          "Store in a cool, dry place away from direct sunlight and out of the reach of children.",
          "Құрғақ, салқын, күн сәулесі түспейтін және балалардың қолы жетпейтін жерде сақтаңыз."), False)
WARN = (("Tarkibiy qismlarga individual sezuvchanlik, homiladorlik va emizish davri. Qo‘llashdan oldin mutaxassis bilan maslahatlashing.",
         "Индивидуальная непереносимость компонентов, беременность и период грудного вскармливания. Перед применением проконсультируйтесь со специалистом.",
         "Individual intolerance to the ingredients, pregnancy and breastfeeding. Consult a specialist before use.",
         "Құрамдас бөліктерге жеке төзбеушілік, жүктілік және емізу кезеңі. Қолданар алдында маманмен кеңесіңіз."), False)

CAPSULES = {"gemorroy-dorisi", "oshqozon-dorisi", "buqoq-dorisi"}
NOT_SINO = {"rosebud-tibet"}


def sections(p):
    if p["img"] in CAPSULES:
        ing = ING_CAPS
    elif p["img"] in NOT_SINO or p["img"].startswith("mahsulot-"):
        ing = ING_NONE
    else:
        ing = ING_HERB
    use = USE_BOGIM if p["img"] == "bogim-moyi" else USE_DEFAULT
    return (("ing", ing), ("use", use), ("store", STORE), ("warn", WARN))


SPECS = (("Hajmi", "Объём", "Volume", "Көлемі"), ("Narxi", "Цена", "Price", "Бағасы"))
FIRST_PAGE = 1
e = html.escape


def spread(p, n):
    """n — chap sahifa: rasm, nomi va ikonkalar; n+1 — o'ng sahifa: 4 tilda to'liq ma'lumot."""
    ph = ' class="ph"' if p.get("ph") else ""
    ph_title = " ph" if p.get("ph_title") or p.get("ph") else ""
    icons = "\n".join(
        f'        <li><span class="medal"><svg class="ic"><use href="#{i}"/></svg></span><b>{e(uz)}</b></li>'
        for i, uz, ru, en, kz in p["icons"])

    def block(code, tag):
        k = LANG_I[code]
        secs = "".join(
            f'<div><dt>{e(SEC_TITLES[key][k])}</dt><dd{" class=\"ph\"" if todo else ""}>{e(texts[k])}</dd></div>'
            for key, (texts, todo) in sections(p))
        return (f'        <div class="inf__lang" lang="{code if code != "kz" else "kk"}"><span class="lang__tag">{tag}</span>'
                f'<h4{ph}>{e(p[code][0])}</h4><p class="inf__desc{" ph" if p.get("ph") else ""}">{e(p[code][1])}</p>'
                f'<dl class="inf__secs">{secs}</dl></div>')

    langs = "\n".join(block(code, tag) for code, tag in LANGS)
    vol = VOL.get(p["img"])
    specs = "\n".join(
        f'        <div><dt>{e(l[0])}<small>{e(" · ".join(l[1:]))}</small></dt>'
        f'<dd{"" if (k == 0 and vol) else " class=\"ph\""}>{e(v)}</dd></div>'
        for k, (l, v) in enumerate(zip(SPECS, (vol or "—", "— so‘m"))))
    return f"""  <!-- ============ {n}–{n + 1}. {p['title'].upper()} ============ -->
  <section class="page pp">
    <img class="pp__bg" data-img src="img/mahsulot/{p['img']}.jpg" alt="{e(p['title'])}">
    <div class="pp__shade" aria-hidden="true"></div>
    <header class="pp__head">
      <div class="pp__top"><img src="img/logo.png" alt=""><span>SINO TIB</span></div>
      <h2 class="pp__title{ph_title}">{e(p['title'])}</h2>
      <p class="pp__sub{' ph' if p.get('ph') else ''}">{e(p['uz'][0])}</p>
      <ul class="pp__icons">
{icons}
      </ul>
    </header>
    <div class="pp__foot">
      <p class="pp__desc{' ph' if p.get('ph') else ''}">{e(p['uz'][1])}</p>
      <div class="pp__end"><img src="img/logo.png" alt=""><span>SINO TIB</span><i></i></div>
    </div>
  </section>

  <section class="page inf">
    <img class="inf__bg" data-img src="img/fon/{p['img']}.jpg" alt="">
    <div class="inf__shade" aria-hidden="true"></div>
    <div class="inf__body">
      <div class="pp__brand"><img src="img/logo.png" alt=""><span>SINO TIB</span></div>
      <h2 class="inf__title{ph_title}">{e(p['title'])}</h2>
      <div class="inf__langs">
{langs}
      </div>
      <dl class="inf__specs">
{specs}
      </dl>
      <div class="pp__bar"><img src="img/logo.png" alt=""><span>SINO TIB</span><i></i><span class="pp__n">{n + 1:02d}</span></div>
    </div>
  </section>
"""


pages = "\n".join(spread(p, FIRST_PAGE + 2 * k) for k, p in enumerate(P))
order_n = FIRST_PAGE + 2 * len(P)
price_n, back_n = order_n + 1, order_n + 2

rows = "\n".join(
    f'          <tr><td class="price__no">{k + 1}</td><td><b>{e(p["title"])}</b><small>{e(p["uz"][0])}</small></td>'
    f'<td>{e(VOL.get(p["img"], "—"))}</td><td class="price__sum">—</td></tr>'
    for k, p in enumerate(P))
price_page = f"""  <!-- ============ {price_n}. NARXLAR ============ -->
  <section class="page">
    <header class="run"><img class="run__logo" src="img/logo.png" alt=""><span class="run__brand">SINO TIB</span><span class="run__label e">Narxlar</span></header>

    <p class="eyebrow">Narxlar ro‘yxati</p>
    <h2 class="display display--wide">Mahsulotlar va narxlar</h2>

    <table class="price">
      <thead>
        <tr><th>№</th><th>Mahsulot</th><th>Hajmi</th><th>Narxi, so‘m</th></tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>

    <footer class="folio"><span class="e">abdushukur.uz</span><span class="folio__n">{price_n:02d}</span></footer>
  </section>

"""

src = open(PATH, encoding="utf-8").read()

start = src.index('<main class="book" id="book">\n') + len('<main class="book" id="book">\n')
end = re.search(r"  <!-- ============ \d+\. BUYURTMA", src).start()
src = src[:start] + "\n" + pages + "\n" + src[end:]
src, k3 = re.subn(r'(<!-- ============ )\d+(\. BUYURTMA.*?folio__n">)\d+(</span>)',
                  lambda m: f"{m.group(1)}{order_n}{m.group(2)}{order_n:02d}{m.group(3)}", src, flags=re.S)
src = re.sub(r'  <!-- ============ \d+\. NARXLAR ============ -->.*?(?=  <!-- ============ \d+\. ORQA MUQOVA)', "", src, flags=re.S)
src, k4 = re.subn(r'  <!-- ============ \d+\. ORQA MUQOVA', price_page + f'  <!-- ============ {back_n}. ORQA MUQOVA', src)
assert (k3, k4) == (1, 1), (k3, k4)
open(PATH, "w", encoding="utf-8").write(src)
print("mahsulotlar:", len(P), "| jami sahifa:", back_n)
