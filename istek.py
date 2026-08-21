# -*- coding: utf-8 -*-
"""http istek yardımcı fonksiyonları - get/post istekleri, oturum yönetimi, proxy desteği"""

import time
import requests
from requests.adapters import HTTPAdapter
# pyrefly: ignore [missing-import]
from urllib3.util.retry import Retry

from yapilandirma import (
    VARSAYILAN_BASLIKLAR,
    ISTEK_ZAMAN_ASIMI,
    BAGLANTI_ZAMAN_ASIMI,
    YENIDEN_DENEME_SAYISI,
)
from yardimci import uyari


class IstekYonetici:
    """http isteklerini yöneten sınıf"""

    def __init__(self, proxy=None, cerez=None, ek_basliklar=None, gecikme=0.0):
        """
        istek yöneticisini başlatır

        parametreler:
            proxy: proxy adresi (örn: http://127.0.0.1:8080)
            cerez: çerez dizgisi (örn: "PHPSESSID=abc123")
            ek_basliklar: ek http başlıkları sözlüğü
            gecikme: istekler arası gecikme süresi (saniye)
        """
        self.oturum = requests.Session()
        self.proxy = proxy
        self.gecikme = gecikme
        self.istek_sayaci = 0
        self.hata_sayaci = 0

        # başlıkları ayarla
        self.oturum.headers.update(VARSAYILAN_BASLIKLAR)
        if ek_basliklar:
            self.oturum.headers.update(ek_basliklar)

        # çerez ayarla
        if cerez:
            self._cerez_ayarla(cerez)

        # proxy ayarla
        if proxy:
            self.oturum.proxies = {
                "http": proxy,
                "https": proxy,
            }

        # ssl doğrulamasını devre dışı bırak (test amaçlı)
        self.oturum.verify = False

        # yeniden deneme mekanizması
        yeniden_deneme = Retry(
            total=YENIDEN_DENEME_SAYISI,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adaptör = HTTPAdapter(max_retries=yeniden_deneme)
        self.oturum.mount("http://", adaptör)
        self.oturum.mount("https://", adaptör)

        # ssl uyarılarını sustur
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )

    def _cerez_ayarla(self, cerez_dizgisi):
        """çerez dizgisini oturuma ekler"""
        for parca in cerez_dizgisi.split(";"):
            parca = parca.strip()
            if "=" in parca:
                anahtar, deger = parca.split("=", 1)
                self.oturum.cookies.set(anahtar.strip(), deger.strip())

    def get(self, url, parametreler=None, basliklar=None, zaman_asimi=None):
        """
        get isteği gönderir

        parametreler:
            url: hedef url
            parametreler: sorgu parametreleri
            basliklar: ek http başlıkları
            zaman_asimi: istek zaman aşımı (saniye)

        dönüş:
            requests.Response nesnesi veya None
        """
        return self._istek_gonder(
            "GET", url, parametreler=parametreler,
            basliklar=basliklar, zaman_asimi=zaman_asimi,
        )

    def post(self, url, veri=None, json_veri=None, basliklar=None, zaman_asimi=None):
        """
        post isteği gönderir

        parametreler:
            url: hedef url
            veri: form verisi
            json_veri: json verisi
            basliklar: ek http başlıkları
            zaman_asimi: istek zaman aşımı (saniye)

        dönüş:
            requests.Response nesnesi veya None
        """
        return self._istek_gonder(
            "POST", url, veri=veri, json_veri=json_veri,
            basliklar=basliklar, zaman_asimi=zaman_asimi,
        )

    def _istek_gonder(self, metot, url, parametreler=None, veri=None,
                      json_veri=None, basliklar=None, zaman_asimi=None):
        """dahili istek gönderme fonksiyonu"""
        if zaman_asimi is None:
            zaman_asimi = (BAGLANTI_ZAMAN_ASIMI, ISTEK_ZAMAN_ASIMI)

        if self.gecikme > 0:
            time.sleep(self.gecikme)

        try:
            self.istek_sayaci += 1
            yanit = self.oturum.request(
                method=metot,
                url=url,
                params=parametreler,
                data=veri,
                json=json_veri,
                headers=basliklar,
                timeout=zaman_asimi,
                allow_redirects=True,
            )

            # WAF / Rate Limit tespiti durumunda otomatik bekleme
            if yanit.status_code in (429, 403, 503):
                if yanit.status_code == 429:
                    uyari(f"hız sınırı (429) algılandı, 2 saniye bekleniyor: {url}")
                    time.sleep(2.0)
                elif yanit.status_code in (403, 503):
                    time.sleep(0.5)

            return yanit

        except requests.exceptions.Timeout:
            self.hata_sayaci += 1
            uyari(f"zaman aşımı: {url}")
            time.sleep(1.0)
            return None

        except requests.exceptions.ConnectionError:
            self.hata_sayaci += 1
            uyari(f"bağlantı hatası: {url}")
            time.sleep(1.0)
            return None

        except requests.exceptions.RequestException as istisna:
            self.hata_sayaci += 1
            uyari(f"istek hatası ({url}): {istisna}")
            return None

    def yanit_suresi_olc(self, url, parametreler=None):
        """
        bir url'ye yapılan isteğin yanıt süresini ölçer (saniye)

        dönüş:
            yanıt süresi (float) veya None
        """
        try:
            baslangic = time.time()
            yanit = self.get(url, parametreler=parametreler)
            bitis = time.time()
            if yanit is not None:
                return bitis - baslangic
            return None
        except Exception:
            return None

    def istatistik(self):
        """istek istatistiklerini döndürür"""
        return {
            "toplam_istek": self.istek_sayaci,
            "hata_sayisi": self.hata_sayaci,
            "basari_orani": (
                f"{((self.istek_sayaci - self.hata_sayaci) / max(self.istek_sayaci, 1)) * 100:.1f}%"
            ),
        }
