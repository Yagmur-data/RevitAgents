# -*- coding: utf-8 -*-
"""One-off batch writer for the 2026-11-04 Project1 (Aerovokzal Severnoye) RF-family review.
Rows are defined inline; writes ForRevitReview/reports/<stem>/<stem>.md for each of the 7 sheets.
Usage: python -I write_md_rf_batch.py <ForRevitReview dir>"""
import sys, os

root = sys.argv[1]
PEN = {"CRITICAL": 20, "WARNING": 8, "ADVISORY": 2}
DATE = "2026-11-04"
BASIS = "RF — ГОСТ Р 21.101-2020 (per ТЗ) + ГОСТ 2.301/2.303/2.304"
sheets = [
    ("AR-1_plan_1_etazha", "АР-1 — План 1 этажа"),
    ("AR-2_plan_2_etazha", "АР-2 — План 2 этажа"),
    ("AR-3_severnyj_fasad", "АР-3 — Северный фасад"),
    ("AR-4_yuzhnyj_fasad", "АР-4 — Южный фасад"),
    ("AR-5_vostochnyj_fasad", "АР-5 — Восточный фасад"),
    ("AR-6_zapadnyj_fasad", "АР-6 — Западный фасад"),
    ("AR-7_razrez", "АР-7 — Разрез"),
]
STAMP = "Основная надпись, sağ şerit (x 1023–1163 mm, tam yükseklik)"
common = [
    (STAMP, "Başlık bloğu / RF-S1", "Autodesk jenerik A0 bloğu: Autodesk logosu, 5x «Consultant/Address/Phone/Fax/e-mail», revizyon tablosu, dikey şerit. ГОСТ Р 21.101 Форма 3 yapısı yok (graf 1–13 ve 25–27: шифр, стадия, лист/листов, организация, разработал/проверил/н.контр/ГИП sütunları, format, заказчик). Form mm ölçüleri: KONTROL EDİLEMEDİ.", "[F] Form 3 title-block .rfa gerekli (köprü .rfa üretemez/düzenleyemez; makinede ГОСТ ailesi yok). Metinle taklit edilmez.", "CRITICAL"),
    (STAMP, "Başlık bloğu / RF-S2, R1", "Stamp alanları: «Project number» = «—» (шифр boş), стадия (П/Р) yok, toplam лист sayısı yok, организация yok, Нормоконтроль ve ГИП alanı yok, заказчик stamp grafinde yok.", "[F] eksik graflar için aile; [A] шифр (ör. XXXX-АР), стадия, организация değerleri Al'dan.", "CRITICAL"),
    (STAMP, "Başlık bloğu / RF-S2", "«Drawn by» = Author, «Checked by» = Checker (Autodesk yer tutucuları); gerçek adlar bilinmiyor.", "[A] gerçek разработал / проверил adları Al'dan; sonra `revit_set_parameter`.", "WARNING"),
    ("Çerçeve, sayfa kenarları (sayfa 1188x840 mm)", "Başlık bloğu / RF-S4", "Ölçülen çerçeve: x 25–1163, y 25–815 mm → 4 kenarda da 25 mm; çizgi kalınlığı 0,25 mm (ince). ГОСТ 2.301: sol 20 mm, diğer üç kenar 5 mm, dış çerçeve KALIN sürekli çizgi.", "[F] aile içinde düzeltilir.", "WARNING"),
    (STAMP, "Başlık bloğu / RF-S6", "İngilizce kalıntılar: «Consultant/Address/Phone/Fax/e-mail», «No./Description/Date», «Project number», «Date», «Drawn by», «Checked by», «Scale», «www.autodesk.com/revit», Autodesk logosu.", "[F] Rusça etiketli Form 3 ailesi.", "WARNING"),
    ("Основная надпись, proje adı / заказчик / pafta adı alanı", "Başlık bloğu / R7, RF-S2", "«Газпромнефть-Снабжение» (18,2 mm yazı) kutudan taşıp «Аэровокзал / Северное» ile üst üste biniyor, sağda çerçeveyi ve sayfa kenarını (≈1202 mm > 1188) aşıyor. Cephe sayfalarında «Северный/Восточный/Западный фасад» yazısı da kutu kenarına değiyor.", "[D] parametre metnini kısalt/satır böl (kısmi çözüm); [F] gerçek çözüm aile yazı tipi/boyutu.", "WARNING"),
    ("Tüm sayfa / çizim alanı", "Düzen / RF-S5", "A0 (1188x840 mm ölçüldü) sayfada çizim alanın yaklaşık %10'unu kaplıyor; 1:100'de plan ≈ 250 mm geniş, A3/A2 yeter. Format seçimi gerekçesiz.", "[A] format kararı (A2/A3, aile ile birlikte).", "ADVISORY"),
    ("Tüm metinler", "Yazı / RF-L2, R10", "Yazı tipleri Trebuchet MS / Arial / Georgia (kuzey oku «N»), dik; ГОСТ 2.304 tip A/B (75° eğik) değil. Nominal yükseklik serisi PDF'ten KONTROL EDİLEMEDİ (em 4,2 mm).", "[K] text/tag tipleri köprüden düzenlenemez; Al'a not.", "ADVISORY"),
]
DIMS1 = "Plan alanı"
rows = {
    "AR-1_plan_1_etazha": [
        ("Tüm komplekt (АР-1 ilk sayfa)", "Set yapısı / RF-N1", "«Общие данные» sayfası yok: ведомость рабочих чертежей (Форма 1), ссылочные документы (Форма 2), общие указания, условные обозначения yok; kapı/pencere ведомость'i de yok (pencere/kapı etiketleri 27/40/41 hiçbir cetvelle eşleştirilemiyor). Komplekt düzeyi bulgu, yalnız АР-1'e puanlandı.", "[D] `revit_create_sheet` + sheet-list/kapı-pencere cetveli; [A] общие указания ve legend metni.", "WARNING"),
        ("Görünüm başlığı «План 1 этажа на отм. 0.000»", "Kotlar / RF-D2", "Kot yazımında ondalık NOKTA; RF: virgül (0,000), birimsiz, sıfır işaretsiz.", "[D] görünüm adını «…на отм. 0,000» yap.", "WARNING"),
        (DIMS1 + ", eksen 1–6 / А–Д çevresi", "Boyutlandırma / RF-D3", "Planda hiç ölçü zinciri yok: eksenler arası, toplam, duvar kalınlığı, açıklık ölçüsü yok.", "[D] `revit_create_dimension` ile eksen-arası + toplam + açıklık zincirleri (mm, birimsiz).", "WARNING"),
        ("Oda yazıları: Санузел женский/мужской (стерильная зона) (eksen Г–В), Помещение для работников ТБ (eksen Д), Серверная…/Помещение уборочного инвентаря/Помещение предвахтового медосмотра (sağ blok, oda 110–113), Лестничная клетка", "Yazı/okunabilirlik / R10, R7", "Oda adları oda sınırından taşıp duvar çizgileri, mobilya, kapı etiketleri ve birbirleriyle üst üste biniyor; «103|104» (merdiven kapısı) üst üste basılmış; «Помещение персонала…» adı 115 yerine 116 bölgesine düşüyor.", "[D] oda etiketlerini küçült/yeniden konumlandır, uzun adları kısalt.", "WARNING"),
        ("Merdiven okları: batı, doğu dış merdiven ve iç merdiven (eksen В–Б)", "Dil / RF-S6", "«UP» yazısı ×3 İngilizce.", "[K] merdiven tipi metni; «ВВЕРХ» için Revit ayarı — köprü ile düzenlenemeyebilir, kontrol et.", "WARNING"),
        ("Kapı etiketleri, tüm plan", "Etiketleme / R5, R6", "Kapı işaretleri 100–118 aynı plandaki oda numaralarıyla (100–118) çakışıyor (ör. Тамбур 118 içinde kapı «101» ≠ oda 101 Зал ожидания; kapı 107 ↔ oda 107); 135/136 sıra dışı. Kapı cetveli seti yok → R6 KONTROL EDİLEMEDİ.", "[D] kapı Mark değerlerini ayrı bir aralığa yeniden numarala (`revit_set_parameter` Mark).", "WARNING"),
        ("Eksen 3 civarı: plan içi ve güney tamburun altı iki başlık «- / ---»; АР-7 kesit başları kapı etiketleri 135/136'nın üzerinde", "Düzen / R5, R7", "Numara ve pafta atfı boş iki daire başlık (kesit/cephe işaretçisi, görünümü paftaya yerleştirilmemiş ya da referanssız); АР-7 başları kapı etiketi 135 ve 136 ile üst üste.", "[D] kullanılmayan işaretçileri sil ya da görünümlerini paftaya koy; başları taşı.", "WARNING"),
        ("Pembe kesikli çizgi, y≈536–551 mm, x 22–890 mm; sol uçta çerçeveyi (x=25) aşıyor", "Düzen / R7", "Yapıya ait olmayan açık kırmızı kesikli çizgi uçlarında daire sembolleriyle plan boyunca geçiyor ve çerçeveyi kesiyor. Ne olduğu PDF'ten KESİN DEĞİL (muhtemelen referans düzlemi/yardımcı nesne).", "[D] ilgili kategoriyi bu görünümde gizle (VG) / nesneyi bul; doğrulama için model okuması gerekir.", "WARNING"),
    ],
    "AR-2_plan_2_etazha": [
        ("Görünüm başlığı «План 2 этажа на отм. +4.200», sol alt", "Kotlar / RF-D2", "Ondalık nokta (+4.200); RF: «+4,200», birimsiz.", "[D] görünüm adını «…на отм. +4,200» yap.", "WARNING"),
        ("Görünüm başlığı, sol alt", "Yazı / R7", "Başlık 2 satıra bölünmüş; «+4.200» ile ölçek yazısı «1 : 100» üst üste.", "[D] başlığı kısalt veya viewport başlığını genişlet.", "ADVISORY"),
        (DIMS1 + ", eksen 1–6 / А–Д çevresi", "Boyutlandırma / RF-D3", "Planda hiç ölçü zinciri yok.", "[D] `revit_create_dimension`.", "WARNING"),
        ("Oda yazıları: Помещение уборочного инвентаря / Санузел мужской / Санузел женский / Кладовая (211–214), Переговорная / инструктаж (207, etiket 124), Предполётная подготовка (208, etiket 125), Лестничная клетка / 205", "Yazı/okunabilirlik / R10, R7", "Oda adları birbirinin ve kapı etiketlerinin üstüne biniyor; merdiven kapısı/oda numarası «205/215» üst üste okunmuyor.", "[D] etiketleri yeniden konumlandır/küçült.", "WARNING"),
        ("Merdiven oklarında «DN» (batı/doğu dış merdiven, iç merdiven)", "Dil / RF-S6", "«DN» ×3 İngilizce.", "[K] merdiven tipi metni (bkz. АР-1).", "WARNING"),
        ("Sayfa genel — plan görünümü", "Semboller / R11", "Kuzey oku ve ölçek çubuğu yok (АР-1'de var).", "[D] semboller/detay bileşeni ekle.", "WARNING"),
        ("Pembe kesikli çizgi, plan boyunca, sol uçta çerçeveyi aşıyor", "Düzen / R7", "АР-1'deki ile aynı belirsiz pembe çizgi. Ne olduğu KESİN DEĞİL.", "[D] VG ile gizle/nesneyi bul.", "WARNING"),
    ],
    "AR-3_severnyj_fasad": [
        ("Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6", "Kot RF biçiminde değil: «0», «4200» mm ve birimsiz tam sayı (olması gereken «0,000», «+4,200» m, 3 ondalık, virgül); seviye adları İngilizce (L1/L2). Çatı/parapet üst kotu ve zemin kotu işareti yok; hiçbir yükseklik ölçüsü yok.", "[D] seviye adlarını Rusça yap; [K] level head biçimi (aile) için Al; [D] çatı ve zemin kotu ekle.", "WARNING"),
        ("Tüm cephe — bina silüeti, zemin çizgisi", "Çizgi / RF-L1", "Ölçülen çizgi kalınlıkları yalnızca 0,10 / 0,15 / 0,25 mm (en kalın 0,25). Bina dış konturu ve zemin çizgisi diğer çizgilerden belirgin kalın değil; cephe düz/ince okunuyor (R2 sayı olarak geçer: 3 kalınlık, oran 2,5).", "[K] object style / view template — köprüden düzenlenemez; Al/Revit ile elle düzeltilmeli.", "WARNING"),
        ("Eksen 3 baloncuğu üstü ve giriş altı: АР-7 kesit başı ve iki «- / ---» işaretçi", "Düzen / R7, R5", "АР-7 kesit başı eksen 3 baloncuğuna biniyor; girişin yanında/altında numarası boş iki işaretçi başlığı.", "[D] işaretçileri sil/taşı.", "WARNING"),
        ("Cephe: iki etiketsiz tireli-noktalı seviye çizgisi; seviye çizgileri yapıdan ≈ 650 mm uzağa uzamış", "Kotlar / R5", "Başlıksız ek seviye çizgileri (muhtemelen sahanlık ve çatı seviyeleri) kot yazısı olmadan görünüyor.", "[D] seviye başlığı/kot ekle ya da bu görünümde gizle.", "ADVISORY"),
    ],
    "AR-4_yuzhnyj_fasad": [
        ("Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6", "АР-3 ile aynı: mm tam sayı kot, İngilizce seviye adları, çatı/zemin kotu ve yükseklik ölçüsü yok.", "[D]/[K] АР-3 ile aynı.", "WARNING"),
        ("Tüm cephe — bina silüeti, zemin çizgisi", "Çizgi / RF-L1", "Ölçülen kalınlıklar 0,10 / 0,15 / 0,25 mm; kontur ve zemin çizgisi belirgin kalın değil.", "[K] object style / view template.", "WARNING"),
        ("Eksen 3 baloncuğu: АР-7 başı; giriş solunda ve altında iki «- / ---» işaretçi", "Düzen / R7, R5", "АР-7 kesit başı eksen 3 baloncuğuna biniyor; numarası boş iki işaretçi.", "[D] sil/taşı.", "WARNING"),
        ("Cephe: etiketsiz iki tireli-noktalı seviye çizgisi, uzun seviye çizgileri", "Kotlar / R5", "АР-3 ile aynı.", "[D] başlık ekle/gizle.", "ADVISORY"),
    ],
    "AR-5_vostochnyj_fasad": [
        ("Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6", "АР-3 ile aynı (mm tam sayı, L1/L2, çatı/zemin kotu ve ölçü yok).", "[D]/[K] АР-3 ile aynı.", "WARNING"),
        ("Tüm cephe — silüet, zemin", "Çizgi / RF-L1", "Çizgi kalınlıkları 0,10 / 0,15 / 0,25 mm; kontur belirgin kalın değil.", "[K] object style / view template.", "WARNING"),
        ("Cephe: etiketsiz iki seviye çizgisi", "Kotlar / R5", "Başlıksız ek seviye çizgileri.", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("Pembe dikey kesikli çizgi (x≈ 387–402 mm, y 136–537 mm), uçlarda daire", "Düzen / R7", "Cephe içinde yapıya ait olmayan açık kırmızı çizgi; АР-1/2'deki pembe nesne ile aynı olabilir — KESİN DEĞİL.", "[D] VG ile gizle/nesneyi bul.", "ADVISORY"),
    ],
    "AR-6_zapadnyj_fasad": [
        ("Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6", "АР-3 ile aynı.", "[D]/[K] АР-3 ile aynı.", "WARNING"),
        ("Tüm cephe — silüet, zemin", "Çizgi / RF-L1", "Çizgi kalınlıkları 0,10 / 0,15 / 0,25 mm; kontur belirgin kalın değil.", "[K] object style / view template.", "WARNING"),
        ("Cephe: etiketsiz iki seviye çizgisi", "Kotlar / R5", "Başlıksız ek seviye çizgileri.", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("Pembe dikey kesikli çizgi, uçlarda daire", "Düzen / R7", "АР-5 ile aynı belirsiz pembe nesne — KESİN DEĞİL.", "[D] VG ile gizle/nesneyi bul.", "ADVISORY"),
    ],
    "AR-7_razrez": [
        ("Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6", "Kot mm tam sayı, seviye adları L1/L2; çatı üst kotu yok.", "[D]/[K] АР-3 ile aynı.", "WARNING"),
        ("Kesit: SSL / FFL", "Seviyeler / WF4", "Kaba döşeme (SSL) ve bitmiş zemin (FFL) ayrı gösterilmiyor; yalnızca L1/L2 tek kot.", "[D] spot-elevation ile FFL/SSL ekle (döşeme ofseti Revit_WallFloor ile doğrulanır).", "WARNING"),
        ("Kesit: kesilen döşeme, kolon, duvar, çatı levhası", "Malzeme tarama / WF2", "Kesilen elemanlar boş (beyaz), tarama/dolgu yok; beton/tuğla/yalıtım ayırt edilemiyor. Kesit çizgi hiyerarşisi (0,50 mm kesit / 0,25 / 0,15 görünür) WF1'e uygun.", "[K] kesit kalıbı/malzeme yüzey deseni (Al ile).", "WARNING"),
        ("Kesit: tüm görünüm", "Boyutlandırma / RF-D3", "Kat yüksekliği, toplam yükseklik, parapet/çatı ölçüsü ve eksen arası zincir yok.", "[D] `revit_create_dimension`.", "WARNING"),
        ("Kesit: etiketsiz iki seviye çizgisi (çatı ve ara)", "Kotlar / R5", "Başlıksız seviye çizgileri.", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("Kesit: katman notu, legend", "WF3 / WF10", "1:100'de katman (döşeme/duvar) liderleri ve malzeme legend'i yok; ölçek gereği ADVISORY.", "[A] detay kesit yapılacaksa Al ile.", "ADVISORY"),
    ],
}
summary = {}
for stem, title in sheets:
    code = title.split(" — ")[0]
    rs = [(code,) + r for r in common] + [(code,) + r for r in rows[stem]]
    raw = 100 - sum(PEN[r[-1]] for r in rs)
    score = max(0, raw)
    crit = any(r[-1] == "CRITICAL" for r in rs)
    status = "APPROVED — RELEASE" if score >= 90 else "APPROVED WITH MINOR COMMENTS" if score >= 75 else "REVISE & RESUBMIT" if score >= 60 else "REJECTED"
    if crit and score >= 75:
        status = "REVISE & RESUBMIT"
    summary[stem] = (title, score, raw, status, rs)
    basis = BASIS + (" + Al office convention — wall/floor/ceiling (WF), yalnız bu kesit sayfası" if stem.startswith("AR-7") else "")
    out = ["# Prodim Revit Sheet Quality Control", "", f"**Date:** {DATE}", f"**Basis applied:** {basis}", f"**Sources:** {stem}.pdf", "",
           "## Reviewed sheets", "", "| Sheet | Score | Status |", "|---|---|---|",
           f"| {title} | {score} | {status} (formül sonucu {raw}; CRITICAL sınırı, taban 0) |", "",
           "## Defect table", "", "| Sheet | Location | Category / R-code | Observed issue | Remediation | Severity | Drafter response |", "|---|---|---|---|---|---|---|"]
    for r in rs:
        out.append("| " + " | ".join(r) + " | |")
    out += ["", "Remediation etiketleri: [D] Revit_Drafter mevcut köprü araçlarıyla; [F] yeni başlık-bloğu .rfa gerekir; [A] Al'dan bilgi/karar; [K] köprüden düzenlenemeyen Revit ayarı (object style, text/tag tipi, view template). Ölçüler PDF vektöründen ölçüldü; Form 3 mm ölçüleri KONTROL EDİLEMEDİ.", ""]
    d = os.path.join(root, "reports", stem)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, stem + ".md"), "w", encoding="utf-8").write("\n".join(out))
for k, v in summary.items():
    print(k, v[1], v[2], v[3], len(v[4]))
