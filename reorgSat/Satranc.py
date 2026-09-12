import pygame
import sys
import time
import Sabitler as C
import Tahta as T

# Game Engine Control Registers
sira_kimde = C.BEYAZ  # Oyuna Beyaz başlar
hamle_gecmisi = []
ileri_gecmis = []
hedef_kare_bulundu=False

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

def hamle_yasal_mi(kaynak, hedef, renk):
    # --- 1. GENEL ÖN KONTROLLER ---
    if kaynak == hedef: return False
    if T.RENK[kaynak] != renk: return False  # Sıra/renk kontrolü
    if T.RENK[hedef] == renk: return False   # Kendi taşını yiyemez

    tas_tipi = T.TAS[kaynak]
    tas_rengi = T.RENK[kaynak]
    # Koordinatları ayrıştır
    k_sat, k_sut = kaynak // 8, kaynak % 8
    h_sat, h_sut = hedef // 8, hedef % 8
    
    # Mesafe farkları
    fark_sat = h_sat - k_sat
    fark_sut = h_sut - k_sut
    mutlak_sat = abs(fark_sat)
    mutlak_sut = abs(fark_sut)

    # Özel durum bayrakları (Simülasyon için)
    is_rok = False
    is_enpassant = False

    # --- 2. TAŞ GEOMETRİLERİ KONTROLÜ ---
    
    # PİYON (T.TAS == 0 kabul edilmiştir)
    if tas_tipi == 0:
        yon = -1 if renk == 1 else 1 # Beyaz yukarı (-satır), Siyah aşağı (+satır) gidiyor varsayımıyla
        ilk_satir = 6 if renk == 1 else 1
        
        # A. Düz İlerleme (Boş kareye)
        if fark_sut == 0 and T.TAS[hedef] == 6:
            if fark_sat == yon: pass
            elif k_sat == ilk_satir and fark_sat == 2 * yon and T.TAS[kaynak + 8 * yon] == 6: pass
            else: return False
        # B. Normal Çapraz Alma
        elif mutlak_sut == 1 and fark_sat == yon and T.RENK[hedef] != 6 and T.RENK[hedef] != renk:
            pass
        # C. Geçerken Alma (En Passant)
        elif mutlak_sut == 1 and fark_sat == yon and T.TAS[hedef] == 6 and hedef == T.en_passant_kare:
            is_enpassant = True
        else:
            return False
   
    
    # AT (T.TAS == 1)
    elif tas_tipi == 1:
        if not ((mutlak_sat == 2 and mutlak_sut == 1) or (mutlak_sat == 1 and mutlak_sut == 2)):
            return False

    # FİL (T.TAS == 2)
    elif tas_tipi == 2:
        if mutlak_sat != mutlak_sut: return False
        # Arada taş var mı taraması
        s_adim = 1 if fark_sat > 0 else -1
        st_adim = 1 if fark_sut > 0 else -1
        curr = kaynak + (s_adim * 8) + st_adim
        while curr != hedef:
            if T.TAS[curr] != 6: return False
            curr += (s_adim * 8) + st_adim

    # KALE (T.TAS == 3)
    elif tas_tipi == 3:
        if fark_sat != 0 and fark_sut != 0: return False
        # Arada taş var mı taraması
        adim = 0
        if fark_sat != 0: adim = 8 if fark_sat > 0 else -8
        else: adim = 1 if fark_sut > 0 else -1
        
        curr = kaynak + adim
        while curr != hedef:
            if T.TAS[curr] != 6: return False
            curr += adim

    # VEZİR (T.TAS == 4)
    elif tas_tipi == 4:
        # Kale veya Fil geometrilerinden birine uymak zorunda
        if mutlak_sat == mutlak_sut: # Fil gibi
            s_adim = 1 if fark_sat > 0 else -1
            st_adim = 1 if fark_sut > 0 else -1
            curr = kaynak + (s_adim * 8) + st_adim
            while curr != hedef:
                if T.TAS[curr] != 6: return False
                curr += (s_adim * 8) + st_adim
        elif fark_sat == 0 or fark_sut == 0: # Kale gibi
            adim = 8 if fark_sat > 0 else -8 if fark_sat < 0 else 1 if fark_sut > 0 else -1
            curr = kaynak + adim
            while curr != hedef:
                if T.TAS[curr] != 6: return False
                curr += adim
        else:
            return False

    # ŞAH (T.TAS == 5)
    elif tas_tipi == 5:
        # Standart 1 kare hareket
        if mutlak_sat <= 1 and mutlak_sut <= 1:
            pass
        # ROK KONTROLÜ (Şah 2 kare yana kayıyorsa)
        elif mutlak_sat == 0 and mutlak_sut == 2:
            # Şah veya ilgili kale daha önce hareket etti mi?
            # Şah şu an tehdit altında mı? (Rok tehdit altındayken yapılamaz)
            if sah_tehdit_altinda_mi(renk): return False
            
            # Şah kanadı mı Vezir kanadı mı?
            if fark_sut == 2: # Şah kanadı (Sağa)
                if renk == 1 and T.beyaz_sah_hareket_etti: return False
                # Aradaki kareler boş mu ve tehdit altında mı?
                if T.TAS[kaynak+1] != 6 or T.TAS[kaynak+2] != 6: return False
                # Şahın geçeceği kare tehdit altında mı?
                if kare_tehdit_altinda_mi(kaynak+1, renk): return False
                is_rok = True
            elif fark_sut == -2: # Vezir kanadı (Sola)
                if renk == 1 and T.beyaz_sah_hareket_etti: return False
                if T.TAS[kaynak-1] != 6 or T.TAS[kaynak-2] != 6 or T.TAS[kaynak-3] != 6: return False
                if kare_tehdit_altinda_mi(kaynak-1, renk): return False
                is_rok = True
            else:
                return False
        else:
            return False

    # --- 3. DEEP SIMULATION (ŞAH GÜVENLİĞİ KONTROLÜ) ---
    # Hamleyi geçici bir `GeciciKare` taklidiyle tahtada simüle ediyoruz
    eski_hedef_tas = T.TAS[hedef]
    eski_hedef_renk = T.RENK[hedef]
    
    # En Passant simülasyon ek yükü (Arkadaki piyonu sil)
    ep_silinen_indeks = None
    if is_enpassant:
        ep_silinen_indeks = hedef + 8 if renk == 1 else hedef - 8
        eski_ep_tas = T.TAS[ep_silinen_indeks]
        eski_ep_renk = T.RENK[ep_silinen_indeks]
        T.TAS[ep_silinen_indeks] = 6
        T.RENK[ep_silinen_indeks] = 2

    # Rok simülasyon ek yükü (Kaleyi geçici kaydır)
    if is_rok:
        kale_eski = (kaynak + 3) if fark_sut == 2 else (kaynak - 4)
        kale_yeni = (kaynak + 1) if fark_sut == 2 else (kaynak - 1)
        T.TAS[kale_yeni] = T.TAS[kale_eski]
        T.RENK[kale_yeni] = T.RENK[kale_eski]
        T.TAS[kale_eski] = 6
        T.RENK[kale_eski] = 2

    # Standart Simülasyon Taşınması
    T.TAS[hedef] = T.TAS[kaynak]
    T.RENK[hedef] = T.RENK[kaynak]
    T.TAS[kaynak] = 6
    T.RENK[kaynak] = 2

    # Şahımız tehlikede kalıyor mu yargısı
    sah_tehlikede = sah_tehdit_altinda_mi(renk)

    # --- TAHTAYI GERİ YÜKLEME (UNDO) ---
    T.TAS[kaynak] = T.TAS[hedef]
    T.RENK[kaynak] = T.RENK[hedef]
    T.TAS[hedef] = eski_hedef_tas
    T.RENK[hedef] = eski_hedef_renk

    if is_enpassant:
        T.TAS[ep_silinen_indeks] = eski_ep_tas
        T.RENK[ep_silinen_indeks] = eski_ep_renk

    if is_rok:
        T.TAS[kale_eski] = T.TAS[kale_yeni]
        T.RENK[kale_eski] = T.RENK[kale_yeni]
        T.TAS[kale_yeni] = 6
        T.RENK[kale_yeni] = 2

    # Eğer hamle şahı tehlikeye atıyorsa geçersizdir!
    if sah_tehlikede:
        return False

    return True


