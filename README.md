# FEEBLE -- Web Güvenlik Açığı Tarayıcı

```
  _____ _____ _____ ____  _     _____
 |  ___| ____| ____| __ )| |   | ____|
 | |_  |  _| |  _| |  _ \| |   |  _|  
 |  _| | |___| |___| |_) | |___| |___ 
 |_|   |_____|_____|____/|_____|_____|
```

Python ile geliştirilmiş modüler bir web güvenlik açığı tarayıcı. SQL Injection, XSS, LFI, Open Redirect, CSRF ve eksik güvenlik başlıkları gibi yaygın güvenlik açıklarını tespit eder. Kali Linux ve Windows ile uyumludur.

[English README (İngilizce Dokümantasyon)](README_EN.md)

---

## Özellikler

| Özellik | Açıklama |
|---|---|
| **SQL Injection** | Error-based, Boolean-based, Time-based blind SQLi tespiti |
| **XSS** | Reflected ve DOM-based XSS açıklarının tespiti |
| **LFI** | Local File Inclusion ve Path Traversal tespiti |
| **Open Redirect** | Yönlendirme açıklarının tespiti |
| **CSRF** | CSRF token eksikliği tespiti |
| **Başlık Güvenliği** | Eksik HTTP güvenlik başlıklarının kontrolü |
| **Sürüngen (Crawler)** | Otomatik sayfa ve form keşfi |
| **Raporlama** | HTML, JSON ve konsol formatında raporlar |
| **Paralel Tarama** | ThreadPool ile eşzamanlı modül çalıştırma |
| **Proxy Desteği** | Burp Suite / OWASP ZAP ile entegrasyon |

---

## Kurulum

### Kali Linux (Önerilen)

```bash
git clone https://github.com/erensogutlu/feeble.git
cd feeble
pip3 install -r requirements.txt
```

### Windows

```bash
pip install -r requirements.txt
```

### Geliştirme Modu (Opsiyonel)

```bash
pip install -e .
```

### Python Sürüm Uyumluluğu

| Python Sürümü | Durum |
|---|---|
| Python 3.8 | Desteklenir |
| Python 3.9 | Desteklenir |
| Python 3.10 | Desteklenir |
| Python 3.11 | Desteklenir |
| Python 3.12+ | Desteklenir |

---

## Kullanım -- Adım Adım Rehber

Feeble'ı kullanmadan önce bilmeniz gereken **2 temel bilgi** vardır:

1. **Hedef URL** - Taramak istediğiniz web sitesinin adresi (örnek: `https://hedef.com`)
2. **Tarama Modu** - Tüm modülleri mi çalıştırmak istiyorsunuz, yoksa sadece belirli olanları mı?

> **IP/URL'yi bilmiyorsanız?** Taramak istediğiniz sitenin adresini tarayıcınızın adres çubuğundan kopyalayın. `https://` ile başladığından emin olun.

---

### 1. Kullanılabilir Modülleri Listeleme

**Ne yapar?** Feeble'da hangi tarama modüllerinin mevcut olduğunu gösterir. İlk kullanımı öncesinde hangi modüllerin bulunduğunu öğrenmek için çalıştırın.

```bash
python ana.py -u https://hedef.com --modul-listesi
```

**Örnek çıktı:**
```
[*] Kullanılabilir modüller:
  sql             -- SQL Injection (Error/Boolean/Time-based)
  xss             -- Cross-Site Scripting (Reflected/Stored)
  lfi             -- Local File Inclusion / Path Traversal
  yonlendirme     -- Open Redirect
  csrf            -- CSRF Token Eksikliği
  baslik          -- HTTP Güvenlik Başlıkları
```

---

### 2. Tam Tarama (Tüm Modüller)

**Ne yapar?** Hedef siteyi **tüm modüllerle** tarar. Önce sürüngen (crawler) ile sayfalarını gezer, formları ve parametreli URL'leri keşfeder; ardından her birini tüm modüllerle test eder.

