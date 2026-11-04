# -*- coding: utf-8 -*-
"""Round-2 generator (2026-11-04) for the Aerovokzal RF review.
Writes ForRevitReview/reports/r2/<pdf-stem>/<pdf-stem>.md for the 8 sheets.
Edit the row data below and re-run for round 3.  Usage: python write_md_rf_r2.py
"""
import os

ROOT = r"C:\Users\user\Desktop\Claude Projects\ForRevitReview\reports\r2"
DATE = "2026-11-04"
BASIS = "RF — ГОСТ Р 21.101-2020 (per ТЗ) + ГОСТ 2.301/2.303/2.304"
WF = " + Al office convention — wall/floor/ceiling (WF)"
PEN = {"CRITICAL": 20, "WARNING": 8, "ADVISORY": 2}

# ---- common stamp rows (same on every sheet) -------------------------------
def common(n):
    s = f"АР-{n}"
    loc = "Основная надпись, sağ şerit (x 1023–1163 mm)"
    return [
        (s, loc, "Başlık bloğu / RF-S1",
         "Autodesk jenerik A0 bloğu hâlâ yerinde: logo, 5x «Consultant/Address/Phone/Fax/e-mail», revizyon tablosu. ГОСТ Р 21.101 Форма 3 yapısı (graf 1–13, 25–27) yok.",
         "[F] Form 3 title-block .rfa (köprü .rfa üretemez). Metinle taklit edilmez.", "CRITICAL"),
        (s, loc, "Başlık bloğu / RF-S2, R1",
         "«Project number» = «—» (шифр boş), стадия П/Р yok, toplam лист sayısı yok, организация, Нормоконтроль, ГИП, заказчик grafı yok. (İlerleme: «Scale» artık «1 : 100» dolu — АР-2…АР-8.)",
         "[F] eksik graflar için aile; [A] шифр, стадия, организация değerleri Al'dan, sonra `revit_set_parameter`.", "CRITICAL"),
        (s, loc, "Başlık bloğu / RF-S2",
         "«Drawn by» = Author, «Checked by» = Checker (yer tutucu).",
         "[A] gerçek разработал / проверил adları Al'dan.", "WARNING"),
        (s, "Çerçeve, sayfa kenarları", "Başlık bloğu / RF-S4",
         "Çerçeve x 25–1163, y 25–815 mm: 4 kenarda 25 mm, 0,25 mm ince çizgi. ГОСТ 2.301: sol 20, diğer 5 mm, dış çerçeve kalın.",
         "[F] aile içinde.", "WARNING"),
        (s, loc, "Başlık bloğu / RF-S6",
         "İngilizce kalıntılar: Consultant/Address/Phone/Fax/e-mail, No./Description/Date, Project number, Date, Drawn by, Checked by, Scale, www.autodesk.com/revit.",
         "[F] Rusça etiketli Form 3 ailesi.", "WARNING"),
        (s, "Основная надпись, заказчик / наименование листа", "Başlık bloğu / R7, RF-S2",
         "«ГПН-Снабжение» (18,2 mm) kısaldı ama hâlâ kutuyu aşıyor: x 1026–1160 mm (kutu ≈1029–1157) ve satırı «Аэровокзал» ile üst üste biniyor (y 604–627 / 613–636 mm). Sayfa adı taşması: АР-4 «Северный фасад» 1022–1163, АР-6 «Восточный фасад» 1019–1167 (çerçeve 1163'ü 4 mm AŞIYOR), АР-7 «Западный фасад» 1023–1163.",
         "[D] Client Name → «ГПН» (tam ad АР-1 notlarına); fasad sayfa adları → «Фасад 6-1», «Фасад 1-6», «Фасад А-Д» (doğu), «Фасад Д-А» (batı); gerçek çözüm [F] aile yazı boyutu.", "WARNING"),
        (s, "Tüm sayfa", "Düzen / RF-S5",
         "A0 (1188x840) sayfada çizim ≈%10 alan kaplıyor; format gerekçesiz.",
         "[A] format kararı (A2/A3, aile ile).", "ADVISORY"),
        (s, "Tüm metinler", "Yazı / RF-L2, R10",
         "Trebuchet MS / Arial / Georgia, dik; ГОСТ 2.304 tip A/B (75°) değil. Nominal yükseklik serisi KONTROL EDİLEMEDİ.",
         "[K] text/tag tipleri köprüden düzenlenemez.", "ADVISORY"),
    ]

