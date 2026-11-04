# Revit ajanları (Claude Code)

Revit 2025 açık dokümanında çalışan Claude Code ajanları ve kullandıkları
kural setleri (skill'ler). Revit ile [RevitMCPServer](https://github.com/KenLP/RevitMCPServer)
eklentisi üzerinden konuşurlar.

## Ajanlar (`.claude/agents/`)

| Ajan | Ne yapar |
|---|---|
| **Revit_Guide** | İlk kez kullanan biri için giriş kapısı; "5 metrelik duvar çiz" gibi düz cümleleri `revit_*` çağrılarına çevirir, işi aşağıdaki uzman ajanlara devreder. |
| **Revit_WallFloor** | Duvar ve döşeme çizer/düzeltir/denetler (çakışan duvarlar, açık birleşimler, seviyeye bağlı olmayan üstler…). |
| **Revit_DoorWindow** | Kapı/pencere yerleştirir, taşır, denetler (duvar içinde mi, çakışma, denizlik, açılış yönü). |
| **Revit_Stair** | Merdiven hesaplar ve kurar (rıht/basamak, sahanlık, korkuluk), yönetmeliğe göre denetler. |
| **Revit_Roof** | Gerçek FootPrintRoof çatı kurar (kırma/beşik/tek eğimli/düz, saçak), denetler. |
| **Revit_Drafter** | Pafta kurar, görünüş yerleştirir, PDF'e verir, Revit_Sheet'e denetletir, puan > 90 olana kadar düzeltir. |
| **Revit_Sheet** | Pafta PDF'lerini grafik açıdan denetler (ISO 128 / ГОСТ-СПДС …), rapor yazar. Revit'e dokunmaz. |
| **Revit_Dynamo** | Dynamo 3.3 `.dyn` grafikleri ve Python node'ları yazar/düzeltir; kullanıcı çalıştırır, sonucu okur. |

Her ajanın klasöründe `scripts/` (hesap script'leri) ve `Memory/lessons.md`
(öğrenilmiş kurallar) var. `Memory/activity_log.md` herkesin kendi
makinesinde tutulur, repoya girmez.

Skill'ler (`.claude/skills/`): `work-discipline`, `revit-sheet-audit`,
`dynamo-revit-authoring`, `wall-floor-code-check`, `door-window-code-check`,
`stair-code-check`, `roof-code-check`.

## Kurulum (bir kez)

Gerekenler: Windows, Revit 2025, [Claude Code](https://claude.com/claude-code),
Git, Node.js, .NET SDK 10, Python 3.

1. Bu repoyu bir çalışma klasörüne klonla:

   ```bash
   git clone https://github.com/Yagmur-data/revit-agents.git "Claude Projects"
   ```

2. Ajanların ihtiyaç duyduğu araçlar (`create_stair` çok kollu, `create_roof`
   düzeltmesi, `create_railing`, `set_wall_type_layers` …) RevitMCPServer'ın
   **fork'unda** duruyor. Aynı klasörün içine klonla:

   ```bash
   git clone -b revit-agents https://github.com/Yagmur-data/RevitMCPServer.git "Claude Projects/RevitMCPServer"
   ```

3. Eklentiyi ve MCP sunucusunu derle (**Revit kapalıyken** — derleme eklentiyi
   `%APPDATA%\Autodesk\Revit\Addins\2025` içine kopyalar):

   ```bash
   dotnet build "Claude Projects/RevitMCPServer/src/RevitAddin/RevitMCPAddin.csproj" -c Release -p:RevitVersion=2025
   ```

   ```bash
   cd "Claude Projects/RevitMCPServer/src/McpServer" && npm install && npm run build
   ```

   `-p:RevitVersion=2025` şart; varsayılanı 2026'dır. Fork, Revit 2025 için
   .NET 10 hedefler (Revit **2025.5** ve sonrası); daha eski bir 2025
   güncellemesinde derleme/yükleme başarısız olur — önce Revit'i güncelle.

4. `.mcp.example.json` dosyasını `.mcp.json` adıyla kopyala ve içindeki yolu
   kendi `RevitMCPServer\src\McpServer\dist\index.js` yolunla değiştir.

5. Revit 2025'i aç (tek bir Revit), bir proje aç, Claude Code'u bu klasörde
   başlat ve yaz: *"Revit_Guide ile başlayalım"*.

## Güncellemeleri almak

```bash
git -C "Claude Projects" pull
```

```bash
git -C "Claude Projects/RevitMCPServer" pull
```

RevitMCPServer'da değişiklik geldiyse 3. adımdaki derlemeyi (Revit kapalıyken)
tekrar çalıştır. Kendi makinende bir ajanın `lessons.md` dosyası değiştiyse
`pull` birleştirme isteyebilir; değişikliğini saklamak istemiyorsan önce
`git -C "Claude Projects" checkout -- .claude` ile geri al.

## Bilinen tuzaklar

[docs/revit-mcp-traps.md](docs/revit-mcp-traps.md) — ör. "unauthorized"
hatası çoğu zaman iki Revit'in aynı anda açık olmasındandır.
