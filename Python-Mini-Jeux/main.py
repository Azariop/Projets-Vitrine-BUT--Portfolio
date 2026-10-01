import pygame
import sys
import random
from jeu.snake import run_snake
from jeu.pong import run_pong
from jeu.casse import run_breakout
from jeu.dodge import run_dodge
from jeu.tic import run_morpion
from jeu.flappy import run_flappy
from jeu.aimtrain import run_aim
from jeu.memory import run_memory

# ===== INITIALISATION =====
pygame.init()
pygame.mixer.init()

# --- SYSTEME DE PLAYLIST  ---

playlist = [f"musique/musique{i}.mp3" for i in range(1, 15)]
index_musique = random.randint(0, 14) 

def charger_et_jouer(index):
    try:
        pygame.mixer.music.load(playlist[index])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
    except:
        print(f"Erreur : Impossible de lire {playlist[index]}")

# On lance la première musique
charger_et_jouer(index_musique)

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sae5 - RetroHub")

# Variables d'état
fullscreen = False
is_muted = False

font_title = pygame.font.SysFont(None, 60)
font_menu = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()

def draw_text(text, y, font=font_menu):
    surface = font.render(text, True, (255, 255, 255))
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)

# ===== BOUCLE PRINCIPALE =====
def main():
    global screen, fullscreen, is_muted, index_musique
    running = True
    while running:
        screen.fill((0, 0, 0))

        draw_text("Sae5 - RetroHub", 80, font_title)
        draw_text("1 - Snake", 160)
        draw_text("2 - Pong", 200)
        draw_text("3 - Breakout", 240)
        draw_text("4 - Dodge Game", 280)
        draw_text("5 - Morpion", 320)
        draw_text("6 - Flappy", 360)
        draw_text("7 - Aim Trainer", 400)
        draw_text("8 - Memory", 440)
        draw_text("ESC - Quitter", 520)

        # INFOS DISCRETES EN BAS
        m_text = font_small.render("m : mute | ctrl+m : suivant | alt+m : precedent", True, (100, 100, 100))
        screen.blit(m_text, (20, HEIGHT - 25))

        f_text = font_small.render("f : plein ecran", True, (100, 100, 100))
        screen.blit(f_text, (WIDTH - 110, HEIGHT - 25))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --- GESTION MUSIQUE ---
                # Touche M toute seule (Mute)
                if event.key == pygame.K_m and not (pygame.key.get_mods() & pygame.KMOD_CTRL or pygame.key.get_mods() & pygame.KMOD_ALT):
                    is_muted = not is_muted
                    if is_muted: pygame.mixer.music.pause()
                    else: pygame.mixer.music.unpause()
                
                # CTRL + M (Suivant)
                elif event.key == pygame.K_m and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    index_musique = (index_musique + 1) % 15 # Retourne à 0 après 14
                    charger_et_jouer(index_musique)
                    is_muted = False
                
                # ALT + M (Précédent)
                elif event.key == pygame.K_m and (pygame.key.get_mods() & pygame.KMOD_ALT):
                    index_musique = (index_musique - 1) % 15 # Retourne à 14 avant 0
                    charger_et_jouer(index_musique)
                    is_muted = False

                # --- GESTION ECRAN ET JEUX ---
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen: screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else: screen = pygame.display.set_mode((WIDTH, HEIGHT))
                
                elif event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_1: run_snake()
                elif event.key == pygame.K_2: run_pong()
                elif event.key == pygame.K_3: run_breakout()
                elif event.key == pygame.K_4: run_dodge()
                elif event.key == pygame.K_5: run_morpion()
                elif event.key == pygame.K_6: run_flappy()
                elif event.key == pygame.K_7: run_aim()
                elif event.key == pygame.K_8: run_memory()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()