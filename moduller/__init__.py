# -*- coding: utf-8 -*-
"""modül kayıt ve yükleme mekanizması"""

from moduller.sql_enjeksiyon import SqlEnjeksiyonModulu
from moduller.xss import XssModulu
from moduller.lfi import LfiModulu
from moduller.acik_yonlendirme import AcikYonlendirmeModulu
from moduller.csrf import CsrfModulu
from moduller.baslik_guvenlik import BaslikGuvenlikModulu
from moduller.bola_idor import BolaIdorModulu

# kullanılabilir modüller sözlüğü
MODULLER = {
    "sql": SqlEnjeksiyonModulu,
    "xss": XssModulu,
    "lfi": LfiModulu,
    "yonlendirme": AcikYonlendirmeModulu,
    "csrf": CsrfModulu,
    "baslik": BaslikGuvenlikModulu,
    "bola": BolaIdorModulu,
}

# modül açıklamaları
MODUL_ACIKLAMALARI = {
    "sql": "SQL Injection (Error/Boolean/Time-based)",
    "xss": "Cross-Site Scripting (Reflected/Stored)",
    "lfi": "Local File Inclusion / Path Traversal",
    "yonlendirme": "Open Redirect",
    "csrf": "CSRF Token Eksikliği",
    "baslik": "HTTP Güvenlik Başlıkları",
    "bola": "BOLA / IDOR Yetki Testi",
}


def modulleri_yukle(modul_isimleri=None):
    """
    belirtilen modülleri yükler

    parametreler:
        modul_isimleri: yüklenecek modül isimlerinin listesi (None ise tümü)

    dönüş:
        modül sınıflarının listesi
    """
    if modul_isimleri is None:
        return list(MODULLER.values())

    yuklenen = []
    for isim in modul_isimleri:
        isim = isim.strip().lower()
        if isim in MODULLER:
            yuklenen.append(MODULLER[isim])
    return yuklenen


def mevcut_modulleri_listele():
    """kullanılabilir modüllerin isim ve açıklama listesini döndürür"""
    return MODUL_ACIKLAMALARI.copy()
