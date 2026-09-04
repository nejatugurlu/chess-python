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
"""
try:
    oyun_listesi = PgnDosyaOkuyucu.pgn_oku("ornek.pgn")
except Exception:
    oyun_listesi = []
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
        self.bilgiler = {}  # Oyuncu adları, tarih, sonuç vb.
        self.hamle_metni = "" # "1. e4 e5 2. Nf3..." hamle zinciri
        self.hamle_listesi = [] # Temizlenmiş hamle listesi ["e4", "e5", "Nf3", "..."]

    def hamleleri_temizle(self):
        """Metin halindeki hamleleri temiz bir listeye dönüştürür"""
        # 1. Parantez içindeki yorumları ve varyantları temizle
        temiz_metin = re.sub(r'\{.*?\}|\(.*?\)', '', self.hamle_metni)
        # 2. Hamle numaralarını temizle (Örn: "1.", "2...")
        temiz_metin = re.sub(r'\d+\.+\s*', '', temiz_metin)
        # 3. Oyun sonucunu temizle (1-0, 0-1, 1/2-1/2)
        temiz_metin = re.sub(r'(1-0|0-1|1/2-1/2|\*)', '', temiz_metin)
        # 4. Gereksiz boşlukları temizle ve listeye böl
        self.hamle_listesi = [h for h in temiz_metin.split() if h]

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


def tahtayi_hamleye_gore_guncelle(oyun, hamle_hedef_indeksi):
    global hamle_yapildi
    """
    Oyunun en başına döner ve hedef indekse kadar olan tüm hamleleri
    move_capture kullanarak sırayla tahta üzerinde simüle eder.
    """
    # 1. Önce tahtayı ilk kurulum konumuna getirin (T.tAHTA_doldur() gibi)
    T.tAHTA_doldur() 
    if hamle_hedef_indeksi == -1:
        return # Başlangıç konumundaysak taşları yürütmeye gerek yok

    # 2. Hedef hamleye kadar olan geçmişi simüle et
    sira = 0 # 0=BEYAZ, 1=SIYAH (Sizin C.BEYAZ sisteminize göre)
    for i in range(hamle_hedef_indeksi + 1):
        hamle_metni = oyun.hamle_listesi[i]
        print(hamle_metni, sira)
        if not hamle_yapildi:
            pygame.time.delay(250) # 1/4 saniye daha bekle
            
        # Sizin yazdığınız move_capture motorunu çağırıyoruz
        
        sonuc = move_capture(hamle_metni, sira)
        
        if isinstance(sonuc,str):
            hamle_sonrasi_ozel_durumlar(sonuc, sira)
            hamle_yapildi= True
            T.kare_lere_tasi_yerlestir()
            pygame.time.delay(250) # 1/4 saniye daha bekle

            
        else:
            eski_idx, yeni_idx, kaynak_j, kaynak_i, hedef_satir, hedef_sutun = sonuc
            
        
        # Arka plandaki matrisi yürütüyoruz
        print(eski_idx, yeni_idx,hamle_yapildi)
        if eski_idx is not None :
            tasobj_tasi(kaynak_j, kaynak_i,hedef_satir,hedef_sutun)
            """
            T.TAS[yeni_idx] = T.TAS[eski_idx]
            T.RENK[yeni_idx] = T.RENK[eski_idx]
            T.TAS[eski_idx] = 6
            T.RENK[eski_idx] = C.BOS
            T.kare_lere_tasi_yerlestir()
            """
            pygame.time.delay(250) # 1/4 saniye daha bekle
            hamle_yapildi=True
            
        # Sıra değişimi (Siyah <-> Beyaz)
        sira = 1 if sira == 0 else 0

    # 3. Grafik arayüze taşları yerleştirin
    T.kare_lere_tasi_yerlestir()

def hamle_sonrasi_ozel_durumlar(sonuc, hamle_rengi):
    """
    Okunabilirliği artırmak için rok, piyon terfi vb. 
    tüm yan senaryoları burada topluyoruz.
    """

    # === A. KISA ROK SENARYOSU ===
    if sonuc == "KISA_ROK":
        if hamle_rengi == 0:  # BEYAZ (Satır 0)
            T.TAS[6], T.RENK[6] = 5, 0      # Şah e1 -> g1
            T.TAS[5], T.RENK[5] = 4, 0      # Kale h1 -> f1
            T.TAS[4], T.RENK[4] = 6, 2                     # e1 boşalt
            T.TAS[7], T.RENK[7] = 6, 2                     # h1 boşalt
        else:  # SİYAH (Satır 7)
            T.TAS[62], T.RENK[62] = 5, 1  # Şah e8 -> g8
            T.TAS[61], T.RENK[61] = 4, 1  # Kale h8 -> f8
            T.TAS[60], T.RENK[60] = 6, 2                   # e8 boşalt
            T.TAS[63], T.RENK[63] = 6, 2                   # h8 boşalt
 
    # === B. UZUN ROK SENARYOSU ===
    elif sonuc == "UZUN_ROK":
        if hamle_rengi == 1:  # BEYAZ (Satır 0)
            T.TAS[2], T.RENK[2] = 5, 0      # Şah e1 -> c1
            T.TAS[3], T.RENK[3] = 4, 0      # Kale a1 -> d1
            T.TAS[4], T.RENK[4] = 6, 2                     # e1 boşalt
            T.TAS[0], T.RENK[0] = 6, 2                     # a1 boşalt
        else:  # SİYAH (Satır 7)
            T.TAS[58], T.RENK[58] = 5, 1  # Şah e8 -> c8
            T.TAS[59], T.RENK[59] = 4, 1  # Kale a8 -> d8
            T.TAS[60], T.RENK[60] = 6, 2                   # e8 boşalt
            T.TAS[56], T.RENK[56] = 6, 2                   # a8 boşalt
    return

    # === C. İLERİDE EKLENECEK ÖZEL DURUMLAR (Piyon Terfi vb.) ===
    # İleride buraya 'Geçerken Alma' veya 'Piyon Vezir Oldu mu?' kurallarını 
    # ana kodu hiç bozmadan sadece buraya bir 'if' ekleyerek temizce koyabiliriz.
# -------------------------------------------------------------
# ÇİZİM FONKSİYONU
# -------------------------------------------------------------
def arayuz_ciz():
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
    
    if secilen_oyun is not None:
        for i, hamle in enumerate(secilen_oyun.hamle_listesi):
            if i % 2 == 0:
                satir = (i // 2) + 1
                metin = f"{satir}. {hamle}"
                sutun = 0
            else:
                metin = f"{hamle}"
                sutun = 1
            
            # Her hamle metni için tıklanabilir hayali bir küçük alan oluşturuyoruz
            pos_x = rSAG_PANEL.x + 20 + (sutun * 100)
            pos_y = rSAG_PANEL.y + 50 + (satir * 25)
            rHAMLE_TIK = pygame.Rect(pos_x, pos_y, 80, 20)
            
            # Eğer şu an tahtada gösterilen hamleyse rengini Sarı (Aktif) yap
            renk_hamle = AKTIF_SARI if i == mevcut_hamle_sirasi else BEYAZ
            
            txt_hamle = FONT_SISTEM.render(metin, True, renk_hamle)
            ekran.blit(txt_hamle, (pos_x, pos_y))


#---------------PGN--------------------


def pgn_karesini_koordinata(kare_str):
    # kare_str örn: "d4"
    sutun = ord(kare_str[0]) - ord('a') # d -> 3
    yatay = int(kare_str[1]) - 1        # 4 -> 3
    
    # Siyahlar AŞAĞIDA ise: 1. yatay en üsttedir (Satır 0), 8. yatay en alttadır (Satır 7)
    satir = yatay 
    return satir, sutun

def move_capture(pgn_hamle, renk):
    # 1. Temizlik: Şah çekme (+), mat (#) işaretlerini kaldır (x işaretini şimdilik tutuyoruz!)
    hamle = pgn_hamle.replace("+", "").replace("#", "")
    
    if hamle == "O-O": return "KISA_ROK"
    if hamle == "O-O-O": return "UZUN_ROK"

    tas_harfleri = {'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5}
    ek_bilgi = ""
    
    # 2. Taş Tipi Belirleme ve Metin Ayrıştırma
    if hamle[0] in tas_harfleri:
        tas_tipi = tas_harfleri[hamle[0]]
        kalan = hamle[1:] # Örn: 'f3', 'xf7', 'dxd2'
    else:
        tas_tipi = 0 # Piyondur
        kalan = hamle # Örn: 'e4', 'exd5'

    # 3. Taş Yeme (x) Varsa Hedef ve Kaynak Ayrımı
    if "x" in kalan:
        parcalar = kalan.split("x")
        ek_bilgi = parcalar[0]       # 'exd5' ise ek_bilgi = 'e' olur (Piyonun kalktığı dikey)
        hedef_metni = parcalar[1]    # Hedef kesinlikle 'd5' olur
    else:
        hedef_metni = kalan[-2:]     # Son iki karakter her zaman hedeftir (örn: 'e4')
        if len(kalan) > 2:
            ek_bilgi = kalan[:-2]    # Örn: 'Nbd2' ise ek_bilgi = 'b' olur

    # Hedef koordinat hesaplama
    hedef_satir, hedef_sutun = pgn_karesini_koordinata(hedef_metni)
    yeni_indeks = hedef_satir * 8 + hedef_sutun
    hedef_kare = T.tAHTA[hedef_satir][hedef_sutun]
    print(hedef_satir,hedef_sutun, "hedef")
    # 4. TERSİNE ARAMA
    for j in range(8):
        for i in range(8):
            kaynak_indeks = j * 8 + i
            
            if T.TAS[kaynak_indeks] == tas_tipi and T.RENK[kaynak_indeks] == renk:
                kaynak_kare = T.tAHTA[j][i]
                print(j,i, "kaynak")
                if S.hamle_yasal_mi(kaynak_kare, hedef_kare, simülasyon=True):
                    # Ek bilgi doğrulaması (Çakışma Önleme)
                    if ek_bilgi:
                        if ek_bilgi.isalpha(): # Sütun doğrulaması ('e' dikeyinden mi geliyor?)
                            sutun_indeks = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}[ek_bilgi]
                            if i != sutun_indeks: continue
                        elif ek_bilgi.isdigit(): # Satır doğrulaması
                            if j != (int(ek_bilgi) - 1): continue # Siyahlar aşağıda mantığına göre
                            
                    return kaynak_indeks, yeni_indeks, j, i, hedef_satir, hedef_sutun
                    
    return None, None,None, None,None, None

def tasobj_tasi(eski_j, eski_i, yeni_j, yeni_i):
    # Matris indekslerini hesapla
    eski_idx = eski_j * 8 + eski_i
    yeni_idx = yeni_j * 8 + yeni_i
    
    # Arka plandaki sayı listelerini (RAM) taşı
    T.TAS[yeni_idx] = T.TAS[eski_idx]
    T.RENK[yeni_idx] = T.RENK[eski_idx]
    
    T.tAHTA[yeni_j][yeni_i].tas_rengi=T.tAHTA[eski_j][eski_i].tas_rengi
    T.tAHTA[yeni_j][yeni_i].tas_tipi=T.tAHTA[eski_j][eski_i].tas_tipi
    T.tAHTA[yeni_j][yeni_i].tas_resmi=T.tAHTA[eski_j][eski_i].tas_resmi
    
    # Eski yerleri boşalt
    T.TAS[eski_idx] = 6
    T.RENK[eski_idx] = C.BOS
    
    T.tAHTA[eski_j][eski_i].tas_rengi=C.BOS
    T.tAHTA[eski_j][eski_i].tas_tipi=6
    T.tAHTA[eski_j][eski_i].tas_resmi=T.tasResmi[C.BEYAZ][6]
    




# -------------------------------------------------------------
# MAIN GAME LOOP
# -------------------------------------------------------------

sira_kimde=C.BEYAZ
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
                        mevcut_hamle_sirasi = -1
                        tahtayi_hamleye_gore_guncelle(secilen_oyun, mevcut_hamle_sirasi)
                        break
                # B. OYNATICI BUTON KONTROLLERİ
                if secilen_oyun is not None:
                    toplam_hamle = len(secilen_oyun.hamle_listesi)
                    
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
