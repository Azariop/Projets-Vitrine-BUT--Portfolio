import pygame
import sys
import random

# ===== CONSTANTES FIXES (MODE HARD+) =====
GAME_WIDTH = 400
GAME_HEIGHT = 600
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (50, 255, 50)
JAUNE = (255, 255, 0)
ROUGE = (255, 50, 50)
BLEU = (0, 102, 255)

class FlappyGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
            
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 80)
        self.font_small = pygame.font.SysFont(None, 40)
        
        self.update_offsets()
        
        # --- RÉGLAGES PLUS DURS ---
        self.gravity = 0.40      # Plus lourd
        self.jump_force = -7     # Saut sec
        self.pipe_speed = 5      # Plus rapide
        self.gap_size = 145      # Passage encore plus serré
        
        self.reset_game_state()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - GAME_WIDTH) // 2
        self.offset_y = (self.screen.get_height() - GAME_HEIGHT) // 2

    def reset_game_state(self):
        self.bird_y = GAME_HEIGHT // 2
        self.bird_vel = 0
        self.bird_size = 30
        self.pipes = []
        self.score = 0
        self.spawn_timer = 0
        self.running = True

    def spawn_pipe(self):
        height = random.randint(100, GAME_HEIGHT - self.gap_size - 100)
        self.pipes.append({'x': GAME_WIDTH, 'top': height, 'passed': False})

    def gerer_ecran_et_musique(self, event):
        import main
        if event.key == pygame.K_f:
            pygame.display.toggle_fullscreen()
            self.update_offsets()
        if event.key == pygame.K_m:
            if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()

    def draw_text_centered(self, text, y_rel, color, font):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.screen.get_width() // 2, self.offset_y + y_rel))
        self.screen.blit(surf, rect)

    def start_screen(self, only_info=False):
        waiting = True
        show_info = only_info
        while waiting:
            self.screen.fill(NOIR)
            if not show_info:
                self.draw_text_centered("FLAPPY CUBE", 60, JAUNE, self.font_big)
                lines = [
                    "FLECHE HAUT - Sauter",
                    "ESPACE - Pause",
                    "I - Aspect Educatif",
                    "EFFACER - Menu Hub"
                ]
            else:
                self.draw_text_centered("INFOS", 80, BLEU, self.font_big)
                lines = [
                "[ TOUCHES ] : Fleche HAUT pour battre des ailes et monter.",
                "",
                "[ HISTOIRE ] : Sorti en 2013 par Dong Nguyen, ce jeu est devenu un",
                "phenomene social avant d'etre retire des stores par son createur.",
                "Il utilise une physique de gravite simple mais ultra exigeante.",
                "",
                "ESPACE ou I - Retour"
            ]

            y = 200
            for l in lines:
                self.draw_text_centered(l, y, BLANC, self.font_small)
                y += 50
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_ecran_et_musique(event)
                    if event.key == pygame.K_i: 
                        show_info = not show_info
                        if only_info and not show_info: return "CONTINUE"
                    if event.key == pygame.K_UP and not show_info: waiting = False
                    if event.key == pygame.K_BACKSPACE: return "QUIT"
        return "START"

    def pause_menu(self):
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 200, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre | I - Info", 320, BLANC, self.font_small)
            self.draw_text_centered("EFFACER - Menu Hub", 380, BLANC, self.font_small)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_ecran_et_musique(event)
                    if event.key == pygame.K_SPACE: pausing = False
                    if event.key == pygame.K_i: self.start_screen(only_info=True)
                    if event.key == pygame.K_BACKSPACE: return "MENU"
        return "CONTINUE"

    def run(self):
        if self.start_screen() == "QUIT": return
        self.reset_game_state()

        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    self.gerer_ecran_et_musique(event)
                    if event.key == pygame.K_UP:
                        self.bird_vel = self.jump_force
                    if event.key == pygame.K_SPACE:
                        if self.pause_menu() == "MENU": return

            # Physique
            self.bird_vel += self.gravity
            self.bird_y += self.bird_vel
            bird_rect = pygame.Rect(self.offset_x + 50, self.offset_y + self.bird_y, self.bird_size, self.bird_size)

            if self.bird_y < 0 or self.bird_y > GAME_HEIGHT - self.bird_size:
                self.running = False

            # Tuyaux
            self.spawn_timer += 1
            if self.spawn_timer > 65: # Plus de tuyaux
                self.spawn_pipe()
                self.spawn_timer = 0

            for p in self.pipes[:]:
                p['x'] -= self.pipe_speed
                t_rect = pygame.Rect(self.offset_x + p['x'], self.offset_y, 50, p['top'])
                b_rect = pygame.Rect(self.offset_x + p['x'], self.offset_y + p['top'] + self.gap_size, 50, GAME_HEIGHT)

                if bird_rect.colliderect(t_rect) or bird_rect.colliderect(b_rect):
                    self.running = False

                if not p['passed'] and p['x'] < 50:
                    self.score += 1
                    p['passed'] = True
                if p['x'] < -50: self.pipes.remove(p)

            # Dessin
            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_WIDTH+4, GAME_HEIGHT+4), 2)
            for p in self.pipes:
                pygame.draw.rect(self.screen, VERT, (self.offset_x + p['x'], self.offset_y, 50, p['top']))
                pygame.draw.rect(self.screen, VERT, (self.offset_x + p['x'], self.offset_y + p['top'] + self.gap_size, 50, GAME_HEIGHT))
            pygame.draw.rect(self.screen, JAUNE, bird_rect)
            
            score_txt = self.font_small.render(f"Score: {self.score}", True, BLANC)
            self.screen.blit(score_txt, (self.offset_x + 10, self.offset_y + 10))
            pygame.display.flip()

        self.game_over_screen()

    def game_over_screen(self):
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered("GAME OVER", 200, ROUGE, self.font_big)
            self.draw_text_centered(f"Score Final: {self.score}", 300, BLANC, self.font_small)
            self.draw_text_centered("R: Rejouer | EFFACER: Menu", 400, BLANC, self.font_small)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_ecran_et_musique(event)
                    if event.key == pygame.K_r: 
                        self.reset_game_state(); self.run(); return
                    if event.key == pygame.K_BACKSPACE: return

def run_flappy():
    FlappyGame().run()