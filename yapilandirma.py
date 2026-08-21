# -*- coding: utf-8 -*-
"""genel yapılandırma sabitleri ve varsayılan ayarlar"""

import os

# geliştirici bilgisi
GELISTIRICI = "erensogutlu"

# proje kök dizini
KOK_DIZIN = os.path.dirname(os.path.abspath(__file__))

# payload dosyaları dizini
PAYLOAD_DIZINI = os.path.join(KOK_DIZIN, "payloadlar")

# varsayılan http başlıkları
VARSAYILAN_BASLIKLAR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# zaman aşımı ayarları (saniye)
ISTEK_ZAMAN_ASIMI = 10
BAGLANTI_ZAMAN_ASIMI = 5

# hız sınırlaması ve waf ayarları
VARSAYILAN_GECIKME = 0.0  # istekler arası varsayılan gecikme (saniye)
WAF_YAVASLAMA_SURESI = 2.0  # 429 alındığında uygulanacak bekleme süresi
WAF_DURUM_KODLARI = [429, 403, 503]

# sürüngen ayarları
SURUNGAN_MAKS_DERINLIK = 3
SURUNGAN_MAKS_SAYFA = 100
SURUNGAN_GECIKME = 0.5  # saniye

# tarama ayarları
MAKS_ESLESMEN = 5  # eşzamanlı thread sayısı
YENIDEN_DENEME_SAYISI = 2

# risk seviyeleri
RISK_KRITIK = "KRİTİK"
RISK_YUKSEK = "YÜKSEK"
RISK_ORTA = "ORTA"
RISK_DUSUK = "DÜŞÜK"
RISK_BILGI = "BİLGİ"

# renk kodları (konsol çıktısı için)
RENKLER = {
    RISK_KRITIK: "RED",
    RISK_YUKSEK: "RED",
    RISK_ORTA: "YELLOW",
    RISK_DUSUK: "CYAN",
    RISK_BILGI: "WHITE",
}

# sql injection hata kalıpları
SQL_HATA_KALIPLARI = {
    "MySQL": [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark",
        "mysql_fetch",
        "mysql_num_rows",
        "mysql_query",
    ],
    "PostgreSQL": [
        "pg_query",
        "pg_exec",
        "valid postgresql result",
        "npgsql",
        "pgsql",
        "unterminated quoted string",
    ],
    "MSSQL": [
        "microsoft sql server",
        "mssql_query",
        "odbc sql server driver",
        "sqlsrv",
        "unclosed quotation mark after the character string",
    ],
    "Oracle": [
        "ora-00933",
        "ora-01756",
        "oracle error",
        "oracle.*driver",
        "quoted string not properly terminated",
    ],
    "SQLite": [
        "sqlite3.operationalerror",
        "sqlite_error",
        "unable to prepare statement",
        "unrecognized token",
        "sqlite.error",
    ],
}

# güvenlik başlıkları listesi
GUVENLIK_BASLIKLARI = {
    "X-Frame-Options": {
        "aciklama": "tıklama saldırılarına (clickjacking) karşı koruma sağlar",
        "onerilen": "DENY veya SAMEORIGIN",
    },
    "Content-Security-Policy": {
        "aciklama": "xss ve veri enjeksiyonu saldırılarına karşı koruma sağlar",
        "onerilen": "default-src 'self'",
    },
    "Strict-Transport-Security": {
        "aciklama": "https bağlantısını zorunlu kılar",
        "onerilen": "max-age=31536000; includeSubDomains",
    },
    "X-Content-Type-Options": {
        "aciklama": "mime tipi koklama saldırılarını engeller",
        "onerilen": "nosniff",
    },
    "X-XSS-Protection": {
        "aciklama": "tarayıcı xss filtresi",
        "onerilen": "1; mode=block",
    },
    "Referrer-Policy": {
        "aciklama": "referrer bilgisi sızıntısını kontrol eder",
        "onerilen": "strict-origin-when-cross-origin",
    },
    "Permissions-Policy": {
        "aciklama": "tarayıcı özelliklerine erişimi kısıtlar",
        "onerilen": "geolocation=(), microphone=(), camera=()",
    },
}
