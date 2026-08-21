# -*- coding: utf-8 -*-
"""out-of-band (oob) etkileşim istemcisi - blind rce, blind ssrf, log4j tespiti için callback jeton yönetimi"""

import uuid
import time


class OobYonetici:
    """oob callback jetonlarını oluşturan ve etkileşimleri doğrulayan sınıf"""

    def __init__(self, oob_sunucu="oob.feeble-scanner.test"):
        self.oob_sunucu = oob_sunucu
        self.olusturulan_jetonlar = {}

    def jeton_uret(self, acik_tipi="Blind SSRF", url=""):
        """
        benzersiz bir oob callback jetonu ve domaini üretir

        dönüş:
            (jeton_id, callback_domain)
        """
        jeton_id = str(uuid.uuid4())[:8]
        callback_url = f"http://{jeton_id}.{self.oob_sunucu}"
        self.olusturulan_jetonlar[jeton_id] = {
            "tip": acik_tipi,
            "url": url,
            "zaman": time.time(),
            "tetiklendi": False,
        }
        return jeton_id, callback_url

    def etkilesim_dogrula(self, jeton_id):
        """
        verilen jeton_id için etkileşim gelip gelmediğini doğrular (örnek/simülasyon)
        """
        if jeton_id in self.olusturulan_jetonlar:
            return self.olusturulan_jetonlar[jeton_id]["tetiklendi"]
        return False

    def jeton_tetikle_manuel(self, jeton_id):
        """test veya simülasyon amaçlı jetonu tetiklendi olarak işaretler"""
        if jeton_id in self.olusturulan_jetonlar:
            self.olusturulan_jetonlar[jeton_id]["tetiklendi"] = True
