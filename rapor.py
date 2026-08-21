# -*- coding: utf-8 -*-
"""rapor üretici - html, json ve konsol formatında çıktı"""

import json
import html
from datetime import datetime

from yapilandirma import RISK_KRITIK, RISK_YUKSEK, RISK_ORTA, RISK_DUSUK, RISK_BILGI, RENKLER
from yardimci import renkli_yaz, bilgi, basari


class RaporUretici:
    """tarama sonuçlarını raporlayan sınıf"""

    def __init__(self, hedef_url, bulgular, tarama_suresi=0, istek_istatistik=None):
        """
        rapor üreticiyi başlatır

        parametreler:
            hedef_url: taranan hedef url
            bulgular: bulgu listesi
            tarama_suresi: tarama süresi (saniye)
            istek_istatistik: istek istatistikleri sözlüğü
        """
        self.hedef_url = hedef_url
        self.bulgular = bulgular
        self.tarama_suresi = tarama_suresi
        self.istek_istatistik = istek_istatistik or {}
        self.tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def konsol_rapor(self):
        """konsola renkli rapor yazdırır"""
        print("\n" + "=" * 70)
        print(renkli_yaz("  TARAMA RAPORU", "CYAN"))
        print("=" * 70)
        print(f"  Hedef    : {self.hedef_url}")
        print(f"  Tarih    : {self.tarih}")
        print(f"  Süre     : {self.tarama_suresi:.1f} saniye")
        if self.istek_istatistik:
            print(f"  İstekler : {self.istek_istatistik.get('toplam_istek', 0)} "
                  f"(başarı: {self.istek_istatistik.get('basari_orani', 'N/A')})")
        print("=" * 70)

        if not self.bulgular:
            print(renkli_yaz("\n  [+] Guvenlik acigi bulunamadi.\n", "GREEN"))
            return

        # risk seviyesine göre grupla
        risk_gruplari = self._risk_gruplari()

        toplam = len(self.bulgular)
        print(f"\n  Toplam Bulgu: {toplam}")
        for risk, sayi in risk_gruplari.items():
            renk = RENKLER.get(risk, "WHITE")
            print(f"    {renkli_yaz(f'[{risk}]', renk)} {sayi} bulgu")
        print()

        # bulguları yazdır
        for i, bulgu in enumerate(self.bulgular, 1):
            risk = bulgu["risk"]
            renk = RENKLER.get(risk, "WHITE")
            print(f"  {renkli_yaz(f'[{risk}]', renk)} #{i} — {bulgu['tip']}")
            print(f"    URL     : {bulgu['url']}")
            print(f"    Açıklama: {bulgu['aciklama']}")
            if bulgu.get("payload"):
                print(f"    Payload : {bulgu['payload']}")
            if bulgu.get("detay"):
                print(f"    Detay   : {bulgu['detay']}")
            if bulgu.get("kanit"):
                kanit = bulgu["kanit"][:200]
                print(f"    Kanıt   : {kanit}")
            print()

        print("=" * 70)

    def json_rapor(self, dosya_yolu=None):
        """json formatında rapor üretir"""
        rapor = {
            "hedef": self.hedef_url,
            "tarih": self.tarih,
            "tarama_suresi": f"{self.tarama_suresi:.1f}s",
            "istek_istatistik": self.istek_istatistik,
            "toplam_bulgu": len(self.bulgular),
            "risk_ozeti": self._risk_gruplari(),
            "bulgular": self.bulgular,
        }

        json_metni = json.dumps(rapor, ensure_ascii=False, indent=2)

        if dosya_yolu:
            with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                dosya.write(json_metni)
            basari(f"json rapor kaydedildi: {dosya_yolu}")
        else:
            print(json_metni)

        return json_metni

    def html_rapor(self, dosya_yolu=None):
        """html formatında rapor üretir"""
        risk_gruplari = self._risk_gruplari()

        # risk renkleri
        risk_renkleri = {
            RISK_KRITIK: "#dc3545",
            RISK_YUKSEK: "#fd7e14",
            RISK_ORTA: "#ffc107",
            RISK_DUSUK: "#17a2b8",
            RISK_BILGI: "#6c757d",
        }

        # bulgu satırları
        bulgu_satirlari = ""
        for i, bulgu in enumerate(self.bulgular, 1):
            risk = bulgu["risk"]
            renk = risk_renkleri.get(risk, "#6c757d")
            payload_html = html.escape(bulgu.get("payload", "")) if bulgu.get("payload") else "-"
            kanit_html = html.escape(bulgu.get("kanit", "")[:300]) if bulgu.get("kanit") else "-"
            detay_html = html.escape(bulgu.get("detay", "")) if bulgu.get("detay") else "-"

            bulgu_satirlari += f"""
            <tr>
                <td>{i}</td>
                <td><span class="risk-badge" style="background-color:{renk}">{html.escape(risk)}</span></td>
                <td>{html.escape(bulgu['tip'])}</td>
                <td class="url-cell">{html.escape(bulgu['url'])}</td>
                <td>{html.escape(bulgu['aciklama'])}</td>
                <td><code>{payload_html}</code></td>
                <td>{detay_html}</td>
            </tr>"""

        # özet kartları
        ozet_kartlari = ""
        for risk, sayi in risk_gruplari.items():
            renk = risk_renkleri.get(risk, "#6c757d")
            ozet_kartlari += f"""
            <div class="ozet-kart" style="border-left: 4px solid {renk}">
                <div class="ozet-sayi">{sayi}</div>
                <div class="ozet-baslik">{html.escape(risk)}</div>
            </div>"""

        html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feeble Güvenlik Raporu — {html.escape(self.hedef_url)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f1a;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid #2a2a4a;
        }}
        header h1 {{
            font-size: 28px;
            color: #00d4ff;
            margin-bottom: 8px;
        }}
        header p {{ color: #8888aa; font-size: 14px; }}
        .bilgi-satir {{ margin: 4px 0; }}
        .bilgi-etiket {{ color: #888; }}
        .ozet-container {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .ozet-kart {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            flex: 1;
            min-width: 120px;
            text-align: center;
            border: 1px solid #2a2a4a;
        }}
        .ozet-sayi {{ font-size: 36px; font-weight: bold; color: #fff; }}
        .ozet-baslik {{ font-size: 12px; text-transform: uppercase; color: #888; margin-top: 4px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1a1a2e;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #2a2a4a;
        }}
        th {{
            background: #16213e;
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            text-transform: uppercase;
            color: #00d4ff;
            border-bottom: 2px solid #2a2a4a;
        }}
        td {{
            padding: 10px 16px;
            border-bottom: 1px solid #2a2a4a;
            font-size: 13px;
            vertical-align: top;
        }}
        tr:hover {{ background: #16213e; }}
        .risk-badge {{
            padding: 3px 10px;
            border-radius: 4px;
            color: #fff;
            font-size: 11px;
            font-weight: bold;
            white-space: nowrap;
        }}
        .url-cell {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: #4da6ff;
        }}
        code {{
            background: #0d1117;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            color: #ff6b6b;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            color: #555;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Feeble Guvenlik Raporu</h1>
            <p class="bilgi-satir"><span class="bilgi-etiket">Hedef:</span> {html.escape(self.hedef_url)}</p>
            <p class="bilgi-satir"><span class="bilgi-etiket">Tarih:</span> {self.tarih}</p>
            <p class="bilgi-satir"><span class="bilgi-etiket">Süre:</span> {self.tarama_suresi:.1f} saniye</p>
            <p class="bilgi-satir"><span class="bilgi-etiket">Toplam Bulgu:</span> {len(self.bulgular)}</p>
        </header>

        <div class="ozet-container">
            {ozet_kartlari}
        </div>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Risk</th>
                    <th>Tip</th>
                    <th>URL</th>
                    <th>Açıklama</th>
                    <th>Payload</th>
                    <th>Detay</th>
                </tr>
            </thead>
            <tbody>
                {bulgu_satirlari if self.bulgular else '<tr><td colspan="7" style="text-align:center;padding:30px;color:#4caf50;">[+] Guvenlik acigi bulunamadi.</td></tr>'}
            </tbody>
        </table>

        <footer>
            <p>Feeble Web Güvenlik Tarayıcı v1.0.0 — Geliştirici: erensogutlu — {self.tarih}</p>
        </footer>
    </div>
</body>
</html>"""

        if dosya_yolu:
            with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                dosya.write(html_icerik)
            basari(f"html rapor kaydedildi: {dosya_yolu}")

        return html_icerik

    def _risk_gruplari(self):
        """bulguları risk seviyesine göre gruplar"""
        gruplar = {}
        for bulgu in self.bulgular:
            risk = bulgu["risk"]
            gruplar[risk] = gruplar.get(risk, 0) + 1
        return gruplar
