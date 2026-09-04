import pygame
import sys
import time

# Game Constants
BEYAZ = 0
SIYAH = 1
BOS = 2

kd = 50
ki = 48
frk = (kd - ki) / 2
solN = 330  #75
ustN = 40   #75
solKutuN = solN
ustKutuN = ustN + 9 * kd + kd / 2

# Colors
kareKoyuRenk = (183, 154, 53)
kareAcikRenk = (252, 227, 109)
fonRenkOyun = (255, 230, 255)
fonRenkSatranc = (255, 250, 205)

EKRAN_EN = 800
EKRAN_BOY = 750
KARE_EN = 50

pygame.font.init()
font_sira = pygame.font.SysFont("Arial", 20, bold=True)
font_tus = pygame.font.SysFont("Arial", 14, bold=True)

# Interface Rectangles
rSATRANCCERCEVESI = pygame.Rect(kd, kd / 2, 22 * kd + kd / 2, 14 * kd + kd / 2)
rSATRANCPANELI = pygame.Rect(solN-kd/2, ustN, 14 * kd, 14 * kd + kd / 2)
rTUSPANELI = pygame.Rect(solN + 1 * kd + kd / 2, ustN + 10 * kd + kd / 2, 12 * kd, 3 * kd / 4)
rOYUNPANELI = pygame.Rect(solN + 9 * kd, ustN, 16 * kd + kd / 2, 14 * kd + kd / 2)
rBASLIKETIKETI = pygame.Rect(kd, kd / 4, 10 * kd, kd / 2)
rOYUNPANOSU = pygame.Rect(5 * kd, kd, 10 * kd, 9 * kd + kd / 2)
rHAMLEPANOSU = pygame.Rect(kd / 2, kd, 4 * kd, 9 * kd + kd / 2)

# Navigation Buttons
rBASAGITTUSU = pygame.Rect(solN + 2 * kd, ustN + 8 * kd + kd / 2, 2 * kd, kd / 2)
rGERITUSU = pygame.Rect(solN + 4 * kd + kd / 4, ustN + 8 * kd + kd / 2, 2 * kd, kd / 2)
rILERITUSU = pygame.Rect(solN + 6 * kd + kd / 2, ustN + 8 * kd + kd / 2, 2 * kd, kd / 2)
rSONAGITTUSU = pygame.Rect(solN + 8 * kd + 3 * kd / 4, ustN + 8 * kd + kd / 2, 2 * kd, kd / 2)
rSIRA = pygame.Rect(solN-kd/2, ustN + 8 * kd+ kd/10 , 5 * kd + kd / 2, 2 * kd)

# Promotion Layout Buttons
rVEZIR_BUTON = pygame.Rect(EKRAN_EN / 2 - 110, EKRAN_BOY / 2 - 30, 50, 60)
rKALE_BUTON  = pygame.Rect(EKRAN_EN / 2 - 55,  EKRAN_BOY / 2 - 30, 50, 60)
rFIL_BUTON   = pygame.Rect(EKRAN_EN / 2,       EKRAN_BOY / 2 - 30, 50, 60)
rAT_BUTON    = pygame.Rect(EKRAN_EN / 2 + 55,  EKRAN_BOY / 2 - 30, 50, 60)