def common_status(first_old):
    """round-1 common rows -> status (all STILL OPEN except the scale field)"""
    return [
        ("Stamp = Autodesk bloğu (RF-S1)", "STILL OPEN", "[F]"),
        ("Stamp alanları boş (RF-S2)", "STILL OPEN (Scale dolu — kısmen)", "[F]/[A]"),
        ("Drawn/Checked yer tutucu", "STILL OPEN", "[A]"),
        ("Çerçeve 25 mm / ince (RF-S4)", "STILL OPEN", "[F]"),
        ("İngilizce stamp metni (RF-S6)", "STILL OPEN", "[F]"),
        ("Client Name / sayfa adı taşması (R7)", "STILL OPEN (kısaltıldı, hâlâ taşıyor)", "[D]"),
        ("A0 format", "STILL OPEN", "[A]"),
        ("Fontlar", "STILL OPEN", "[K]"),
    ]

PINK_PLAN = ("Pembe kesikli çizgi y≈536–551 mm, x 22–890 mm; uçlardaki daireler çerçeveyi (x=25) kesiyor",
             "Düzen / R7",
             "Plan 2'de açık kırmızı (255,170,170) çizgi sürüyor; L1 planında kayboldu (Drafter'ın gizlediği «WF - L1 base check» ile aynı nesne olması muhtemel — KESİN DEĞİL).",
             "[D] VG → Annotation Categories: bu görünümde Sections/«WF - L1 base check» işaretçisini gizle; sürerse nesneyi sec. listesinden bul.", "WARNING")

sheets = {}

# ---------------------------------------------------------------- АР-1
sheets[1] = dict(
    stem="AR-1_obshchie_dannye", name="Общие данные", wf=False,
    status=[("(yeni sayfa — round 1'de yoktu)", "NEW", "RF-N1: «Общие данные» sayfası artık var; ведомость + 4 общие указания metin notu olarak")],
    extra=[
        ("АР-1", "Ведомость рабочих чертежей + Общие указания (sol üst)", "Set yapısı / RF-N1",
         "Sayfa listesi doğru (АР-1…АР-8, Kiril «АР», adlarla uyumlu) ve 4 madde 1:100, mm, kotlar, 25000x16000 ile modele uyuyor (kot ölçümü: ara sahanlık ≈ +2,1; çatı ≈ +8,1 — notla uyumlu). Ancak: Форма 1 tablosu değil düz metin (Лист / Наименование / Примечание sütunu yok), Форма 2 (ссылочные документы), условные обозначения, kapı/pencere ведомость'i ve ТЭП yok. Metin kutudan taşmıyor.",
         "[D] `revit_create_text_note` ile Форма 2 başlığı + «Условные обозначения» maddeleri (oda etiketi, kapı/pencere, eksen, kot işareti) ekle; [A] ссылочные документы listesi Al'dan; [F] tablo çerçevesi Form 1.", "WARNING"),
        ("АР-1", "Основная надпись, graf 25 «Scale»", "Başlık bloğu / RF-S2",
         "NEW: «Scale» alanı boş (diğer 7 sayfada «1 : 100»). Genel veri sayfasında ölçekli görüntü yok; tire/«—» yazılmalı.",
         "[D] sheet Scale parametresini «—» yap.", "ADVISORY"),
    ])

