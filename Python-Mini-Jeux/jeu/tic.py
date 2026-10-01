import pygame
import sys
import random

# ===== CONSTANTES DU JEU =====
GAME_SIZE = 700
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 102, 255)
ROUGE = (255, 0, 0)
TAILLE_CASE = GAME_SIZE // 3

class MorpionGame:
    def __init__(self):
        # Récupération de l'écran global pour garder le plein écran
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1200, 800))
            
        pygame.display.set_caption("Morpion - SAE")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 100)
        self.font_menu = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 24)

        self.update_offsets()

        self.vs_bot = True
        self.score_max = 3
        self.score = {"X": 0, "O": 0}
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.running = True

    def update_offsets(self):
        """Centre la grille de 700x700 dans la fenêtre actuelle"""
        self.offset_x = (self.screen.get_width() - GAME_SIZE) // 2
        self.offset_y = (self.screen.get_height() - GAME_SIZE) // 2

    def gerer_musique_et_ecran(self, event):
        """Gère Musique et Plein écran sans erreur circulaire"""
        import main # Import local pour éviter l'ImportError
        
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

    def bot_play(self):
        """IA Intelligente (Gagne, Bloque ou joue Centre/Hasard)"""
        # 1. Tenter de gagner ou de bloquer
        for mark in ["O", "X"]: 
            for i in range(3):
                # Lignes
                row = self.board[i]
                if row.count(mark) == 2 and row.count("") == 1:
                    self.board[i][row.index("")] = "O"
                    return
                # Colonnes
                col = [self.board[j][i] for j in range(3)]
                if col.count(mark) == 2 and col.count("") == 1:
                    self.board[col.index("")][i] = "O"
                    return
            # Diagonales
            d1 = [self.board[i][i] for i in range(3)]
            if d1.count(mark) == 2 and d1.count("") == 1:
                self.board[d1.index("")][d1.index("")] = "O"; return
            d2 = [self.board[i][2-i] for i in range(3)]
            if d2.count(mark) == 2 and d2.count("") == 1:
                idx = d2.index(""); self.board[idx][2-idx] = "O"; return

        # 2. Jouer centre ou hasard
        if self.board[1][1] == "": self.board[1][1] = "O"
        else:
            empty = [(i,j) for i in range(3) for j in range(3) if self.board[i][j] == ""]
            if empty:
                i,j = random.choice(empty)
                self.board[i][j] = "O"

    def start_screen(self, only_info=False):
        selecting = True
        show_info = only_info
        while selecting:
            self.screen.fill(NOIR)
            if not show_info:
                self.draw_text_centered("MORPION", 100, BLANC, self.font_big)
                lines = [
                    f"Mode : {'Vs Bot' if self.vs_bot else '1v1'} (Fleches G/D)",
                    f"Score max : {self.score_max} (+/-)",
                    "ESPACE - Jouer", "I - Cote Educatif", "EFFACER - Menu Hub"
                ]
            else:
                self.draw_text_centered("INFOS", 100, BLEU, self.font_big)
                lines = [
                "[ TOUCHES ] : Cliquez avec la Souris sur une case vide.",
                "",
                "[ HISTOIRE ] : Ses origines remontent a l'Egypte antique. C'est l'un des",
                "premiers jeux joues par une IA (OXO en 1952). C'est un jeu a",
                "'information complete' : si on joue parfaitement, on ne perd jamais.",
                "",
                "ESPACE ou I - Retour"
            ]
            y = 250
            for l in lines:
                self.draw_text_centered(l, y, BLANC, self.font_menu)
                y += 60
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "QUIT"
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_BACKSPACE: return "QUIT"
                    if event.key == pygame.K_i: 
                        show_info = not show_info
                        if only_info and not show_info: return "CONTINUE"
                    if event.key == pygame.K_SPACE and not show_info: selecting = False
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]: self.vs_bot = not self.vs_bot
                    if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS]: self.score_max += 1
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.score_max = max(1, self.score_max - 1)
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

    def draw_actual_board(self):
        self.screen.fill(NOIR)
        for i in range(1, 3):
            pygame.draw.line(self.screen, BLANC, (self.offset_x + TAILLE_CASE*i, self.offset_y), 
                             (self.offset_x + TAILLE_CASE*i, self.offset_y + GAME_SIZE), 4)
            pygame.draw.line(self.screen, BLANC, (self.offset_x, self.offset_y + TAILLE_CASE*i), 
                             (self.offset_x + GAME_SIZE, self.offset_y + TAILLE_CASE*i), 4)
        for i in range(3):
            for j in range(3):
                mark = self.board[i][j]
                if mark != "":
                    color = BLEU if mark == "X" else ROUGE
                    txt = self.font_big.render(mark, True, color)
                    self.screen.blit(txt, txt.get_rect(center=(self.offset_x + j*TAILLE_CASE + TAILLE_CASE//2, 
                                                               self.offset_y + i*TAILLE_CASE + TAILLE_CASE//2)))
        pygame.display.flip()

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "": return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "": return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "": return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "": return self.board[0][2]
        if not any("" in row for row in self.board): return "Egalite"
        return None

    def run(self):
        if self.start_screen() == "QUIT": return
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        while self.running:
            self.clock.tick(60)
            self.draw_actual_board()
            winner = self.check_winner()
            if winner:
                if self.end_game_screen(winner) == "MENU": return
                self.board = [["" for _ in range(3)] for _ in range(3)]; self.current_player = "X"; continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_SPACE:
                        if self.pause() == "MENU": return
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_player == "X":
                    mx, my = pygame.mouse.get_pos()
                    row, col = (my - self.offset_y) // TAILLE_CASE, (mx - self.offset_x) // TAILLE_CASE
                    if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == "":
                        self.board[row][col] = "X"; self.current_player = "O"
            if self.vs_bot and self.current_player == "O" and not self.check_winner():
                pygame.time.delay(400); self.bot_play(); self.current_player = "X"

    def end_game_screen(self, winner):
        if winner != "Egalite": self.score[winner] += 1
        while True:
            self.screen.fill(NOIR)
            self.draw_text_centered(f"RESULTAT : {winner}", 250, BLANC, self.font_menu)
            self.draw_text_centered("R - Rejouer | EFFACER - Menu Hub", 350, BLANC, self.font_menu)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.gerer_musique_et_ecran(event)
                    if event.key == pygame.K_r: return "REPLAY"
                    if event.key == pygame.K_BACKSPACE: return "MENU"

def run_morpion():
    MorpionGame().run()