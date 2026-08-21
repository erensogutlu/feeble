# -*- coding: utf-8 -*-
"""open redirect tarama modülü - yönlendirme açıklarının tespiti"""

import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from moduller.temel_modul import TemelModul
from yapilandirma import PAYLOAD_DIZINI, RISK_ORTA
from yardimci import bilgi, basari, uyari


class AcikYonlendirmeModulu(TemelModul):
    """open redirect açıklarını tarayan modül"""

    @property
    def isim(self):
        return "Open Redirect"

    @property
    def aciklama(self):
        return "açık yönlendirme (open redirect) açıklarının tespiti"

    # yaygın yönlendirme parametreleri
    YONLENDIRME_PARAMETRELERI = [
        "url", "redirect", "redir", "return", "returnurl", "return_url",
        "next", "goto", "target", "dest", "destination", "continue",
        "redirect_uri", "redirect_url", "callback", "forward", "out",
        "view", "login_url", "logout", "checkout_url", "image_url",
        "ref", "site", "to", "uri", "u", "r",
        "hedef", "yonlendir", "git", "sayfa",
    ]

    def __init__(self, istek_yonetici):
        super().__init__(istek_yonetici)
        self.payloadlar = self._payloadlari_yukle()

    def _payloadlari_yukle(self):
        """payload dosyasından yönlendirme payloadlarını yükler"""
        dosya_yolu = os.path.join(PAYLOAD_DIZINI, "yonlendirme_payloadlar.txt")
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                return [satir.strip() for satir in dosya if satir.strip() and not satir.startswith("#")]
        except FileNotFoundError:
            uyari("yönlendirme payload dosyası bulunamadı, varsayılan payloadlar kullanılıyor")
            return self._varsayilan_payloadlar()

    def _varsayilan_payloadlar(self):
        """dosya bulunamazsa kullanılacak varsayılan payloadlar"""
        return [
            "https://evil.com",
            "//evil.com",
            "https://evil.com%2f%2f",
            "/\\evil.com",
            "https:evil.com",
        ]

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """open redirect taramasını çalıştırır"""
        bilgi(f"open redirect taraması başlatılıyor: {hedef_url}")

        # parametreli url'leri tara
        if parametreli_urllar:
            for url in parametreli_urllar:
                self._url_parametrelerini_tara(url)

        # yönlendirme parametreleri olmayan url'leri de test et
        self._potansiyel_parametreleri_tara(hedef_url)

        bilgi(f"open redirect taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _url_parametrelerini_tara(self, url):
        """url parametrelerini open redirect için tarar"""
        parcalanmis = urlparse(url)
        parametreler = parse_qs(parcalanmis.query, keep_blank_values=True)

        for parametre_adi in parametreler:
            # yönlendirme ile ilişkili parametre mi?
            iliskili = any(
                anahtar in parametre_adi.lower()
                for anahtar in self.YONLENDIRME_PARAMETRELERI
            )

            if not iliskili:
                continue

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

                # yönlendirme kontrolü
                if self._yonlendirme_kontrol(yanit, payload):
                    basari(f"open redirect bulundu: {url} — parametre: {parametre_adi}")
                    self.bulgu_ekle(
                        url=url,
                        tip="Open Redirect",
                        risk=RISK_ORTA,
                        aciklama=f"açık yönlendirme — parametre: {parametre_adi}",
                        detay=f"uygulama dış siteye yönlendirme yapıyor",
                        payload=payload,
                        kanit=f"yönlendirilen url: {yanit.url}",
                    )
                    break

    def _potansiyel_parametreleri_tara(self, hedef_url):
        """yönlendirme parametresi ekleyerek test eder"""
        for parametre in self.YONLENDIRME_PARAMETRELERI[:10]:
            for payload in self.payloadlar[:3]:
                parcalanmis = urlparse(hedef_url)
                mevcut_sorgu = parcalanmis.query
                if mevcut_sorgu:
                    yeni_sorgu = f"{mevcut_sorgu}&{parametre}={payload}"
                else:
                    yeni_sorgu = f"{parametre}={payload}"

                test_url = urlunparse((
                    parcalanmis.scheme, parcalanmis.netloc, parcalanmis.path,
                    parcalanmis.params, yeni_sorgu, parcalanmis.fragment,
                ))

                yanit = self.istek_yonetici.get(test_url)
                if yanit is None:
                    continue

                if self._yonlendirme_kontrol(yanit, payload):
                    basari(f"open redirect bulundu: {hedef_url} — parametre: {parametre}")
                    self.bulgu_ekle(
                        url=hedef_url,
                        tip="Open Redirect",
                        risk=RISK_ORTA,
                        aciklama=f"açık yönlendirme — potansiyel parametre: {parametre}",
                        detay="url'de bulunmayan ama uygulama tarafından işlenen parametre",
                        payload=payload,
                        kanit=f"yönlendirilen url: {yanit.url}",
                    )
                    return  # bir tane bulunca yeterli

    def _yonlendirme_kontrol(self, yanit, payload):
        """yanıtın dış siteye yönlendirme yapıp yapmadığını kontrol eder"""
        # yönlendirme geçmişini kontrol et
        if yanit.history:
            for gecmis_yanit in yanit.history:
                konum = gecmis_yanit.headers.get("Location", "")
                if self._dis_site_mi(konum, payload):
                    return True

        # son url kontrolü
        if self._dis_site_mi(yanit.url, payload):
            return True

        return False

    def _dis_site_mi(self, url, payload):
        """url'nin dış siteye (evil.com) işaret edip etmediğini kontrol eder"""
        try:
            # payload'daki hedef domain'i çıkar
            payload_temiz = payload.replace("\\", "/")
            for onEk in ["https://", "http://", "//"]:
                if payload_temiz.startswith(onEk):
                    payload_temiz = payload_temiz[len(onEk):]
                    break

            hedef_domain = payload_temiz.split("/")[0].split("%")[0]

            # yanıt url'sinde hedef domain var mı?
            if hedef_domain and hedef_domain in url:
                return True
        except Exception:
            pass
        return False