**Ne zaman kullanılır?** Bir siteyi ilk kez tarıyorsanız veya kapsamlı bir güvenlik değerlendirmesi yapmak istiyorsanız.

```bash
python ana.py -u https://hedef.com --tam-tarama
```

**Parçalara ayırarak açıklayalım:**

| Parametre | Ne yazılır | Anlamı |
|---|---|---|
| `-u` | `https://hedef.com` | Taranacak web sitesinin URL'si |
| `--tam-tarama` | (parametre yok) | Tüm modülleri çalıştır |

**Araç çalışırken ne olur?**
1. Banner ve yapılandırma bilgisi gösterilir.
2. Sürüngen sayfaları gezer, bağlantıları ve formları keşfeder.
3. Her modül sırayla (veya paralel) çalıştırılır.
4. Bulunan açıklar renkli olarak konsola yazdırılır.
5. Tarama tamamlanınca özet rapor gösterilir.
6. **Ctrl+C** tuşlarsanız tarama durdurulur.

**Örnek bulgu çıktısı:**
```
[+] SQL injection bulundu (error-based): https://hedef.com/sayfa?id=1
[+] Reflected XSS bulundu: https://hedef.com/ara?q=test
[*] Eksik güvenlik başlıkları: X-Frame-Options, Content-Security-Policy
```

---

### 3. Belirli Modüllerle Tarama

**Ne yapar?** Sadece seçtiğiniz modülleri çalıştırır. Örneğin sadece SQL Injection ve XSS taramasi yapabilirsiniz.

**Ne zaman kullanılır?** Belirli bir açık türünü aramak istediğinizde veya tarama süresini kısaltmak için.

```bash
python ana.py -u https://hedef.com -m sql,xss
```

**Açıklama:**
- `-m sql,xss` - Virgüllerle ayırarak istediğiniz modülleri seçin.
- Kullanılabilir modül isimleri: `sql`, `xss`, `lfi`, `yonlendirme`, `csrf`, `baslik`

**Daha fazla örnek:**
```bash
# Sadece SQL Injection
python ana.py -u https://hedef.com -m sql

# Sadece güvenlik başlıkları kontrolü
python ana.py -u https://hedef.com -m baslik

# LFI ve Open Redirect
python ana.py -u https://hedef.com -m lfi,yonlendirme
```

---

### 4. Rapor Çıktısı (JSON ve HTML)

**Ne yapar?** Tarama sonuçlarını farklı formatlarda kaydeder. Varsayılan olarak sonuçlar konsola yazdırılır; ancak JSON veya HTML formatında dosyaya kaydedebilirsiniz.

**a) JSON rapor (makine tarafından okunabilir):**
```bash
python ana.py -u https://hedef.com --tam-tarama -c json -d rapor.json
```

**b) HTML rapor (tarayıcıda görüntüleyebilir):**
```bash
python ana.py -u https://hedef.com --tam-tarama -c html -d rapor.html
```

**c) JSON çıktısını konsola yazdırma (dosyaya kaydetmeden):**
```bash
python ana.py -u https://hedef.com --tam-tarama -c json
```

> HTML rapor, siyah tema ile şık bir tasarıma sahiptir ve doğrudan tarayıcıda açılabilir.

---

### 5. Proxy ile Tarama (Burp Suite / ZAP)

**Ne yapar?** Tüm istekleri bir proxy üzerinden yönlendirir. Burp Suite veya OWASP ZAP gibi araçlarla birlikte kullanmak için idealdir.

**Ne zaman kullanılır?** İstekleri proxy aracında incelemek veya kaydetmek istediğinizde.

```bash
python ana.py -u https://hedef.com --tam-tarama --proxy http://127.0.0.1:8080
```

> Burp Suite varsayılan olarak `127.0.0.1:8080` portunda çalışır.

---

### 6. Cookie ile Oturum Desteği

