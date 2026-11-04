---
name: Al's wall / floor / ceiling drawing conventions
description: Al's own two texts (sent 2026-10-30) on line weights, material hatches, levels, build-up notation and how floor slab, floor finish and ceiling are shown in sections (1:5–1:100), the floor finish plan and the reflected ceiling plan (RCP). Used by wall-floor-code-check §3d (build-up, FFL/FCL) and, for the graphics, by Revit_Drafter / Revit_Sheet. Footnote markers of the source were removed; wording otherwise as sent.
---

# Duvar, döşeme, kaplama ve tavan gösterimi (Al, 2026-10-30)

İki metin; ikincisi §5–§9. Al kaynak belge adı vermedi (köşeli parantezli dipnot numaraları çıkarıldı).

Mimari ve iç mimari projelerde döşeme (floor slab), kaplama (floor finish) ve
tavan (ceiling) gösterimleri iki temel görünüş düzleminde ifade edilir:
kesit çizimleri (1:5, 1:10, 1:20 detay kesitleri ile 1:50, 1:100 genel
kesitler) ve plan çizimleri (Zemin Kaplama Planı ile Yansıtılmış Tavan Planı
/ RCP).

## 1. Kesit ve detay çizimlerinde katman sıralaması (yukarıdan aşağıya)

| Katman | Gösterim | Kalınlık / not |
|---|---|---|
| A. Zemin kaplaması (floor finish) | İnce/orta çizgi 0.25–0.35 mm. Tarama: seramik/karo grid; ahşap parke çift çizgi/kesit taraması; halı/PVC ince nokta veya boşluk | Tür + kalınlık yazılır (örn. 15 mm lamine parke, 10 mm porselen seramik) |
| B. Yapıştırıcı / harç | İnce nokta/lekeleme taraması | 3–5 mm |
| C. Tesviye şapı (screed) | Çok ince nokta taraması | genellikle 30–50 mm |
| D. Isı / ses / su yalıtımı (insulation, DPC) | Isı/ses: zikzak veya dalgalı çizgi; nem/su (DPC/membran): koyu kalın bant veya özel kesikli çizgi | — |
| E. Taşıyıcı döşeme plağı (structural slab) | Kesitte kesildiği için en kalın çizgi 0.50–0.70 mm veya donatılı beton taraması (nokta + küçük üçgen) | Tür + kalınlık yazılır (örn. 150 mm betonarme plak, kaset döşeme) |
| F. Tavan | Doğrudan sıvalı tavan: plak alt yüzüne ince sıva. Asma tavan: plenum boşluğu, askı çubukları, ana/ara profiller, kaplama plakları (alçıpan, taşyünü karo, lineer metal) ölçekli | — |

## 2. Zemin kaplama planı

1. Plan, bitmiş zemine yukarıdan bakış (1.00 m kotundan kesip aşağı bakış).
2. Duvarlar ve taşıyıcılar kesitte → kalın çizgi.
3. Seramik/mermer/karo: başlangıç derz noktası (starter tile) belirtilir, derz eksenleri ince çizgi.
4. Malzeme geçişleri: eşik profilleri, genleşme/dilatasyon derzleri gösterilir.
5. Bitmiş zemin kotu `FFL +2.750` veya daire içinde nokta işaretiyle oda ortasında.
6. Mahal etiketi: ad, alan (m²), zemin kaplama kodu (örn. K01 epoksi, K02 lamine parke), pafta lejantına referanslı.

## 3. Yansıtılmış tavan planı (RCP)

Yere konmuş aynadan tavana bakış — oryantasyon taban planıyla birebir çakışır.

1. Modüler asma tavan (60×60, 60×120): profil aksları ince çizgi; alçıpan tavan: tavan sınırları, kaset/ışıklık detayları.
2. Tavan kotu bitmiş zemine göre net: `FCL = +2.60 m` veya tavan yüksekliği 260 cm.
3. Entegrasyon: aydınlatma (gömme/sıva üstü, LED hat, spot); HVAC üfleme/emme anemostad ve menfezler; sprinkler, duman dedektörü, acil anons hoparlörü; müdahale kapakları kesikli/ince çizgiyle.

## 4. Ölçülendirme ve notasyon

- Lider çizgileri: detay kesitlerinde katmanlar dikey hizada rehber oklarla sırayla listelenir.
- Planda bitmiş kot `FFL +0.000`; kesitte kaba ve bitmiş kotlar dikey hizalı oklarla (örn. kaba döşeme `+2.690`, bitmiş döşeme `+2.750`).

## 5. Çizgi kalınlıkları ve tipleri (ikinci metin)

- Kesit çizgileri (kalın düz): kesilen taşıyıcı duvarlar, betonarme perde/kolon, döşeme plakları — ölçeğe göre 0.50–1.00 mm.
- Görünüş çizgileri (orta düz): kesite girmeyip arkada görünen duvar sınırları, parapetler, döşeme kenarları — 0.35–0.50 mm.
- Aks çizgileri noktalı kesikli 0.25–0.35 mm; ölçü ve bağlama çizgileri ince düz 0.25 mm.
- Gizli / üst kot elemanları (kesikli): döşeme altındaki kirişler, lento sınırları, üst kottaki döşeme boşlukları, asma tavan hatları.

## 6. Malzeme taramaları

