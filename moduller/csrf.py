# -*- coding: utf-8 -*-
"""csrf token eksikliği tarama modülü"""

from moduller.temel_modul import TemelModul
from yapilandirma import RISK_ORTA, RISK_DUSUK
from yardimci import bilgi, basari


class CsrfModulu(TemelModul):
    """csrf token eksikliğini tarayan modül"""

    @property
    def isim(self):
        return "CSRF"

    @property
    def aciklama(self):
        return "csrf token eksikliği tespiti"

    # csrf token ile ilişkili alan isimleri
    CSRF_ANAHTAR_KELIMELERI = [
        "csrf", "token", "_token", "nonce", "authenticity_token",
        "csrf_token", "csrfmiddlewaretoken", "__requestverificationtoken",
        "antiforgery", "xsrf", "_csrf",
    ]

    def tara(self, hedef_url, formlar=None, parametreli_urllar=None):
        """csrf taramasını çalıştırır"""
        bilgi(f"csrf taraması başlatılıyor: {hedef_url}")

        if not formlar:
            bilgi("form bulunamadı — csrf kontrolü atlanıyor")
            return self.bulgular

        for form in formlar:
            self._form_kontrol(form)

        bilgi(f"csrf taraması tamamlandı — {len(self.bulgular)} bulgu")
        return self.bulgular

    def _form_kontrol(self, form):
        """formda csrf token olup olmadığını kontrol eder"""
        aksiyon = form["aksiyon"]
        metot = form["metot"]
        alanlar = form["alanlar"]
        csrf_var = form.get("csrf_tokeni_var", False)

        # sadece post formlarını kontrol et (get formları genelde idempotent)
        if metot != "POST":
            return

        if csrf_var:
            # Token var ama sunucunun boş/sahte tokenı doğrulayıp doğrulamadığını kontrol et
            self._aktif_token_testi(form)
            return

        # form alanlarında csrf token araması
        token_bulundu = False
        for alan_adi in alanlar:
            alan_kucuk = alan_adi.lower()
            for anahtar in self.CSRF_ANAHTAR_KELIMELERI:
                if anahtar in alan_kucuk:
                    token_bulundu = True
                    break
            if token_bulundu:
                break

        if not token_bulundu:
            # formun hassas bir işlem yapıp yapmadığını kontrol et
            hassas_mi = self._hassas_form_mu(form)

            if hassas_mi:
                basari(f"csrf token eksikliği: {aksiyon}")
                self.bulgu_ekle(
                    url=aksiyon,
                    tip="CSRF Token Eksikliği",
                    risk=RISK_ORTA,
                    aciklama="post formu csrf token içermiyor",
                    detay=f"form: {aksiyon}, metot: {metot}, alan sayısı: {len(alanlar)}",
                )
            else:
                self.bulgu_ekle(
                    url=aksiyon,
                    tip="CSRF Token Eksikliği (Düşük)",
                    risk=RISK_DUSUK,
                    aciklama="post formu csrf token içermiyor (düşük riskli form)",
                    detay=f"form: {aksiyon}, metot: {metot}",
                )

    def _aktif_token_testi(self, form):
        """csrf token var ama sunucunun boş/sahte token kabul edip etmediğini test eder"""
        aksiyon = form["aksiyon"]
        veri = {}
        for alan_adi, alan_bilgi in form["alanlar"].items():
            kucuk = alan_adi.lower()
            if any(k in kucuk for k in self.CSRF_ANAHTAR_KELIMELERI):
                veri[alan_adi] = "invalid_token_123"  # Sahte token
            else:
                veri[alan_adi] = alan_bilgi.get("deger", "test")

        yanit = self.istek_yonetici.post(aksiyon, veri=veri)
        if yanit is not None and yanit.status_code == 200:
            self.bulgu_ekle(
                url=aksiyon,
                tip="Zayıf CSRF Token Doğrulaması",
                risk=RISK_ORTA,
                aciklama="sunucu geçersiz/sahte CSRF token'ı kabul etti",
                detay=f"form: {aksiyon}, gönderilen sahte token: invalid_token_123",
            )

    def _hassas_form_mu(self, form):
        """formun hassas bir işlem yapıp yapmadığını tahmin eder"""
        hassas_anahtar_kelimeler = [
            "login", "register", "password", "delete", "update", "edit",
            "admin", "settings", "profile", "payment", "transfer", "send",
            "giris", "kayit", "sifre", "sil", "guncelle", "duzenle",
            "ayar", "profil", "odeme", "gonder",
        ]

        aksiyon = form["aksiyon"].lower()
        alanlar = form["alanlar"]

        # aksiyon url'sinde hassas kelime var mı?
        for kelime in hassas_anahtar_kelimeler:
            if kelime in aksiyon:
                return True

        # password tipi alan var mı?
        for alan_adi, alan_bilgi in alanlar.items():
            if alan_bilgi["tip"] == "password":
                return True
            if any(kelime in alan_adi.lower() for kelime in hassas_anahtar_kelimeler):
                return True

        return False
