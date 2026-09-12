import pygame
import sys
import os
from tkinter import filedialog, Tk  # Dosya seçici için gerekli kütüphaneler
import re
# NOT: Kendi projenizdeki move_capture fonksiyonunu buraya import etmelisiniz
# from Satranc import move_capture 
import Sabitler as C
import Tahta as T
import Satranc as S

pygame.init()
pygame.font.init()
# Tkinter'ın boş bir ana pencere açmasını engellemek için arka planda gizliyoruz
root = Tk()
root.withdraw()

GENISLIK, YUKSEKLIK = 1050, 750 # Butonlar için yüksekliği biraz artırdık
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Commodore Nejat - PGN Interactive Viewer")

# Commodore 64 Renk Paleti
C64_LACIVERT = (0, 0, 136)
C64_MAVI     = (53, 136, 253)
BEYAZ        = (255, 255, 255)
SIYAH        = (0, 0, 0)
GRI          = (150, 150, 150)
AÇIK_GRI     = (240, 240, 240)
AKTIF_SARI   = (255, 215, 0)

FONT_14 = pygame.font.SysFont("Courier New", 14, bold=True)
FONT_SISTEM = pygame.font.SysFont("Courier New", 16, bold=True)
FONT_BASLIK = pygame.font.SysFont("Courier New", 20, bold=True)

# -------------------------------------------------------------
# VERİ VE DURUM YÖNETİMİ
# -------------------------------------------------------------
oyun_listesi = []
saf_hamleler = []
"""
try:
    saf_hamleler = PgnDosyaOkuyucu.pgn_oku("ornek.pgn")
except Exception:
    saf_hamleler = []
"""
secilen_oyun = None
secilen_oyun_indeksi = -1
mevcut_hamle_sirasi = -1 # -1: Başlangıç konumu, 0: İlk hamle yapıldı, 1: İkinci...
global hamle_yapildi
hamle_yapildi=False

# -------------------------------------------------------------
# ARAYÜZ BÖLGELERİ (RECTANGLE)
# -------------------------------------------------------------
rSOL_PANEL   = pygame.Rect(10, 10, 280, 620)
rORTA_PANO   = pygame.Rect(300, 10, 400, 400)
rSAG_PANEL   = pygame.Rect(760, 10, 280, 620)

# Oynatıcı Kontrol Butonları (Tahtanın hemen altında)

rBUTON_BASA  = pygame.Rect(320, 650, 85, 40)
rBUTON_GERI  = pygame.Rect(425, 650, 85, 40)
rBUTON_ILERI = pygame.Rect(530, 650, 85, 40)
rBUTON_SONA  = pygame.Rect(635, 650, 85, 40)

# Oynatıcı Kontrol Butonları (Tahtanın hemen altında)

rBUTON_PGN_YUKLE  = pygame.Rect(425, 700, 85, 40)
rBUTON_PGN_SAKLA = pygame.Rect(530, 700, 85, 40)

# -------------------------------------------------------------
# TAHTAYI BELİRLİ BİR HAMLE ANINA GETİREN MOTOR FONKSİYON
# -------------------------------------------------------------
class PgnOyun:
    def __init__(self):
        self.bilgiler = {}
        self.hamle_metni = ""
        self.saf_hamleler = []  # Bizim motorun sırayla tüketeceği liste ['e4', 'e5', 'Nf3', 'Nc6']

    def hamleleri_temizle(self):
        """Metin halindeki hamleleri temiz bir listeye dönüştürür"""
        # 1. Parantez içindeki yorumları ve varyantları temizle
        temiz_metin = re.sub(r'\{.*?\}|\(.*?\)', '', self.hamle_metni)
        # 2. Hamle numaralarını temizle (Örn: "1.", "2...")
        temiz_metin = re.sub(r'\d+\.+\s*', '', temiz_metin)
        # 3. Oyun sonucunu temizle (1-0, 0-1, 1/2-1/2)
        temiz_metin = re.sub(r'(1-0|0-1|1/2-1/2|\*)', '', temiz_metin)
        # 4. Gereksiz boşlukları temizle ve listeye böl
        self.saf_hamleler = [h for h in temiz_metin.split() if h]


    def xxxhamleleri_temizle(self):
        """
        Hamle metnindeki '1.', '2...', '{yorumlar}' ve '1-0' gibi 
        fazlalıkları temizler, geriye sadece saf hamle string listesini bırakır.
        """
        # 1. Kıvrımlı parantez içindeki yorumları siliyoruz: { ... }
        metin = re.sub(r'\{.*?\}', '', self.hamle_metni)
        
        # 2. Hamle numaralarını ve noktalarını siliyoruz: '1.', '2...', '12.'
        metin = re.sub(r'\d+\.+\s*', '', metin)
   