**Ne yapar?** Giriş yapılmış sayfalar için çerez ekleyerek oturum desteği sağlar. Giriş gerektiren sayfaların arkasındaki açıkları bulmak için kullanılır.

**Ne zaman kullanılır?** Hedef sitenin taranmasını istediğiniz bölümleri giriş gerektiriyorsa.

```bash
python ana.py -u https://hedef.com --tam-tarama --cerez "PHPSESSID=abc123; token=xyz789"
```

**Çerez nasıl bulunur?**
1. Tarayıcıda hedef siteye giriş yapın.
2. **F12** ile Geliştirici Araçları'nı açın.
3. **Application/Storage > Cookies** bölümünden çerez adını ve değerini kopyalayın.
4. `--cerez "isim=deger"` şeklinde komuta ekleyin.

---

### 7. Sürüngen Ayarları

Sürügenin davranışını özelleştirmek için:

**a) Derinlik sınırı ayarlama (varsayılan: 3):**
```bash
python ana.py -u https://hedef.com --tam-tarama --derinlik 5
```

**b) Maksimum sayfa sayısı (varsayılan: 100):**
```bash
python ana.py -u https://hedef.com --tam-tarama --maks-sayfa 200
```

**c) Sürüngeni devre dışı bırakma (sadece hedef URL taranır):**
```bash
python ana.py -u https://hedef.com --tam-tarama --surungan-yok
```

> Sürüngen devre dışı bırakılırsa sadece girilen URL taranır, alt sayfalar gezilmez.

---

### 8. Yardım Menüsü

Tüm parametreleri ve kısa açıklamalarını görmek için:

```bash
python ana.py -h
```

---

## Hızlı Başlangıç -- Sıfırdan Tarama Senaryosu

Hiç bilmiyorsanız, bu adımları sırayla takip edin:

```bash
# Adım 1: Kullanılabilir modülleri görün
python ana.py -u https://hedef.com --modul-listesi

# Adım 2: Hedef siteyi tam tarayın
python ana.py -u https://hedef.com --tam-tarama

# Adım 3: Sonuçları HTML rapor olarak kaydedin
python ana.py -u https://hedef.com --tam-tarama -c html -d rapor.html

# Adım 4: Raporu tarayıcıda açın ve inceleyin
```

---

## Tüm Parametreler (Referans Tablosu)

