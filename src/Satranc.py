import pygame
import sys
import time
import Sabitler as C
import Tahta as T

# Game Engine Control Registers
sira_kimde = C.BEYAZ  # Oyuna Beyaz başlar
hamle_gecmisi = []
ileri_gecmis = []

# Special move state track flags
beyaz_sah_hareket_etti = False
beyaz_kale_sol_hareket_etti = False
beyaz_kale_sag_hareket_etti = False
siyah_sah_hareket_etti = False
siyah_kale_sol_hareket_etti = False
siyah_kale_sag_hareket_etti = False

# Promotion sub-states
terfi_bekleniyor = False
terfi_kare_indeksi = -1
terfi_oyuncu_rengi = C.BEYAZ

oyun_BASLADI = False

# -------------------------------------------------------------
# 3. ASSET LOADING & ASSIGNMENTS
# -------------------------------------------------------------
"""
ekran = pygame.display.set_mode((C.EKRAN_EN, C.EKRAN_BOY), pygame.RESIZABLE)
pygame.display.set_caption("Commodore Nejat Chess Engine")
"""

def sira_degistir():
    """
    ÖĞRENCİLER İÇİN ALTIN NOT: if-else kullanmadan sıra değiştirme!
    Eğer Sabitler dosyanızda BEYAZ = 0 ve SIYAH = 1 (veya 1 ve 2) ise,
    XOR (^) operatörü veya toplamdan çıkarma ile tek satırda sırayı döndürürüz.
    """
    global sira_kimde
    # Eğer BEYAZ=0, SIYAH=1 ise: 1 - 0 = 1 (Siyah olur), 1 - 1 = 0 (Beyaz olur)
    # Eğer projenizde değerler farklıysa (örn: 1 ve 2), aşağıdaki yöntemi kullanabilirsiniz:
    sira_kimde = C.SIYAH if sira_kimde == C.BEYAZ else C.BEYAZ

def sah_tehdit_altinda_mi(renk):
    # 1. Önce rengi belirtilen şahın tahtadaki (j, i) koordinatını bulalım
    sah_koordinat = None
    for j in range(8):
        for i in range(8):
            ks = j * 8 + i
            if T.TAS[ks] == 5 and T.RENK[ks] == renk: # 5 = Şah
                sah_koordinat = (j, i)
                break
        if sah_koordinat: break
        
    if not sah_koordinat: return False

    # 2. Rakibin tüm taşlarını tara ve şahı vurabiliyorlar mı kontrol et
    rakip_renk = C.SIYAH if renk == C.BEYAZ else C.BEYAZ
    for j in range(8):
        for i in range(8):
            ks = j * 8 + i
            if T.TAS[ks] < 6 and T.RENK[ks] == rakip_renk:
                # Burada sizin taş hareket kurallarınızı çağırmamız gerekir
                # 🧠 KRİTİK: hamle_yasal_mi'ye simülasyon=True parametresini geçiyoruz!
                if hamle_yasal_mi(T.tAHTA[j][i], T.tAHTA[sah_koordinat[0]][sah_koordinat[1]], simülasyon=True):
                    return True 
    return False


