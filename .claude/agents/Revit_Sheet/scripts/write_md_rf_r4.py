# -*- coding: utf-8 -*-
"""Round-4 (final) generator (2026-11-04) for the Aerovokzal RF review.
Writes ForRevitReview/reports/r4/<pdf-stem>/<pdf-stem>.md for the 8 sheets.
Edit the row data and re-run for a later round.  Run: python -X utf8 write_md_rf_r4.py
"""
import os

ROOT = r"C:\Users\user\Desktop\Claude Projects\ForRevitReview\reports\r4"
DATE = "2026-11-04"
BASIS = "RF — ГОСТ Р 21.101-2020 (per ТЗ) + ГОСТ 2.301/2.303/2.304"
WF = " + Al office convention — wall/floor/ceiling (WF)"
PEN = {"CRITICAL": 20, "WARNING": 8, "ADVISORY": 2}
LOC = "Основная надпись, sağ şerit (x 1023–1163 mm)"


def common(n):
    s = f"АР-{n}"
    return [
        (s, LOC, "Başlık bloğu / RF-S1",
         "Autodesk jenerik A0 bloğu yerinde: logo, 5x «Consultant/Address/Phone/Fax/e-mail», revizyon tablosu. Form 3 yapısı (graf 1–13, 25–27) yok. [F]",
         "[F] Form 3 title-block .rfa (köprü .rfa üretemez). Metinle taklit edilmez.", "CRITICAL"),
        (s, LOC, "Başlık bloğu / RF-S2, R1",
         "«Project number» = «—» (шифр boş), стадия П/Р, toplam лист sayısı, организация, Нормоконтроль, ГИП, заказчик (graf 27) damgada yok. [F]/[A]",
         "[F] eksik graflar için aile; [A] шифр, стадия, организация Al'dan, sonra `revit_set_parameter`.", "CRITICAL"),
        (s, LOC, "Başlık bloğu / RF-S2",
         "«Drawn by» = Author, «Checked by» = Checker (yer tutucu). [A]",
         "[A] gerçek разработал / проверил adları Al'dan.", "WARNING"),
        (s, "Çerçeve, sayfa kenarları", "Başlık bloğu / RF-S4",
         "Çerçeve 4 kenarda 25 mm, 0,25 mm ince çizgi (r3 ölçümü, çizgi kalınlığı sayıları r4'te aynı). ГОСТ 2.301: sol 20, diğer 5 mm, dış çerçeve kalın. [F]",
         "[F] aile içinde.", "WARNING"),
        (s, LOC, "Başlık bloğu / RF-S6",
         "İngilizce kalıntılar: Consultant/Address/Phone/Fax/e-mail, No./Description/Date, Project number, Date, Drawn by, Checked by, Scale, www.autodesk.com/revit. [F]",
         "[F] Rusça etiketli Form 3 ailesi.", "WARNING"),
        (s, "Tüm sayfa", "Düzen / RF-S5",
         "A0 (1188x840) sayfada çizim ≈%10 alan kaplıyor; format gerekçesiz. [A]",
         "[A] format kararı (A2/A3, aile ile).", "ADVISORY"),
        (s, "Tüm metinler", "Yazı / RF-L2, R10",
         "Trebuchet MS, dik; ГОСТ 2.304 tip A/B (75°) değil. Nominal yükseklik serisi KONTROL EDİLEMEDİ. [K]",
         "[K] text/tag tipleri köprüden düzenlenemez.", "ADVISORY"),
    ]


def common_status():
    return [
        ("Stamp = Autodesk bloğu (RF-S1)", "STILL OPEN", "[F]"),
        ("Stamp alanları boş (RF-S2)", "STILL OPEN", "[F]/[A]"),
        ("Drawn/Checked yer tutucu", "STILL OPEN", "[A]"),
        ("Çerçeve 25 mm / ince (RF-S4)", "STILL OPEN", "[F]"),
        ("İngilizce stamp metni (RF-S6)", "STILL OPEN", "[F]"),
        ("A0 format", "STILL OPEN", "[A]"),
        ("Fontlar", "STILL OPEN", "[K]"),
    ]


