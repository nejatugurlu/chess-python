import pygame
import sys
import time
import Sabitler as C

pygame.init()
pygame.font.init()

def safe_load(filename, color=(200, 200, 200)):
    try:
        return pygame.image.load(filename)
    except pygame.error:
        surface = pygame.Surface((C.KARE_EN, C.KARE_EN), pygame.SRCALPHA)
        if filename != "BOS.gif":
            pygame.draw.circle(surface, color, (C.KARE_EN/2, C.KARE_EN/2), C.KARE_EN/3)
        return surface

resimDosyaIsmi = [
["BP.gif", "BA.gif", "BF.gif", "BK.gif", "BV.gif", "BS.gif", "BOS.gif"],
["SP.gif", "SA.gif", "SF.gif", "SK.gif", "SV.gif", "SS.gif", "BOS.gif"]
]

tasResmi = [[None for _ in range(7)] for _ in range(2)]
for i in range(2):
    for j in range(7):
        color_hint = (240, 240, 240) if i == 0 else (40, 40, 40)
        img = safe_load("pic/"+resimDosyaIsmi[i][j], color_hint)
        tasResmi[i][j] = pygame.transform.scale(img, (C.KARE_EN, C.KARE_EN))


class SatrancKaresi:
    def __init__(self, satir, sutun, x_konum, y_konum, boyut, kare_rengi):
        self.satir = satir
        self.sutun = sutun
        self.rect = pygame.Rect(x_konum, y_konum, boyut, boyut)
        self.renk = kare_rengi
        self.tas_rengi = C.BOS
        self.tas_tipi = 6
        self.tas_resmi = tasResmi[C.BEYAZ][6]
        self.surukleniyor = False

    def tasi_yerlestir(self, tas_rengi, tas_tipi):
        self.tas_rengi = tas_rengi
        self.tas_tipi = tas_tipi
        if tas_rengi != C.BOS and tas_tipi < 6:
            self.tas_resmi = tasResmi[tas_rengi][tas_tipi]
        else:
            self.tas_resmi = tasResmi[C.BEYAZ][6]

    def tasi_kaldir(self):
        self.surukleniyor = True

    def tasi_birak(self):
        self.surukleniyor = False

    def bosalt(self):
        self.tas_rengi = C.BOS
        self.tas_tipi = 6
        self.tas_resmi = tasResmi[C.BEYAZ][6]
        self.surukleniyor = False

    def ciz(self, yuzey):
        pygame.draw.rect(yuzey, self.renk, self.rect)
        if self.tas_rengi != C.BOS and not self.surukleniyor:
            yuzey.blit(self.tas_resmi, self.rect.topleft)

    def tiklandi_mi(self, fare_konumu):
        return self.rect.collidepoint(fare_konumu)


tAHTA = [[None for _ in range(8)] for _ in range(8)]
for j in range(8):
    for i in range(8):
        x = C.solN + i * C.KARE_EN
        y = C.ustN + j * C.KARE_EN
        renk = C.kareAcikRenk if (i + j) % 2 == 0 else C.kareKoyuRenk
        tAHTA[j][i] = SatrancKaresi(j, i, x, y, C.KARE_EN, renk)

kUTU = [[None for _ in range(8)] for _ in range(4)]
for j in range(4):
    for i in range(8):
        x = C.solKutuN + i * C.KARE_EN
        y = C.ustKutuN + j * C.KARE_EN
        kUTU[j][i] = SatrancKaresi(j, i, x, y, C.KARE_EN, C.fonRenkSatranc)


standart_taslar = [3, 1, 2, 4, 5, 2, 1, 3]
    # 2. Ana tahtayı (TAS listesini) standart satranç dizilimine getir
yen1_tas = [6] * 64
yen1_renk = [0] * 64
# Siyah Taşları Yerleştir (0-15 arası indeksler, Renk: 0)
for i in range(8):
    yen1_tas[i] = standart_taslar[i]       # Arka sıra
    yen1_renk[i] = 0
    yen1_tas[8 + i] = 0                    # Piyonlar
    yen1_renk[8 + i] = 0