def yasal_hamle_var_mi(renk):
    # Oyuncunun tahtadaki tüm taşlarını tara
    for j in range(8):
        for i in range(8):
            kaynak_indeks = j * 8 + i
            if T.TAS[kaynak_indeks] < 6 and T.RENK[kaynak_indeks] == renk:
                
                for hedef_j in range(8):
                    for hedef_i in range(8):
                        hedef_indeks = hedef_j * 8 + hedef_i
                        if kaynak_indeks == hedef_indeks: continue
                        
                        # Bu hamle kurallara uygun mu? (simülasyon=True yapıyoruz)
                        if hamle_yasal_mi(T.tAHTA[j][i], T.tAHTA[hedef_j][hedef_i], simülasyon=True):
                            
                            # --- GEÇİCİ DURUMU SAKLA (Simülasyon) ---
                            eski_tas_kaynak = T.TAS[kaynak_indeks]
                            eski_renk_kaynak = T.RENK[kaynak_indeks]
                            eski_tas_hedef = T.TAS[hedef_indeks]
                            eski_renk_hedef = T.RENK[hedef_indeks]
                            
                            # Kare nesnelerinin içindeki değerleri de sakla
                            kare_kaynak = T.tAHTA[j][i]
                            kare_hedef = T.tAHTA[hedef_j][hedef_i]
                            eski_kare_kaynak_tip = kare_kaynak.tas_tipi
                            eski_kare_kaynak_renk = kare_kaynak.tas_rengi
                            eski_kare_hedef_tip = kare_hedef.tas_tipi
                            eski_kare_hedef_renk = kare_hedef.tas_rengi
                            
                            # --- HAMLEYİ YAP ---
                            T.TAS[hedef_indeks] = T.TAS[kaynak_indeks]
                            T.RENK[hedef_indeks] = T.RENK[kaynak_indeks]
                            T.TAS[kaynak_indeks] = 6
                            T.RENK[kaynak_indeks] = C.BOS # 2 veya boş renginiz neyse
                            
                            # Kare nesnelerini güncelle
                            kare_hedef.tas_tipi = kare_kaynak.tas_tipi
                            kare_hedef.tas_rengi = kare_kaynak.tas_rengi
                            kare_kaynak.tas_tipi = 6
                            kare_kaynak.tas_rengi = C.BOS

                            # Şah kurtuldu mu bak
                            sah_kurtuldu = not sah_tehdit_altinda_mi(renk)
                            
                            # --- ESKİ HALİNE GERİ GETİR ---
                            T.TAS[kaynak_indeks] = eski_tas_kaynak
                            T.RENK[kaynak_indeks] = eski_renk_kaynak
                            T.TAS[hedef_indeks] = eski_tas_hedef
                            T.RENK[hedef_indeks] = eski_renk_hedef
                            
                            kare_kaynak.tas_tipi = eski_kare_kaynak_tip
                            kare_kaynak.tas_rengi = eski_kare_kaynak_renk
                            kare_hedef.tas_tipi = eski_kare_hedef_tip
                            kare_hedef.tas_rengi = eski_kare_hedef_renk
                            
                            if sah_kurtuldu:
                                return True 
                                
    return False



def hamle_yasal_mi(eski_kare, yeni_kare, simülasyon=False):
    # KURAL 1: Sürüklenen taşın rengi, sırası gelen oyuncuyla aynı olmalı
    # Eğer arka planda mat simülasyonu yapıyorsak bu kuralı devre dışı bırakıyoruz
    if not simülasyon:
        if eski_kare.tas_rengi != sira_kimde:
            return False

    # KURAL 2: Kendi taşını yemeyi engelle
    if yeni_kare.tas_rengi == eski_kare.tas_rengi:
        return False
        
    satir_fark = yeni_kare.satir - eski_kare.satir
    sutun_fark = yeni_kare.sutun - eski_kare.sutun
    tas_tipi = eski_kare.tas_tipi
    tas_rengi = eski_kare.tas_rengi

    # ---- TAS HAREKET KONTROLLERİ ----
    
    # tas_tipi = 0 (Piyon), Siyahlar aşağıda kuralı
    if tas_tipi == 0:
        # Satır ve sütun farklarını mutlak değer KULLANMADAN hesaplıyoruz
        satir_fark = yeni_kare.satir - eski_kare.satir
        sutun_fark = yeni_kare.sutun - eski_kare.sutun

        # ========================================================
        # 1. BEYAZ PİYON KURALLARI (Yukarıdan Aşağıya İniyor: + Yön)
        # ========================================================
        if tas_rengi == C.BEYAZ:
            # A. 1 Kare Düz İlerleme
            if sutun_fark == 0 and satir_fark == +1 and yeni_kare.tas_rengi == C.BOS: 
                return True
            if ((sutun_fark == 1) or(sutun_fark == -1)) and satir_fark == +1 and yeni_kare.tas_tipi == 0: 
                return True
                
            # B. 2 Kare İlk Hamle Zıplaması (Beyazlar üstte, yani 1. satırda başlar)
            if eski_kare.satir == 1 and sutun_fark == 0 and satir_fark == +2:
                # Hem hedef kare boş olmalı hem de önündeki geçiş karesi (Satır 2) boş olmalı
                if yeni_kare.tas_rengi == C.BOS and T.TAS[2 * 8 + eski_kare.sutun] == 6:
                    return True
        else:
            if sutun_fark == 0 and satir_fark == -1 and yeni_kare.tas_rengi == C.BOS: 
                return True
            if ((sutun_fark == 1) or(sutun_fark == -1)) and satir_fark == -1 and yeni_kare.tas_tipi == 0: 
                return True
                
            # B. 2 Kare İlk Hamle Zıplaması (Beyazlar üstte, yani 1. satırda başlar)
            if eski_kare.satir == 6 and sutun_fark == 0 and satir_fark == -2:
                # Hem hedef kare boş olmalı hem de önündeki geçiş karesi (Satır 2) boş olmalı
                if yeni_kare.tas_rengi == C.BOS and T.TAS[5 * 8 + eski_kare.sutun] == 6:
                    return True




    # Knight Rules
    elif tas_tipi == 1:
        return (abs(satir_fark) == 2 and abs(sutun_fark) == 1) or (abs(satir_fark) == 1 and abs(sutun_fark) == 2)

    # Bishop Rules
    elif tas_tipi == 2:
        if abs(satir_fark) == abs(sutun_fark): return yol_temiz_mi(eski_kare, yeni_kare)
        return False

    # Rook Rules
    elif tas_tipi == 3:
        if satir_fark == 0 or sutun_fark == 0: return yol_temiz_mi(eski_kare, yeni_kare)
        return False

    # King Rules (Including Castling)
    elif tas_tipi == 5:
        if abs(satir_fark) <= 1 and abs(sutun_fark) <= 1: return True
        
        if satir_fark == 0 and abs(sutun_fark) == 2:
            if tas_rengi == C.BEYAZ and not beyaz_sah_hareket_etti:
                if yeni_kare.sutun == 6 and not beyaz_kale_sag_hareket_etti and T.TAS[61] == 6 and T.TAS[62] == 6: return True
                if yeni_kare.sutun == 2 and not beyaz_kale_sol_hareket_etti and T.TAS[57] == 6 and T.TAS[58] == 6 and T.TAS[59] == 6: return True
            elif tas_rengi == C.SIYAH and not siyah_sah_hareket_etti:
                if yeni_kare.sutun == 6 and not siyah_kale_sag_hareket_etti and T.TAS[5] == 6 and T.TAS[6] == 6: return True
                if yeni_kare.sutun == 2 and not siyah_kale_sol_hareket_etti and T.TAS[1] == 6 and T.TAS[2] == 6 and T.TAS[3] == 6: return True
        
        return False

    # Queen Rules
    elif tas_tipi == 4:
        if (satir_fark == 0 or sutun_fark == 0) or (abs(satir_fark) == abs(sutun_fark)): return yol_temiz_mi(eski_kare, yeni_kare)
        return False
        
    return False


