# -*- coding: utf-8 -*-
"""bola / idor (broken object level authorization) yetki test modülü"""

import re
from urllib.parse import urlparse, parse_qs

from moduller.temel_modul import TemelModul
from yapilandirma import RISK_YUKSEK, RISK_ORTA
from yardimci import bilgi, basari, uyari


class BolaIdorModulu(TemelModul):
    """iki farklı kullanıcı oturumu ile bola / idor açıklarını tarayan modül"""

    @property
    def isim(self):
        return "BOLA / IDOR"

    @property
    def aciklama(self):
        return "yetkisiz nesne erişimi ve idor açıklarının tespiti"

    def __init__(self, istek_yonetici, cerez_b=None):
        super().__init__(istek_yonetici)
        self.cerez_b = cerez_b

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """bola / idor taramasını çalıştırır"""
        bilgi(f"BOLA / IDOR taraması başlatılıyor: {hedef_url}")

        if not self.cerez_b:
            uyari("ikinci kullanıcı çerezi (--cerez-b) belirtilmedi, BOLA testi sınırlı modda çalışıyor")
            return self.bulgular

        urller_ve_id = []

        # Parametreli URL'lerde ID kalıpları ara (?id=10, ?user_id=5)
        if parametreli_urllar:
            for url in parametreli_urllar:
                parcalanmis = urlparse(url)
                params = parse_qs(parcalanmis.query)
                for p_adi, p_val in params.items():
                    if any(k in p_adi.lower() for k in ["id", "user", "account", "order", "no", "doc"]):
                        if p_val and p_val[0].isdigit():
                            urller_ve_id.append((url, p_adi, p_val[0]))

        # URL yolunda sayısal ID ara (/user/105/profile)
        if re.search(r'/\d+(?:/|$)', hedef_url):
            urller_ve_id.append((hedef_url, "PATH_ID", re.findall(r'/(\d+)', hedef_url)[0]))

        for test_url, id_adi, id_degeri in urller_ve_id:
            self._bola_testi_yap(test_url, id_adi, id_degeri)

        bilgi(f"BOLA / IDOR taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _bola_testi_yap(self, url, id_adi, id_degeri):
        """User A oturumu ile erişilen kaynağa User B çerezi ile erişim testi yapar"""
        # User A isteği (varsayılan oturum)
        yanit_a = self.istek_yonetici.get(url)
        if yanit_a is None or yanit_a.status_code != 200:
            return

        # User B çerezi ile istek atılması (ek başlıklar / çerez ile)
        basliklar_b = {"Cookie": self.cerez_b}
        yanit_b = self.istek_yonetici.get(url, basliklar=basliklar_b)

        if yanit_b is not None and yanit_b.status_code == 200:
            # İki yanıtın benzerliğini ve boyut farkını kontrol et
            boyut_farki = abs(len(yanit_a.text) - len(yanit_b.text))
            if boyut_farki < (len(yanit_a.text) * 0.2):  # %20'den az fark varsa veri erişilmiştir
                basari(f"BOLA / IDOR açığı tespit edildi: {url}")
                self.bulgu_ekle(
                    url=url,
                    tip="BOLA / IDOR Yetkisiz Erişim",
                    risk=RISK_YUKSEK,
                    aciklama=f"Kullanıcı B, Kullanıcı A'ya ait nesneye yetkisiz erişebiliyor (ID: {id_degeri})",
                    detay=f"Parametre/Path: {id_adi}, Yanıt Boyutları: A={len(yanit_a.text)}, B={len(yanit_b.text)}",
                    kanit=f"HTTP 200 OK (User B erişimi sağlandı)",
                )
