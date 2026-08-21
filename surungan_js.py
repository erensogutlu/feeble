# -*- coding: utf-8 -*-
"""headless js & spa (single page application) sürüngen katmanı"""

import re
from urllib.parse import urljoin, urlparse

from yardimci import bilgi, uyari


class SurunganJs:
    """javascript tabanlı dinamik sürüngen sınıfı"""

    def __init__(self, temel_url, istek_yonetici=None):
        self.temel_url = temel_url
        self.istek_yonetici = istek_yonetici
        self.kesfedilen_endpointler = set()
        self.playwright_mevcut = False

        try:
            import playwright  # type: ignore # noqa: F401
            self.playwright_mevcut = True
        except ImportError:
            self.playwright_mevcut = False

    def tara(self, url=None):
        """
        js sürüngenini çalıştırır. Playwright varsa tarayıcıda yürütür, yoksa static js analizi yapar.
        """
        hedef = url or self.temel_url
        bilgi(f"JS sürüngeni çalıştırılıyor: {hedef}")

        if self.playwright_mevcut:
            self._playwright_ile_tara(hedef)
        else:
            self._statik_js_analizi(hedef)

        return list(self.kesfedilen_endpointler)

    def _statik_js_analizi(self, url):
        """Playwright yüklü değilse HTML içindeki JS ve harici .js dosyalarındaki API endpointlerini tespit eder"""
        if not self.istek_yonetici:
            return

        yanit = self.istek_yonetici.get(url)
        if yanit is None or not yanit.text:
            return

        # HTML içindeki fetch/axios/ajax yönlendirmeleri
        self._js_metninden_endpoint_cikar(yanit.text, url)

        # Harici .js dosyalarını bul ve incele
        js_linkleri = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', yanit.text, re.IGNORECASE)
        for js_link in js_linkleri[:10]:  # ilk 10 JS dosyasını incele
            tam_js_url = urljoin(url, js_link)
            js_yanit = self.istek_yonetici.get(tam_js_url)
            if js_yanit and js_yanit.text:
                self._js_metninden_endpoint_cikar(js_yanit.text, url)

    def _js_metninden_endpoint_cikar(self, metin, temel_url):
        """JS kodları içindeki API endpoint ve URL kalıplarını regex ile ayıklar"""
        kalıplar = [
            r'["\'](/(?:api|v[0-9]|user|admin|auth|get|post|update|delete)/[^"\'\s>]+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\s*\.\s*(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
            r'\$\.ajax\s*\(\s*\{\s*url\s*:\s*["\']([^"\']+)["\']',
        ]
        for kalip in kalıplar:
            eslesmeler = re.findall(kalip, metin, re.IGNORECASE)
            for eslesme in eslesmeler:
                tam_url = urljoin(temel_url, eslesme)
                self.kesfedilen_endpointler.add(tam_url)

    def _playwright_ile_tara(self, url):
        """Playwright headless browser kullanarak SPA sayfalarını ve DOM ağacını yürütür"""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Ağ isteklerini dinle
                def istek_yakala(request):
                    self.kesfedilen_endpointler.add(request.url)

                page.on("request", istek_yakala)

                page.goto(url, wait_until="networkidle", timeout=15000)

                # Sayfadaki linkleri topla
                hrefs = page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                for href in hrefs:
                    if href:
                        self.kesfedilen_endpointler.add(href)

                browser.close()
        except Exception as e:
            uyari(f"Playwright tarama hatası: {e}")
            self._statik_js_analizi(url)
