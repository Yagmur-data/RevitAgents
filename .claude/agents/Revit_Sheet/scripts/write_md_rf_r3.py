# -*- coding: utf-8 -*-
"""Round-3 generator (2026-11-04) for the Aerovokzal RF review.
Writes ForRevitReview/reports/r3/<pdf-stem>/<pdf-stem>.md for the 8 sheets.
Edit the row data below and re-run for round 4.  Usage: python write_md_rf_r3.py
"""
import os

ROOT = r"C:\Users\user\Desktop\Claude Projects\ForRevitReview\reports\r3"
DATE = "2026-11-04"
BASIS = "RF — ГОСТ Р 21.101-2020 (per ТЗ) + ГОСТ 2.301/2.303/2.304"
WF = " + Al office convention — wall/floor/ceiling (WF)"
PEN = {"CRITICAL": 20, "WARNING": 8, "ADVISORY": 2}
LOC = "Основная надпись, sağ şerit (x 1023–1163 mm)"


def common(n):
    s = f"АР-{n}"
    return [
        (s, LOC, "Başlık bloğu / RF-S1",
         "Autodesk jenerik A0 bloğu hâlâ yerinde: logo, 5x «Consultant/Address/Phone/Fax/e-mail», revizyon tablosu. Form 3 yapısı (graf 1–13, 25–27) yok. [F]",
         "[F] Form 3 title-block .rfa (köprü .rfa üretemez). Metinle taklit edilmez.", "CRITICAL"),
        (s, LOC, "Başlık bloğu / RF-S2, R1",
         "«Project number» = «—» (шифр boş), стадия П/Р, toplam лист sayısı, организация, Нормоконтроль, ГИП yok. Заказчик (graf 27) damgada yok: Client Name boşaltıldı, ad АР-1'de metin notu olarak duruyor (taşma bitti, graf hâlâ boş). [F]/[A]",
         "[F] eksik graflar için aile; [A] шифр, стадия, организация Al'dan, sonra `revit_set_parameter`.", "CRITICAL"),
        (s, LOC, "Başlık bloğu / RF-S2",
         "«Drawn by» = Author, «Checked by» = Checker (yer tutucu). [A]",
         "[A] gerçek разработал / проверил adları Al'dan.", "WARNING"),
        (s, "Çerçeve, sayfa kenarları", "Başlık bloğu / RF-S4",
         "Çerçeve x 25–1163, y 25–815 mm (yeniden ölçüldü): 4 kenarda 25 mm, 0,25 mm ince çizgi. ГОСТ 2.301: sol 20, diğer 5 mm, dış çerçeve kalın. [F]",
         "[F] aile içinde.", "WARNING"),
        (s, LOC, "Başlık bloğu / RF-S6",
         "İngilizce kalıntılar: Consultant/Address/Phone/Fax/e-mail, No./Description/Date, Project number, Date, Drawn by, Checked by, Scale, www.autodesk.com/revit. [F]",
         "[F] Rusça etiketli Form 3 ailesi.", "WARNING"),
        (s, "Tüm sayfa", "Düzen / RF-S5",
         "A0 (1188x840) sayfada çizim ≈%10 alan kaplıyor; format gerekçesiz. [A]",
         "[A] format kararı (A2/A3, aile ile).", "ADVISORY"),
        (s, "Tüm metinler", "Yazı / RF-L2, R10",
         "Trebuchet MS / Arial / Georgia, dik; ГОСТ 2.304 tip A/B (75°) değil. Nominal yükseklik serisi KONTROL EDİLEMEDİ. [K]",
         "[K] text/tag tipleri köprüden düzenlenemez.", "ADVISORY"),
    ]


def common_status():
    return [
        ("Stamp = Autodesk bloğu (RF-S1)", "STILL OPEN", "[F]"),
        ("Stamp alanları boş (RF-S2)", "STILL OPEN (Scale dolu; заказчик graf 27 artık boş)", "[F]/[A]"),
        ("Drawn/Checked yer tutucu", "STILL OPEN", "[A]"),
        ("Çerçeve 25 mm / ince (RF-S4)", "STILL OPEN", "[F]"),
        ("İngilizce stamp metni (RF-S6)", "STILL OPEN", "[F]"),
        ("Client Name / sayfa adı kutudan taşıyor (R7)", "CLOSED", "Client Name boş; «Аэровокзал Северное» ve sayfa adı x 1030–1156 mm, çerçevenin (1163) içinde, üst üste binme yok"),
        ("A0 format", "STILL OPEN", "[A]"),
        ("Fontlar", "STILL OPEN", "[K]"),
    ]