| Parametre | Kısa Hali | Zorunlu mu? | Açıklama |
|---|---|---|---|
| `--url` | `-u` | Evet | Taranacak hedef URL |
| `--tam-tarama` | -- | Hayır | Tüm modüllerle tam tarama |
| `--moduller` | `-m` | Hayır | Kullanılacak modüller (virgüllü: sql,xss,lfi) |
| `--cikti` | `-c` | Hayır | Rapor formatı: konsol, json, html |
| `--dosya` | `-d` | Hayır | Rapor çıktı dosyası yolu |
| `--derinlik` | -- | Hayır | Sürüngen maks derinlik (varsayılan: 3) |
| `--maks-sayfa` | -- | Hayır | Sürüngen maks sayfa (varsayılan: 100) |
| `--surungan-yok` | -- | Hayır | Sürüngeni devre dışı bırak |
| `--proxy` | -- | Hayır | Proxy adresi (örn: http://127.0.0.1:8080) |
| `--cerez` | -- | Hayır | Çerez dizgisi (örn: "PHPSESSID=abc123") |
| `--thread` | `-t` | Hayır | Eşzamanlı thread sayısı (varsayılan: 5) |
| `--gecikme` | -- | Hayır | İstekler arası gecikme (saniye) |
| `--cerez-b` | -- | Hayır | İkinci kullanıcı çerezi (BOLA / IDOR testi için) |
| `--waf-bypass` | -- | Hayır | Adaptif WAF mutasyon motorunu aktif et |
| `--js-surungan` | -- | Hayır | Headless JavaScript & SPA tarama katmanını aktif et |
| `--sablonlar` | -- | Hayır | YAML zafiyet şablon dosyası veya dizini |
| `--modul-listesi` | -- | Hayır | Kullanılabilir modülleri listele |
| `--help` | `-h` | Hayır | Yardım mesajını göster |

---

## Proje Yapısı

```
feeble/
├── ana.py                     <- CLI giriş noktası
├── tarayici.py                <- Ana tarayıcı motoru
├── surungan.py                <- Web sürüngen (crawler)
├── istek.py                   <- HTTP istek yardımcıları
├── rapor.py                   <- Rapor üretici (HTML/JSON/Konsol)
├── yapilandirma.py            <- Yapılandırma sabitleri
├── yardimci.py                <- Yardımcı fonksiyonlar
├── __init__.py                <- Paket tanımı
├── __main__.py                <- python -m feeble desteği
├── setup.py                   <- Paket kurulumu
├── requirements.txt           <- Bağımlılıklar
├── test_feeble.py             <- Test scripti
├── moduller/
│   ├── __init__.py            <- Modül kayıt mekanizması
│   ├── temel_modul.py         <- Soyut temel sınıf
│   ├── sql_enjeksiyon.py      <- SQL Injection tarayıcı
│   ├── xss.py                 <- XSS tarayıcı
│   ├── lfi.py                 <- LFI tarayıcı
│   ├── acik_yonlendirme.py    <- Open Redirect tarayıcı
│   ├── csrf.py                <- CSRF tarayıcı
│   └── baslik_guvenlik.py     <- Başlık güvenliği kontrolü
├── payloadlar/
│   ├── sql_payloadlar.txt     <- SQL Injection payloadları (44 adet)
│   ├── xss_payloadlar.txt     <- XSS payloadlari (31 adet)
│   ├── lfi_payloadlar.txt     <- LFI payloadları (31 adet)
│   └── yonlendirme_payloadlar.txt <- Open Redirect payloadları (26 adet)
└── README.md                  <- Bu dosya
```

---

## Sık Sorulan Sorular

**S: "ModuleNotFoundError" hatası alıyorum?**
Bağımlılıkları kurun: `pip install -r requirements.txt`

**S: Hangi Python sürümünü kullanmalıyım?**
Python 3.8 veya üstü. Terminale `python --version` yazarak kontrol edebilirsiniz.

**S: Tarama çok uzun sürüyor?**
`--surungan-yok` ile sürüngeni devre dışı bırakın veya `--maks-sayfa 20` ile sayfa sayısını sınırlayın. Ayrıca `-m sql` gibi tek modül seçebilirsiniz.

**S: HTTPS siteleri taranabilir mi?**
Evet. SSL doğrulaması devre dışı bırakılmıştır, HTTPS siteler sorunsuz taranır.

**S: Proxy ile kullanabilir miyim?**
Evet. `--proxy http://127.0.0.1:8080` parametresiyle Burp Suite veya ZAP ile entegre çalışır.

**S: Sonuçları nasıl kaydederim?**
`-c json -d rapor.json` veya `-c html -d rapor.html` ile dosyaya kaydedebilirsiniz.

**S: Ctrl+C yapınca ne olur?**
Tarama güvenli bir şekilde durdurulur, o ana kadarki sonuçlar korunur.

---

## Yasal Uyarı

Bu araç **yalnızca eğitim ve yetkili güvenlik testleri** için tasarlanmıştır.
İzinsiz web uygulaması taraması **yasa dışıdır** ve ciddi hukuki sonuçlar doğurabilir.
Aracı kullanmadan önce ilgili sistem yöneticisinden **yazılı izin** aldığınızdan emin olun.

---

## Lisans

Bu proje eğitim amaçlıdır.

---

**Geliştirici:** erensogutlu  
**Sürüm:** 1.0.0  
**Platform:** Kali Linux / Windows / Python 3.8+
