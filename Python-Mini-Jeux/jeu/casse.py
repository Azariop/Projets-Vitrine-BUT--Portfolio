import pygame
import sys
import random

# ===== CONSTANTES =====
GAME_WIDTH = 800
GAME_HEIGHT = 600
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 102, 255)
ROUGE = (255, 50, 50)
VERT = (50, 255, 50)

class BreakoutGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
            
        pygame.display.set_caption("Casse-Briques - SAE")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 80)
        self.font_menu = pygame.font.SysFont(None, 35)
        
        self.update_offsets()
        
        # --- RÉGLAGES INITIAUX ---
        self.difficulty = 1  # 1: Trés Lent, 2: Moyen, 3: Rapide
        self.cols = 10
        self.rows = 4
        self.lives_start = 3
        self.reset_game_state()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - GAME_WIDTH) // 2
        self.offset_y = (self.screen.get_height() - GAME_HEIGHT) // 2

    def reset_game_state(self):
        self.paddle_w, self.paddle_h = 120, 15
        self.paddle_x = GAME_WIDTH // 2 - self.paddle_w // 2
        self.paddle_y = GAME_HEIGHT - 40
        self.paddle_speed = 9
        
        self.ball_radius = 8
        self.reset_ball()
        
        self.lives = self.lives_start
        self.score = 0
        self.bricks = []
        self.create_bricks()
        self.running = True

    def reset_ball(self):
        self.ball_x = GAME_WIDTH // 2
        self.ball_y = GAME_HEIGHT // 2 + 50
        # VITESSES RÉAJUSTÉES (Plus douces)
        spd = [3, 5, 8][self.difficulty - 1]
        self.ball_dx = spd * random.choice([-1, 1])
        self.ball_dy = -spd

    def create_bricks(self):
        self.bricks = []
        margin = 40
        available_width = GAME_WIDTH - (margin * 2)
        brick_w = available_width // self.cols
        brick_h = 25
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(margin + c * brick_w, 70 + r * brick_h, brick_w - 4, brick_h - 4)
                self.bricks.append(rect)

    def gerer_musique_et_ecran(self, event):
        import main
        if event.key == pygame.K_m:
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
                self.draw_text_centered("CASSE-BRIQUES", 60, ROUGE, self.font_big)
                diff_txt = ["Tranquille", "Standard", "Expert"][self.difficulty - 1]
                lines = [
                    f"Vitesse : {diff_txt} (V / B)",
                    f"Largeur Mur : {self.cols} colonnes (G / D)",
                    f"Hauteur Mur : {self.rows} lignes (Z / S)",
                    f"Vies : {self.lives_start} (+ / -)",
                    "",
                    "ESPACE - Lancer la partie", "I - Infos", "EFFACER - Menu Hub"
                ]
            else:
                self.draw_text_centered("INFOS", 80, BLEU, self.font_big)
                lines = [
                "[ TOUCHES ] : Fleches Gauche / Droite pour bouger la plateforme.",
                "",
                "[ HISTOIRE ] : Cree par Steve Jobs et Steve Wozniak (fondateurs d'Apple)",
                "pour Atari en 1976. C'est une evolution de Pong ou le joueur",
                "doit detruire un mur brique par brique.",
                "",
                "ESPACE ou I - Retour"
            ]
            
            y = 180
            for l in lines:
                self.draw_text_centered(l, y, BLANC, self.font_menu)
                y += 45
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        if pygame.mixer.music.get_pause(): 
                         pygame.mixer.music.unpause()    
                    else: 
                        pygame.mixer.music.pause()
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_BACKSPACE: return "QUIT"
                    if event.key == pygame.K_i: show_info = not show_info
                    if not show_info:
                        if event.key == pygame.K_SPACE: selecting = False
                        # Réglages
                        if event.key == pygame.K_v: self.difficulty = min(3, self.difficulty + 1)
                        if event.key == pygame.K_b: self.difficulty = max(1, self.difficulty - 1)
                        if event.key == pygame.K_RIGHT: self.cols = min(20, self.cols + 1)
                        if event.key == pygame.K_LEFT: self.cols = max(5, self.cols - 1)
                        if event.key == pygame.K_z: self.rows = min(10, self.rows + 1)
                        if event.key == pygame.K_s: self.rows = max(1, self.rows - 1)
                        if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS]: self.lives_start = min(10, self.lives_start + 1)
                        if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.lives_start = max(1, self.lives_start - 1)
        return "START"

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
            if keys[pygame.K_LEFT] and self.paddle_x > 0: self.paddle_x -= self.paddle_speed
            if keys[pygame.K_RIGHT] and self.paddle_x < GAME_WIDTH - self.paddle_w: self.paddle_x += self.paddle_speed

            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy

            if self.ball_x <= 0 or self.ball_x >= GAME_WIDTH - self.ball_radius*2: self.ball_dx *= -1
            if self.ball_y <= 0: self.ball_dy *= -1
            
            if self.ball_y >= GAME_HEIGHT:
                self.lives -= 1
                if self.lives <= 0:
                    if self.end_game_screen("GAME OVER") == "MENU": return
                    self.reset_game_state()
                else: self.reset_ball()

            ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_radius*2, self.ball_radius*2)
            paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_w, self.paddle_h)
            
            if ball_rect.colliderect(paddle_rect):
                self.ball_dy *= -1
                self.ball_y = self.paddle_y - self.ball_radius*2

            for brick in self.bricks[:]:
                if ball_rect.colliderect(brick):
                    self.bricks.remove(brick)
                    self.ball_dy *= -1
                    self.score += 10
                    break

            if not self.bricks:
                if self.end_game_screen("VICTOIRE !") == "MENU": return
                self.reset_game_state()

            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_WIDTH+4, GAME_HEIGHT+4), 2)
            pygame.draw.rect(self.screen, BLEU, (self.offset_x + self.paddle_x, self.offset_y + self.paddle_y, self.paddle_w, self.paddle_h))
            pygame.draw.circle(self.screen, BLANC, (int(self.offset_x + self.ball_x + self.ball_radius), int(self.offset_y + self.ball_y + self.ball_radius)), self.ball_radius)
            for b in self.bricks:
                pygame.draw.rect(self.screen, VERT, (self.offset_x + b.x, self.offset_y + b.y, b.width, b.height))
            
            self.draw_text_centered(f"Score: {self.score} | Vies: {self.lives}", 30, BLANC, self.font_menu)
            pygame.display.flip()

    def pause(self):
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 200, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre | EFFACER - Menu", 320, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: pausing = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE: return "MENU"
        return "CONTINUE"

    def end_game_screen(self, msg):
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered(msg, 200, ROUGE if "OVER" in msg else VERT, self.font_big)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu Hub", 350, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return "REPLAY"
                    if event.key == pygame.K_BACKSPACE: return "MENU"

def run_breakout():
    BreakoutGame().run()