def sah_tehdit_altinda_mi(renk):
    # 1. Kendi şahımızın 64'lük listedeki indeksini bulalım
    sah_indeks = None
    for i in range(64):
        if T.TAS[i] == 6 and T.RENK[i] == renk: # Şah = 6 kabul ettik
            sah_indeks = i
            break
            
    # Eğer tahtada şah yoksa (örn: test tahtalarında) tehdit yoktur
    if sah_indeks is None: 
        return False
        
    # 2. Şahın bulunduğu karenin tehdit altında olup olmadığını döndür
    return kare_tehdit_altinda_mi(sah_indeks, renk)


def kare_tehdit_altinda_mi(hedef_kare, savunma_rengi):
    """
    Belirli bir karenin, rakip taşlar tarafından tehdit edilip edilmediğini kontrol eder.
    Rok kontrollerinde şahın geçeceği karelerin güvenliği için de bu ortak fonksiyon kullanılır.
    """
    rakip_renk = 0 if savunma_rengi == 1 else 1
    
    # Koordinatları çıkartalım
    h_sat, h_sut = hedef_kare // 8, hedef_kare % 8
    
    # Tahtadaki tüm kareleri tarayarak rakip taşları buluyoruz
    for kaynak_kare in range(64):
        if T.RENK[kaynak_kare] != rakip_renk:
            continue # Bizim renkteyse veya boşsa geç
            
        rakip_tas = T.TAS[kaynak_kare]
        
        k_sat, k_sut = kaynak_kare // 8, kaynak_kare % 8
        fark_sat = h_sat - k_sat
        fark_sut = h_sut - k_sut
        mutlak_sat = abs(fark_sat)
        mutlak_sut = abs(fark_sut)
        
        # --- RAKİP TAŞLARIN GEOMETRİK VURUŞ KONTROLLERİ ---
        
        # Rakip Piyon
        if rakip_tas == 0:
            # Rakip beyaz ise yukarı (-satır), siyah ise aşağı (+satır) vurur
            # Buradaki 'yon' savunma rengine göre ters çalışır
            yon = 1 if rakip_renk == 1 else -1 
            if fark_sat == yon and mutlak_sut == 1:
                return True
                
        # Rakip At
        elif rakip_tas == 1:
            if (mutlak_sat == 2 and mutlak_sut == 1) or (mutlak_sat == 1 and mutlak_sut == 2):
                return True
                
        # Rakip Fil
        elif rakip_tas == 2:
            if mutlak_sat == mutlak_sut:
                if aradaki_yol_bos_mu(kaynak_kare, hedef_kare, fark_sat, fark_sut):
                    return True
                    
        # Rakip Kale
        elif rakip_tas == 3:
            if fark_sat == 0 or fark_sut == 0:
                if aradaki_yol_bos_mu(kaynak_kare, hedef_kare, fark_sat, fark_sut):
                    return True
                    
        # Rakip Vezir
        elif rakip_tas == 4:
            if mutlak_sat == mutlak_sut or fark_sat == 0 or fark_sut == 0:
                if aradaki_yol_bos_mu(kaynak_kare, hedef_kare, fark_sat, fark_sut):
                    return True
                    
        # Rakip Şah (İki şah yan yana gelemez koruması)
        elif rakip_tas == 5:
            if mutlak_sat <= 1 and mutlak_sut <= 1:
                return True
                
    return False


