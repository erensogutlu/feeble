# -*- coding: utf-8 -*-
"""xss (cross-site scripting) tarama modülü - reflected ve stored xss tespiti"""

import os
import re
import html
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from moduller.temel_modul import TemelModul
from yapilandirma import PAYLOAD_DIZINI, RISK_YUKSEK, RISK_ORTA
from yardimci import bilgi, basari, uyari


class XssModulu(TemelModul):
    """xss açıklarını tarayan modül"""

    @property
    def isim(self):
        return "XSS"

    @property
    def aciklama(self):
        return "reflected ve stored cross-site scripting tespiti"

    def __init__(self, istek_yonetici):
        super().__init__(istek_yonetici)
        self.payloadlar = self._payloadlari_yukle()

    def _payloadlari_yukle(self):
        """payload dosyasından xss payloadlarını yükler"""
        dosya_yolu = os.path.join(PAYLOAD_DIZINI, "xss_payloadlar.txt")
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                return [satir.strip() for satir in dosya if satir.strip() and not satir.startswith("#")]
        except FileNotFoundError:
            uyari("xss payload dosyası bulunamadı, varsayılan payloadlar kullanılıyor")
            return self._varsayilan_payloadlar()

    def _varsayilan_payloadlar(self):
        """dosya bulunamazsa kullanılacak varsayılan payloadlar"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "\"><script>alert('XSS')</script>",
            "'\"><img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
        ]

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """xss taramasını çalıştırır"""
        bilgi(f"xss taraması başlatılıyor: {hedef_url}")

        # parametreli url'leri tara
        if parametreli_urllar:
            for url in parametreli_urllar:
                self._url_parametrelerini_tara(url)

        # formları tara
        if formlar:
            for form in formlar:
                self._form_tara(form)

        # dom tabanlı xss ipuçları
        self._dom_xss_kontrol(hedef_url)

        bilgi(f"xss taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _url_parametrelerini_tara(self, url):
        """url parametrelerini xss için tarar"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        for parametre_adi in parametreler:
            for payload in self.payloadlar:
                test_parametreleri = parametreler.copy()
                test_parametreleri[parametre_adi] = [payload]
                yeni_sorgu = urlencode(test_parametreleri, doseq=True)
                test_url = urlunparse((
                    parcalanmis.scheme, parcalanmis.netloc, parcalanmis.path,
                    parcalanmis.params, yeni_sorgu, parcalanmis.fragment,
                ))

                yanit = self.istek_yonetici.get(test_url)
                if yanit is None:
                    continue

                # payload yansıma kontrolü
                if self._yansiyor_mu(payload, yanit.text):
                    basari(f"reflected xss bulundu: {url} — parametre: {parametre_adi}")
                    self.bulgu_ekle(
                        url=url,
                        tip="Reflected XSS",
                        risk=RISK_YUKSEK,
                        aciklama=f"reflected xss açığı — parametre: {parametre_adi}",
                        detay=f"payload yanıtta yansıdı — encode edilmemiş html/js içeriği",
                        payload=payload,
                        kanit=self._kanit_cikar(payload, yanit.text),
                    )
                    break  # bu parametre için yeterli

    def _form_tara(self, form):
        """form alanlarını xss için tarar"""
        aksiyon = form["aksiyon"]
        metot = form["metot"]
        alanlar = form["alanlar"]

        for alan_adi, alan_bilgi in alanlar.items():
            if alan_bilgi["tip"] in ("hidden", "submit", "password"):
                continue

            for payload in self.payloadlar[:8]:
                test_verisi = {}
                for ad, bilgi_dict in alanlar.items():
                    if ad == alan_adi:
                        test_verisi[ad] = payload
                    else:
                        test_verisi[ad] = bilgi_dict["deger"] or "test"

                if metot == "POST":
                    yanit = self.istek_yonetici.post(aksiyon, veri=test_verisi)
                else:
                    yanit = self.istek_yonetici.get(aksiyon, parametreler=test_verisi)

                if yanit is None:
                    continue

                if self._yansiyor_mu(payload, yanit.text):
                    basari(f"xss bulundu (form): {aksiyon} — alan: {alan_adi}")
                    self.bulgu_ekle(
                        url=aksiyon,
                        tip="Reflected XSS (Form)",
                        risk=RISK_YUKSEK,
                        aciklama=f"reflected xss açığı — form alanı: {alan_adi}",
                        detay=f"form: {aksiyon}, metot: {metot}",
                        payload=payload,
                        kanit=self._kanit_cikar(payload, yanit.text),
                    )
                    break

    def _yansiyor_mu(self, payload, yanit_metni):
        """payload'ın yanıtta encode edilmeden yansıyıp yansımadığını kontrol eder"""
        # doğrudan yansıma
        if payload in yanit_metni:
            return True

        # html entity decode edilmiş halini kontrol et
        decode_edilmis = html.unescape(yanit_metni)
        if payload in decode_edilmis:
            return True

        return False

    def _dom_xss_kontrol(self, url):
        """dom tabanlı xss ipuçlarını kontrol eder"""
        yanit = self.istek_yonetici.get(url)
        if yanit is None:
            return

        tehlikeli_kaliplar = [
            (r"document\.write\s*\(", "document.write"),
            (r"\.innerHTML\s*=", "innerHTML"),
            (r"\.outerHTML\s*=", "outerHTML"),
            (r"eval\s*\(", "eval"),
            (r"document\.location\s*=", "document.location"),
            (r"window\.location\s*=", "window.location"),
            (r"\.insertAdjacentHTML\s*\(", "insertAdjacentHTML"),
        ]

        bulunan_kaliplar = []
        for kalip, isim in tehlikeli_kaliplar:
            if re.search(kalip, yanit.text):
                bulunan_kaliplar.append(isim)

        if bulunan_kaliplar:
            self.bulgu_ekle(
                url=url,
                tip="DOM-based XSS İpucu",
                risk=RISK_ORTA,
                aciklama="dom tabanlı xss'e yol açabilecek tehlikeli javascript kalıpları bulundu",
                detay=f"bulunan kalıplar: {', '.join(bulunan_kaliplar)}",
            )

    def _kanit_cikar(self, payload, yanit_metni, bağlam_uzunlugu=100):
        """yanıt metninden payload'ın bulunduğu bağlamı çıkarır"""
        konum = yanit_metni.find(payload)
        if konum == -1:
            return ""
        baslangic = max(0, konum - bağlam_uzunlugu)
        bitis = min(len(yanit_metni), konum + len(payload) + bağlam_uzunlugu)
        return f"...{yanit_metni[baslangic:bitis]}..."