ROOMS1 = ("АР-2", "План 1 этажа: 102 Кафетерий, 103 Лестничная клетка, 104/105/106 санузлы + VIP, 109 (Помещение для работников ТБ), 110–115 sağ blok",
          "Yazı/okunabilirlik / R10, R7",
          "Etiket adları hâlâ oda içine sığmıyor (etiket odadan çıkamıyor, ad kısaltılmadı). Ölçülen: 103 «Лестничная клетка» merdiven basamaklarının ve «UP»un üstünde, 103 numarası «UP» ile çakışık; 102 «Кафетерий (20 пос. мест)» masa/sandalye çizimlerinin üstünde, kapı Д3 yayına değiyor; 109 adı oda ÜSTÜNDE, dış duvar çizgisini kesiyor (oda dışına taşmış); 111 «Помещение уборочного инвентаря» 111 numarasının üstünde, 112 «Серверная, кроссовая, узел связи» 113 kutusuna giriyor; 113/114 «Санузел …» WC sembollerinin üstünde; 115 «Помещение персонала по организации авиаперевозок» 3 satır, odanın üst ve alt duvarını kesiyor; 104–106 adları WC/mobilya ile çakışık; 110 numarası yatağın/ kutunun üstünde. Düzelenler: 101, 107, 108, 116, 117, 118 temiz. (Drafter'ın listesi 102/103/111/112/115 — ek olarak 109, 110, 113, 114 ve 104–106 yazı/donatı çakışması var.)",
          "[D] 1) Oda etiketi tipinde yazı yüksekliğini ГОСТ 2.304 serisinden 2,5 mm'ye indir (yüklü daha küçük etiket tipi varsa `revit_tag_element`/tip değiştirme); 2) adı sığmayan odalarda etiketi serbest bırak (leader) — ama oda içinde; 3) [A] Al'ın onayıyla: planda yalnız oda NUMARASI, adlar АР-1'de «Экспликация помещений» (ГОСТ uygulaması) — ad kısaltma gerekmez.",
          "WARNING")

ROOMS2 = ("АР-3", "План 2 этажа: 201 Кабинет специалистов, 205 Лестничная клетка, 207 Переговорная, 208, 209, 210, 211/212, 213",
          "Yazı/okunabilirlik / R10, R7",
          "Kalan çakışmalar: 201 adı masa/sandalye çizimlerinin üstünde; 205 «Лестничная клетка» Д20 etiketi ve 205 numarasıyla çakışık, merdiven duvarını kesiyor; 207 «Переговорная / инструктаж (персонал авиаперевозок)» 3 satır, masa ve 207 numarasının üstünde; 208 numarası mobilya üstünde; 209 «Комната отдыха экипажей» duvar çizgisini kesiyor; 210 numarası sandalyelerin üstünde; 211 «Помещение уборочного инвентаря» ve 213 «Санузел женский» komşu duvar ile Д29/Д31 etiketine giriyor, 212 adı 211/212 sınır duvarını kesiyor. Temiz: 202, 203, 204, 206, 214, 215. (Drafter'ın listesi 201/205/207 — ek: 208–213.)",
          "[D] ROOMS1 ile aynı üç adım (2,5 mm etiket tipi; leader'lı iç konum; [A] Экспликация помещений).", "WARNING")

WINTAG = lambda n, d1, d2: (f"АР-{n}", "Pencere etiketleri (eşkenar dörtgen) — dış duvarlar", "Etiketleme / R6, R5",
          f"NEW: pencere etiketleri «{d1}» ve «{d2}» gösteriyor (Type Mark), АР-1 ведомость окон ise марка ОК1…ОК21 veriyor. Planda hiçbir yerde «ОК…» yok → ledger satırları çizimde bulunamıyor. Sayılar tutuyor (plan 1: 8 + 1 = ledger L1 9; plan 2: 11 + 1 = ledger L2 12; kapılar Д1–Д19 / Д20–Д35 = ledger L1 19 / L2 16), yani şiddet düşürüldü: etiketler var ama yanlış parametreyi okuyor.",
          "[D] pencere etiketini Mark okuyan bir etiket tipiyle yeniden yerleştir (`revit_tag_element`, yüklü tipler `revit_list_families`); yoksa [A] ledger'a «Тип. марка» sütunu ekle (27 = Casement-Double, 40/41 = Fixed) ya da pencereler için Type Mark = ОК tipi şeması.", "WARNING")

