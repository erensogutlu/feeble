# -*- coding: utf-8 -*-
"""tüm modüllerin miras aldığı soyut temel sınıf"""

from abc import ABC, abstractmethod


class TemelModul(ABC):
    """
    tarama modülleri için soyut temel sınıf

    her modül bu sınıftan miras almalı ve tara() metotunu uygulamalıdır
    """

    def __init__(self, istek_yonetici):
        """
        modülü başlatır

        parametreler:
            istek_yonetici: IstekYonetici nesnesi
        """
        self.istek_yonetici = istek_yonetici
        self.bulgular = []

    @property
    @abstractmethod
    def isim(self):
        """modül ismi"""
        pass

    @property
    @abstractmethod
    def aciklama(self):
        """modül açıklaması"""
        pass

    @abstractmethod
    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """
        taramayı çalıştırır

        parametreler:
            hedef_url: taranacak url
            formlar: keşfedilen formların listesi
            parametreli_urllar: parametreli url'lerin listesi

        dönüş:
            bulgu listesi
        """
        pass

    def bulgu_ekle(self, url, tip, risk, aciklama, detay=None, payload=None, kanit=None):
        """
        yeni bir bulgu ekler

        parametreler:
            url: açığın bulunduğu url
            tip: açık tipi
            risk: risk seviyesi (KRİTİK, YÜKSEK, ORTA, DÜŞÜK, BİLGİ)
            aciklama: açığın kısa açıklaması
            detay: detaylı bilgi
            payload: kullanılan payload
            kanit: açığın kanıtı
        """
        bulgu = {
            "modul": self.isim,
            "url": url,
            "tip": tip,
            "risk": risk,
            "aciklama": aciklama,
            "detay": detay or "",
            "payload": payload or "",
            "kanit": kanit or "",
        }
        self.bulgular.append(bulgu)
        return bulgu

    def bulgulari_al(self):
        """toplanan bulguları döndürür"""
        return self.bulgular

    def temizle(self):
        """bulguları temizler"""
        self.bulgular = []
