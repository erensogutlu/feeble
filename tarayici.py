# -*- coding: utf-8 -*-
"""ana tarayıcı motoru - modülleri yükler, sürüngeni çalıştırır, sonuçları toplar"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from yapilandirma import MAKS_ESLESMEN
from istek import IstekYonetici
from surungan import Surungan
from rapor import RaporUretici
from moduller import modulleri_yukle, MODUL_ACIKLAMALARI
from yardimci import bilgi, basari, uyari, hata, sure_formatla


class Tarayici:
    """ana tarayıcı motoru sınıfı"""

    def __init__(self, hedef_url, moduller=None, proxy=None, cerez=None,
                 maks_derinlik=None, maks_sayfa=None, eslesmen=None, gecikme=0.0,
                 cerez_b=None, waf_bypass=False, js_surungan=False, sablonlar=None):
        """
        tarayıcıyı başlatır
        """
        self.hedef_url = hedef_url
        self.modul_isimleri = moduller
        self.eslesmen = eslesmen or MAKS_ESLESMEN
        self.bulgular = []
        self.cerez_b = cerez_b
        self.waf_bypass = waf_bypass
        self.js_surungan_aktif = js_surungan
        self.sablonlar = sablonlar

        # istek yöneticisi
        self.istek_yonetici = IstekYonetici(proxy=proxy, cerez=cerez, gecikme=gecikme)

        # sürüngen
        self.surungan = Surungan(
            istek_yonetici=self.istek_yonetici,
            temel_url=hedef_url,
            maks_derinlik=maks_derinlik,
            maks_sayfa=maks_sayfa,
        )

        # modülleri yükle
        modul_siniflar = modulleri_yukle(self.modul_isimleri)
        self.moduller = []
        for sinif in modul_siniflar:
            if sinif.__name__ == "BolaIdorModulu":
                self.moduller.append(sinif(self.istek_yonetici, cerez_b=self.cerez_b))
            else:
                self.moduller.append(sinif(self.istek_yonetici))

    def tara(self, surungan_kullan=True):
        """
        taramayı başlatır

        parametreler:
            surungan_kullan: sürüngenle sayfa keşfi yapılsın mı?

        dönüş:
            bulgular listesi
        """
        baslangic = time.time()

        bilgi(f"hedef: {self.hedef_url}")
        bilgi(f"yüklenen modüller: {len(self.moduller)}")
        for modul in self.moduller:
            bilgi(f"  -- {modul.isim}: {modul.aciklama}")

        # sürüngen ile sayfa keşfi
        kesfedilen = {"linkler": [], "formlar": [], "parametreli_urllar": []}
        if surungan_kullan:
            bilgi("sürüngen ile sayfa keşfi başlatılıyor...")
            kesfedilen = self.surungan.tara()
        else:
            bilgi("sürüngen devre dışı — sadece hedef url taranacak")

        # WAF fuzzing ve mutasyon hazırlığı
        if self.waf_bypass:
            bilgi("WAF karakter fuzzing ön taraması başlatılıyor...")
            from waf_mutasyon import WafMutator
            mutator = WafMutator(self.istek_yonetici)
            mutator.karakter_fuzzing(self.hedef_url)

        # JS sürüngeni ile dinamik sayfa keşfi
        if self.js_surungan_aktif:
            bilgi("Headless JS sürüngeni çalıştırılıyor...")
            from surungan_js import SurunganJs
            js_surungan = SurunganJs(self.hedef_url, self.istek_yonetici)
            js_endpointleri = js_surungan.tara()
            for ep in js_endpointleri:
                if ep not in kesfedilen.get("linkler", []):
                    kesfedilen.setdefault("linkler", []).append(ep)

        # YAML Şablon Motorunu çalıştır
        if self.sablonlar:
            bilgi(f"YAML şablon motoru başlatılıyor: {self.sablonlar}")
            from sablon_motoru import SablonMotoru
            sm = SablonMotoru(self.istek_yonetici)
            sablon_bulgulari = sm.sablon_tara(self.hedef_url, self.sablonlar)
            self.bulgular.extend(sablon_bulgulari)

        formlar = kesfedilen.get("formlar", [])
        parametreli_urllar = kesfedilen.get("parametreli_urllar", [])

        # modülleri çalıştır
        bilgi("tarama modülleri çalıştırılıyor...")
        self._modulleri_calistir(formlar, parametreli_urllar)

        # sonuçları topla
        for modul in self.moduller:
            self.bulgular.extend(modul.bulgulari_al())

        bitis = time.time()
        tarama_suresi = bitis - baslangic

        bilgi(f"tarama tamamlandı — {sure_formatla(tarama_suresi)}")
        bilgi(f"toplam bulgu: {len(self.bulgular)}")

        return {
            "bulgular": self.bulgular,
            "tarama_suresi": tarama_suresi,
            "istek_istatistik": self.istek_yonetici.istatistik(),
            "kesfedilen": kesfedilen,
        }

    def _modulleri_calistir(self, formlar, parametreli_urllar):
        """modülleri paralel olarak çalıştırır"""
        if self.eslesmen <= 1:
            # sıralı çalıştır
            for modul in self.moduller:
                try:
                    modul.tara(self.hedef_url, formlar=formlar,
                              parametreli_urllar=parametreli_urllar)
                except Exception as istisna:
                    hata(f"{modul.isim} modülünde hata: {istisna}")
        else:
            # paralel çalıştır
            with ThreadPoolExecutor(max_workers=self.eslesmen) as havuz:
                gelecekler = {}
                for modul in self.moduller:
                    gelecek = havuz.submit(
                        modul.tara, self.hedef_url,
                        formlar=formlar,
                        parametreli_urllar=parametreli_urllar,
                    )
                    gelecekler[gelecek] = modul

                for gelecek in as_completed(gelecekler):
                    modul = gelecekler[gelecek]
                    try:
                        gelecek.result()
                    except Exception as istisna:
                        hata(f"{modul.isim} modülünde hata: {istisna}")

    def rapor_uret(self, format="konsol", dosya_yolu=None):
        """
        tarama sonuçlarını raporlar

        parametreler:
            format: rapor formatı (konsol, json, html)
            dosya_yolu: çıktı dosyası yolu

        dönüş:
            rapor metni
        """
        sonuclar = self.tara() if not self.bulgular else {
            "bulgular": self.bulgular,
            "tarama_suresi": 0,
            "istek_istatistik": self.istek_yonetici.istatistik(),
        }

        uretici = RaporUretici(
            hedef_url=self.hedef_url,
            bulgular=self.bulgular,
            tarama_suresi=sonuclar.get("tarama_suresi", 0),
            istek_istatistik=sonuclar.get("istek_istatistik"),
        )

        if format == "json":
            return uretici.json_rapor(dosya_yolu)
        elif format == "html":
            return uretici.html_rapor(dosya_yolu)
        else:
            uretici.konsol_rapor()
            return None