sheets = {}

# ---------------------------------------------------------------- АР-1
sheets[1] = dict(
    stem="AR-1_obshchie_dannye", name="Общие данные", wf=False,
    status=[
        ("Ведомость + общие указания, Форма 2, kapı/pencere ведомость, условные обозначения, ТЭП (RF-N1, r2 WARNING)", "CLOSED (kısmen)", "Eklendi ve doğrulandı: ведомость рабочих чертежей АР-1…АР-8 yeni adlarla (Фасад 6-1, 1-6, А-Д, Д-А, Разрез) sayfalarla birebir; Ведомость дверей 35 satır (Д1–Д35) + tip sayıları 10+13+2+8+2 = 35; Ведомость окон 21 satır + 19+1+1 = 21; Ведомость ссылочных и прилагаемых документов (2 dosya). Kalan: Форма 1 tablo biçimi, условные обозначения, ТЭП → STILL OPEN (aşağıda)"),
        ("«Scale» alanı boş (RF-S2, r2 ADVISORY)", "STILL OPEN", "[D]"),
        ("Ledger Rusça, hizalı, şemaya uygun", "NEW", "İngilizce aile adları + hizasız boru-ayraçlı metin; aşağıda"),
    ],
    extra=[
        ("АР-1", "Sol sütun: Ведомость рабочих чертежей / Общие указания / Ведомость ссылочных…", "Set yapısı / RF-N1",
         "Kalan eksikler: «Условные обозначения» (oda etiketi, kapı/pencere etiketi, eksen, kot) yok; ТЭП yok; sayfa listesi düz metin (Лист / Наименование / Примечание sütunları, Форма 1 çerçevesi yok); «Ведомость ссылочных и прилагаемых документов» satırları ham dosya adları («1792566000574-ТЗ_…docx», «…Рендер … (версия 11172).pdf») — Форма 2'de doküman adı/kodu beklenir. Metin sayfa içinde, çakışma/taşma yok.",
         "[D] `revit_create_text_note` ile «Условные обозначения» maddeleri; [A] ссылочные документлер için ad/kod Al'dan; [F] Form 1/2 tablo çerçevesi.", "WARNING"),
        ("АР-1", "Основная надпись, graf 25 «Scale»", "Başlık bloğu / RF-S2",
         "«Scale» alanı hâlâ boş (АР-2…АР-8'de «1 : 100»). Ölçekli görüntü yok → «—» yazılmalı.",
         "[D] sheet Scale parametresini «—» yap.", "ADVISORY"),
        ("АР-1", "Ведомость дверей (x 466–752, y 51–517 mm), Ведомость окон (x 60–336, y 305–601 mm)", "Dil / RF-S6, RF-D3",
         "NEW: ledger satırları İngilizce aile adlarıyla: «M_Door-Passage-Double-Flush: 1800 x 2100mm», «M_Door-Passage-Single-Vision_Lite», «M_Door-Exterior-Single-Two_Lite», «M_Window-Casement-Double», «M_Window-Fixed: EIW 30 1400 x 1800mm»; boyutlarda «mm» eki (RF-D3: birimsiz); seviye «L1/L2». Hem 35 kapı hem 21 pencere satırında ve tip sayıları bölümünde tekrar ediyor.",
         "[D] ledger metnini Rusça tip tanımıyla yeniden yaz (örn. «Дверь двупольная 1800×2100»); [A] Rusça tip adları Al'dan; kalıcı çözüm: aile tipi adlarını yeniden adlandır ([K] köprüde tip-adı aracı yoksa).", "WARNING"),
        ("АР-1", "Ведомость дверей / окон — biçim", "Düzen / R6",
         "NEW: ledger «Марка | Тип | Ширина × высота, мм | Уровень» şeklinde boru ayraçlı düz metin; orantılı fontta sütunlar hizasız (satır sonları 713–752 mm arası oynuyor); canlı schedule değil → modelle senkron kalmaz (R6 riski). Şu anki sayımlar plandaki etiketlerle tutuyor (R6 şimdilik geçti).",
         "[D] gerçek Revit door/window schedule'ı (`revit_create_schedule` varsa) sayfaya koy, Rusça başlıklarla; metin ledger'ı kaldır.", "ADVISORY"),
    ])