def yol_temiz_mi(eski_kare, yeni_kare):
    sat_fark = yeni_kare.satir - eski_kare.satir
    sut_fark = yeni_kare.sutun - eski_kare.sutun
    sat_ek = 0 if sat_fark == 0 else (1 if sat_fark > 0 else -1)
    sut_ek = 0 if sut_fark == 0 else (1 if sut_fark > 0 else -1)
    
    sat_simdi = eski_kare.satir + sat_ek
    sut_simdi = eski_kare.sutun + sut_ek
    
    while sat_simdi != yeni_kare.satir or sut_simdi != yeni_kare.sutun:
        if T.TAS[sat_simdi * 8 + sut_simdi] != 6:
            return False
        sat_simdi += sat_ek
        sut_simdi += sut_ek
    return True


def hamle_kaydet():
    global hamle_gecmisi, ileri_gecmis
    #kutu_t_kopya = [row.copy() for row in T.KUTU_TAS]
    #kutu_r_kopya = [row.copy() for row in T.KUTU_RENK]
    flags = (beyaz_sah_hareket_etti, beyaz_kale_sol_hareket_etti, beyaz_kale_sag_hareket_etti,
             siyah_sah_hareket_etti, siyah_kale_sol_hareket_etti, siyah_kale_sag_hareket_etti)
    
    durum_kopya = (T.RENK.copy(), T.TAS.copy(), sira_kimde, T.KUTU_RENK.copy(), T.KUTU_TAS.copy(), flags)
    hamle_gecmisi.append(durum_kopya)
    ileri_gecmis.clear()


