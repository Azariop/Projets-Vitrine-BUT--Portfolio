import pygame
import random
import time

# ===== CONSTANTES =====
GAME_SIZE = 600
BLANC, NOIR, ROUGE, VERT, BLEU, JAUNE = (255,255,255), (0,0,0), (255,50,50), (50,255,50), (0,102,255), (255,255,0)
COULEURS_BASE = [ROUGE, VERT, BLEU, JAUNE, (255,165,0), (128,0,128), (0,255,255), (150,75,0)] * 2

class MemoryGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 80)
        self.font_small = pygame.font.SysFont(None, 35)
        self.update_offsets()
        self.reset_game_state()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - GAME_SIZE) // 2
        self.offset_y = (self.screen.get_height() - GAME_SIZE) // 2

    def reset_game_state(self):
        random.shuffle(COULEURS_BASE)
        self.cards = []
        for i in range(16):
            row, col = i // 4, i % 4
            rect = pygame.Rect(col * 150 + 10, row * 150 + 10, 130, 130)
            self.cards.append({'rect': rect, 'color': COULEURS_BASE[i], 'revealed': False, 'matched': False})
        
        self.selected = []
        self.waiting = False
        self.timer_flip = 0
        self.score = 0
        self.clicks = 0
        self.start_time = time.time()
        self.final_time = 0
        self.running = True

    def draw_text_centered(self, text, y_rel, color, font):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.screen.get_width() // 2, self.offset_y + y_rel))
        self.screen.blit(surf, rect)

    def menu_info(self):
        info = True
        while info:
            self.screen.fill(NOIR)
            self.draw_text_centered("INFOS - MEMORY", 100, BLEU, self.font_big)
            lines = [
                "[ TOUCHES ] : Cliquez sur les cartes pour trouver les paires.",
                "",
                "[ HISTOIRE ] : Appele aussi 'Concentration', c'est un jeu traditionnel",
                "tres ancien. Le principe est d'associer un visuel a une position",
                "spatiale pour renforcer l'hippocampe (zone de la memoire).",
                "",
                "ESPACE ou I - Retour"
            ]
            for i, l in enumerate(lines):
                self.draw_text_centered(l, 250 + i*50, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key in [pygame.K_i, pygame.K_SPACE]:
                    info = False

    def pause_menu(self):
        pause_start = time.time() # Pour ne pas penaliser le chrono pendant la pause
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 250, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre | I - Infos | EFFACER - Menu Hub", 350, BLANC, self.font_small)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE: 
                        self.start_time += (time.time() - pause_start) # On decale le temps de depart
                        pausing = False
                    if e.key == pygame.K_i: self.menu_info()
                    if e.key == pygame.K_BACKSPACE: return "QUIT"
        return "CONTINUE"

    def run(self):
        while self.running:
            self.clock.tick(60)
            
            # Calcul du chrono
            if self.score < 8:
                elapsed_time = int(time.time() - self.start_time)
            
            mouse_pos = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()
                        self.update_offsets()
                    if e.key == pygame.K_i:
                        self.menu_info()
                    if e.key == pygame.K_SPACE: 
                        if self.pause_menu() == "QUIT": return

                if e.type == pygame.MOUSEBUTTONDOWN and not self.waiting and self.score < 8:
                    for card in self.cards:
                        adj_rect = card['rect'].move(self.offset_x, self.offset_y)
                        if adj_rect.collidepoint(mouse_pos) and not card['revealed'] and not card['matched']:
                            card['revealed'] = True
                            self.selected.append(card)
                            self.clicks += 1 # On compte le clic
                            
                            if len(self.selected) == 2:
                                if self.selected[0]['color'] == self.selected[1]['color']:
                                    self.selected[0]['matched'] = self.selected[1]['matched'] = True
                                    self.selected = []
                                    self.score += 1
                                    if self.score == 8: self.final_time = elapsed_time
                                else:
                                    self.waiting = True
                                    self.timer_flip = pygame.time.get_ticks()

            if self.waiting and pygame.time.get_ticks() - self.timer_flip > 600:
                self.selected[0]['revealed'] = self.selected[1]['revealed'] = False
                self.selected, self.waiting = [], False

            # DESSIN
            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_SIZE+4, GAME_SIZE+4), 2)
            
            for card in self.cards:
                cx, cy = self.offset_x + card['rect'].x, self.offset_y + card['rect'].y
                color = card['color'] if (card['revealed'] or card['matched']) else (60, 60, 60)
                pygame.draw.rect(self.screen, color, (cx, cy, 130, 130))
                pygame.draw.rect(self.screen, BLANC, (cx, cy, 130, 130), 2)

            # HUD (Temps et Clics)
            self.draw_text_centered(f"Paires: {self.score}/8  |  Clics: {self.clicks}  |  Temps: {elapsed_time}s", -40, BLANC, self.font_small)
            
            if self.score == 8:
                overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0,0))
                self.draw_text_centered("VICTOIRE !", 200, VERT, self.font_big)
                self.draw_text_centered(f"Score : {self.clicks} clics en {self.final_time} secondes", 300, JAUNE, self.font_small)
                self.draw_text_centered("R: Rejouer | EFFACER: Menu Hub", 400, BLANC, self.font_small)
                if pygame.key.get_pressed()[pygame.K_r]: self.reset_game_state()

            pygame.display.flip()

def run_memory(*args):
    MemoryGame().run()