# ---------------------------------------------------------------- АР-2
sheets[2] = dict(
    stem="AR-2_plan_1_etazha", name="План 1 этажа", wf=False,
    status=[
        ("Kapı marka = oda no (R5/R6, r2 WARNING)", "CLOSED", "Д1–Д19 hepsi planda, oda numaralarıyla çakışmıyor, ledger L1 = 19 ile tutuyor"),
        ("Kesit başları АР-8, 135/136 ve eksen-3 balonu üstünde (R7, r2 WARNING)", "CLOSED (kısmen)", "Д18/Д19 başın dışına taşındı; eksen 3 balonu temiz. Artık: güney baş oku 117 etiketine/Д19 kapı yayına değiyor, kuzey baş Тамбур 118 dış hattında → ADVISORY"),
        ("Oda yazıları taşıyor (R10/R7, r2 WARNING)", "STILL OPEN", "101, 107, 108, 116–118 temizlendi; kalanı aşağıda"),
        ("«UP» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Ölçü: açıklık/duvar zinciri (RF-D3, r2 ADVISORY)", "STILL OPEN", "[D]"),
        ("Pembe kesikli çizgi, boş işaretçiler", "CLOSED", "(r2'de kapanmıştı; yine yok — vektörde yalnız siyah)"),
        ("Pencere etiketleri = ledger marka", "NEW", "aşağıda"),
    ],
    extra=[
        ROOMS1,
        ("АР-2", "Merdiven okları: batı/doğu dış merdiven, iç merdiven (В–Б)", "Dil / RF-S6",
         "«UP» ×3 İngilizce (değişmedi).", "[K] merdiven tipi metni — köprüden düzenlenemez; Al'a not («ВВЕРХ»).", "WARNING"),
        WINTAG(2, "27", "40"),
        ("АР-2", "Kesit başları «АР-8»: kuzey (Тамбур 118 üstü) ve güney (Тамбур 117 / Д19 yayı)", "Düzen / R7",
         "Д18/Д19 etiketleri ve eksen-3 balonu artık temiz. Artık: güney baş okunun ucu 117 numara kutusuna ve Д19 kapı yayına değiyor; kuzey baş dairesi Тамбур 118 çıkıntı hattının üstünde.",
         "[D] kesit başlarını 20–30 mm dışarı (veranda hattının ötesine) çek.", "ADVISORY"),
        ("АР-2", "Plan alanı, eksen 1–6 / А–Д", "Boyutlandırma / RF-D3",
         "Zincirler tamam (25000, 16000) ama duvar kalınlığı, kapı/pencere açıklıkları ölçülü değil.",
         "[D] `revit_create_dimension` ile dış duvar açıklık zinciri (mm, birimsiz).", "ADVISORY"),
    ])

# ---------------------------------------------------------------- АР-3
sheets[3] = dict(
    stem="AR-3_plan_2_etazha", name="План 2 этажа", wf=False,
    status=[
        ("Pembe kesikli «WF - L1 base check» (R7, r2 WARNING)", "CLOSED", "bu planda pembe/kırmızı vektör yok (yalnız siyah)"),
        ("Oda yazıları taşıyor (R10/R7)", "STILL OPEN", "202–204, 206, 214, 215 temiz; kalanı aşağıda"),
        ("«DN» ×3 (RF-S6)", "STILL OPEN", "[K]"),
        ("Kuzey oku + ölçek çubuğu yok (R11)", "STILL OPEN", "[D]"),
        ("Kapı etiketleri Д20–Д35", "CLOSED (doğrulandı)", "16 etiket, ledger L2 = 16 ile tutuyor; kesit başları (АР-8) hiçbir etikete değmiyor"),
        ("Pencere etiketleri = ledger marka", "NEW", "aşağıda"),
    ],
    extra=[
        ROOMS2,
        ("АР-3", "Merdiven okları «DN» ×3", "Dil / RF-S6", "«DN» İngilizce.", "[K] merdiven tipi metni.", "WARNING"),
        ("АР-3", "Sayfa genel — plan görünümü", "Semboller / R11",
         "Kuzey oku ve ölçek çubuğu YOK (АР-2'de var). Vektör/metinde «N» ve çubuk yok.", "[D] АР-2'deki ölçek çubuğu + kuzey oku detay bileşenlerini bu görünüme ekle.", "WARNING"),
        WINTAG(3, "27", "41"),
    ])