- Tuğla/kagir: 45° eğik tek veya çift paralel çizgi. Beton/betonarme: ince nokta + küçük üçgen; donatılı betonda ilave çapraz hat veya koyu dolgu. Isı yalıtımı (taş yünü, EPS/XPS): dalgalı/zikzak. Sıva/harç: çok ince noktalı lekeleme.
- Döşeme kesitinde DPC koyu bant/membran çizgisi, şap ince nokta, ısı/ses yalıtımı zikzak, betonarme plak donatılı beton sembolü — katman katman.
- Planda kaplamalar ölçekli: seramik grid, ahşap parke balıksırtı/sepet, doğal taş.

## 7. Kotlandırma ve ölçülendirme

- Planda: FFL kısaltması veya ±0.000'a göre `x` işaretli nokta (örn. `FFL 12.335`, `+2.750`).
- Kesit/görünüşte: çizim dışına uzatılan projeksiyon çizgisi üzerinde dolu/boş ok (kaba `+2.690`, bitmiş `+2.750`).
- Modüler ölçülendirme: duvar kalınlıkları, kapı-pencere açıklıkları, döşeme kalınlıkları 100 / 300 mm modüllerine uygun, içten dışa zincir ölçü.

## 8. Kesit detayı katman notasyonu (1:10, 1:20, 1:50)

- Hizalı rehber çizgileriyle uygulama sırasına göre, dıştan içe veya üstten alta.
- Zemin: kaplama (seramik/parke) → yapıştırıcı → tesviye şapı → su/ısı yalıtım membranı → betonarme plak → tavan sıvası / asma tavan.
- Duvar: dış cephe kaplaması / dış sıva → ısı yalıtımı → duvar gövdesi (tuğla/gazbeton/briket) → iç sıva → iç yüzey boya/kaplama.

## 9. Pafta düzeni

- Referans akslar baloncuk içinde harf ve rakamla.
- Ölçek, kuzey oku, detay işaretçileri ve kesit yönü sembolleri CSI UDS / NCS kurallarına göre pafta kancası ve başlık alanına (HR notu: yalnız US NCS ailesi seçilen işlerde; TS EN ISO 128 varsayılanında ISO 5457/7200/7519 — `revit-sheet-audit/references/wall-floor-ceiling-graphics.md`).

## 10. Üçüncü metin (Al, 2026-10-30) — döşeme-kaplama, alçıpan bölme duvar ve asma tavan

Al'in andığı çerçeve: CSI UDS / NCS, ISO 128 / ISO 7519, BS EN 13964 (asma tavanlar), IBC Chapter 25 / ASTM C840 (alçıpan sistemleri). Köşeli parantezli kaynak numaraları çıkarıldı; kaynak listesi verilmedi.

**Döşeme / kaplama — çizgi hiyerarşisi**
- Kesit çizgisi 0.50–0.70 mm: kesilen betonarme döşeme plağı ve kaba yapı.
- Orta çizgi 0.25–0.35 mm: tesviye şapı, yalıtım membranları, süpürgelik hatları, arkada görünen döşeme sınırları.
- İnce çizgi 0.13–0.18 mm: seramik, mermer, ahşap kaplama derzleri (plan).

**Taramalar**: taşıyıcı döşeme donatılı beton sembolü (ince nokta + küçük üçgen) veya koyu dolu dolgu; şap ince noktalı lekeleme; ısı/ses yalıtımı dalgalı/zikzak; kaplama: karo/seramik ölçekli grid, ahşap parke balıksırtı / sepet / düz plank, doğal taş/mermer plaka boyutunda derz ağı.

**Kot ve imalat notasyonu**: FFL (bitmiş zemin, `FFL +3.500`, `FFL 12.335`, oda ortasında veya kot noktalarında); **SSL** (Structural Slab Level — taşıyıcı kaba betonarme üst kotu); başlangıç karosu (serim yönü ve derz aksı); katman listesi dikey rehber çizgide dıştan içe / üstten alta — örnek: 10 mm porselen seramik → yapıştırıcı → 40 mm tesviye şapı → su yalıtımı → 150 mm betonarme döşeme.

**Alçıpan bölme duvar**
- Plan: duvar sınırları çift çizgi; içinde C ve U galvaniz profillerin (C-stud, U-runner) aksları ve etiketleri.
- Kesit/detay: alçıpan levha katmanları ölçekli dikey çizgilerle (12.5 mm standart, 15 mm veya yangına dayanıklı Type X); profil içindeki taşyünü/camyünü dolgusu dalgalı hatla.
- Duvar tipi kodlaması: planda lejant referanslı (örn. `W1` tek kat alçıpanlı duvar, `W2` çift kat Type X akustik duvar).

**Asma tavan (EN 13964 / RCP)**
- RCP: yere konan aynadan yukarı bakış; tavan paftası taban planıyla birebir çakışır.
- FCL bitmiş zemine göre (`FCL = +2.60 m`).
- Monolitik alçıpan tavan: derzsiz tek yüzey; karkas (T-24, C-kanal, askı çubukları) detay kesitinde ölçekli. Modüler tavan (60×60 / 60×120): görünür veya gizli taşıyıcılı T-grid planda ince hatla.
- Entegrasyon: aydınlatma (spot, LED bant, armatür), HVAC anemostad/menfez, sprinkler, duman dedektörü, müdahale kapakları kesikli/ince çizgiyle.

**Pafta düzeni (CSI UDS / NCS)**: `A-101` zemin kat planı, `A-102` RCP, `A-103` zemin kaplama planı, `A-501` sistem ve detay kesitleri; tüm taramalar, çizgi tipleri, duvar/döşeme tipleri pafta kenarındaki lejantta (keynotes & symbols) tanımlı.
