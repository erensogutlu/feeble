# -*- coding: utf-8 -*-
"""yardımcı fonksiyonlar - url doğrulama, renklendirme, banner"""

import re
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse

from colorama import Fore, Style, init

# colorama'yı başlat
init(autoreset=True)

# banner metni
BANNER = r"""
  _____ _____ _____ ____  _     _____
 |  ___| ____| ____| __ )| |   | ____|
 | |_  |  _| |  _| |  _ \| |   |  _|  
 |  _| | |___| |___| |_) | |___| |___ 
 |_|   |_____|_____|____/|_____|_____|
  web güvenlik açığı tarayıcı v1.0.0
  geliştirici: erensogutlu
"""

# renk eşlemeleri
RENK_ESLEMESI = {
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE,
    "MAGENTA": Fore.MAGENTA,
    "BLUE": Fore.BLUE,
}


def banner_yazdir():
    """renkli banner'ı konsola yazdırır"""
    print(f"{Fore.CYAN}{BANNER}{Style.RESET_ALL}")


def renkli_yaz(metin, renk="WHITE"):
    """verilen renkte metin döndürür"""
    renk_kodu = RENK_ESLEMESI.get(renk.upper(), Fore.WHITE)
    return f"{renk_kodu}{metin}{Style.RESET_ALL}"


def bilgi(metin):
    """bilgi mesajı yazdırır"""
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {metin}")


def basari(metin):
    """başarı mesajı yazdırır"""
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {metin}")


def uyari(metin):
    """uyarı mesajı yazdırır"""
    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {metin}")


def hata(metin):
    """hata mesajı yazdırır"""
    print(f"{Fore.RED}[-]{Style.RESET_ALL} {metin}")


def kritik(metin):
    """kritik mesajı yazdırır"""
    print(f"{Fore.RED}{Style.BRIGHT}[!!]{Style.RESET_ALL} {metin}")


def url_dogrula(url):
    """url'nin geçerli olup olmadığını kontrol eder"""
    try:
        sonuc = urlparse(url)
        return all([sonuc.scheme, sonuc.netloc])
    except Exception:
        return False


def url_normalize(url):
    """url'yi normalize eder (son slash ekler vb.)"""
    parcalanmis = urlparse(url)
    if not parcalanmis.scheme:
        url = "http://" + url
        parcalanmis = urlparse(url)
    return url


def ayni_domain_mi(url1, url2):
    """iki url'nin aynı domain'de olup olmadığını kontrol eder"""
    try:
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        if not domain1 or not domain2:
            return False
        return domain1 == domain2
    except Exception:
        return False


def url_birlestir(temel_url, yol):
    """temel url ile yolu birleştirir"""
    return urljoin(temel_url, yol)


def parametre_ekle(url, parametre_adi, deger):
    """url'ye parametre ekler veya mevcut parametreyi günceller"""
    parcalanmis = urlparse(url)
    parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)
    parametreler[parametre_adi] = [deger]
    yeni_sorgu = urlencode(parametreler, doseq=True)
    yeni_url = urlunparse((
        parcalanmis.scheme,
        parcalanmis.netloc,
        parcalanmis.path,
        parcalanmis.params,
        yeni_sorgu,
        parcalanmis.fragment,
    ))
    return yeni_url


def parametreleri_al(url):
    """url'den parametreleri sözlük olarak döndürür"""
    parcalanmis = urlparse(url)
    return parse_qs(parcalanmis.query, keep_blank_values=True)


def dosya_uzantisi_al(url):
    """url'den dosya uzantısını döndürür"""
    yol = urlparse(url).path
    if "." in yol:
        return yol.rsplit(".", 1)[-1].lower()
    return ""


def statik_dosya_mi(url):
    """url'nin statik bir dosyaya işaret edip etmediğini kontrol eder"""
    statik_uzantilar = {
        "css", "js", "jpg", "jpeg", "png", "gif", "svg", "ico",
        "woff", "woff2", "ttf", "eot", "mp3", "mp4", "avi", "pdf",
        "zip", "tar", "gz", "rar", "7z",
    }
    uzanti = dosya_uzantisi_al(url)
    return uzanti in statik_uzantilar


def sure_formatla(saniye):
    """saniye değerini okunabilir formata çevirir"""
    if saniye < 60:
        return f"{saniye:.1f} saniye"
    dakika = int(saniye // 60)
    kalan_saniye = saniye % 60
    return f"{dakika} dakika {kalan_saniye:.1f} saniye"
