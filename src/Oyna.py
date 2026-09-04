import pygame
import sys
import time
import Sabitler as C
import Tahta as T
import Satranc as S

# -------------------------------------------------------------
# 1. INITIALIZATION & SETUP
# -------------------------------------------------------------
pygame.init()
pygame.font.init()

oyun_BASLADI = False    
secili_kare = None
suruklenen_tas_resmi = None
fare_konum = (0, 0)
mat_durumu = False
kazanan_renk = None

# -------------------------------------------------------------
# 6. RUNTIME MAIN GAME LOOP
# -------------------------------------------------------------

T.kUTU_doldur()
#S.sira_kimde=C.SIYAH
running = True
while running:
    fare_konum = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # ---------------------------------------------------------
                # TERFİ MENÜSÜ TIKLAMA KONTROLÜ
                # ---------------------------------------------------------
                if S.terfi_bekleniyor:
                    secilen_tas = None
                    if C.rVEZIR_BUTON.collidepoint(fare_konum): secilen_tas = 4
                    elif C.rKALE_BUTON.collidepoint(fare_konum): secilen_tas = 3
                    elif C.rFIL_BUTON.collidepoint(fare_konum):  secilen_tas = 2
                    elif C.rAT_BUTON.collidepoint(fare_konum):   secilen_tas = 1
                    
                    if secilen_tas is not None:
                        T.TAS[S.terfi_kare_indeksi] = secilen_tas
                        S.terfi_bekleniyor = False
                        S.terfi_kare_indeksi = -1
                        S.sira_degistir()
                        continue

                # ---------------------------------------------------------
                # KONTROL BUTONLARI (GERİ / BAŞA GİT)
                # ---------------------------------------------------------
                if C.rGERITUSU.collidepoint(fare_konum):
                    S.hamle_geri_al()
                    mat_durumu = False # Mat durumunu sıfırla
                    if len(S.hamle_gecmisi) == 0:
                        T.tAHTA_doldur()
                        T.kUTU_bosalt()
                        oyun_BASLADI = False
                           
                elif C.rBASAGITTUSU.collidepoint(fare_konum):
                    while len(S.hamle_gecmisi) > 0:
                        S.hamle_geri_al()
                    T.tAHTA_doldur()
                    T.kUTU_bosalt()
                    oyun_BASLADI = False
                    
                # ---------------------------------------------------------
                # TAHTADAN TAŞ SEÇME VE SÜRÜKLEMEYE BAŞLAMA
                # ---------------------------------------------------------
                else:
                    if mat_durumu: 
                        continue # Eğer mat durumundaysak tıklamaları yok say, taş seçilmesin
                    
                    if not oyun_BASLADI:
                        T.tAHTA_doldur()
                        T.kUTU_bosalt()
                        oyun_BASLADI = True
                        S.sira_kimde = C.BEYAZ  # S modülündeki sırayı eşitledik
                        continue
                    
                    for j in range(8):
                        for i in range(8):
                            kare = T.tAHTA[j][i]
                            if kare.tiklandi_mi(fare_konum) and kare.tas_rengi == S.sira_kimde:
                                S.hamle_kaydet()
                                secili_kare = kare
                                suruklenen_tas_resmi = kare.tas_resmi
                                kare.tasi_kaldir()
                                break
                                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and secili_kare is not None:
                hedef_kare_bulundu = False
                
                for j in range(8):
                    for i in range(8):
                        hedef_kare = T.tAHTA[j][i]
                        
                        if hedef_kare.tiklandi_mi(fare_konum):
                            if S.hamle_yasal_mi(secili_kare, hedef_kare):
                                eski_indeks = secili_kare.satir * 8 + secili_kare.sutun
                                yeni_indeks = j * 8 + i
                                
                                if yeni_indeks != eski_indeks:
                                    # Rakip taş varsa kutuya gönder
                                    if T.TAS[yeni_indeks] != 6:T.kUTU_ya_tas_ekle(T.RENK[yeni_indeks], T.TAS[yeni_indeks])
                                    
                                    # Taşı yeni yerine taşı
                                    T.TAS[yeni_indeks] = T.TAS[eski_indeks]
                                    T.RENK[yeni_indeks] = T.RENK[eski_indeks]
                                    
                                    # 🧠 KRİTİK ADIM: Rok, Terfi ve Bayrak durumlarını Satranc.py'de çözüyoruz
                                    S.hamle_sonrasi_ozel_durumlari_yonet(secili_kare, eski_indeks, yeni_indeks, i, j)
                                    
                                # Eski kareyi boşalt
                                T.TAS[eski_indeks] = 6
                                T.RENK[eski_indeks] = C.BOS
                                
                                # Sıra Değişimi Kontrolü
                                if not S.terfi_bekleniyor: 
                                    S.sira_degistir()
                                    
                                T.kare_lere_tasi_yerlestir()
                                hedef_kare_bulundu = True
                                break
                                
                if not hedef_kare_bulundu:
                    secili_kare.tasi_birak()
                    if len(S.hamle_gecmisi) > 0: 
                        S.hamle_gecmisi.pop()
                        
                if not S.yasal_hamle_var_mi(S.sira_kimde):
                    if S.sah_tehdit_altinda_mi(S.sira_kimde):
                        mat_durumu = True
                        # Sıra kimdeyse o mat olmuştur, yani rakibi kazanmıştır
                        kazanan_renk = C.BEYAZ if S.sira_kimde == C.SIYAH else C.SIYAH
                    else:
                        print("PAT! Oyun berabere bitti.")
                        
                secili_kare = None
                suruklenen_tas_resmi = None

    # -------------------------------------------------------------
    # GRAPHICS RENDERING EXECUTION SEQUENCE
    # -------------------------------------------------------------
    S.arayuz_elemanlarini_ciz()
    S.terfi_menüsünü_ciz()
    T.TahtaEkranda()    
    
    if suruklenen_tas_resmi is not None:
        T.ekran.blit(suruklenen_tas_resmi, (fare_konum[0] - C.KARE_EN / 2, fare_konum[1] - C.KARE_EN / 2))
    # 🧠 EĞER MAT OLDUYSA PENCEREYİ EN ÜSTE ÇİZ
    if mat_durumu:
        S.mat_penceresini_ciz(kazanan_renk)
        pygame.display.flip()
        time.sleep(2)
    pygame.display.flip()

pygame.quit()
sys.exit()
