# -*- coding: utf-8 -*-
"""http güvenlik başlıkları kontrolü modülü"""

from moduller.temel_modul import TemelModul
from yapilandirma import GUVENLIK_BASLIKLARI, RISK_YUKSEK, RISK_ORTA, RISK_DUSUK, RISK_BILGI
from yardimci import bilgi, basari, uyari


class BaslikGuvenlikModulu(TemelModul):
    """http güvenlik başlıklarını kontrol eden modül"""

    @property
    def isim(self):
        return "Başlık Güvenliği"

    @property
    def aciklama(self):
        return "eksik veya yanlış yapılandırılmış http güvenlik başlıklarının kontrolü"

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """güvenlik başlıkları taramasını çalıştırır"""
        bilgi(f"güvenlik başlıkları kontrolü başlatılıyor: {hedef_url}")

        yanit = self.istek_yonetici.get(hedef_url)
        if yanit is None:
            uyari(f"hedef url'ye erişilemedi: {hedef_url}")
            return self.bulgular

        basliklar = yanit.headers
        eksik_basliklar = []
        yanlis_yapilandirilmis = []

        for baslik_adi, baslik_bilgi in GUVENLIK_BASLIKLARI.items():
            deger = basliklar.get(baslik_adi)

            if deger is None:
                eksik_basliklar.append(baslik_adi)
                self.bulgu_ekle(
                    url=hedef_url,
                    tip=f"Eksik Güvenlik Başlığı: {baslik_adi}",
                    risk=RISK_ORTA if baslik_adi in (
                        "Content-Security-Policy",
                        "Strict-Transport-Security",
                        "X-Frame-Options",
                    ) else RISK_DUSUK,
                    aciklama=f"{baslik_adi} başlığı eksik — {baslik_bilgi['aciklama']}",
                    detay=f"önerilen değer: {baslik_bilgi['onerilen']}",
                )
            else:
                # değer kontrolü
                sorun = self._deger_kontrol(baslik_adi, deger)
                if sorun:
                    yanlis_yapilandirilmis.append(baslik_adi)
                    self.bulgu_ekle(
                        url=hedef_url,
                        tip=f"Zayıf Güvenlik Başlığı: {baslik_adi}",
                        risk=RISK_DUSUK,
                        aciklama=f"{baslik_adi} başlığı zayıf yapılandırılmış — {sorun}",
                        detay=f"mevcut değer: {deger}, önerilen: {baslik_bilgi['onerilen']}",
                    )

        # özet bilgi
        if eksik_basliklar:
            bilgi(f"eksik güvenlik başlıkları: {', '.join(eksik_basliklar)}")
        if yanlis_yapilandirilmis:
            bilgi(f"zayıf yapılandırılmış başlıklar: {', '.join(yanlis_yapilandirilmis)}")
        if not eksik_basliklar and not yanlis_yapilandirilmis:
            bilgi("tüm güvenlik başlıkları mevcut ve doğru yapılandırılmış")

        # ek güvenlik kontrolleri
        self._ek_kontroller(hedef_url, basliklar)

        bilgi(f"başlık güvenliği kontrolü tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _deger_kontrol(self, baslik_adi, deger):
        """başlık değerinin güvenli olup olmadığını kontrol eder"""
        deger_kucuk = deger.lower()

        if baslik_adi == "X-Frame-Options":
            if deger_kucuk not in ("deny", "sameorigin"):
                return "geçersiz değer, deny veya sameorigin olmalı"

        elif baslik_adi == "X-Content-Type-Options":
            if deger_kucuk != "nosniff":
                return "değer nosniff olmalı"

        elif baslik_adi == "X-XSS-Protection":
            if "0" == deger_kucuk:
                return "xss filtresi devre dışı bırakılmış"

        elif baslik_adi == "Strict-Transport-Security":
            if "max-age=0" in deger_kucuk:
                return "max-age 0 olarak ayarlanmış, hsts etkisiz"

        elif baslik_adi == "Content-Security-Policy":
            tehlikeli_direktifler = ["unsafe-inline", "unsafe-eval", "*"]
            for direktif in tehlikeli_direktifler:
                if direktif in deger_kucuk:
                    return f"tehlikeli direktif bulundu: {direktif}"

        return None

    def _ek_kontroller(self, url, basliklar):
        """ek güvenlik kontrollerini yapar"""
        # sunucu bilgisi sızıntısı
        sunucu = basliklar.get("Server")
        if sunucu:
            self.bulgu_ekle(
                url=url,
                tip="Sunucu Bilgisi Sızıntısı",
                risk=RISK_BILGI,
                aciklama=f"server başlığı sunucu bilgisini ifşa ediyor: {sunucu}",
                detay="server başlığı kaldırılmalı veya değeri gizlenmelidir",
            )

        # x-powered-by sızıntısı
        powered_by = basliklar.get("X-Powered-By")
        if powered_by:
            self.bulgu_ekle(
                url=url,
                tip="Teknoloji Bilgisi Sızıntısı",
                risk=RISK_BILGI,
                aciklama=f"x-powered-by başlığı teknoloji bilgisini ifşa ediyor: {powered_by}",
                detay="x-powered-by başlığı kaldırılmalıdır",
            )

        # CORS hatalı yapılandırma kontrolü
        try:
            cors_yanit = self.istek_yonetici.get(url, basliklar={"Origin": "https://evil.com"})
            if cors_yanit is not None:
                allow_origin = cors_yanit.headers.get("Access-Control-Allow-Origin")
                allow_credentials = cors_yanit.headers.get("Access-Control-Allow-Credentials")
                if allow_origin == "https://evil.com" or allow_origin == "*":
                    risk = RISK_YUKSEK if allow_credentials == "true" else RISK_ORTA
                    self.bulgu_ekle(
                        url=url,
                        tip="CORS Hatalı Yapılandırma",
                        risk=risk,
                        aciklama="sunucu güvenilmeyen origin isteklerini kabul ediyor",
                        detay=f"Access-Control-Allow-Origin: {allow_origin}, Access-Control-Allow-Credentials: {allow_credentials}",
                    )
        except Exception:
            pass