# ---------------------------------------------------------------- facades
def facade(n):
    return [
        (f"АР-{n}", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, zemin/çatı kotu işareti yok. АР-1 notu +2,100 ve +8,100'ü beyan ediyor; fasaddaki iki başlıksız tireli-noktalı çizgi bu seviyeler — kot işareti yok. Eksen zinciri var, toplam (25000/16000) yok.",
         "[D] seviye adlarını Rusça yap («Этаж 1» …); çatı/sahanlık/zemin için kot işareti ekle (spot elevation, «+8,100» biçimi; yoksa [K] level head biçimi, Al).", "WARNING"),
        (f"АР-{n}", "Tüm cephe — silüet, zemin", "Çizgi / RF-L1",
         "Çizgiler yalnız 0,10/0,15/0,25 mm (0,7 mm = ölçü işaretleri); dış kontur ve zemin çizgisi belirgin kalın değil.",
         "[K] object style / view template — köprüden düzenlenemez; Al/Revit elle.", "WARNING"),
        (f"АР-{n}", "Cephe: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5",
         "Kotsuz iki ek seviye çizgisi (sahanlık ve çatı).", "[D] başlık ekle ya da bu görünümde gizle.", "ADVISORY"),
    ]


def fstatus(extra):
    return [
        ("Sayfa/görünüm adı (r2 yönlendirme: «Северный фасад» vb.)", "CLOSED", extra),
        ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"),
        ("Çizgi kalınlıkları (RF-L1)", "STILL OPEN", "[K]"),
        ("Başlıksız seviye çizgileri", "STILL OPEN", "[D]"),
    ]


sheets[4] = dict(stem="AR-4_fasad_6-1", name="Фасад 6-1", wf=False,
                 status=fstatus("«Фасад 6-1»: eksenler soldan sağa 6→1 (kuzeyden bakış, planın АР-4 oku ile uyumlu); damga ve görünüm başlığı aynı; kutudan taşmıyor"), extra=facade(4))
sheets[5] = dict(stem="AR-5_fasad_1-6", name="Фасад 1-6", wf=False,
                 status=fstatus("«Фасад 1-6»: 1→6 soldan sağa (güneyden bakış) — doğru"), extra=facade(5))
sheets[6] = dict(stem="AR-6_fasad_A-D", name="Фасад А-Д", wf=False,
                 status=fstatus("«Фасад А-Д»: А→Д soldan sağa (doğudan bakış) — doğru; r2'deki 4 mm çerçeve aşımı bitti") +
                 [("Pembe dikey kesit işaretçisi (r2 ADVISORY)", "CLOSED", "pembe vektör yok")], extra=facade(6))
sheets[7] = dict(stem="AR-7_fasad_D-A", name="Фасад Д-А", wf=False,
                 status=fstatus("«Фасад Д-А»: Д→А soldan sağa (batıdan bakış) — doğru") +
                 [("Pembe dikey kesit işaretçisi (r2 ADVISORY)", "CLOSED", "pembe vektör yok")], extra=facade(7))