class PgnDosyaOkuyucu:
    @staticmethod
    def pgn_oku(dosya_yolu):
        """PGN dosyasını okur ve içindeki tüm oyunları nesne olarak listeler"""
        oyunlar = []
        mevcut_oyun = PgnOyun()
        hamle_blogu = False

        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            for satir in f:
                satir = satir.strip()
                if not satir: continue

                # 1. Bilgi Etiketlerini Yakala: [Metot "Değer"]
                if satir.startswith('['):
                    if hamle_blogu: # Yeni bir oyuna geçildiyse eskisini kaydet
                        mevcut_oyun.hamleleri_temizle()
                        oyunlar.append(mevcut_oyun)
                        mevcut_oyun = PgnOyun()
                        hamle_blogu = False
                    
                    eslesme = re.match(r'\[(\w+)\s+"(.*?)"\]', satir)
                    if eslesme:
                        anahtar, deger = eslesme.groups()
                        mevcut_oyun.bilgiler[anahtar] = deger

                # 2. Hamle Satırlarını Yakala
                else:
                    hamle_blogu = True
                    mevcut_oyun.hamle_metni += satir + " "

            # Son oyunu listeye ekle
            if mevcut_oyun.hamle_metni:
                mevcut_oyun.hamleleri_temizle()
                oyunlar.append(mevcut_oyun)

        return oyunlar

def dosya_sec_ve_yukle():
    global oyun_listesi, secilen_oyun, secilen_oyun_indeksi, mevcut_hamle_sirasi
    
    # Kullanıcıya sadece .pgn dosyalarını gösteren sistem penceresini açar
    dosya_yolu = filedialog.askopenfilename(
        title="Bir PGN Dosyası Seçin",
        filetypes=[("PGN Satranç Dosyası", "*.pgn"), ("Tüm Dosyalar", "*.*")]
    )
    
    if dosya_yolu: # Eğer kullanıcı iptal etmeyip bir dosya seçtiyse
        # Parser modülümüzü çağırıp yeni oyunları listeye yüklüyoruz
        oyun_listesi = PgnDosyaOkuyucu.pgn_oku(dosya_yolu)
        
        # Yeni dosya yüklenince eski seçimleri ve tahtayı sıfırlıyoruz
        secilen_oyun = None
        secilen_oyun_indeksi = -1
        mevcut_hamle_sirasi = -1
        print(f"Başarıyla yüklendi: {os.path.basename(dosya_yolu)} ({len(oyun_listesi)} Oyun bulundu)")



    # === C. İLERİDE EKLENECEK ÖZEL DURUMLAR (Piyon Terfi vb.) ===
    # İleride buraya 'Geçerken Alma' veya 'Piyon Vezir Oldu mu?' kurallarını 
    # ana kodu hiç bozmadan sadece buraya bir 'if' ekleyerek temizce koyabiliriz.