# Beyaz Taşları Yerleştir (48-63 arası indeksler, Renk: 1)
for i in range(8):
    yen1_tas[48 + i] = 0                   # Piyonlar
    yen1_renk[48 + i] = 1
    yen1_tas[56 + i] = standart_taslar[i]  # Arka sıra
    yen1_renk[56 + i] = 1
    
TAS = yen1_tas
RENK = yen1_renk

yen2_tas = [6] * 32
yen2_renk = [0] * 32

for i in range(8):
    yen2_tas[i] = standart_taslar[i]       # Arka sıra
    yen2_renk[i] = 0
    yen2_tas[8 + i] = 0                    # Piyonlar
    yen2_renk[8 + i] = 0
    
for i in range(8):
    yen2_tas[16 + i] = 0                   # Piyonlar
    yen2_renk[16 + i] = 1
    yen2_tas[24 + i] = standart_taslar[i]  # Arka sıra
    yen2_renk[24 + i] = 1
    
KUTU_TAS = yen2_tas
KUTU_RENK = yen2_renk

def kare_lere_SatrancKaresi_yerleştir():
    
    tAHTA = [[None for _ in range(8)] for _ in range(8)]
    for j in range(8):
        for i in range(8):
            x = C.solN + i * C.KARE_EN
            y = C.ustN + j * C.KARE_EN
            renk = C.kareAcikRenk if (i + j) % 2 == 0 else C.kareKoyuRenk
            tAHTA[j][i] = SatrancKaresi(j, i, x, y, C.KARE_EN, renk)

    kUTU = [[None for _ in range(8)] for _ in range(4)]
    for j in range(4):
        for i in range(8):
            #print(i,j)
            x = C.solKutuN + i * C.KARE_EN
            y = C.ustKutuN + j * C.KARE_EN
            kUTU[j][i] = SatrancKaresi(j, i, x, y, C.KARE_EN, C.fonRenkSatranc)


def tAHTA_doldur():
    # 3. Grafiksel arayüzü güncelle
    for j in range(8):
        for i in range(8):
            ks = j * 8 + i
            if TAS[ks] < 6:
                tAHTA[j][i].tasi_yerlestir(RENK[ks], TAS[ks])
            else: 
                tAHTA[j][i].bosalt()

def kUTU_doldur():
    # 3. Grafiksel arayüzü güncelle
    for j in range(4):
        for i in range(8):
            ks = j * 8 + i
            if KUTU_TAS[ks] < 6 : 
                kUTU[j][i].tasi_yerlestir(KUTU_RENK[ks], KUTU_TAS[ks])
            else: 
                kUTU[j][i].bosalt()
            
def tAHTA_bosalt():
    for j in range(8):
        for i in range(8): tAHTA[j][i].bosalt()
        
def kUTU_bosalt():
    for j in range(4):
        for i in range(8):
            kUTU[j][i].bosalt()
            ks = j * 8 + i
            KUTU_TAS[ks]=6
            
def kUTU_ya_tas_ekle(tas_rengi, tas_tipi):
    for j in range(4):
        for i in range(8):
            ks = j * 8 + i
            if KUTU_TAS[ks] == 6 : 
                kUTU[j][i].tasi_yerlestir(tas_rengi, tas_tipi)
                KUTU_TAS[ks]=tas_tipi
                return

def kare_lere_tasi_yerlestir():
    # Ana tahtadaki 8x8 kareleri güncelle (j döngüsü eklendi ve içeri kaydırıldı)
    global TAS, RENK
    global KUTU_TAS, KUTU_RENK
    for j in range(8):
        for i in range(8):
            ks = j * 8 + i
            if TAS[ks] < 6: 
                tAHTA[j][i].tasi_yerlestir(RENK[ks], TAS[ks])
            else: 
                tAHTA[j][i].bosalt()
    
    # Yan paneldeki (kUTU) yedeklenen/yenilen taşları güncelle
    for j in range(4):
        for i in range(8):
            ks = j * 8 + i
            if KUTU_TAS[ks] < 6: 
                kUTU[j][i].tasi_yerlestir(KUTU_RENK[ks], KUTU_TAS[ks])
    
