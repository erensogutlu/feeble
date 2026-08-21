# -*- coding: utf-8 -*-
"""web sürüngen (crawler) - sayfaları gezer, linkleri ve formları keşfeder"""

import time
from urllib.parse import urlparse, urljoin

# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

from yapilandirma import (
    SURUNGAN_MAKS_DERINLIK,
    SURUNGAN_MAKS_SAYFA,
    SURUNGAN_GECIKME,
)
from yardimci import bilgi, uyari, ayni_domain_mi, statik_dosya_mi, url_dogrula


class Surungan:
    """web sürüngen sınıfı - hedef sitedeki sayfaları ve formları keşfeder"""

    def __init__(self, istek_yonetici, temel_url, maks_derinlik=None, maks_sayfa=None):
        """
        sürüngeni başlatır

        parametreler:
            istek_yonetici: IstekYonetici nesnesi
            temel_url: taranacak ana url
            maks_derinlik: maksimum tarama derinliği
            maks_sayfa: maksimum taranacak sayfa sayısı
        """
        self.istek_yonetici = istek_yonetici
        self.temel_url = temel_url
        self.maks_derinlik = maks_derinlik or SURUNGAN_MAKS_DERINLIK
        self.maks_sayfa = maks_sayfa or SURUNGAN_MAKS_SAYFA

        # keşfedilen veriler
        self.ziyaret_edilenler = set()
        self.kesfedilen_linkler = set()
        self.kesfedilen_formlar = []
        self.parametreli_urllar = set()

    def tara(self):
        """
        sürüngeni başlatır ve keşfedilen sayfaları döndürür

        dönüş:
            sözlük: linkler, formlar, parametreli url'ler
        """
        bilgi(f"sürüngen başlatılıyor: {self.temel_url}")
        bilgi(f"maks derinlik: {self.maks_derinlik}, maks sayfa: {self.maks_sayfa}")

        self._sayfayi_tara(self.temel_url, derinlik=0)

        bilgi(
            f"sürüngen tamamlandı — "
            f"{len(self.ziyaret_edilenler)} sayfa ziyaret edildi, "
            f"{len(self.kesfedilen_formlar)} form bulundu, "
            f"{len(self.parametreli_urllar)} parametreli url bulundu"
        )

        return {
            "linkler": list(self.kesfedilen_linkler),
            "formlar": self.kesfedilen_formlar,
            "parametreli_urllar": list(self.parametreli_urllar),
            "ziyaret_edilen_sayfa_sayisi": len(self.ziyaret_edilenler),
        }

    def _sayfayi_tara(self, url, derinlik):
        """bir sayfayı tarar ve linkleri/formları keşfeder"""
        # sınır kontrolleri
        if derinlik > self.maks_derinlik:
            return
        if len(self.ziyaret_edilenler) >= self.maks_sayfa:
            return
        if url in self.ziyaret_edilenler:
            return
        if not ayni_domain_mi(self.temel_url, url):
            return
        if statik_dosya_mi(url):
            return

        self.ziyaret_edilenler.add(url)
        self.kesfedilen_linkler.add(url)

        # parametreli url kontrolü
        parcalanmis = urlparse(url)
        if parcalanmis.query:
            self.parametreli_urllar.add(url)

        # sayfayı indir
        yanit = self.istek_yonetici.get(url)
        if yanit is None:
            return

        # sadece html içeriği işle
        icerik_tipi = yanit.headers.get("Content-Type", "")
        if "text/html" not in icerik_tipi:
            return

        try:
            soup = BeautifulSoup(yanit.text, "html.parser")
        except Exception:
            return

        # linkleri keşfet
        self._linkleri_kesfet(soup, url)

        # formları keşfet
        self._formlari_kesfet(soup, url)

        # gecikme
        time.sleep(SURUNGAN_GECIKME)

        # alt sayfaları tara
        for link in list(self.kesfedilen_linkler):
            if link not in self.ziyaret_edilenler:
                self._sayfayi_tara(link, derinlik + 1)

    def _linkleri_kesfet(self, soup, mevcut_url):
        """sayfadaki linkleri keşfeder"""
        for etiket in soup.find_all("a", href=True):
            href = etiket["href"].strip()

            # javascript ve anchor linklerini atla
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            # tam url'ye çevir
            tam_url = urljoin(mevcut_url, href)

            # fragment'ı kaldır
            parcalanmis = urlparse(tam_url)
            tam_url = tam_url.split("#")[0]

            # geçerli url kontrolü
            if not url_dogrula(tam_url):
                continue

            # aynı domain kontrolü
            if not ayni_domain_mi(self.temel_url, tam_url):
                continue

            self.kesfedilen_linkler.add(tam_url)

    def _formlari_kesfet(self, soup, mevcut_url):
        """sayfadaki formları keşfeder"""
        for form in soup.find_all("form"):
            form_verisi = self._form_ayristir(form, mevcut_url)
            if form_verisi:
                # aynı formu tekrar ekleme
                tekrar = False
                for mevcut in self.kesfedilen_formlar:
                    if (mevcut["aksiyon"] == form_verisi["aksiyon"] and
                            mevcut["metot"] == form_verisi["metot"]):
                        tekrar = True
                        break
                if not tekrar:
                    self.kesfedilen_formlar.append(form_verisi)

    def _form_ayristir(self, form, mevcut_url):
        """bir form etiketini ayrıştırarak bilgilerini çıkarır"""
        aksiyon = form.get("action", "").strip()
        metot = form.get("method", "GET").upper().strip()

        # aksiyonu tam url'ye çevir
        if aksiyon:
            aksiyon = urljoin(mevcut_url, aksiyon)
        else:
            aksiyon = mevcut_url

        # form alanlarını topla
        alanlar = {}
        for girdi in form.find_all(["input", "textarea", "select"]):
            alan_adi = girdi.get("name")
            if not alan_adi:
                continue

            alan_tipi = girdi.get("type", "text").lower()
            alan_degeri = girdi.get("value", "")

            # gizli ve submit alanlarını özel işle
            if alan_tipi == "submit":
                continue

            alanlar[alan_adi] = {
                "tip": alan_tipi,
                "deger": alan_degeri,
            }

        # csrf token kontrolü
        csrf_tokeni_var = False
        csrf_anahtar_kelimeleri = ["csrf", "token", "_token", "nonce", "authenticity"]
        for alan_adi in alanlar:
            for anahtar in csrf_anahtar_kelimeleri:
                if anahtar in alan_adi.lower():
                    csrf_tokeni_var = True
                    break

        return {
            "aksiyon": aksiyon,
            "metot": metot,
            "alanlar": alanlar,
            "sayfa_url": mevcut_url,
            "csrf_tokeni_var": csrf_tokeni_var,
        }