def hamle_geri_al():
    global beyaz_sah_hareket_etti, beyaz_kale_sol_hareket_etti, beyaz_kale_sag_hareket_etti
    global siyah_sah_hareket_etti, siyah_kale_sol_hareket_etti, siyah_kale_sag_hareket_etti
    global sira_kimde
    
    if len(hamle_gecmisi) > 0:
        eski_durum = hamle_gecmisi.pop()
        T.RENK = eski_durum[0]
        T.TAS = eski_durum[1]
        sira_kimde = eski_durum[2]
        T.KUTU_RENK = eski_durum[3]
        T.KUTU_TAS = eski_durum[4]
        flags = eski_durum[5]
        beyaz_sah_hareket_etti, beyaz_kale_sol_hareket_etti, beyaz_kale_sag_hareket_etti, siyah_sah_hareket_etti, siyah_kale_sol_hareket_etti, siyah_kale_sag_hareket_etti = flags
        T.kare_lere_tasi_yerlestir()

def arayuz_elemanlarini_ciz():
    T.ekran.fill(C.fonRenkOyun)
    pygame.draw.rect(T.ekran, C.fonRenkSatranc, C.rSATRANCPANELI)
    buttons = [(C.rBASAGITTUSU, "|<"), (C.rGERITUSU, "<<"), (C.rILERITUSU, ">>"), (C.rSONAGITTUSU, ">|")]
    for rect, label in buttons:
        pygame.draw.rect(T.ekran, (200, 200, 200), rect)
        pygame.draw.rect(T.ekran, (0, 0, 0), rect, 1)
        text_surf = C.font_tus.render(label, True, (0, 0, 0))
        T.ekran.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))
    metin = "SIRA:BEYAZ" if sira_kimde == C.SIYAH else "SIRA:SİYAH"
    kutu_renk = (255, 255, 255) if sira_kimde == C.SIYAH else (0, 0, 0)
    yazi_yuzeyi = C.font_sira.render(metin, True, (30, 30, 30))
    T.ekran.blit(yazi_yuzeyi, (C.rSIRA.x-C.kd/6 , C.rSIRA.y + C.kd/2))
    
    gosterge_kutusu = pygame.Rect(C.rSIRA.x+C.kd/6 + 2*C.kd, C.rSIRA.y + C.kd/2, 20, 20)
    pygame.draw.rect(T.ekran, kutu_renk, gosterge_kutusu)
    pygame.draw.rect(T.ekran, (0, 0, 0), gosterge_kutusu, 2)

def terfi_menüsünü_ciz():
    if not terfi_bekleniyor: return
    arka_kutu = pygame.Rect(C.EKRAN_EN / 2 - 130, C.EKRAN_BOY / 2 - 60, 260, 110)
    pygame.draw.rect(T.ekran, (240, 240, 240), arka_kutu)
    pygame.draw.rect(T.ekran, (0, 0, 0), arka_kutu, 3)
    yazi_surf = C.font_sira.render("Piyon Terfi Seçimi:", True, (0, 0, 0))
    T.ekran.blit(yazi_surf, (C.EKRAN_EN / 2 - yazi_surf.get_width() / 2, EKRAN_BOY / 2 - 55))
    butonlar = [(C.rVEZIR_BUTON, 4), (C.rKALE_BUTON, 3), (C.rFIL_BUTON, 2), (C.rAT_BUTON, 1)]
    for rect, parca_tipi in butonlar:
        pygame.draw.rect(T.ekran, (255, 255, 255), rect)
        pygame.draw.rect(T.ekran, (100, 100, 100), rect, 1)
        T.ekran.blit(tasResmi[terfi_oyuncu_rengi][parca_tipi], (rect.x, rect.y))
    T.kare_lere_tasi_yerlestir()
        
        
