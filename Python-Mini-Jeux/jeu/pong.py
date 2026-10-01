import pygame
import sys
import random

# ===== CONSTANTES DU JEU =====
GAME_WIDTH = 1000
GAME_HEIGHT = 700
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 102, 255)
ROUGE = (255, 50, 50)
OR = (255, 215, 0)

# Vitesse des raquettes (Z/S et Haut/Bas)
PADDLE_SPEED = 8 

class PongGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
            
        pygame.display.set_caption("Pong - SAE")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 100)
        self.font_menu = pygame.font.SysFont(None, 40)
        
        self.update_offsets()
        
        # --- RÉGLAGES PAR DÉFAUT ---
        self.vs_bot = True
        self.difficulty = 2 # 1: Facile, 2: Moyen, 3: Hard
        self.score_max = 5
        self.reset_game_state()

    def update_offsets(self):
        """Centre le terrain de 1000x700 dans la fenêtre"""
        self.offset_x = (self.screen.get_width() - GAME_WIDTH) // 2
        self.offset_y = (self.screen.get_height() - GAME_HEIGHT) // 2

    def reset_game_state(self):
        self.paddle_w, self.paddle_h = 15, 110
        self.p1_y = GAME_HEIGHT // 2 - self.paddle_h // 2
        self.p2_y = GAME_HEIGHT // 2 - self.paddle_h // 2
        self.ball_x = GAME_WIDTH // 2
        self.ball_y = GAME_HEIGHT // 2
        self.ball_size = 15
        
        # Vitesse initiale de la balle
        self.base_speed = 4 
        self.ball_dx = self.base_speed * random.choice([-1, 1])
        self.ball_dy = self.base_speed * random.choice([-1, 1])
        
        self.vitesse_affichee = 40
        self.score = {"P1": 0, "P2": 0}
        self.running = True

    def gerer_musique_et_ecran(self, event):
        """Gestion Playlist (M, Ctrl+M, Alt+M) et Plein écran (F)"""
        import main
        if event.key == pygame.K_m:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL:
                main.index_musique = (main.index_musique + 1) % 15
                main.charger_et_jouer(main.index_musique)
            elif mods & pygame.KMOD_ALT:
                main.index_musique = (main.index_musique - 1) % 15
                main.charger_et_jouer(main.index_musique)
            else:
                if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
                else: pygame.mixer.music.unpause()
        if event.key == pygame.K_f:
            pygame.display.toggle_fullscreen()
            self.update_offsets()

    def draw_text_centered(self, text, y_rel, color, font):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.screen.get_width() // 2, self.offset_y + y_rel))
        self.screen.blit(surf, rect)

    def start_screen(self, only_info=False):
        selecting = True
        show_info = only_info
        while selecting:
            self.screen.fill(NOIR)
            if not show_info:
                self.draw_text_centered("PONG", 80, BLANC, self.font_big)
                diff_label = ["IA Facile", "IA Normale", "IA Hard"][self.difficulty - 1]
                lines = [
                    f"Mode : {'Vs Bot' if self.vs_bot else '1v1'} (Fleches G/D)",
                    f"Niveau Bot : {diff_label} (Z/S pour changer)",
                    f"Score max : {self.score_max} (+/-)",
                    "ESPACE - Jouer", "I - Aspect Educatif", "EFFACER - Menu Hub"
                ]
            else:
                self.draw_text_centered("INFOS", 80, BLEU, self.font_big)
                lines = [
                "[ TOUCHES ] : Z (Haut) et S (Bas) pour deplacer la raquette.",
                "",
                "[ HISTOIRE ] : Sorti par Atari en 1972, Pong est le premier jeu video",
                "a avoir connu un succes commercial massif. Il simule un tennis",
                "de table et a lance l'industrie des bornes d'arcade.",
                "",
                "ESPACE ou I - Retour"
            ]

            y = 250
            for l in lines:
                self.draw_text_centered(l, y, BLANC, self.font_menu)
                y += 55
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_BACKSPACE: return "QUIT"
                    if event.key == pygame.K_i: 
                        show_info = not show_info
                        if only_info and not show_info: return "CONTINUE"
                    if not show_info:
                        if event.key == pygame.K_SPACE: selecting = False
                        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]: self.vs_bot = not self.vs_bot
                        if event.key == pygame.K_z: self.difficulty = min(3, self.difficulty + 1)
                        if event.key == pygame.K_s: self.difficulty = max(1, self.difficulty - 1)
                        if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS]: self.score_max += 1
                        if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.score_max = max(1, self.score_max - 1)
        return "START"

    def pause(self):
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 200, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre", 320, BLANC, self.font_menu)
            self.draw_text_centered("I - Info Educative", 380, BLANC, self.font_menu)
            self.draw_text_centered("EFFACER - Menu Hub", 440, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_SPACE: pausing = False
                    if event.key == pygame.K_i: self.start_screen(only_info=True)
                    if event.key == pygame.K_BACKSPACE: return "MENU"
        return "CONTINUE"

    def reset_ball(self):
        self.ball_x, self.ball_y = GAME_WIDTH // 2, GAME_HEIGHT // 2
        self.ball_dx = self.base_speed * random.choice([-1, 1])
        self.ball_dy = self.base_speed * random.choice([-1, 1])
        self.vitesse_affichee = 40

    def run(self):
        if self.start_screen() == "QUIT": return
        self.reset_game_state()
        
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_SPACE:
                        if self.pause() == "MENU": return

            keys = pygame.key.get_pressed()
            # Joueur 1 (Z/S)
            if keys[pygame.K_z] and self.p1_y > 0: self.p1_y -= PADDLE_SPEED
            if keys[pygame.K_s] and self.p1_y < GAME_HEIGHT - self.paddle_h: self.p1_y += PADDLE_SPEED

            # IA ou Joueur 2
            if self.vs_bot:
                v_ia = [6, 9, 13][self.difficulty - 1]
                if self.p2_y + self.paddle_h // 2 < self.ball_y: self.p2_y += v_ia
                if self.p2_y + self.paddle_h // 2 > self.ball_y: self.p2_y -= v_ia
            else:
                if keys[pygame.K_UP] and self.p2_y > 0: self.p2_y -= PADDLE_SPEED
                if keys[pygame.K_DOWN] and self.p2_y < GAME_HEIGHT - self.paddle_h: self.p2_y += PADDLE_SPEED

            # MOUVEMENT BALLE
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy

            # Rebond Haut/Bas
            if self.ball_y <= 0:
                self.ball_y = 0
                self.ball_dy *= -1
            elif self.ball_y >= GAME_HEIGHT - self.ball_size:
                self.ball_y = GAME_HEIGHT - self.ball_size
                self.ball_dy *= -1

            ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size)
            p1_rect = pygame.Rect(20, self.p1_y, self.paddle_w, self.paddle_h)
            p2_rect = pygame.Rect(GAME_WIDTH - 35, self.p2_y, self.paddle_w, self.paddle_h)

            # COLLISIONS ET ACCÉLÉRATION PRO
            if ball_rect.colliderect(p1_rect) or ball_rect.colliderect(p2_rect):
                self.ball_dx *= -1
                
                # Phase 1 : Avant 120 km/h (Physique)
                if self.vitesse_affichee < 120:
                    self.ball_dx *= 1.10
                    self.ball_dy *= 1.10
                # Phase 2 : Après 120 km/h (Mode Pro)
                else:
                    boost = 0.3 # Accélération physique infinie mais fine
                    if self.ball_dx > 0: self.ball_dx += boost
                    else: self.ball_dx -= boost
                
                # Calcul de l'affichage km/h
                self.vitesse_affichee = int(abs(self.ball_dx) * 10)

                # Sécurité anti-crash : sortir la balle de la raquette
                if self.ball_dx > 0: self.ball_x = p1_rect.right + 1
                else: self.ball_x = p2_rect.left - self.ball_size - 1

            # Points
            if self.ball_x < 0:
                self.score["P2"] += 1; self.reset_ball()
            elif self.ball_x > GAME_WIDTH:
                self.score["P1"] += 1; self.reset_ball()

            # Victoire
            if self.score["P1"] >= self.score_max or self.score["P2"] >= self.score_max:
                winner = "Joueur 1" if self.score["P1"] >= self.score_max else "Bot"
                if self.end_game_screen(winner) == "MENU": return
                self.reset_game_state()

            # DESSIN
            self.screen.fill(NOIR)
            # Bordure terrain
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_WIDTH+4, GAME_HEIGHT+4), 2)
            # Raquettes
            pygame.draw.rect(self.screen, BLANC, (self.offset_x + 20, self.offset_y + self.p1_y, self.paddle_w, self.paddle_h))
            pygame.draw.rect(self.screen, ROUGE, (self.offset_x + GAME_WIDTH - 35, self.offset_y + self.p2_y, self.paddle_w, self.paddle_h))
            # Balle
            pygame.draw.ellipse(self.screen, BLANC, (self.offset_x + self.ball_x, self.offset_y + self.ball_y, self.ball_size, self.ball_size))
            
            # Textes (Score et Vitesse)
            self.draw_text_centered(f"{self.score['P1']} | {self.score['P2']}", 40, BLANC, self.font_menu)
            v_txt = self.font_menu.render(f"{self.vitesse_affichee} km/h", True, OR if self.vitesse_affichee >= 120 else BLANC)
            self.screen.blit(v_txt, (self.offset_x + 20, self.offset_y + 20))
            
            pygame.display.flip()

    def end_game_screen(self, winner):
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered(f"{winner} GAGNE !", 250, BLANC, self.font_big)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu Hub", 380, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_r: return "REPLAY"
                    if event.key == pygame.K_BACKSPACE: return "MENU"

def run_pong():
    PongGame().run()