# ---------------------------------------------------------------- АР-2
sheets[2] = dict(
    stem="AR-2_plan_1_etazha", name="План 1 этажа", wf=False,
    status=[
        ("Görünüm başlığı ondalık nokta (RF-D2)", "CLOSED", "«План 1 этажа на отм. 0,000» — virgül, birimsiz, işaretsiz"),
        ("Planda ölçü zinciri yok (RF-D3)", "CLOSED", "1–6: 5500+8000+3500+3000+5000 = 25000; А–Д: 5000+3000+3500+4500 = 16000; zincirler kapalı, üst üste binme yok. Kalan: açıklık/duvar ölçüsü → ADVISORY (aşağıda)"),
        ("Pembe kesikli çizgi (R7)", "CLOSED", "bu planda yok (vektörde pembe stroke yok)"),
        ("«- / ---» boş işaretçiler (R5/R7)", "CLOSED (kısmen)", "boş işaretçiler gitti; АР-8 kesit başları 135/136 üzerinde → STILL OPEN"),
        ("Общие данные sayfası yok (RF-N1)", "CLOSED (kısmen)", "АР-1 var; içerik eksikleri АР-1 raporunda"),
        ("Oda yazıları taşıyor (R10/R7)", "STILL OPEN", "104/105/113/114 iyileşti, geri kalanı sürüyor"),
        ("«UP» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Kapı marka = oda no (R5/R6)", "STILL OPEN", "[D]"),
    ],
    extra=[
        ("АР-2", "План 1 этажа: 106–116 bloğu (Помещение для работников ТБ/109-110, Багажное/116, Помещение персонала/115, Санузел/113-114, Серверная/113, уборочного инвентаря/112, предвахтового/111-110), Зал ожидания вылета/107, Лестничная клетка 103|104", "Yazı/okunabilirlik / R10, R7",
         "Oda adları hâlâ oda sınırından taşıyor: duvar çizgileri, mobilya/sıhhi tesisat ve komşu etiket numaralarıyla üst üste (111–113 sağ blok adları birbirinin içine giriyor; «103|104» okunmuyor). Taşınan 104/105/113/114'te ad odanın içine girdi ama WC sembolleriyle çakışıyor.",
         "[D] kalan etiketlerin yazı tipini/konumunu düzelt: Серверная / связь → «Серверная», «Помещение уборочного инвентаря» → «Убор. инвентаря», «Помещение предвахтового медосмотра» → «Медосмотр», 103|104 etiketlerini ayır (`revit_tag_element` offset).", "WARNING"),
        ("АР-2", "Merdiven okları: batı/doğu dış merdiven, iç merdiven (В–Б)", "Dil / RF-S6",
         "«UP» ×3 İngilizce (değişmedi).", "[K] merdiven tipi metni — köprüden düzenlenemez; Al'a not («ВВЕРХ»).", "WARNING"),
        ("АР-2", "Kapı etiketleri, tüm plan", "Etiketleme / R5, R6",
         "Kapı Mark 100–118 oda numaralarıyla çakışıyor (Тамбур 118 içinde kapı «101», oda 101 Зал ожидания…); 135/136 sıra dışı. Kapı cetveli yok → R6 KONTROL EDİLEMEDİ.",
         "[D] Mark'ı ayrı aralığa al: `revit_set_parameter` Mark = «Д1…Д45», pencere «ОК1…».", "WARNING"),
        ("АР-2", "Kesit başları «АР-8»: kuzey (kapı 135, eksen 3) ve güney (kapı 136, Тамбур 117)", "Düzen / R7",
         "Kesit başları kapı etiketleri 135/136 ve güney başı eksen 3 baloncuğunun üstüne biniyor (değişmedi; round-1'deki aynı çakışma, kesit şimdi АР-8 numaralı).",
         "[D] kesit çizgisini/başlarını verandanın dışına kaydır ya da 135/136 etiketini ofsetle.", "WARNING"),
        ("АР-2", "Plan alanı, eksen 1–6 / А–Д", "Boyutlandırma / RF-D3",
         "Zincirler tamam ama yalnız eksen-arası+toplam; duvar kalınlığı, kapı/pencere açıklıkları ölçülü değil.",
         "[D] `revit_create_dimension` ile dış duvar açıklık zinciri (mm, birimsiz).", "ADVISORY"),
    ])

# ---------------------------------------------------------------- АР-3
sheets[3] = dict(
    stem="AR-3_plan_2_etazha", name="План 2 этажа", wf=False,
    status=[
        ("Görünüm başlığı «+4.200» (RF-D2)", "CLOSED", "«План 2 этажа, отм. +4,200»"),
        ("Başlık/ölçek yazısı üst üste (R7)", "CLOSED", "tek satır"),
        ("Planda ölçü zinciri yok (RF-D3)", "CLOSED", "25000 ve 16000 zincirleri, toplamlar tutuyor, kapalı"),
        ("Oda yazıları taşıyor (R10/R7)", "STILL OPEN", "214 düzeldi; 207, 211/212, 213/214, 205 sürüyor"),
        ("«DN» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Kuzey oku + ölçek çubuğu yok (R11)", "STILL OPEN", "[D]"),
        ("Pembe kesikli çizgi (R7)", "STILL OPEN", "[D]"),
    ],
    extra=[
        ("АР-3", "План 2 этажа: 207 Переговорная (kapı 124), 208 Предполётная (kapı 125), 211 Помещение уборочного инвентаря / 212 Санузел мужской, 213 Санузел женский / 214 Кладовая, 205 Лестничная клетка (203/205), 206 Коридор", "Yazı/okunabilirlik / R10, R7",
         "Kalan taşmalar: 207/208 adı kapı etiketi 124/125 ile; 211 ve 212 adları birbirinin üstünde okunmuyor; 213 «Санузел женский» 214 «Кладовая» ile yan yana çakışıyor; 205 numarası ve «Лестничная клетка» merdiven içinde üst üste. (207 ve 214 taşındı, 214 düzeldi.)",
         "[D] adları kısalt («Убор. инвентаря», «Сан. м», «Сан. ж») ve etiket ofsetini düzelt.", "WARNING"),
        ("АР-3", "Merdiven okları «DN» ×3", "Dil / RF-S6", "«DN» İngilizce.", "[K] merdiven tipi metni.", "WARNING"),
        ("АР-3", "Sayfa genel — plan görünümü", "Semboller / R11",
         "Kuzey oku ve ölçek çubuğu YOK (АР-2'de var).", "[D] АР-2'deki ölçek çubuğu + kuzey oku detay bileşenlerini bu görünüme ekle.", "WARNING"),
        ("АР-3",) + PINK_PLAN,
    ])

