import pygame
import sys
import random

# ===== CONSTANTES DU JEU =====
GAME_SIZE = 600
GRID_SIZE = 20
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 102, 255)
OR = (255, 215, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
            
        pygame.display.set_caption("Snake - SAE")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 80)
        self.font_menu = pygame.font.SysFont(None, 40)
        
        self.update_offsets()
        
        # --- TES RÉGLAGES D'ORIGINE ---
        self.difficulty = 1 # 1: Facile, 2: Moyen, 3: Difficile
        self.nb_pommes = 1
        self.reset_game()

    def update_offsets(self):
        self.offset_x = (self.screen.get_width() - GAME_SIZE) // 2
        self.offset_y = (self.screen.get_height() - GAME_SIZE) // 2

    def reset_game(self):
        self.snake = [(GAME_SIZE // 2, GAME_SIZE // 2)]
        self.direction = (GRID_SIZE, 0)
        self.foods = [self.spawn_food() for _ in range(self.nb_pommes)]
        self.score = 0
        self.fps = 10 + (self.difficulty * 5) # La vitesse dépend de la difficulté
        self.running = True

    def spawn_food(self):
        while True:
            food = (random.randint(0, (GAME_SIZE // GRID_SIZE) - 1) * GRID_SIZE,
                    random.randint(0, (GAME_SIZE // GRID_SIZE) - 1) * GRID_SIZE)
            if food not in self.snake:
                return food

    def gerer_musique_et_ecran(self, event):
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
                self.draw_text_centered("SNAKE", 50, VERT, self.font_big)
                
                diff_label = ["Facile", "Moyen", "Difficile"][self.difficulty - 1]
                lines = [
                    f"Difficulte : {diff_label} (Fleches G/D)",
                    f"Nombre de pommes : {self.nb_pommes} (+/-)",
                    "",
                    "ESPACE - Jouer",
                    "I - Aspect Educatif",
                    "EFFACER - Menu Hub"
                ]
            else:
                self.draw_text_centered("INFOS", 50, BLEU, self.font_big)
                lines = [
                   "[ TOUCHES ] : Fleches directionnelles pour diriger le serpent.",
                    "",
                    "[ HISTOIRE ] : Apparu en 1976 sous le nom 'Blockade', ce jeu est devenu",
                    "mondialement celebre grace aux telephones Nokia en 1997.",
                    "C'est l'ancetre du genre 'action-puzzle' qui teste l'anticipation.",
                    "",
                    "ESPACE ou I - Retour"
                ]

            y = 180
            for l in lines:
                self.draw_text_centered(l, y, BLANC, self.font_menu)
                y += 50
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "QUIT"
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_BACKSPACE: return "QUIT"
                    if event.key == pygame.K_i: 
                        show_info = not show_info
                        if only_info and not show_info: return "CONTINUE"
                    
                    if not show_info:
                        if event.key == pygame.K_SPACE: selecting = False
                        if event.key == pygame.K_RIGHT: self.difficulty = min(3, self.difficulty + 1)
                        if event.key == pygame.K_LEFT: self.difficulty = max(1, self.difficulty - 1)
                        if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS]: self.nb_pommes = min(10, self.nb_pommes + 1)
                        if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.nb_pommes = max(1, self.nb_pommes - 1)
        return "START"

    def pause(self):
        pausing = True
        while pausing:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0,0))
            self.draw_text_centered("PAUSE", 200, BLANC, self.font_big)
            self.draw_text_centered("ESPACE - Reprendre", 320, BLANC, self.font_menu)
            self.draw_text_centered("I - Info / EFFACER - Menu", 380, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_SPACE: pausing = False
                    if event.key == pygame.K_i: self.start_screen(only_info=True)
                    if event.key == pygame.K_BACKSPACE: return "MENU"
        return "CONTINUE"

    def run(self):
        if self.start_screen() == "QUIT": return
        self.reset_game()
        
        while self.running:
            self.clock.tick(self.fps)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_SPACE:
                        if self.pause() == "MENU": return
                    elif event.key == pygame.K_UP and self.direction != (0, GRID_SIZE):
                        self.direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -GRID_SIZE):
                        self.direction = (0, GRID_SIZE)
                    elif event.key == pygame.K_LEFT and self.direction != (GRID_SIZE, 0):
                        self.direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-GRID_SIZE, 0):
                        self.direction = (GRID_SIZE, 0)

            new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

            if (new_head[0] < 0 or new_head[0] >= GAME_SIZE or 
                new_head[1] < 0 or new_head[1] >= GAME_SIZE or 
                new_head in self.snake):
                if self.end_game_screen() == "MENU": return
                self.reset_game(); continue

            self.snake.insert(0, new_head)

            # Manger une des pommes
            ate_food = False
            for i, f in enumerate(self.foods):
                if new_head == f:
                    self.score += 1
                    self.foods[i] = self.spawn_food()
                    ate_food = True
                    break
            
            if not ate_food:
                self.snake.pop()

            self.screen.fill(NOIR)
            pygame.draw.rect(self.screen, BLANC, (self.offset_x-2, self.offset_y-2, GAME_SIZE+4, GAME_SIZE+4), 2)
            
            for segment in self.snake:
                pygame.draw.rect(self.screen, VERT, (self.offset_x + segment[0], self.offset_y + segment[1], GRID_SIZE-2, GRID_SIZE-2))
            
            for f in self.foods:
                pygame.draw.rect(self.screen, ROUGE, (self.offset_x + f[0], self.offset_y + f[1], GRID_SIZE-2, GRID_SIZE-2))
            
            self.draw_text_centered(f"Score: {self.score}", GAME_SIZE + 40, BLANC, self.font_menu)
            pygame.display.flip()

    def end_game_screen(self):
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered("GAME OVER", 200, ROUGE, self.font_big)
            self.draw_text_centered(f"Score: {self.score}", 300, BLANC, self.font_menu)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu", 400, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_r: return "REPLAY"
                    if event.key == pygame.K_BACKSPACE: return "MENU"

def run_snake():
    SnakeGame().run()