# -------------------------------------------------------------
# ÇİZİM FONKSİYONU
# -------------------------------------------------------------
def arayuz_ciz():
    global oyun_listesi
    ekran.fill(C64_LACIVERT)
    
    # 1. SOL PANEL: OYUN LİSTESİ VE DOSYA AÇ BUTONU
    pygame.draw.rect(ekran, C64_MAVI, rSOL_PANEL)
    pygame.draw.rect(ekran, BEYAZ, rSOL_PANEL, 2)
    
    txt_baslik = FONT_BASLIK.render("OYUN LİSTESİ", True, BEYAZ)
    ekran.blit(txt_baslik, (rSOL_PANEL.x + 10, rSOL_PANEL.y + 10))
    
    
    for idx, oyun in enumerate(oyun_listesi):
        rBUTON = pygame.Rect(rSOL_PANEL.x + 10, rSOL_PANEL.y + 110 + (idx * 60), 260, 50)
        renk_arka = BEYAZ if idx == secilen_oyun_indeksi else C64_LACIVERT
        renk_yazi = SIYAH if idx == secilen_oyun_indeksi else BEYAZ
        pygame.draw.rect(ekran, renk_arka, rBUTON)
        pygame.draw.rect(ekran, BEYAZ, rBUTON, 1)
        
        beyaz = oyun.bilgiler.get("White", "Bilinmeyen")
        siyah = oyun.bilgiler.get("Black", "Bilinmeyen")
        txt_oyun = FONT_SISTEM.render(f"{beyaz} vs {siyah}", True, renk_yazi)
        ekran.blit(txt_oyun, (rBUTON.x + 5, rBUTON.y + 15))
    """
    # 2. ORTA PANEL: SATRANÇ PANOSU VE KONTROL BUTONLARI
    #pygame.draw.rect(ekran, AÇIK_GRI, rORTA_PANO)
    pygame.draw.rect(ekran, SIYAH, rORTA_PANO, 2)
    """
    #T.TahtaEkranda()
    
    # Oynatıcı Butonlarını Çiz (Geri/İleri)
    for btn, txt in [(rBUTON_BASA, "|<"), (rBUTON_GERI, "<"), (rBUTON_ILERI, ">"), (rBUTON_SONA, ">|")]:
        pygame.draw.rect(ekran, C64_MAVI, btn)
        pygame.draw.rect(ekran, BEYAZ, btn, 2)
        txt_btn = FONT_BASLIK.render(txt, True, BEYAZ)
        ekran.blit(txt_btn, (btn.x + (btn.width - txt_btn.get_width())//2, btn.y + 8))
    # PGN Butonlarını Çiz (Geri/İleri)
    for btn, txt in [(rBUTON_PGN_YUKLE, "PGN YÜKLE"), (rBUTON_PGN_SAKLA, "PGN SAKLA")]:
        pygame.draw.rect(ekran, C64_MAVI, btn)
        pygame.draw.rect(ekran, BEYAZ, btn, 2)
        txt_btn = FONT_14.render(txt, True, BEYAZ)
        ekran.blit(txt_btn, (btn.x + (btn.width - txt_btn.get_width())//2, btn.y + 8))

    # 3. SAĞ PANEL: HAMLE PANOSU (TIKLANABİLİR)
    pygame.draw.rect(ekran, C64_MAVI, rSAG_PANEL)
    pygame.draw.rect(ekran, BEYAZ, rSAG_PANEL, 2)
    txt_h_baslik = FONT_BASLIK.render("HAMLE LİSTESİ", True, BEYAZ)
    ekran.blit(txt_h_baslik, (rSAG_PANEL.x + 10, rSAG_PANEL.y + 10))
    #print(secilen_oyun,"sec")
    if secilen_oyun is not None:
        for i, hamle in enumerate(secilen_oyun.saf_hamleler):
            if i % 2 == 0:
                satir = (i // 2) + 1
                metin = f"{satir}. {hamle}"
                #print(satir,hamle,"sat")
                sutun = 0
            else:
                metin = f"{hamle}"
                sutun = 1
                #print(sutun,hamle,"sut")
            # Her hamle metni için tıklanabilir hayali bir küçük alan oluşturuyoruz
            pos_x = rSAG_PANEL.x + 20 + (sutun * 100)
            pos_y = rSAG_PANEL.y + 50 + (satir * 25)
            rHAMLE_TIK = pygame.Rect(pos_x, pos_y, 80, 20)
            
            # Eğer şu an tahtada gösterilen hamleyse rengini Sarı (Aktif) yap
            renk_hamle = AKTIF_SARI if i == mevcut_hamle_sirasi else BEYAZ
            
            txt_hamle = FONT_SISTEM.render(metin, True, renk_hamle)
            ekran.blit(txt_hamle, (pos_x, pos_y))


#---------------PGN--------------------
def hamle_oku_belirle(pgn_hamle, renk):
    # 1. PGN metnindeki gereksiz karakterleri temizle (+, #, !, ? gibi)
    hamle = pgn_hamle.replace("+", "").replace("#", "").replace("!", "").replace("?", "")
    
    # ROK KONTROLÜ
    if hamle in ["O-O", "0-0"]: # Şah kanadı roku
        kaynak = 60 if renk == 1 else 4  # Sizin tahta diziliminize göre Şah başlangıç indeksi
        hedef = kaynak + 2
        return kaynak, hedef
    elif hamle in ["O-O-O", "0-0-0"]: # Vezir kanadı roku
        kaynak = 60 if renk == 1 else 4
        hedef = kaynak - 2
        return kaynak, hedef

    # HEDEF KAREYİ BULMA (Her zaman string'in son iki karakteridir: örn 'f3', 'e4')
    # Eğer terfi varsa (örn: 'e8=Q'), terfi karakterini ayıkla
    terfi_tasi = None
    if "=" in hamle:
        hamle, terfi_tasi = hamle.split("=")
        
    hedef_notasyon = hamle[-2:] # örn: 'f3'
    # 'a1' -> sütun:0, satır:7 mantığıyla 64'lük dizideki indekse çeviren fonksiyonunuz:
    hedef_kare = notasyonu_indekse_cevir(hedef_notasyon) 

    # TAŞ TİPİNİ BELİRLEME
    # İlk karakter büyük harfse taştır (N, B, R, Q, K), küçük harfse piyon hamlesidir
    ilk_karakter = hamle[0]
    if ilk_karakter in ['N', 'B', 'R', 'Q', 'K']:
        tas_tipi = ilk_karakter
        ipucu_metni = hamle[1:-2].replace("x", "") # Örn: 'Nbd7' ise ipucu 'b' kalır, 'Nf3' ise boş kalır
    else:
        tas_tipi = 'P' # Piyon
        ipucu_metni = hamle[:-2].replace("x", "") # Örn: 'exd5' ise ipucu 'e' (kaynak sütun) kalır

    # TERSİNE TARAMA VE YASAL ADAYI BULMA
    # Tahtadaki 64 kareyi tarayıp, o renkteki ve o tipteki taşları buluyoruz
    adaylar = []
    for kare_indeks in range(64):
        print(kare_indeks,"****",renk,T.RENK[kare_indeks],"   ",tas_tipi,harf_karsiligi(T.TAS[kare_indeks]))
        if T.RENK[kare_indeks] == renk and harf_karsiligi(T.TAS[kare_indeks]) == tas_tipi:
            # Bu taş hedef kareye yasal olarak gidebiliyor mu?
            if S.hamle_yasal_mi(kare_indeks, hedef_kare, renk):
                adaylar.append(kare_indeks)
                print(renk,kare_indeks,"***")
    # AYRIMI NETLEŞTİRME (Disambiguation)
    # Eğer birden fazla taş aynı yere gidebiliyorsa (örn: iki kale de d1'e gelebiliyor, 'R1d1' veya 'Rad1')
    if len(adaylar) == 1:
        return adaylar[0], hedef_kare
    elif len(adaylar) > 1:
        for aday in adaylar:
            aday_notasyon = indeksi_notasyona_cevir(aday) # örn: 'a1' -> sütun 'a', satır '1'
            # PGN'deki ipucu karakteri adayın sütununda veya satırında var mı kontrol et
            if ipucu_metni in aday_notasyon:
                return aday, hedef_kare

    return None, None # Hata durumu

def pgn_sonraki_hamle_oynat():
    global secilen_oyun, mevcut_hamle_sirasi
    
    if not secilen_oyun: return
    
    # Sıradaki hamle indeksini artır
    mevcut_hamle_sirasi += 1
    
    # Oyun bitti mi kontrolü
    if mevcut_hamle_sirasi >= len(secilen_oyun.saf_hamleler):
        print("Oyun bitti!")
        return

    # Sıradaki hamle metnini al (Örn: 'Nf3')
    pgn_hamle = secilen_oyun.saf_hamleler[mevcut_hamle_sirasi]
    
    # Sıra kimde? (0: Beyaz, 1: Siyah mantığınıza göre veya tam tersi)
    # Çift indeksler (0, 2, 4...) Beyaz, Tek indeksler (1, 3, 5...) Siyah hamlesidir
    renk = 1 if (mevcut_hamle_sirasi % 2 == 0) else 0 
    print(mevcut_hamle_sirasi,renk,"sıra renk")
    # Sizinle az önce tasarladığımız o ortak Satranc fonksiyonlarını çağırıyoruz:
    # 1. Metinden kaynak ve hedef kare indekslerini bul (Tersine tarama)
    kaynak, hedef = hamle_oku_belirle(pgn_hamle, renk)
    
    if kaynak is not None and hedef is not None:
        # 2. Yasallığından zaten eminiz (Tersine taramada kontrol edildi), doğrudan UYGULA!
        hamle_uygula(kaynak, hedef)
        print(f"Oynatılan PGN Hamlesi: {pgn_hamle} (Kaynak: {kaynak} -> Hedef: {hedef})")
    else:
        print(f"Hata: {pgn_hamle} hamlesi için kaynak/hedef çözülemedi!")# -------------------------------------------------------------


def pgn_konumunu_guncelle(hedef_hamle_indeksi):
    """
    Oyunu en baştan (başlangıç konumundan) alır ve 
    hedef_hamle_indeksi'ne kadar olan tüm hamleleri sırayla uygulayarak tahtayı senkronize eder.
    """
    global mevcut_hamle_sirasi, secilen_oyun
    
    if not secilen_oyun: return

    # 1. Tahtayı başlangıç (fabrika ayarları) konumuna getiriyoruz
    tahtayi_sifirla_ve_baslat() # T.TAS ve T.RENK dizilerinizi ilk haline getiren fonksiyonunuz
    
    # 2. Rok ve En-passant bayraklarını ilk konumuna çekiyoruz
    T.en_passant_kare = None
    T.beyaz_sah_hareket_etti = False
    T.siyah_sah_hareket_etti = False
    # (Varsa kale bayraklarınız da burada sıfırlanır)

    # 3. İlk hamleden hedef indekse kadar tahtayı hızlıca simüle ederek kuruyoruz
    for i in range(hedef_hamle_indeksi + 1):
        pgn_hamle = secilen_oyun.saf_hamleler[i]
        renk = 1 if (i % 2 == 0) else 0 # Çift indeks Beyaz, Tek indeks Siyah
        
        # Sizinle yazdığımız tersine tarama ve yasal karar mekanizması
        kaynak, hedef = hamle_oku_belirle(pgn_hamle, renk)
        
        if kaynak is not None and hedef is not None:
            # Buradaki hamle_uygula en sonda otomatik senkronize_et() çağırıyor
            hamle_uygula(kaynak, hedef)
            
    # 4. Mevcut indeks kaydını güncelle
    mevcut_hamle_sirasi = hedef_hamle_indeksi
    
    # 5. Görsel matrisi ve yan paneli nihai olarak tazele
    senkronize_et()
    taslari_tahtaya_yerlestir()

def pgn_ileri_git():
    global mevcut_hamle_sirasi, secilen_oyun
    if not secilen_oyun: return
    
    # Eğer oynatılacak sonraki bir hamle varsa indeksi artır ve konumu kur
    if mevcut_hamle_sirasi + 1 < len(secilen_oyun.saf_hamleler):
        pgn_konumunu_guncelle(mevcut_hamle_sirasi + 1)
        print(f"İleri sarıldı. Hamle No: {mevcut_hamle_sirasi + 1}")

def pgn_geri_git():
    global mevcut_hamle_sirasi, secilen_oyun
    if not secilen_oyun: return
    
    # Eğer geri gidilecek hamle varsa bir azalt, en başa dönmek için -1'e kadar izin ver
    if mevcut_hamle_sirasi >= 0:
        pgn_konumunu_guncelle(mevcut_hamle_sirasi - 1)
        print(f"Geri sarıldı. Mevcut Hamle İndeksi: {mevcut_hamle_sirasi}")

def notasyonu_indekse_cevir(notasyon):
    """
    Örnek: 'e4' -> sütun: 4 (e), satır: 4 (8-4) -> İndeks hesaplar
    Beyazlar altta (7. satır), Siyahlar üstte (0. satır) mantığına göredir.
    """
    if len(notasyon) < 2: 
        return None
        
    sutun_harf = notasyon[0].lower() # 'e'
    satir_rakam = notasyon[1]        # '4'
    
    # Harfleri 0-7 arası sütun indeksine çeviriyoruz
    # 'a'=0, 'b'=1, 'c'=2, 'd'=3, 'e'=4, 'f'=5, 'g'=6, 'h'=7
    sutun = ord(sutun_harf) - ord('a')
    
    # Satırları 0-7 arası bilgisayar satır indeksine çeviriyoruz
    # Satrançta 8. satır yukarıdadır (indeks 0), 1. satır aşağıdadır (indeks 7)
    satir = 8 - int(satir_rakam)
    
    # 64'lük tek boyutlu dizi indeks formülü: (Satır * 8) + Sütun
    indeks = (satir * 8) + sutun
    return indeks

def indeksi_notasyona_cevir(indeks):
    """
    Örnek: 21 -> satır ve sütun hesaplar -> 'f3' stringini döner.
    """
    satir = indeks // 8
    sutun = indeks % 8
    
    # Sütun indeksini harfe geri çeviriyoruz (0 -> 'a', 5 -> 'f')
    sutun_harf = chr(ord('a') + sutun)
    
    # Bilgisayar satır indeksini satranç satırına çeviriyoruz (0 -> '8', 7 -> '1')
    satir_rakam = str(8 - satir)
    
    return sutun_harf + satir_rakam

def harf_karsiligi(tas_no):
    """T.TAS içindeki sayısal kodların PGN harf karşılıkları"""
    sozluk = {
        0: 'P',  # Piyon (Pawn)
        1: 'N',  # At (Knight)
        2: 'B',  # Fil (Bishop)
        3: 'R',  # Kale (Rook)
        4: 'Q',  # Vezir (Queen)
        5: 'K'   # Şah (King)
    }
    return sozluk.get(tas_no, '')

def tahtayi_hamleye_gore_guncelle(oyun, hamle_hedef_indeksi):
    global hamle_yapildi
    global renk
    """
    Oyunun en başına döner ve hedef indekse kadar olan tüm hamleleri
    hamle_oku_belirle kullanarak sırayla tahta üzerinde simüle eder.
    """
    # 1. Önce tahtayı ilk kurulum konumuna getirin (T.tAHTA_doldur() gibi)
    T.tAHTA_doldur() 
    if hamle_hedef_indeksi == -1:
        return # Başlangıç konumundaysak taşları yürütmeye gerek yok

    # 2. Hedef hamleye kadar olan geçmişi simüle et

    renk = 1 # 0=BEYAZ, 1=SIYAH (Sizin C.BEYAZ sisteminize göre)
    for i in range(hamle_hedef_indeksi + 1):
        hamle_metni = oyun.saf_hamleler[i]
        print(hamle_metni, renk,"hamle")
        if not hamle_yapildi:
            pygame.time.delay(500) # Bir saniye daha bekle
            
        # Sizin yazdığınız move_capture motorunu çağırıyoruz
        eski_idx, yeni_idx = hamle_oku_belirle(hamle_metni, renk)
        
        # Arka plandaki matrisi yürütüyoruz
        print(eski_idx, yeni_idx,hamle_yapildi)
        if eski_idx is not None :
            T.TAS[yeni_idx] = T.TAS[eski_idx]
            T.RENK[yeni_idx] = T.RENK[eski_idx]
            T.TAS[eski_idx] = 6
            T.RENK[eski_idx] = C.BOS
            T.kare_lere_tasi_yerlestir()
            pygame.time.delay(500) # Bir saniye daha bekle
            hamle_yapildi=True
        # Sıra değişimi (Siyah <-> Beyaz)
        renk = 1 if renk == 0 else 0

    # 3. Grafik arayüze taşları yerleştirin
    T.kare_lere_tasi_yerlestir()

# MAIN GAME LOOP
# -------------------------------------------------------------

sira_kimde=C.SIYAH
T.tAHTA_doldur()

# Test hamlesinin sadece BİR KEZ çalışması için bir kontrol bayrağı (flag) koyuyoruz

 
hamle_yapildi = False

running = True
while running:
    fare_konum = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # A. DOSYA AÇ BUTONUNA TIKLANDI MI?
                if rBUTON_PGN_YUKLE.collidepoint(fare_konum):
                    dosya_sec_ve_yukle()
                    continue # Döngünün başına dön, alt listeleri tarama
                
                # B. OYUN LİSTESİ SEÇİMİ (Y değerini yeni düzene göre güncelledik: y + 110)
                for idx, oyun in enumerate(oyun_listesi):
                    rBUTON = pygame.Rect(rSOL_PANEL.x + 10, rSOL_PANEL.y + 110 + (idx * 60), 260, 50)
                    if rBUTON.collidepoint(fare_konum):
                        secilen_oyun = oyun
                        secilen_oyun_indeksi = idx
                        print("idx",idx)
                        mevcut_hamle_sirasi = -1
                        tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                        break
                # B. OYNATICI BUTON KONTROLLERİ
                if secilen_oyun is not None:
                    toplam_hamle = len(secilen_oyun.saf_hamleler)
                    
                    if rBUTON_BASA.collidepoint(fare_konum):
                        mevcut_hamle_sirasi = -1
                        tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                    elif rBUTON_GERI.collidepoint(fare_konum):
                        if mevcut_hamle_sirasi > -1:
                            mevcut_hamle_sirasi -= 1
                            tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                    elif rBUTON_ILERI.collidepoint(fare_konum):
                        if mevcut_hamle_sirasi < toplam_hamle - 1:
                            mevcut_hamle_sirasi += 1
                            tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                    elif rBUTON_SONA.collidepoint(fare_konum):
                        mevcut_hamle_sirasi = toplam_hamle - 1
                        tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)

                    # C. SAĞ PANELDEKİ HAMLEYE DOĞRUDAN TIKLAMA
                    for i in range(toplam_hamle):
                        if i % 2 == 0:
                            sat_idx = (i // 2) + 1
                            sut_idx = 0
                        else:
                            sut_idx = 1
                        
                        p_x = rSAG_PANEL.x + 20 + (sut_idx * 100)
                        p_y = rSAG_PANEL.y + 50 + (sat_idx * 25)
                        rHAMLE_KUTU = pygame.Rect(p_x, p_y, 80, 20)
                        
                        if rHAMLE_KUTU.collidepoint(fare_konum):
                            mevcut_hamle_sirasi = i
                            tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                            break

    
    arayuz_ciz()
    T.TekTahtaEkranda()
    
    
    
    
   
    pygame.display.flip()
    
pygame.quit()
sys.exit()