ROOMS1 = ("АР-2", "План 1 этажа: 102, 103, 104, 105, 109, 110, 111, 112, 113, 114, 115",
          "Yazı/okunabilirlik / R10, R7",
          "r4 taşımalarından sonra (PDF'te yeniden ölçüldü): 106 ÇÖZÜLDÜ («VIP зона» artık mobilya kutusuna yalnız değiyor, numara temiz). 104/105: numaralar WC'lerden çıktı ama «Санузел мужской/женский (стерильная зона)» adları hâlâ klozet + lavabo sembollerinin üstünde. 109: ad hâlâ üst dış duvar çizgisine oturuyor, numara 8 mm aşağı gidince mobilya kutusu ve Д10 etiketiyle çakıştı (r3'ten kötü). 110: numara pencere etiketi «27» ile çakışık kaldı, ad 111 numara kutusuna değiyor. 113/114: adlar 34 mm genişliğinde, oda ile uyumsuz; 3,5 mm sağa kaydırınca «Санузел мужской» / «женский» doğu dış duvarını ≈2 mm KESİYOR (r3'te içerideydi), 113 adı 112|113 duvarını ve klozet sembollerini kesiyor [NEW]. 102, 103, 111, 112, 115 değişmedi (Drafter da açık diyor). Temiz: 101, 106, 107, 108, 116, 117, 118.",
          "[D] Oda etiketi tipinde 2,5 mm yazı + leader'lı iç konum (yalnız etiket tipi/leader mümkünse); [A] Al onayıyla planda yalnız oda NUMARASI + АР-1'e «Экспликация помещений» (taşan adların tek gerçek çözümü: ad oda genişliğinden uzun); [K] köprü etiket tipini küçültemez.",
          "WARNING")

ROOMS2 = ("АР-3", "План 2 этажа: 201, 205, 207, 208, 209, 211, 212, 213",
          "Yazı/okunabilirlik / R10, R7",
          "r4 taşımalarından sonra: 210 ÇÖZÜLDÜ (ad ve numara temiz; yalnız «пищи» sonu Д28 etiket kenarına değiyor). 208: numara masa dikdörtgeninin üstüne indi, «Предполетная» üst duvarı/Д27 ağzını kesiyor (çözülmedi). 211: ad 4 mm sola gitti, 210|211 duvarını ve Д29/küçük sembolü kesiyor. 213: numara temiz ama «Санузел женский» (34 mm) oda genişliğini aşıyor, iki yan duvarı da kesiyor (≈7 mm); 212 «Санузел мужской» aynı biçimde iki duvarı kesiyor (değişmedi). 201 (ad masalarda), 205 (ad Д20/duvar), 207 (3 satır, masa + numara), 209 değişmedi. Temiz: 202, 203, 204, 206, 214, 215.",
          "[D]/[A]/[K] ROOMS1 ile aynı: tip küçültme [K]; kalıcı çözüm [A] planda yalnız numara + Экспликация помещений.", "WARNING")

WINTAG = lambda n, d1, d2: (f"АР-{n}", "Pencere etiketleri (eşkenar dörtgen) — dış duvarlar", "Etiketleme / R6, R5",
          f"Etiketler Type Mark gösteriyor («{d1}», «{d2}»), АР-1 ведомость окон ise марка ОК1…ОК21. Önceki WARNING ADVISORY'ye indirildi (gerekçe: АР-1'de ledger'a «Тип» sütunu (27/40/41) eklendi ve Условные обозначения md. 6 «ромб на окне — номер типа»ı açıklıyor; sayılar katlara göre tutuyor: plan 1 8×27 + 1×40 = ledger L1 9; plan 2 11×27 + 1×41 = ledger L2 12). Kalan boşluk: 19 pencere aynı «27» etiketini taşıyor, ОК1…ОК21 tek tek planda bulunamıyor. [D]/[A]",
          "[D] Mark okuyan pencere etiketi tipi (`revit_tag_element` + `revit_list_families`) — köprüde yoksa [A] Type Mark'ı ОК-şemasına çevirmek (her instance için ayrı değil) ya da ledger'ı tipe göre grupla.", "ADVISORY")

