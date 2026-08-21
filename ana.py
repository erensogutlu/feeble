# -*- coding: utf-8 -*-
"""cli giriş noktası - komut satırı argümanları ve tarama başlatıcı"""

import sys
import argparse

from yardimci import banner_yazdir, bilgi, hata, url_dogrula, url_normalize
from tarayici import Tarayici
from moduller import mevcut_modulleri_listele


def arguman_ayristirici():
    """komut satırı argümanlarını ayrıştırır"""
    ayristirici = argparse.ArgumentParser(
        prog="feeble",
        description="Feeble — Web Güvenlik Açığı Tarayıcı (Geliştirici: erensogutlu)",
        epilog="Geliştirici: erensogutlu | Örnek: python -m feeble -u https://hedef.com --tam-tarama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # hedef url (zorunlu)
    ayristirici.add_argument(
        "-u", "--url",
        required=True,
        help="Taranacak hedef URL (örn: https://hedef.com)",
    )

    # tarama modu
    ayristirici.add_argument(
        "--tam-tarama",
        action="store_true",
        default=False,
        help="Tüm modüllerle tam tarama yapar (varsayılan)",
    )

    ayristirici.add_argument(
        "-m", "--moduller",
        type=str,
        default=None,
        help="Kullanılacak modüller (virgülle ayrılmış: sql,xss,lfi,yonlendirme,csrf,baslik)",
    )

    # çıktı formatı
    ayristirici.add_argument(
        "-c", "--cikti",
        choices=["konsol", "json", "html"],
        default="konsol",
        help="Rapor çıktı formatı (varsayılan: konsol)",
    )

    ayristirici.add_argument(
        "-d", "--dosya",
        type=str,
        default=None,
        help="Rapor çıktı dosyası yolu (json veya html için)",
    )

    # sürüngen ayarları
    ayristirici.add_argument(
        "--derinlik",
        type=int,
        default=None,
        help="Sürüngen maksimum derinlik (varsayılan: 3)",
    )

    ayristirici.add_argument(
        "--maks-sayfa",
        type=int,
        default=None,
        help="Sürüngen maksimum sayfa sayısı (varsayılan: 100)",
    )

    ayristirici.add_argument(
        "--surungan-yok",
        action="store_true",
        default=False,
        help="Sürüngeni devre dışı bırak, sadece hedef URL'yi tara",
    )

    # bağlantı ayarları
    ayristirici.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="Proxy adresi (örn: http://127.0.0.1:8080)",
    )

    ayristirici.add_argument(
        "--cerez",
        type=str,
        default=None,
        help="Çerez dizgisi (örn: \"PHPSESSID=abc123; token=xyz\")",
    )

    ayristirici.add_argument(
        "--gecikme",
        type=float,
        default=0.0,
        help="İstekler arası gecikme süresi saniye cinsinden (varsayılan: 0.0)",
    )

    ayristirici.add_argument(
        "--cerez-b",
        type=str,
        default=None,
        help="İkinci kullanıcı çerezi (BOLA / IDOR testi için)",
    )

    ayristirici.add_argument(
        "--waf-bypass",
        action="store_true",
        default=False,
        help="Adaptif WAF mutasyon motorunu aktif hale getirir",
    )

    ayristirici.add_argument(
        "--js-surungan",
        action="store_true",
        default=False,
        help="Headless JavaScript & SPA tarama katmanını aktif hale getirir",
    )

    ayristirici.add_argument(
        "--sablonlar",
        type=str,
        default=None,
        help="Çalıştırılacak YAML zafiyet şablonu veya dizini",
    )

    # eşzamanlılık
    ayristirici.add_argument(
        "-t", "--thread",
        type=int,
        default=None,
        help="Eşzamanlı thread sayısı (varsayılan: 5)",
    )

    # modül listesi
    ayristirici.add_argument(
        "--modul-listesi",
        action="store_true",
        default=False,
        help="Kullanılabilir modülleri listeler ve çıkar",
    )

    return ayristirici


def ana_fonksiyon():
    """ana program giriş noktası"""
    banner_yazdir()

    ayristirici = arguman_ayristirici()
    arglar = ayristirici.parse_args()

    # modül listesi modu
    if arglar.modul_listesi:
        bilgi("kullanılabilir modüller:")
        for isim, aciklama in mevcut_modulleri_listele().items():
            print(f"  {isim:15s} — {aciklama}")
        sys.exit(0)

    # url doğrulama
    hedef_url = url_normalize(arglar.url)
    if not url_dogrula(hedef_url):
        hata(f"geçersiz url: {arglar.url}")
        sys.exit(1)

    # modülleri belirle
    modul_listesi = None
    if arglar.moduller:
        modul_listesi = [m.strip() for m in arglar.moduller.split(",")]
        bilgi(f"seçilen modüller: {', '.join(modul_listesi)}")
    else:
        bilgi("tüm modüller ile tam tarama yapılacak")

    # tarayıcıyı oluştur
    try:
        tarayici = Tarayici(
            hedef_url=hedef_url,
            moduller=modul_listesi,
            proxy=arglar.proxy,
            cerez=arglar.cerez,
            maks_derinlik=arglar.derinlik,
            maks_sayfa=arglar.maks_sayfa,
            eslesmen=arglar.thread,
            gecikme=arglar.gecikme,
            cerez_b=arglar.cerez_b,
            waf_bypass=arglar.waf_bypass,
            js_surungan=arglar.js_surungan,
            sablonlar=arglar.sablonlar,
        )
    except Exception as istisna:
        hata(f"tarayıcı başlatılamadı: {istisna}")
        sys.exit(1)

    # taramayı başlat
    try:
        sonuclar = tarayici.tara(surungan_kullan=not arglar.surungan_yok)
    except KeyboardInterrupt:
        hata("\ntarama kullanıcı tarafından durduruldu")
        sys.exit(1)
    except Exception as istisna:
        hata(f"tarama sırasında hata: {istisna}")
        sys.exit(1)

    # rapor üret
    from rapor import RaporUretici

    uretici = RaporUretici(
        hedef_url=hedef_url,
        bulgular=sonuclar["bulgular"],
        tarama_suresi=sonuclar["tarama_suresi"],
        istek_istatistik=sonuclar["istek_istatistik"],
    )

    if arglar.cikti == "json":
        uretici.json_rapor(arglar.dosya)
    elif arglar.cikti == "html":
        dosya = arglar.dosya or "feeble_rapor.html"
        uretici.html_rapor(dosya)
    else:
        uretici.konsol_rapor()

    # çıktı dosyası belirtilmişse json/html otomatik kaydet
    if arglar.dosya and arglar.cikti == "konsol":
        bilgi("konsol çıktısı için dosya kaydı yapılmaz, -c json veya -c html kullanın")


if __name__ == "__main__":
    ana_fonksiyon()