# ---------------------------------------------------------------- facades
def facade(n, stem, name, pink):
    rows = [
        (f"АР-{n}", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, zemin/çatı kotu işareti ve yükseklik ölçüsü yok. АР-1 notu +2,100 ve +8,100'ü beyan ediyor; fasaddaki iki başlıksız tireli-noktalı çizgi tam bu seviyeler (≈+2,1 / ≈+8,1 ölçüldü) — başlık/kot yok. Eksen zinciri var ama toplam (25000/16000) yok.",
         "[D] seviye adlarını Rusça yap («Этаж 1» …); çatı/sahanlık/zemin için kot işareti ekle (varsa spot elevation aracı; yoksa [K] level head biçimi, Al); [K] «0,000/+4,200» biçimi aile.", "WARNING"),
        (f"АР-{n}", "Tüm cephe — silüet, zemin", "Çizgi / RF-L1",
         "Çizgiler yalnız 0,10/0,15/0,25 mm (0,7 mm = ölçü işaretleri); dış kontur ve zemin çizgisi belirgin kalın değil.",
         "[K] object style / view template — köprüden düzenlenemez; Al/Revit elle.", "WARNING"),
        (f"АР-{n}", "Cephe: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5",
         "Kotsuz iki ek seviye çizgisi (yukarıya bak: sahanlık ve çatı).", "[D] başlık ekle ya da bu görünümde gizle.", "ADVISORY"),
    ]
    if pink:
        rows.append((f"АР-{n}", "Dikey pembe kesikli çizgi, uçlarda daire (üst ve alt)", "Düzen / R7",
                     "Cephe içinde yapıya ait olmayan açık kırmızı kesit/referans işaretçisi (x≈387–402 mm bbox, y 136–537); N/S'de gizlenen aynı nesne olması muhtemel — KESİN DEĞİL.",
                     "[D] VG → Sections kategorisini bu görünümde gizle.", "ADVISORY"))
    return rows

sheets[4] = dict(stem="AR-4_severnyj_fasad", name="Северный фасад", wf=False,
    status=[("Eksen-arası zincir yok", "CLOSED", "5000/3000/3500/8000/5500, 6→1 sırası, bubble'larla uyumlu"),
            ("АР-7 kesit başı ve «- / ---» işaretçiler (R7/R5)", "CLOSED", "bu fasadda görünmüyor"),
            ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"), ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
            ("Başlıksız seviye çizgileri", "STILL OPEN", "[D] — artık +2,1/+8,1 olduğu doğrulandı")],
    extra=facade(4, "", "", False))
sheets[5] = dict(stem="AR-5_yuzhnyj_fasad", name="Южный фасад", wf=False,
    status=[("Eksen-arası zincir yok", "CLOSED", "5500/8000/3500/3000/5000, 1→6"),
            ("Kesit başı ve «- / ---» işaretçiler", "CLOSED", "görünmüyor"),
            ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"), ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
            ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]")],
    extra=facade(5, "", "", False))