sheets = {}

sheets[1] = dict(
    stem="AR-1_obshchie_dannye", name="Общие данные", wf=False,
    status=[
        ("Ledger Rusça, hizalı, şemaya uygun (r3 NEW, WARNING + ADVISORY)", "CLOSED",
         "Kapı ledger'ı Марка 468 | Наименование 500 | Размер 835 | Этаж 900 mm, pencere Марка 60 | Тип 90 | Наименование 115 | Размер 270 | Этаж 330 mm: sütunlar sabit x'te, en uzun ad 781 mm'de bitiyor (Размер 835'te başlıyor) → taşma/çakışma yok; «mm» yalnız başlıkta («Размер, мм»), İngilizce aile adı yok («EIW 30» yangın direnci kodu). Say: kapı 10+13+2+8+2 = 35 (1. kat 19, 2. kat 16), pencere 19+1+1 = 21 (9 + 12) — satırlardan sayıldı, tipler ve katlar tutuyor, plan etiketleriyle de (Д1–Д19, Д20–Д35; 27/40 ve 27/41)"),
        ("Eski ledger'lar gizlendi (hayalet kalmış mı?)", "CLOSED", "PDF metin dökümünde «M_Door», «M_Window», «L1/L2» boru-ayraçlı eski satır yok; tek ledger var"),
        ("«Условные обозначения» yok (RF-N1)", "CLOSED", "7 madde eklendi (eksen, seviye, kesit/cephe işaretçisi, oda, kapı, pencere, ölçü). İçerik plandaki sembollerle uyuşuyor (АР-4…АР-8 işaretçileri, Д ovali, «27/40» eşkenar dörtgeni); md. 2 ayrı satırda"),
        ("ТЭП yok (RF-N1)", "CLOSED (tutarlılık notları aşağıda)", "Blok eklendi: 25000×16000, 2 kat, 4200/3900 (АР-1 md. 3 ve АР-8 ölçüleriyle tutuyor), 18 + 15 oda (plan etiketleri 101–118 ve 201–215 ile tutuyor), 390,0 + 381,4 = 771,3"),
        ("Form 1/2 tablo çerçevesi, ссылочные документ adları (RF-N1, r3 WARNING)", "STILL OPEN (WARNING → ADVISORY: içerik şartı sağlandı, yalnız biçim kaldı)", "[F]/[A]"),
        ("«Scale» alanı boş (RF-S2)", "STILL OPEN", "[D]"),
    ],
    extra=[
        ("АР-1", "Sol sütun: Ведомость рабочих чертежей / Общие указания / Ведомость ссылочных…", "Set yapısı / RF-N1",
         "İçerik şartı artık tamam (ведомость, общие указания, условные обозначения, ТЭП, ledger'lar). Kalan yalnız biçim: sayfa listesi düz metin (Форма 1 çerçevesi yok), «Ведомость ссылочных…» satırları ham dosya adları («1792566000574-ТЗ_…docx», «…Рендер… (версия 11172).pdf»). Metin kutularında taşma yok (en sağ satır x 936 mm < damga 1023 mm). RF-N1 WARNING → ADVISORY.",
         "[F] Form 1/2 tablo çerçevesi (family/tablo); [A] ссылочные документ ad/kodları Al'dan.", "ADVISORY"),
        ("АР-1", "Основная надпись, graf 25 «Scale»", "Başlık bloğu / RF-S2",
         "«Scale» alanı hâlâ boş (АР-2…АР-8'de «1 : 100»). Ölçekli görüntü yok → «—» yazılmalı.",
         "[D] sheet Scale parametresini «—» yap. (Drafter: köprüde olanaksız — yine de [D] etiketli kalıyor, doğrulanmadı.)", "ADVISORY"),
        ("АР-1", "Ведомость дверей / окон — biçim", "Düzen / R6",
         "Ledger'lar hizalı ve Rusça; ancak hâlâ düz metin notları, canlı schedule değil → modelle senkron kalmaz. Sayımlar şimdilik plan etiketleriyle tutuyor.",
         "[D] gerçek Revit door/window schedule (`revit_create_schedule` varsa); yoksa her model değişikliğinde metni elle yenile.", "ADVISORY"),
        ("АР-1", "ТЭП: «Итого: 771,3 м²» (x 468, y 718 mm)", "Tutarlılık / R6",
         "NEW: 390,0 + 381,4 = 771,4, yazılan toplam 771,3. Not «сумма площадей помещений Revit» → toplam gizli yuvarlanmamış değerlerden; okuyucu için tutarsız görünüyor. Oda alanları planlarda hiçbir yerde gösterilmiyor (Экспликация yok), bu yüzden 390,0 / 381,4 PDF'ten doğrulanamaz: KONTROL EDİLEMEDİ.",
         "[D] toplamı 771,4 yaz (ya da alanları 2 ondalıkla ver); [A] planlara/Экспликация'ya oda alanı ekle.", "ADVISORY"),
        ("АР-1", "Условные обозначения md. 2 (x 468, y 576 mm) ↔ Общие указания md. 3", "Dil/birim / RF-D2, RF-D3",
         "NEW: md. 2 «отметка уровня, мм» diyor; md. 3 seviyeleri metre olarak yazıyor (L1 0,000; +4,200) — çizimlerdeki seviye başlıkları ise mm tam sayı (0, 4200). Aynı sayfada iki birim; RF-D2 kotu metre, 3 ondalık ister.",
         "[A] kot birimine karar (RF: m, 3 ondalık); [K]/[D] seviye başlığı biçimi köprüden değiştirilemiyor — en azından md. 2'yi gerçek çizimle uyumlu yaz.", "ADVISORY"),
    ])

