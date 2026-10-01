import pygame
import random
import time

# ===== CONSTANTES =====
WIDTH_GAME, HEIGHT_GAME = 1000, 700
BLANC, NOIR, ROUGE, VERT, BLEU, JAUNE = (255,255,255), (0,0,0), (255,50,50), (50,255,50), (0,102,255), (255,255,0)

class AimTrainer:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.font_big, self.font_small = pygame.font.SysFont(None, 80), pygame.font.SysFont(None, 40)
        self.update_offsets()
        self.difficulty_time = 2.0
        self.reset_game_state()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - WIDTH_GAME) // 2
        self.offset_y = (self.screen.get_height() - HEIGHT_GAME) // 2

    def reset_game_state(self):
        self.target = None
        self.score = 0
        self.running = True
        self.spawn_target()

    def spawn_target(self):
        radius = random.randint(20, 35)
        self.target = {
            'x': random.randint(radius, WIDTH_GAME - radius),
            'y': random.randint(radius, HEIGHT_GAME - radius),
            'r': radius,
            'start_time': time.time()
        }

    def draw_text_centered(self, text, y_rel, color, font):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.screen.get_width()//2, self.offset_y + y_rel))
        self.screen.blit(surf, rect)

    def menu_info(self):
        info = True
        while info:
            self.screen.fill(NOIR)
            self.draw_text_centered("INFOS - AIM TRAINER", 100, BLEU, self.font_big)
            lines = [
                "[ TOUCHES ] : Cliquez le plus vite possible sur les cibles rouges.",
                "",
                "[ HISTOIRE ] : Les Aim Trainers sont nes avec la scene competitive",
                "de Quake et Counter-Strike. Ils servent d'echauffement pour",
                "developper la memoire musculaire et les micro-ajustements.",
                "",
                "ESPACE ou I - Retour"
            ]
            for i, l in enumerate(lines): self.draw_text_centered(l, 250 + i*50, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key in [pygame.K_i, pygame.K_SPACE]: info = False

    def pause_menu(self):
        pause_start = time.time()
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 250, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre | I - Infos | EFFACER - Menu", 350, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE: 
                        self.target['start_time'] += (time.time() - pause_start)
                        pausing = False
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key == pygame.K_BACKSPACE: return "QUIT"
        return "CONTINUE"

    def start_screen(self):
        waiting = True
        while waiting:
            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, WIDTH_GAME+4, HEIGHT_GAME+4), 2)
            self.draw_text_centered("AIM TRAINER", 100, VERT, self.font_big)
            self.draw_text_centered("1: Facile (3s) | 2: Moyen (2s) | 3: Hard (1s)", 250, BLANC, self.font_small)
            self.draw_text_centered("Ne ratez aucune cible !", 320, ROUGE, self.font_small)
            self.draw_text_centered("I - Infos | F - Plein Ecran", 450, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f: pygame.display.toggle_fullscreen(); self.update_offsets()
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key in [pygame.K_1, pygame.K_KP1]: self.difficulty_time = 3.0; waiting = False
                    if e.key in [pygame.K_2, pygame.K_KP2]: self.difficulty_time = 2.0; waiting = False
                    if e.key in [pygame.K_3, pygame.K_KP3]: self.difficulty_time = 1.0; waiting = False
                    if e.key == pygame.K_BACKSPACE: return "QUIT"
        return "START"

    def run(self):
        while True:
            if self.start_screen() == "QUIT": return
            self.reset_game_state()
            game_on = True
            
            while game_on:
                self.clock.tick(60)
                m_pos = pygame.mouse.get_pos()
                now = time.time()

                if now - self.target['start_time'] > self.difficulty_time:
                    if self.end_screen("TROP LENT !") == "QUIT": return
                    game_on = False

                for e in pygame.event.get():
                    if e.type == pygame.QUIT: return
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_f: pygame.display.toggle_fullscreen(); self.update_offsets()
                        if e.key == pygame.K_i: self.menu_info()
                        if e.key == pygame.K_SPACE:
                            if self.pause_menu() == "QUIT": return
                    
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        tx, ty = self.offset_x + self.target['x'], self.offset_y + self.target['y']
                        if ((m_pos[0]-tx)**2 + (m_pos[1]-ty)**2)**0.5 < self.target['r']:
                            self.score += 1
                            self.spawn_target()
                        else:
                            if self.end_screen("RATE !") == "QUIT": return
                            game_on = False

                self.screen.fill(NOIR)
                pygame.draw.rect(self.screen, (20,20,20), (self.offset_x, self.offset_y, WIDTH_GAME, HEIGHT_GAME))
                pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, WIDTH_GAME+4, HEIGHT_GAME+4), 2)
                
                pct = 1.0 - ((now - self.target['start_time']) / self.difficulty_time)
                pygame.draw.circle(self.screen, ROUGE, (self.offset_x+self.target['x'], self.offset_y+self.target['y']), self.target['r'])
                pygame.draw.circle(self.screen, BLANC, (self.offset_x+self.target['x'], self.offset_y+self.target['y']), max(0, int(self.target['r']*pct)), 3)
                
                self.draw_text_centered(f"Score: {self.score}", 30, BLANC, self.font_small)
                pygame.display.flip()

    def end_screen(self, msg):
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered(msg, 200, ROUGE, self.font_big)
            self.draw_text_centered(f"Score: {self.score}", 300, JAUNE, self.font_small)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu Hub", 420, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r: return "REPLAY"
                    if e.key == pygame.K_BACKSPACE: return "QUIT"

def run_aim():
    AimTrainer().run()