# -*- coding: utf-8 -*-
"""kapsamli test scripti"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

hatalar = []
basarili = 0

def test(isim, kosul, detay=""):
    global basarili
    if kosul:
        basarili += 1
        print(f"  [OK] {isim}")
    else:
        hatalar.append(isim)
        print(f"  [HATA] {isim} {detay}")


print("=" * 60)
print("  FEEBLE - KAPSAMLI TEST RAPORU")
print("=" * 60)

# ============================================================
print("\n[1/8] YAPILANDIRMA TESTLERİ")
# ============================================================
from yapilandirma import (
    KOK_DIZIN, PAYLOAD_DIZINI, VARSAYILAN_BASLIKLAR,
    ISTEK_ZAMAN_ASIMI, BAGLANTI_ZAMAN_ASIMI,
    SURUNGAN_MAKS_DERINLIK, SURUNGAN_MAKS_SAYFA, SURUNGAN_GECIKME,
    MAKS_ESLESMEN, YENIDEN_DENEME_SAYISI,
    RISK_KRITIK, RISK_YUKSEK, RISK_ORTA, RISK_DUSUK, RISK_BILGI,
    RENKLER, SQL_HATA_KALIPLARI, GUVENLIK_BASLIKLARI,
)

test("KOK_DIZIN var ve gecerli", os.path.isdir(KOK_DIZIN))
test("PAYLOAD_DIZINI var ve gecerli", os.path.isdir(PAYLOAD_DIZINI))
test("VARSAYILAN_BASLIKLAR dict", isinstance(VARSAYILAN_BASLIKLAR, dict) and "User-Agent" in VARSAYILAN_BASLIKLAR)
test("ISTEK_ZAMAN_ASIMI > 0", ISTEK_ZAMAN_ASIMI > 0)
test("BAGLANTI_ZAMAN_ASIMI > 0", BAGLANTI_ZAMAN_ASIMI > 0)
test("SURUNGAN_MAKS_DERINLIK > 0", SURUNGAN_MAKS_DERINLIK > 0)
test("SURUNGAN_MAKS_SAYFA > 0", SURUNGAN_MAKS_SAYFA > 0)
test("MAKS_ESLESMEN > 0", MAKS_ESLESMEN > 0)
test("5 risk seviyesi tanimli", all([RISK_KRITIK, RISK_YUKSEK, RISK_ORTA, RISK_DUSUK, RISK_BILGI]))
test("RENKLER 5 girdi", len(RENKLER) >= 5)
test("SQL_HATA_KALIPLARI 5 veritabani", len(SQL_HATA_KALIPLARI) == 5)
test("GUVENLIK_BASLIKLARI 7 baslik", len(GUVENLIK_BASLIKLARI) == 7)

# ============================================================
print("\n[2/8] PAYLOAD DOSYALARI TESTLERİ")
# ============================================================
payload_dosyalari = {
    "sql_payloadlar.txt": 10,
    "xss_payloadlar.txt": 10,
    "lfi_payloadlar.txt": 10,
    "yonlendirme_payloadlar.txt": 5,
}
for dosya, min_sayi in payload_dosyalari.items():
    tam_yol = os.path.join(PAYLOAD_DIZINI, dosya)
    var_mi = os.path.isfile(tam_yol)
    test(f"{dosya} dosyasi var", var_mi)
    if var_mi:
        with open(tam_yol, "r", encoding="utf-8") as f:
            satirlar = [s.strip() for s in f if s.strip() and not s.startswith("#")]
        test(f"{dosya} en az {min_sayi} payload ({len(satirlar)} mevcut)", len(satirlar) >= min_sayi)

# ============================================================
print("\n[3/8] YARDIMCI FONKSİYON TESTLERİ")
# ============================================================
from yardimci import (
    url_dogrula, url_normalize, ayni_domain_mi, url_birlestir,
    parametre_ekle, parametreleri_al, dosya_uzantisi_al,
    statik_dosya_mi, sure_formatla, renkli_yaz, banner_yazdir,
)

# url_dogrula
test("url_dogrula('https://a.com') = True", url_dogrula("https://a.com") == True)
test("url_dogrula('http://test.org/p') = True", url_dogrula("http://test.org/p") == True)
test("url_dogrula('') = False", url_dogrula("") == False)
test("url_dogrula('not-url') = False", url_dogrula("not-url") == False)
test("url_dogrula('ftp://x.com') = True", url_dogrula("ftp://x.com") == True)

# url_normalize
test("url_normalize http ekleme", url_normalize("example.com").startswith("http://"))
test("url_normalize https korunur", url_normalize("https://x.com") == "https://x.com")

# ayni_domain_mi
test("ayni_domain_mi ayni", ayni_domain_mi("https://a.com/x", "https://a.com/y") == True)
test("ayni_domain_mi farkli", ayni_domain_mi("https://a.com", "https://b.com") == False)
test("ayni_domain_mi bos", ayni_domain_mi("", "") == False)

# url_birlestir
test("url_birlestir mutlak", url_birlestir("https://a.com/", "/p") == "https://a.com/p")
test("url_birlestir goreceli", url_birlestir("https://a.com/dir/", "page") == "https://a.com/dir/page")

# parametre_ekle
test("parametre_ekle yeni", "q=test" in parametre_ekle("https://a.com", "q", "test"))
test("parametre_ekle mevcut", "q=new" in parametre_ekle("https://a.com?q=old", "q", "new"))

# parametreleri_al
p = parametreleri_al("https://a.com?a=1&b=2&c=3")
test("parametreleri_al 3 parametre", len(p) == 3)
test("parametreleri_al bos url", parametreleri_al("https://a.com") == {})

# dosya_uzantisi_al
test("dosya_uzantisi js", dosya_uzantisi_al("https://a.com/f.js") == "js")
test("dosya_uzantisi yok", dosya_uzantisi_al("https://a.com/page") == "")
test("dosya_uzantisi php", dosya_uzantisi_al("https://a.com/index.php") == "php")

# statik_dosya_mi
test("statik css", statik_dosya_mi("https://a.com/s.css") == True)
test("statik png", statik_dosya_mi("https://a.com/i.png") == True)
test("statik degil php", statik_dosya_mi("https://a.com/p.php") == False)
test("statik degil html", statik_dosya_mi("https://a.com/p.html") == False)

# sure_formatla
test("sure_formatla saniye", sure_formatla(30) == "30.0 saniye")
test("sure_formatla dakika", "1 dakika" in sure_formatla(90))

# renkli_yaz
test("renkli_yaz icerik", "test" in renkli_yaz("test", "RED"))
test("renkli_yaz gecersiz renk", "test" in renkli_yaz("test", "GECERSIZ"))

# ============================================================
print("\n[4/8] ISTEK YONETİCİ TESTLERİ")
# ============================================================
from istek import IstekYonetici

# varsayilan
iy = IstekYonetici()
test("IstekYonetici varsayilan", iy.istek_sayaci == 0 and iy.hata_sayaci == 0)
test("IstekYonetici oturum var", iy.oturum is not None)
test("IstekYonetici verify=False", iy.oturum.verify == False)

# proxy
iy2 = IstekYonetici(proxy="http://127.0.0.1:8080")
test("IstekYonetici proxy ayarlandi", iy2.oturum.proxies.get("http") == "http://127.0.0.1:8080")

# cerez
iy3 = IstekYonetici(cerez="sess=abc; token=xyz")
cerezler = dict(iy3.oturum.cookies.items())
test("IstekYonetici cerez sess", cerezler.get("sess") == "abc")
test("IstekYonetici cerez token", cerezler.get("token") == "xyz")

# ek basliklar
iy4 = IstekYonetici(ek_basliklar={"X-Custom": "test123"})
test("IstekYonetici ek baslik", iy4.oturum.headers.get("X-Custom") == "test123")

# istatistik
stat = iy.istatistik()
test("istatistik toplam_istek", "toplam_istek" in stat)
test("istatistik basari_orani", "basari_orani" in stat)

# erisilemeyen url testi
yanit = iy.get("http://192.0.2.1:9999/yok")  # erisilemeyen url
test("get erisilemeyen url None doner", yanit is None)
test("hata sayaci artti", iy.hata_sayaci > 0)

# ============================================================
print("\n[5/8] MODUL TESTLERİ")
# ============================================================
from moduller import modulleri_yukle, mevcut_modulleri_listele, MODULLER
from moduller.temel_modul import TemelModul
from moduller.sql_enjeksiyon import SqlEnjeksiyonModulu
from moduller.xss import XssModulu
from moduller.lfi import LfiModulu
from moduller.acik_yonlendirme import AcikYonlendirmeModulu
from moduller.csrf import CsrfModulu
from moduller.baslik_guvenlik import BaslikGuvenlikModulu

# modulleri_yukle
test("modulleri_yukle tumu 7", len(modulleri_yukle()) == 7)
test("modulleri_yukle sql,xss", len(modulleri_yukle(["sql", "xss"])) == 2)
test("modulleri_yukle tekli", len(modulleri_yukle(["lfi"])) == 1)
test("modulleri_yukle gecersiz", len(modulleri_yukle(["yok"])) == 0)
test("modulleri_yukle bosluklu", len(modulleri_yukle([" sql ", " xss "])) == 2)

# mevcut_modulleri_listele
aciklamalar = mevcut_modulleri_listele()
test("modul aciklamalari 7 girdi", len(aciklamalar) == 7)
test("sql aciklama var", "sql" in aciklamalar)
test("baslik aciklama var", "baslik" in aciklamalar)

# her modülü baslat ve property kontrol
iy_test = IstekYonetici()
tum_moduller = [
    SqlEnjeksiyonModulu(iy_test),
    XssModulu(iy_test),
    LfiModulu(iy_test),
    AcikYonlendirmeModulu(iy_test),
    CsrfModulu(iy_test),
    BaslikGuvenlikModulu(iy_test),
]

for m in tum_moduller:
    test(f"{m.isim}: isim tanimli", len(m.isim) > 0)
    test(f"{m.isim}: aciklama tanimli", len(m.aciklama) > 0)
    test(f"{m.isim}: TemelModul miras", isinstance(m, TemelModul))
    test(f"{m.isim}: bulgular bos basladi", m.bulgular == [])

# bulgu ekleme/alma/temizleme
m_test = tum_moduller[0]
b = m_test.bulgu_ekle("https://t.com", "Test", "YUKSEK", "test", detay="d", payload="p", kanit="k")
test("bulgu_ekle donus degeri", b["url"] == "https://t.com")
test("bulgu modul ismi", b["modul"] == m_test.isim)
test("bulgu detay", b["detay"] == "d")
test("bulgu payload", b["payload"] == "p")
test("bulgu kanit", b["kanit"] == "k")
test("bulgulari_al 1 sonuc", len(m_test.bulgulari_al()) == 1)
m_test.temizle()
test("temizle sonrasi bos", len(m_test.bulgulari_al()) == 0)

# payload yukleme
test("SQL payloadlar yuklendi", len(SqlEnjeksiyonModulu(iy_test).payloadlar) > 10)
test("XSS payloadlar yuklendi", len(XssModulu(iy_test).payloadlar) > 10)
test("LFI payloadlar yuklendi", len(LfiModulu(iy_test).payloadlar) > 10)
test("Yonlendirme payloadlar yuklendi", len(AcikYonlendirmeModulu(iy_test).payloadlar) > 5)

# CSRF sabit listeler
csrf_m = CsrfModulu(iy_test)
test("CSRF anahtar kelimeleri var", len(csrf_m.CSRF_ANAHTAR_KELIMELERI) > 5)

# Open Redirect sabit listeler
yr_m = AcikYonlendirmeModulu(iy_test)
test("Yonlendirme parametreleri var", len(yr_m.YONLENDIRME_PARAMETRELERI) > 10)

# LFI dosya kalıpları
lfi_m = LfiModulu(iy_test)
test("LFI dosya kaliplari var", len(lfi_m.DOSYA_KALIPLARI) >= 3)

# ============================================================
print("\n[6/8] RAPOR URETICI TESTLERİ")
# ============================================================
from rapor import RaporUretici

# bos rapor
r1 = RaporUretici("https://test.com", [], tarama_suresi=5.5)
r1.konsol_rapor()
test("bos konsol rapor", True)  # cokmediyse basarili

# json rapor
test_bulgular = [
    {"modul": "SQL", "url": "https://t.com", "tip": "SQLi", "risk": RISK_KRITIK,
     "aciklama": "test", "detay": "d", "payload": "p", "kanit": "k"},
    {"modul": "XSS", "url": "https://t.com", "tip": "XSS", "risk": RISK_YUKSEK,
     "aciklama": "test2", "detay": "", "payload": "", "kanit": ""},
]

r2 = RaporUretici("https://test.com", test_bulgular, tarama_suresi=10.0,
                  istek_istatistik={"toplam_istek": 50, "hata_sayisi": 1, "basari_orani": "98.0%"})

json_dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output.json")
json_metin = r2.json_rapor(json_dosya)
test("json rapor dosya olusturuldu", os.path.isfile(json_dosya))

with open(json_dosya, "r", encoding="utf-8") as f:
    veri = json.load(f)
test("json toplam_bulgu", veri["toplam_bulgu"] == 2)
test("json hedef", veri["hedef"] == "https://test.com")
test("json bulgular listesi", len(veri["bulgular"]) == 2)
test("json risk_ozeti var", "risk_ozeti" in veri)
os.remove(json_dosya)

# html rapor
html_dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output.html")
html_metin = r2.html_rapor(html_dosya)
test("html rapor dosya olusturuldu", os.path.isfile(html_dosya))
with open(html_dosya, "r", encoding="utf-8") as f:
    icerik = f.read()
test("html DOCTYPE iceriyor", "<!DOCTYPE html>" in icerik)
test("html tablo iceriyor", "<table>" in icerik)
test("html hedef iceriyor", "test.com" in icerik)
test("html stil iceriyor", "<style>" in icerik)
os.remove(html_dosya)

# konsol rapor (bulgulu)
r2.konsol_rapor()
test("bulgulu konsol rapor", True)

# risk gruplari
gruplar = r2._risk_gruplari()
test("risk gruplari dogru", len(gruplar) == 2)

# ============================================================
print("\n[7/8] TARAYICI MOTOR TESTLERİ")
# ============================================================
from tarayici import Tarayici

# varsayilan
t1 = Tarayici(hedef_url="https://test.com")
test("Tarayici varsayilan hedef", t1.hedef_url == "https://test.com")
test("Tarayici 7 modul", len(t1.moduller) == 7)
test("Tarayici eslesmen=5", t1.eslesmen == 5)

# filtreli
t2 = Tarayici(hedef_url="https://test.com", moduller=["sql", "xss"], eslesmen=2)
test("Tarayici 2 modul", len(t2.moduller) == 2)
test("Tarayici eslesmen=2", t2.eslesmen == 2)

# proxy/cerez
t3 = Tarayici(hedef_url="https://test.com", proxy="http://p:8080", cerez="s=1")
test("Tarayici proxy", t3.istek_yonetici.oturum.proxies.get("http") == "http://p:8080")

# surungan
test("Tarayici surungan var", t3.surungan is not None)
test("Tarayici surungan temel_url", t3.surungan.temel_url == "https://test.com")

# ============================================================
print("\n[8/8] CLI TESTLERİ")
# ============================================================
from ana import arguman_ayristirici

ayristirici = arguman_ayristirici()

# yardim test
test("argparse prog", ayristirici.prog == "feeble")

# geçerli argümanlar
args1 = ayristirici.parse_args(["-u", "https://test.com", "--tam-tarama"])
test("CLI url parse", args1.url == "https://test.com")
test("CLI tam-tarama", args1.tam_tarama == True)
test("CLI varsayilan cikti", args1.cikti == "konsol")

args2 = ayristirici.parse_args(["-u", "https://t.com", "-m", "sql,xss", "-c", "json", "-d", "out.json"])
test("CLI moduller parse", args2.moduller == "sql,xss")
test("CLI cikti json", args2.cikti == "json")
test("CLI dosya parse", args2.dosya == "out.json")

args3 = ayristirici.parse_args(["-u", "https://t.com", "--surungan-yok", "--proxy", "http://p:80", "--cerez", "s=1", "-t", "3"])
test("CLI surungan-yok", args3.surungan_yok == True)
test("CLI proxy", args3.proxy == "http://p:80")
test("CLI cerez", args3.cerez == "s=1")
test("CLI thread", args3.thread == 3)

args4 = ayristirici.parse_args(["-u", "https://t.com", "--derinlik", "5", "--maks-sayfa", "50"])
test("CLI derinlik", args4.derinlik == 5)
test("CLI maks-sayfa", args4.maks_sayfa == 50)

args5 = ayristirici.parse_args(["-u", "https://t.com", "--modul-listesi"])
test("CLI modul-listesi", args5.modul_listesi == True)

args6 = ayristirici.parse_args(["-u", "https://t.com", "--gecikme", "0.5"])
test("CLI gecikme parse", args6.gecikme == 0.5)

args7 = ayristirici.parse_args(["-u", "https://t.com", "--cerez-b", "s=2", "--waf-bypass", "--js-surungan", "--sablonlar", "sablonlar/"])
test("CLI cerez-b parse", args7.cerez_b == "s=2")
test("CLI waf-bypass parse", args7.waf_bypass == True)
test("CLI js-surungan parse", args7.js_surungan == True)
test("CLI sablonlar parse", args7.sablonlar == "sablonlar/")

# ============================================================
print("\n[9/9] İLERİ DÜZEY MOTOR TESTLERİ")
# ============================================================
from waf_mutasyon import WafMutator
from surungan_js import SurunganJs
from oob_dinleyici import OobYonetici
from moduller.bola_idor import BolaIdorModulu
from sablon_motoru import SablonMotoru

wm = WafMutator()
mutlar = wm.mutasyon_uret("SELECT * FROM users")
test("WafMutator mutasyon uretti", len(mutlar) > 1)

sjs = SurunganJs("https://test.com")
test("SurunganJs olusturuldu", sjs.temel_url == "https://test.com")

oob = OobYonetici()
j_id, c_url = oob.jeton_uret("SSRF", "https://test.com")
test("OobYonetici jeton uretti", len(j_id) == 8 and "oob" in c_url)

from istek import IstekYonetici
iy = IstekYonetici()
bola = BolaIdorModulu(iy, cerez_b="session=b")
test("BolaIdorModulu olusturuldu", bola.cerez_b == "session=b")

sm = SablonMotoru(iy)
test("SablonMotoru olusturuldu", sm is not None)

# ============================================================
# ÖZET
# ============================================================
print("\n" + "=" * 60)
toplam = basarili + len(hatalar)
print(f"  SONUC: {basarili}/{toplam} test basarili")
if hatalar:
    print(f"  BASARISIZ ({len(hatalar)}):")
    for h in hatalar:
        print(f"    - {h}")
else:
    print("  TUM TESTLER BASARILI!")
print("=" * 60)