sheets[2] = dict(
    stem="AR-2_plan_1_etazha", name="План 1 этажа", wf=False,
    status=[
        ("Oda yazıları taşıyor (R10/R7, r3 WARNING)", "STILL OPEN (kısmen: 106 CLOSED; 104/105 numaraları temiz; 109, 113, 114 kötüleşti)", "bkz. tablo"),
        ("Pencere etiketleri = ledger marka (r3 WARNING)", "STILL OPEN → ADVISORY (АР-1 «Тип» sütunu + legend md. 6)", "[D]/[A]"),
        ("«UP» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Ölçü: açıklık/duvar zinciri (RF-D3)", "STILL OPEN", "[D]"),
        ("Kesit başları АР-8 / 117 etiketi (R7)", "STILL OPEN", "[D]"),
    ],
    extra=[
        ROOMS1,
        ("АР-2", "Merdiven okları: batı/doğu dış merdiven, iç merdiven (В–Б)", "Dil / RF-S6",
         "«UP» ×3 İngilizce (değişmedi).", "[K] merdiven tipi metni — köprüden düzenlenemez; Al'a not («ВВЕРХ»).", "WARNING"),
        WINTAG(2, "27", "40"),
        ("АР-2", "Kesit başları «АР-8»: kuzey (Тамбур 118 üstü) ve güney (Тамбур 117 / Д19 yayı)", "Düzen / R7",
         "Güney baş okunun ucu 117 numara kutusuna ve Д19 kapı yayına değiyor; kuzey baş dairesi Тамбур 118 çıkıntı hattının üstünde (değişmedi).",
         "[D] kesit başlarını 20–30 mm dışarı çek.", "ADVISORY"),
        ("АР-2", "Plan alanı, eksen 1–6 / А–Д", "Boyutlandırma / RF-D3",
         "Zincirler tamam (25000, 16000) ama duvar kalınlığı, kapı/pencere açıklıkları ölçülü değil (Drafter: köprüde olanaksız; [D]).",
         "[D] `revit_create_dimension` ile dış duvar açıklık zinciri (mm, birimsiz).", "ADVISORY"),
    ])