# ---------------------------------------------------------------- АР-8
sheets[8] = dict(stem="AR-8_razrez", name="Разрез", wf=True,
    status=[
        ("Eksen-arası zincir (RF-D3)", "CLOSED", "Д→А 5000+3000+3500+4500 = 16000 kapalı (r2'de kapanmıştı)"),
        ("Kat/toplam yükseklik ölçüsü yok (RF-D3, r2 WARNING)", "CLOSED", "2100 + 2100 + 3900 ve toplam 8100: okuma doğru (2100+2100 = 4200 = L2, 4200+3900 = 8100, tick'ler ±0,00 / +2100 / +4200 / +8100 çizgilerinde); seviye başlıklarının üstüne basmıyor"),
        ("Kot başlığı/RF-D2", "STILL OPEN", "[D]/[K]"),
        ("SSL/FFL (WF4)", "STILL OPEN", "[D]"),
        ("Tarama yok (WF2)", "STILL OPEN", "[K]"),
        ("Başlıksız seviye çizgileri", "STILL OPEN (kısmen: ölçü uçları +2100/+8100'ü tanımlıyor, başlık/kot yok)", "[D]"),
        ("Katman liderleri/legend (WF3/WF10)", "STILL OPEN", "[A]"),
        ("Görünüm başlığı yönü", "NEW", "aşağıda"),
    ],
    extra=[
        ("АР-8", "Seviye başlıkları sağda «L1 0», «L2 4200»", "Kotlar / RF-D2, RF-S6",
         "Değişmedi: mm tam sayı, İngilizce L1/L2, çatı üst kotu (+8,100) için kot işareti yok (yalnız ölçü).", "[D]/[K] АР-4 ile aynı.", "WARNING"),
        ("АР-8", "Kesit: SSL / FFL", "Seviyeler / WF4", "Kaba döşeme (SSL) ve bitmiş zemin (FFL) ayrı gösterilmiyor.",
         "[D] spot elevation ile FFL/SSL (ofset Revit_WallFloor ile doğrulanır).", "WARNING"),
        ("АР-8", "Kesit: kesilen döşeme, kolon, duvar, çatı levhası", "Malzeme tarama / WF2",
         "Kesilen elemanlar hâlâ beyaz, tarama yok (kesit çizgisi 0,5–0,7 mm: WF1 tamam).", "[K] kesit kalıbı/malzeme yüzey deseni (Al ile).", "WARNING"),
        ("АР-8", "Kesit: iki başlıksız seviye çizgisi (≈+2,1 ve ≈+8,1)", "Kotlar / R5", "Başlıksız (yalnız ölçü zinciri uçları).", "[D] başlık ekle/gizle.", "ADVISORY"),
        ("АР-8", "Kesit: katman notu, legend", "WF3 / WF10", "1:100'de katman liderleri ve malzeme legend'i yok.", "[A] detay kesit gerekirse Al ile.", "ADVISORY"),
        ("АР-8", "Görünüm başlığı «Разрез А–Д» (x 169–212, y 709–719 mm)", "Düzen / RF-D1, R5",
         "NEW (ya da r2'de raporlanmamış): başlık «А–Д» (en-dash), çizimde ise Д solda, А sağda (planda başlar doğuya bakıyor); fasad adlandırması soldan-sağa sırayı kullanıyor («Фасад Д-А»). Tire biçimi de fasaddan farklı (– / -).",
         "[D] görünüm adını «Разрез Д-А» (kısa tire) yap, ya da adlandırma kuralını АР-1 notuna yaz.", "ADVISORY"),
        ("АР-8", "Düşey ölçü zinciri, «8100» metni (x 416–421, y 612–623 mm)", "Boyutlandırma / R9",
         "NEW: toplam ölçü metni 8100, 3900/2100 zincirinin tick'ine ve L2 seviye çizgisi saplamasına bitişik (≈3 mm), L2 başlık yazısına 3 mm; okunuyor ama sıkışık.",
         "[D] toplam ölçü zincirini 10–15 mm daha dışarı kaydır (ofset).", "ADVISORY"),
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


HIST = {1: "— (yeni, r2: 14)", 2: "r1 −40 → r2 −10", 3: "r1 −26 → r2 −8", 4: "r1 −2 → r2 6",
        5: "r1 −2 → r2 6", 6: "r1 4 → r2 4", 7: "r1 4 → r2 4", 8: "r1 −12 → r2 −12"}


def main():
    summary = []
    for n, d in sheets.items():
        rows = common(n) + d["extra"]
        raw, sc, band = score(rows)
        summary.append((n, d["name"], raw, sc, band))
        st = d["status"] + common_status()
        out = os.path.join(ROOT, d["stem"])
        os.makedirs(out, exist_ok=True)
        L = ["# Prodim Revit Sheet Quality Control — round 3", "",
             f"**Date:** {DATE}",
             f"**Basis applied:** {BASIS}" + (WF if d["wf"] else ""),
             f"**Sources:** {d['stem']}.pdf", "",
             "## Reviewed sheets", "", "| Sheet | Score | Status |", "|---|---|---|",
             f"| АР-{n} — {d['name']} | {sc} (ham {raw}; {HIST[n]}) | {band} |", "",
             "## Round-2 row → status", "", "| Round-2 row | Status | Not |", "|---|---|---|"]
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