sheets[6] = dict(stem="AR-6_vostochnyj_fasad", name="Восточный фасад", wf=False,
    status=[("Eksen-arası zincir yok", "CLOSED", "4500/3500/3000/5000, А→Д"),
            ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"), ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
            ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"), ("Pembe çizgi", "STILL OPEN", "[D]")],
    extra=facade(6, "", "", True))
sheets[7] = dict(stem="AR-7_zapadnyj_fasad", name="Западный фасад", wf=False,
    status=[("Eksen-arası zincir yok", "CLOSED", "5000/3000/3500/4500, Д→А"),
            ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"), ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
            ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"), ("Pembe çizgi", "STILL OPEN", "[D]")],
    extra=facade(7, "", "", True))

# ---------------------------------------------------------------- АР-8
sheets[8] = dict(stem="AR-8_razrez", name="Разрез", wf=True,
    status=[("Eksen-arası zincir (RF-D3)", "CLOSED (kısmen)", "Д→А: 5000+3000+3500+4500 = 16000 kapalı; yükseklik ölçüleri sürüyor"),
            ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"), ("SSL/FFL (WF4)", "STILL OPEN", "[D]"),
            ("Tarama yok (WF2)", "STILL OPEN", "[K]"), ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"),
            ("Katman liderleri/legend (WF3/WF10)", "STILL OPEN", "[A]")],
    extra=[
        ("АР-8", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, çatı üst kotu yok.", "[D]/[K] АР-4 ile aynı.", "WARNING"),
        ("АР-8", "Kesit: SSL / FFL", "Seviyeler / WF4", "Kaba döşeme (SSL) ve bitmiş zemin (FFL) ayrı gösterilmiyor.",
         "[D] spot elevation ile FFL/SSL (ofset Revit_WallFloor ile doğrulanır).", "WARNING"),
        ("АР-8", "Kesit: kesilen döşeme, kolon, duvar, çatı levhası", "Malzeme tarama / WF2",
         "Kesilen elemanlar hâlâ beyaz, tarama yok (kesit çizgisi 0,5–0,7 mm: WF1 tamam).", "[K] kesit kalıbı/malzeme yüzey deseni (Al ile).", "WARNING"),
        ("АР-8", "Kesit: tüm görünüm", "Boyutlandırma / RF-D3",
         "Eksen zinciri geldi; kat yüksekliği (4200), toplam yükseklik (≈8100), parapet ölçüsü yok.", "[D] `revit_create_dimension` ile düşey zincir (mm).", "WARNING"),
        ("АР-8", "Kesit: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5", "Başlıksız.", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("АР-8", "Kesit: katman notu, legend", "WF3 / WF10", "1:100'de katman liderleri ve malzeme legend'i yok.", "[A] detay kesit gerekirse Al ile.", "ADVISORY"),
    ])

def score(rows):
    raw = 100 - sum(PEN[r[5]] for r in rows)
    sc = max(raw, 0)
    crit = any(r[5] == "CRITICAL" for r in rows)
    if crit and sc >= 75:
        band = "REVISE & RESUBMIT"
    elif sc >= 90: band = "APPROVED — RELEASE"
    elif sc >= 75: band = "APPROVED WITH MINOR COMMENTS"
    elif sc >= 60: band = "REVISE & RESUBMIT"
    else: band = "REJECTED"
    return raw, sc, band

ROUND1 = {1: "—", 2: "0 (ham −40)", 3: "0 (ham −26)", 4: "0 (ham −2)", 5: "0 (ham −2)",
          6: "4", 7: "4", 8: "0 (ham −12)"}

def main():
    summary = []
    for n, d in sheets.items():
        rows = common(n) + d["extra"]
        raw, sc, band = score(rows)
        summary.append((n, d["name"], raw, sc, band))
        st = d["status"] + common_status(None)
        out = os.path.join(ROOT, d["stem"])
        os.makedirs(out, exist_ok=True)
        L = ["# Prodim Revit Sheet Quality Control — round 2", "",
             f"**Date:** {DATE}",
             f"**Basis applied:** {BASIS}" + (WF if d["wf"] else ""),
             f"**Sources:** {d['stem']}.pdf", "",
             "## Reviewed sheets", "", "| Sheet | Score | Status |", "|---|---|---|",
             f"| АР-{n} — {d['name']} | {sc} (ham {raw}; round 1: {ROUND1[n]}) | {band} |", "",
             "## Round-1 row → status", "", "| Round-1 row | Status | Not |", "|---|---|---|"]
        for a, b, c in st:
            L.append(f"| {a} | {b} | {c} |")
        L += ["", "## Defect table", "",
              "| Sheet | Location | Category / R-code | Observed issue | Remediation | Severity | Drafter response |",
              "|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| " + " | ".join(r) + " | |")
        L += ["", "Etiketler: [D] Revit_Drafter köprü araçlarıyla; [F] yeni başlık-bloğu .rfa; [A] Al'dan bilgi/karar; [K] köprüden düzenlenemeyen Revit ayarı. Ölçüler PDF vektöründen/metin kutularından; Form 3 mm ölçüleri KONTROL EDİLEMEDİ. Skor: CRITICAL −20, WARNING −8, ADVISORY −2; CRITICAL varsa üst sınır REVISE & RESUBMIT."]
        with open(os.path.join(out, d["stem"] + ".md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
    for s in summary:
        print(s[0], s[2], s[3], s[4])

main()