def alt_ust_harf_satirlari():

    rUST = pygame.Rect(C.solN, C.ustN -C.kd/2,   8*C.kd ,  C.kd/2)
    rALT = pygame.Rect(C.solN, C.ustN +8*C.kd ,  8*C.kd ,  C.kd/2)

    satir= blk=''
    for i in range(8):blk=blk+' '
    harfler=['a','b','c','d','e','f','g','h']
    for i in range(8):satir=satir+harfler[i]+blk
    satir=""+satir
    yazi_yuzeyi = C.font_sira.render(satir, True, (255, 255, 255))

    pygame.draw.rect(ekran, (0,0,0), rUST, 0)
    ekran.blit(yazi_yuzeyi, (rUST.x + 10, rUST.y ))

    pygame.draw.rect(ekran, (0,0,0), rALT, 0)
    ekran.blit(yazi_yuzeyi, (rALT.x + 10, rALT.y ))

def sol_sag_rakam_kolonlari():

    rSOL = pygame.Rect(C.solN-C.kd/2, C.ustN ,   C.kd/2 , 8*C.kd   )
    rSAG = pygame.Rect(C.solN+8*C.kd, C.ustN  ,  C.kd/2 , 8*C.kd   )

    rakamlar_sol=['1', '2','3','4','5','6','7','8']
    rakamlar_sag=['8', '7','6','5','4','3','2','1']
    pygame.draw.rect(ekran, (0,0,0), rSOL)
    pygame.draw.rect(ekran, (0,0,0), rSOL, 1)
    for i in range(8):
        yazi_yuzeyi = C.font_sira.render(rakamlar_sol[i], True, (255, 255, 255))
        ekran.blit(yazi_yuzeyi, (rSOL.x + 10, rSOL.y+i*C.kd+C.kd/2 ))
    pygame.draw.rect(ekran, (0,0,0), rSAG)
    pygame.draw.rect(ekran, (0,0,0), rSAG, 1)
    for i in range(8):
        yazi_yuzeyi = C.font_sira.render(rakamlar_sag[i], True, (255, 255, 255))
        ekran.blit(yazi_yuzeyi, (rSAG.x + 10, rSAG.y+i*C.kd+C.kd/2 ))

def TahtaEkranda():
    for j in range(8):
        for i in range(8): tAHTA[j][i].ciz(ekran)
    for j in range(4):
        for i in range(8): kUTU[j][i].ciz(ekran)
    alt_ust_harf_satirlari()
    sol_sag_rakam_kolonlari()
    pygame.display.flip()

def TekTahtaEkranda():
    for j in range(8):
        for i in range(8): tAHTA[j][i].ciz(ekran)
    alt_ust_harf_satirlari()
    sol_sag_rakam_kolonlari()
    pygame.display.flip()

ekran = pygame.display.set_mode((C.EKRAN_EN, C.EKRAN_BOY), pygame.RESIZABLE)

"""
pygame.display.set_caption("Commodore Nejat Chess Engine")

kUTU_doldur()
tAHTA_doldur()
TahtaEkranda()

time.sleep(2)


kUTU_bosalt()
tAHTA_doldur()
TahtaEkranda()
time.sleep(2)

kUTU_bosalt()

kUTU[3][3].tasi_yerlestir(1, 2)
kUTU[3][4].tasi_yerlestir(0, 2)

kUTU_ya_tas_ekle(0,0)
kUTU_ya_tas_ekle(0,1)
kUTU_ya_tas_ekle(0,2)
kUTU_ya_tas_ekle(0,3)
kUTU_ya_tas_ekle(0,4)
kUTU_ya_tas_ekle(0,5)
kUTU_ya_tas_ekle(1,0)
kUTU_ya_tas_ekle(1,1)
kUTU_ya_tas_ekle(1,2)
kUTU_ya_tas_ekle(1,3)
kUTU_ya_tas_ekle(1,4)
kUTU_ya_tas_ekle(1,5)

for j in range(4):
    for i in range(8):
        kUTU[j][i].ciz(ekran)
        print(kUTU[j][i].tas_tipi)

pygame.display.flip()
time.sleep(2)

"""