sheets[3] = dict(
    stem="AR-3_plan_2_etazha", name="План 2 этажа", wf=False,
    status=[
        ("Oda yazıları taşıyor (R10/R7, r3 WARNING)", "STILL OPEN (kısmen: 210 CLOSED; 208, 211 çözülmedi, 213 numara temiz ama ad oda dışına taşıyor)", "bkz. tablo"),
        ("Pencere etiketleri = ledger marka (r3 WARNING)", "STILL OPEN → ADVISORY (АР-1 «Тип» sütunu + legend md. 6)", "[D]/[A]"),
        ("«DN» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Kuzey oku + ölçek çubuğu yok (R11)", "STILL OPEN", "[D]"),
    ],
    extra=[
        ROOMS2,
        ("АР-3", "Merdiven okları «DN» ×3", "Dil / RF-S6", "«DN» İngilizce.", "[K] merdiven tipi metni.", "WARNING"),
        ("АР-3", "Sayfa genel — plan görünümü", "Semboller / R11",
         "Kuzey oku ve ölçek çubuğu YOK (АР-2'de var). Drafter köprüde olanaksız diyor; PDF'te hâlâ yok.", "[D] АР-2'deki ölçek çubuğu + kuzey oku detay bileşenlerini bu görünüme ekle (köprüde `revit_place_family_instance` ile detay bileşeni mümkünse).", "WARNING"),
        WINTAG(3, "27", "41"),
    ])


def facade(n):
    return [
        (f"АР-{n}", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, zemin/çatı kotu işareti yok. АР-1 md. 3 +2,100 ve +8,100'ü beyan ediyor; fasaddaki iki başlıksız tireli-noktalı çizgi bu seviyeler — kot işareti yok.",
         "[D] seviye adlarını Rusça yap («Этаж 1» …); [K] spot elevation biçimi.", "WARNING"),
        (f"АР-{n}", "Tüm cephe — silüet, zemin", "Çizgi / RF-L1",
         "Çizgiler yalnız 0,10/0,15/0,25 mm (0,7 mm = ölçü işaretleri); dış kontur ve zemin çizgisi belirgin kalın değil. [K]",
         "[K] object style / view template — köprüden düzenlenemez.", "WARNING"),
        (f"АР-{n}", "Cephe: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5",
         "Kotsuz iki ek seviye çizgisi (sahanlık ve çatı).", "[D] başlık ekle ya da bu görünümde gizle.", "ADVISORY"),
    ]


def fstatus():
    return [
        ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"),
        ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
        ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"),
        ("PDF farkı r3 → r4", "—", "yalnız damga zaman damgası değişti (10:10 → 10:24); görünüm içeriği birebir aynı"),
    ]


for n, nm in [(4, "Фасад 6-1"), (5, "Фасад 1-6"), (6, "Фасад А-Д"), (7, "Фасад Д-А")]:
    stem = {4: "AR-4_fasad_6-1", 5: "AR-5_fasad_1-6", 6: "AR-6_fasad_A-D", 7: "AR-7_fasad_D-A"}[n]
    sheets[n] = dict(stem=stem, name=nm, wf=False, status=fstatus(), extra=facade(n))

