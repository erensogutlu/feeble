# -*- coding: utf-8 -*-
"""yaml tabanlı güvenlik açığı şablon motoru (nuclei benzeri kural ayrıştırıcı)"""

import os
import re
from urllib.parse import urljoin

from yapilandirma import RISK_YUKSEK, RISK_ORTA, RISK_DUSUK, RISK_BILGI
from yardimci import bilgi, basari, uyari


class SablonMotoru:
    """yaml şablonlarını okuyan ve taramayı yürüten sınıf"""

    def __init__(self, istek_yonetici):
        self.istek_yonetici = istek_yonetici
        self.bulgular = []

    def _yaml_oku(self, dosya_yolu):
        """yaml dosyasını okur (PyYAML veya basit dahili ayrıştırıcı)"""
        try:
            import yaml
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            # PyYAML yoksa basit anahtar-değer satır ayrıştırıcısı
            veriler = {"info": {}, "requests": []}
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                mevcut_istek = None
                for satir in f:
                    satir = satir.strip()
                    if satir.startswith("id:"):
                        veriler["id"] = satir.split(":", 1)[1].strip()
                    elif satir.startswith("name:"):
                        veriler["info"]["name"] = satir.split(":", 1)[1].strip().strip('"\'')
                    elif satir.startswith("risk:"):
                        veriler["info"]["risk"] = satir.split(":", 1)[1].strip().strip('"\'')
                    elif satir.startswith("path:"):
                        mevcut_istek = {"path": satir.split(":", 1)[1].strip().strip('"\''), "matchers": []}
                        veriler["requests"].append(mevcut_istek)
                    elif satir.startswith("status:") and mevcut_istek is not None:
                        mevcut_istek["matchers"].append({"type": "status", "status": int(satir.split(":", 1)[1].strip())})
            return veriler

    def sablon_tara(self, hedef_url, sablon_dizini_veya_dosya):
        """
        belirtilen yaml şablonu veya dizindeki tüm şablonları hedef url üzerinde çalıştırır
        """
        bilgi(f"YAML Şablon Motoru çalıştırılıyor: {hedef_url}")

        dosyalar = []
        if os.path.isfile(sablon_dizini_veya_dosya):
            dosyalar.append(sablon_dizini_veya_dosya)
        elif os.path.isdir(sablon_dizini_veya_dosya):
            for kok, _, fs in os.walk(sablon_dizini_veya_dosya):
                for f in fs:
                    if f.endswith(".yaml") or f.endswith(".yml"):
                        dosyalar.append(os.path.join(kok, f))

        for dosya in dosyalar:
            self._tek_sablon_calistir(hedef_url, dosya)

        bilgi(f"YAML Şablon Motoru tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _tek_sablon_calistir(self, hedef_url, dosya_yolu):
        """tek bir yaml şablonunu hedefte yürütür"""
        sablon = self._yaml_oku(dosya_yolu)
        if not sablon or "requests" not in sablon:
            return

        info = sablon.get("info", {})
        isim = info.get("name", sablon.get("id", "Bilinmeyen Şablon"))
        risk = info.get("risk", RISK_ORTA)
        aciklama = info.get("aciklama", "YAML şablonu eşleşti")

        for req in sablon.get("requests", []):
            path = req.get("path", "")
            metot = req.get("method", "GET").upper()
            test_url = urljoin(hedef_url, path)

            yanit = None
            if metot == "GET":
                yanit = self.istek_yonetici.get(test_url)
            elif metot == "POST":
                yanit = self.istek_yonetici.post(test_url, veri=req.get("body", ""))

            if yanit is None:
                continue

            eslestimi = True
            for matcher in req.get("matchers", []):
                m_type = matcher.get("type")
                if m_type == "status":
                    if yanit.status_code != matcher.get("status"):
                        eslestimi = False
                        break
                elif m_type == "word":
                    words = matcher.get("words", [])
                    if not any(w in yanit.text for w in words):
                        eslestimi = False
                        break
                elif m_type == "regex":
                    regexes = matcher.get("regex", [])
                    if not any(re.search(r, yanit.text) for r in regexes):
                        eslestimi = False
                        break

            if eslestimi:
                basari(f"YAML Şablon eşleşti [{isim}]: {test_url}")
                self.bulgular.append({
                    "modul": "YAML Şablon Motoru",
                    "url": test_url,
                    "tip": isim,
                    "risk": risk,
                    "aciklama": aciklama,
                    "detay": f"Şablon Dosyası: {os.path.basename(dosya_yolu)}",
                    "payload": path,
                    "kanit": f"HTTP Status: {yanit.status_code}",
                })