def aradaki_yol_bos_mu(kaynak, hedef, fark_sat, fark_sut):
    """Menzilli taşların (Fil, Kale, Vezir) yolunda engel olup olmadığını tarar"""
    s_adim = 8 if fark_sat > 0 else -8 if fark_sat < 0 else 0
    st_adim = 1 if fark_sut > 0 else -1 if fark_sut < 0 else 0
    
    # Fil için kombine adım düzeltmesi (8'lik satır adımı ile 1'lik sütun adımı birleşir)
    if s_adim != 0 and st_adim != 0:
        adim = (8 if fark_sat > 0 else -8) + (1 if fark_sut > 0 else -1)
    else:
        adim = s_adim + st_adim
        
    curr = kaynak + adim
    while curr != hedef:
        if T.TAS[curr] != 6: # Arada boş olmayan (taş içeren) kare bulduk
            return False
        curr += adim
    return True
        

    """
    #piyon için alternatif yazmaya çalıştım ama başarılı olmadı
    
    # tas_tipi = 0 (Piyon), Siyahlar aşağıda kuralı
    if tas_tipi == 0:

        # ========================================================
        # 1. BEYAZ PİYON KURALLARI (Yukarıdan Aşağıya İniyor: + Yön)
        # ========================================================
        if tas_rengi == C.BEYAZ:
            # A. 1 Kare Düz İlerleme
            if fark_sut == 0 and fark_sat == +1 and T.RENK[hedef] == C.BOS: 
                return True
                
            # B. 2 Kare İlk Hamle Zıplaması (Beyazlar üstte, yani 1. satırda başlar)
            if k_sat == 1 and fark_sut == 0 and fark_sat == +2:
                # Hem hedef kare boş olmalı hem de önündeki geçiş karesi (Satır 2) boş olmalı
                if T.RENK[hedef] == C.BOS and T.TAS[2 * 8 + k_sut] == 6:
                    return True
        else:
            if fark_sut == 0 and fark_sat == -1 and T.RENK[hedef] == C.BOS: 
                return True
                
            # B. 2 Kare İlk Hamle Zıplaması (Beyazlar üstte, yani 1. satırda başlar)
            if k_sat == 6 and fark_sut == 0 and fark_sat == -2:
                # Hem hedef kare boş olmalı hem de önündeki geçiş karesi (Satır 2) boş olmalı
                if T.RENK[hedef] == C.BOS and T.TAS[5 * 8 + k_sut] == 6:
                    return True
    """
 