def hamle_sonrasi_ozel_durumlari_yonet(secili_kare, eski_indeks, yeni_indeks, i, j):
    """
    Ana döngüdeki if kalabalığını önlemek için rok, terfi ve şah/kale hareket 
    durumlarını (bayraklarını) yöneten merkezi fonksiyon.
    """
    import Tahta as T  # Dairesel import hatasını önlemek için lokal import
    import Sabitler as C

    # 1. ROK (CASTLING) HARİTALAMA MANTIĞI
    sonuc=" "
    print(secili_kare.tas_tipi ,secili_kare.sutun ,i,j)
    if secili_kare.tas_tipi == 5 and abs(secili_kare.sutun - i) == 2:
        if i == 6 and j == 7:
            sonuc="KISA_ROK"
            hamle_rengi=1
        elif i == 2 and j == 7:
            sonuc="UZUN_ROK"
            hamle_rengi=1
        elif i == 6 and j == 0:
            sonuc="KISA_ROK"
            hamle_rengi=0
        elif i == 2 and j == 0:
            sonuc="UZUN_ROK"
            hamle_rengi=0
    print(sonuc)        
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
    
    
    
    # 2. ŞAH HAREKET ETTİ Mİ BAYRAKLARI
    if secili_kare.tas_tipi == 4:
        global beyaz_sah_hareket_etti, siyah_sah_hareket_etti
        if sira_kimde == C.BEYAZ: 
            beyaz_sah_hareket_etti = True
            siyah_sah_hareket_etti = False
        else: 
            siyah_sah_hareket_etti = True
            beyaz_sah_hareket_etti = False
    # 3. KALE HAREKET ETTİ Mİ BAYRAKLARI
    elif secili_kare.tas_tipi == 3:
        global beyaz_kale_sol_hareket_etti, beyaz_kale_sag_hareket_etti
        global siyah_kale_sol_hareket_etti, siyah_kale_sag_hareket_etti
        
        if eski_indeks == 56:    beyaz_kale_sol_hareket_etti = True
        elif eski_indeks == 63:  beyaz_kale_sag_hareket_etti = True
        elif eski_indeks == 0:   siyah_kale_sol_hareket_etti = True
        elif eski_indeks == 7:   siyah_kale_sag_hareket_etti = True

    # 4. TERFİ KONTROLÜ
    if secili_kare.tas_tipi == 0 and (j == 0 or j == 7):
        global terfi_bekleniyor, terfi_kare_indeksi, terfi_oyuncu_rengi
        terfi_bekleniyor = True
        terfi_kare_indeksi = yeni_indeks
        terfi_oyuncu_rengi = sira_kimde        
    
def mat_penceresini_ciz(kazanan_renk):
    # Ana ekran genişlik/yükseklik değerlerini T modülünden veya sabitlerden alalım
    # Ekranın tam ortasında 400x200 boyutlarında bir kutu oluşturuyoruz
    pencere_en = 400
    pencere_boy = 200
    ekran_en = T.ekran.get_width()
    ekran_boy = T.ekran.get_height()
    
    merkez_x = (ekran_en - pencere_en) // 2
    merkez_y = (ekran_boy - pencere_boy) // 2
    
    rPENCERE = pygame.Rect(merkez_x, merkez_y, pencere_en, pencere_boy)
    
    # Commodore esintili Lacivert Arka Plan ve Beyaz Çerçeve
    pygame.draw.rect(T.ekran, (0, 0, 136), rPENCERE) # Lacivert
    pygame.draw.rect(T.ekran, (255, 255, 255), rPENCERE, 4) # Beyaz Kenarlık
    
    # Yazı Tipleri (font_sira veya benzeri bir font nesnesini kullanabilirsiniz)
    font_mat = pygame.font.SysFont("Courier New", 32, bold=True)
    font_alt = pygame.font.SysFont("Courier New", 18)
    
    # Kazanan metnini belirle
    renk_metni = "BEYAZ KAZANDI!" if kazanan_renk == C.SIYAH else "SIYAH KAZANDI!"
    
    # Yazıları Render Et
    yazi_mat = font_mat.render("ŞAH MAT!", True, (255, 255, 255))
    yazi_kazanan = font_mat.render(renk_metni, True, (255, 215, 0)) # Altın Sarısı
    yazi_ipucu = font_alt.render("[Geri Tuşu] ile hamleyi geri alabilirsiniz", True, (200, 200, 200))
    
    # Yazıları Pencereye Ortalayarak Yerleştir
    T.ekran.blit(yazi_mat, (merkez_x + (pencere_en - yazi_mat.get_width()) // 2, merkez_y + 30))
    T.ekran.blit(yazi_kazanan, (merkez_x + (pencere_en - yazi_kazanan.get_width()) // 2, merkez_y + 85))
    T.ekran.blit(yazi_ipucu, (merkez_x + (pencere_en - yazi_ipucu.get_width()) // 2, merkez_y + 150))



"""
T.tAHTA_doldur()
running = True
while running:

    
    T.TekTahtaEkranda()
    sira_kimde=C.BEYAZ
    
    T.TAS[36] = T.TAS[52]
    T.kare_lere_tasi_yerlestir()
    #T.TAS[52] = 6
    T.kare_lere_tasi_yerlestir()
    
    
    pygame.display.flip()

pygame.quit()
sys.exit()
"""

