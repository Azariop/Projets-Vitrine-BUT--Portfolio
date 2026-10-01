import pygame
import random

# ===== CONSTANTES FIXES =====
GAME_SIZE = 700
BLANC, NOIR, ROUGE, VERT, BLEU, JAUNE = (255,255,255), (0,0,0), (255,50,50), (50,255,50), (0,102,255), (255,255,0)

class DodgeGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.font_big, self.font_small = pygame.font.SysFont(None, 80), pygame.font.SysFont(None, 40)
        self.update_offsets()
        self.reset_game_state()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - GAME_SIZE) // 2
        self.offset_y = (self.screen.get_height() - GAME_SIZE) // 2

    def reset_game_state(self):
        self.player_rect = pygame.Rect(GAME_SIZE//2, GAME_SIZE//2, 30, 30)
        self.enemies = []
        self.score = 0
        self.spawn_timer = 0
        self.running = True

    def draw_text_centered(self, text, y_rel, color, font):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.screen.get_width()//2, self.offset_y + y_rel))
        self.screen.blit(surf, rect)

    def menu_info(self):
        info = True
        while info:
            self.screen.fill(NOIR)
            self.draw_text_centered("INFOS - DODGE", 100, BLEU, self.font_big)
            lines = [
                "[ TOUCHES ] : Fleches Directionnelles pour esquiver les blocs.",
                "",
                "[ HISTOIRE ] : Inspire des jeux de type 'Bullet Hell' japonais (comme Touhou).",
                "Ces jeux testent la concentration extreme et la vision peripherique",
                "en saturant l'ecran d'obstacles a eviter au pixel pres.",
                "",
                "ESPACE ou I - Retour"
            ]
            for i, l in enumerate(lines): self.draw_text_centered(l, 250 + i*50, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key in [pygame.K_i, pygame.K_SPACE]: info = False

    def pause_menu(self):
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)); self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 250, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre | I - Infos | EFFACER - Menu Hub", 350, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE: pausing = False
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key == pygame.K_BACKSPACE: return "QUIT"
        return "CONTINUE"

    def start_screen(self):
        """Ecran de presentation"""
        waiting = True
        while waiting:
            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_SIZE+4, GAME_SIZE+4), 2)
            self.draw_text_centered("DODGE GAME", 200, ROUGE, self.font_big)
            self.draw_text_centered("ESPACE - Commencer", 320, BLANC, self.font_small)
            self.draw_text_centered("I - Infos | F - Plein Ecran", 380, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f: pygame.display.toggle_fullscreen(); self.update_offsets()
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key == pygame.K_SPACE: waiting = False
                    if e.key == pygame.K_BACKSPACE: return "QUIT"
        return "START"

    def end_screen(self):
        """Ecran de Game Over"""
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered("GAME OVER", 200, ROUGE, self.font_big)
            self.draw_text_centered(f"Score Final: {self.score}", 300, JAUNE, self.font_small)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu Hub", 400, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r: return "REPLAY"
                    if e.key == pygame.K_BACKSPACE: return "QUIT"

    def run(self):
        if self.start_screen() == "QUIT": return
        
        while self.running:
            self.clock.tick(60)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f: pygame.display.toggle_fullscreen(); self.update_offsets()
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key == pygame.K_SPACE: 
                        if self.pause_menu() == "QUIT": return
            
            keys = pygame.key.get_pressed()
            speed = 7
            if keys[pygame.K_LEFT] and self.player_rect.x > 0: self.player_rect.x -= speed
            if keys[pygame.K_RIGHT] and self.player_rect.x < GAME_SIZE-30: self.player_rect.x += speed
            if keys[pygame.K_UP] and self.player_rect.y > 0: self.player_rect.y -= speed
            if keys[pygame.K_DOWN] and self.player_rect.y < GAME_SIZE-30: self.player_rect.y += speed

            self.spawn_timer += 1
            if self.spawn_timer > 12:
                side = random.choice(['t','b','l','r'])
                s = random.randint(15,40)
                if side=='t': ex, ey, dx, dy = random.randint(0,GAME_SIZE), -s, random.uniform(-2,2), random.uniform(2,5)
                elif side=='b': ex, ey, dx, dy = random.randint(0,GAME_SIZE), GAME_SIZE, random.uniform(-2,2), random.uniform(-5,-2)
                elif side=='l': ex, ey, dx, dy = -s, random.randint(0,GAME_SIZE), random.uniform(2,5), random.uniform(-2,2)
                else: ex, ey, dx, dy = GAME_SIZE, random.randint(0,GAME_SIZE), random.uniform(-5,-2), random.uniform(-2,2)
                
                self.enemies.append({'r': pygame.Rect(ex, ey, s, s), 'dx': dx*1.8, 'dy': dy*1.8})
                self.spawn_timer = 0

            for en in self.enemies[:]:
                en['r'].x += en['dx']; en['r'].y += en['dy']
                if en['r'].colliderect(self.player_rect):
                    if self.end_screen() == "QUIT": return
                    self.reset_game_state()
                if not en['r'].inflate(100,100).colliderect(pygame.Rect(0,0,GAME_SIZE,GAME_SIZE)):
                    self.enemies.remove(en); self.score += 1

            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_SIZE+4, GAME_SIZE+4), 2)
            pygame.draw.rect(self.screen, VERT, (self.offset_x+self.player_rect.x, self.offset_y+self.player_rect.y, 30, 30))
            for en in self.enemies:
                pygame.draw.rect(self.screen, ROUGE, (self.offset_x+en['r'].x, self.offset_y+en['r'].y, en['r'].width, en['r'].height))
            self.draw_text_centered(f"Score: {self.score}", 30, BLANC, self.font_small)
            pygame.display.flip()

def run_dodge():
    DodgeGame().run()