sheets[8] = dict(stem="AR-8_razrez", name="Разрез", wf=True,
    status=[
        ("Görünüm başlığı «Разрез А–Д» ↔ çizim Д→А (r3 NEW ADVISORY)", "CLOSED", "Başlık «Разрез Д-А» (kısa tire), çizimde Д solda, А sağda — uyumlu; fasad adlandırmasıyla aynı biçim"),
        ("8100 toplam ölçü L2 sapına bitişik (r3 NEW ADVISORY)", "CLOSED (kısmen) → yeniden ifade", "Ölçü zinciri sola taşındı (x 183 mm), L2 başlığı/saplamasıyla çakışma bitti; ancak «8100» metni (y 618–623) tam L2 seviye çizgisinin (y 619,4) yüksekliğinde — çizgi metin etrafında kesiliyor (181,7–186,5 mm arası boşluk). Okunuyor; ADVISORY kalıyor"),
        ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"),
        ("SSL/FFL (WF4)", "STILL OPEN", "[D]"),
        ("Tarama yok (WF2)", "STILL OPEN", "[K]"),
        ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"),
        ("Katman liderleri/legend (WF3/WF10)", "STILL OPEN", "[A]"),
    ],
    extra=[
        ("АР-8", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, çatı üst kotu (+8,100) için kot işareti yok.", "[D]/[K] АР-4 ile aynı.", "WARNING"),
        ("АР-8", "Kesit: SSL / FFL", "Seviyeler / WF4", "Kaba döşeme (SSL) ve bitmiş zemin (FFL) ayrı gösterilmiyor.",
         "[D] spot elevation ile FFL/SSL.", "WARNING"),
        ("АР-8", "Kesit: kesilen döşeme, kolon, duvar, çatı levhası", "Malzeme tarama / WF2",
         "Kesilen elemanlar hâlâ beyaz, tarama yok (kesit çizgisi 0,5–0,7 mm: WF1 tamam). [K]", "[K] kesit kalıbı/malzeme yüzey deseni (Al ile).", "WARNING"),
        ("АР-8", "Kesit: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5", "Başlıksız (yalnız ölçü zinciri uçları).", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("АР-8", "Kesit: katman notu, legend", "WF3 / WF10", "1:100'de katman liderleri ve malzeme legend'i yok.", "[A] detay kesit gerekirse Al ile.", "ADVISORY"),
        ("АР-8", "Toplam ölçü «8100» (x 183–187, y 618–623 mm) ↔ L2 seviye çizgisi (y 619,4)", "Boyutlandırma / R9",
         "Ölçü artık sol tarafta, L2 başlığına/saplamaya çakışmıyor; fakat metin L2 seviye çizgisinin tam üstünde, çizgi metin yüksekliğinde kesilmiş. Okunaklı, düşük risk.",
         "[D] ölçü metnini (text position) çizginin 3–5 mm üstüne/altına al ya da ofseti artır.", "ADVISORY"),
    ])


def score(rows):
    raw = 100 - sum(PEN[r[5]] for r in rows)
    sc = max(raw, 0)
    crit = any(r[5] == "CRITICAL" for r in rows)
    if crit and sc >= 75:
        band = "REVISE & RESUBMIT"
    elif sc >= 90:
        band = "APPROVED — RELEASE"
    elif sc >= 75:
        band = "APPROVED WITH MINOR COMMENTS"
    elif sc >= 60:
        band = "REVISE & RESUBMIT"
    else:
        band = "REJECTED"
    return raw, sc, band


HIST = {1: "r2 14 → r3 12 → r4", 2: "r1 −40 → r2 −10 → r3 4 → r4", 3: "r1 −26 → r2 −8 → r3 0 → r4",
        4: "r1 −2 → r2 6 → r3 14 → r4", 5: "r1 −2 → r2 6 → r3 14 → r4", 6: "r1 4 → r2 4 → r3 14 → r4",
        7: "r1 4 → r2 4 → r3 14 → r4", 8: "r1 −12 → r2 −12 → r3 0 → r4"}


def main():
    for n, d in sheets.items():
        rows = common(n) + d["extra"]
        raw, sc, band = score(rows)
        st = d["status"] + common_status()
        out = os.path.join(ROOT, d["stem"])
        os.makedirs(out, exist_ok=True)
        L = ["# Prodim Revit Sheet Quality Control — round 4 (final)", "",
             f"**Date:** {DATE}",
             f"**Basis applied:** {BASIS}" + (WF if d["wf"] else ""),
             f"**Sources:** {d['stem']}.pdf", "",
             "## Reviewed sheets", "", "| Sheet | Score | Status |", "|---|---|---|",
             f"| АР-{n} — {d['name']} | {sc} (ham {raw}; {HIST[n]} {raw}) | {band} |", "",
             "## Round-3 row → status", "", "| Round-3 row | Status | Not |", "|---|---|---|"]
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
        print(n, raw, sc, band)


main()
