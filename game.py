from setting import *
from grid import *
import pygame_gui
class Game:
    def __init__(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Gomoku')
        self.clock = pygame.time.Clock()
        self.grid = Grid(self.screen, (15, 15), (40, 40),(300, 300))

        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.manager.get_theme().load_theme('themes/game_theme.json')
        reset_btn_surf = pygame.Surface((200,50))
        reset_btn_rect = reset_btn_surf.get_rect(topleft=(SCREEN_WIDTH, 0)).move(-280,120)
        self.reset_button = pygame_gui.elements.UIButton(relative_rect=reset_btn_rect, text="Reset", 
                                                       manager=self.manager,
                                                       object_id="#reset_btn")
        black_options_surf = pygame.Surface((150,50))
        black_options_rect = black_options_surf.get_rect(midleft=(SCREEN_WIDTH, 0)).move(-180,30)
        self.black_options = pygame_gui.elements.UIDropDownMenu(options_list=['Human','AI','AI-3','AI-2'], 
                                                                starting_option='Human',
                                                                relative_rect=black_options_rect,
                                                                manager=self.manager,
                                                                object_id="#black_options")
        
        white_options_surf = pygame.Surface((150,50))
        white_options_rect = white_options_surf.get_rect(midleft=(SCREEN_WIDTH, 0)).move(-180,80)
        self.white_options = pygame_gui.elements.UIDropDownMenu(options_list=['Human','AI','AI-3','AI-2'], 
                                                                starting_option='Human',
                                                                relative_rect=white_options_rect,
                                                                manager=self.manager,
                                                                object_id="#white_options")
    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.reset_button:
                    print("~Reset grid")
                    self.grid.reset_grid()
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.black_options:
                    self.grid.black_AI = event.text in ["AI", "AI-3", "AI-2"]
                    if event.text == "AI":
                        self.grid.black_highest_tree_level = 4
                    elif event.text == "AI-3":
                        self.grid.black_highest_tree_level = 3
                    elif event.text == "AI-2":
                        self.grid.black_highest_tree_level = 2
                    # print("~Selected black option:", event.text)
                elif event.ui_element == self.white_options:
                    self.grid.white_AI = event.text in ["AI", "AI-3", "AI-2"]
                    if event.text == "AI":
                        self.grid.white_highest_tree_level = 4
                    elif event.text == "AI-3":
                        self.grid.white_highest_tree_level = 3
                    elif event.text == "AI-2":
                        self.grid.white_highest_tree_level = 2
                    # print("~Selected white option:", event.text)

    def draw(self):
        self.screen.fill((140,70,40))
        self.grid.draw()
        font = pygame.font.Font('fonts/Electrolize-Regular.ttf', 32)
        text_1 = font.render("Black", True, (0,0,0))
        text_rect_1 = text_1.get_frect(midleft=(SCREEN_WIDTH, 0)).move(-280,30)
        self.screen.blit(text_1, text_rect_1)
        text_2 = font.render("White", True, (250,250,250))
        text_rect_2 = text_2.get_frect(midleft=(SCREEN_WIDTH, 0)).move(-280,80)
        self.screen.blit(text_2, text_rect_2)
        result = None
        if self.grid.state == Game_State.DRAW:
            result = "Draw!"
        elif self.grid.state == Game_State.WHITE_WIN:
            result = "White win!"
        elif self.grid.state == Game_State.BLACK_WIN:
            result = "Black win!"
        if result != None:
            text_3 = font.render(result, True, (250,250,0))
            text_rect_3 = text_3.get_frect(midleft=(SCREEN_WIDTH, 0)).move(-280,200)
            self.screen.blit(text_3, text_rect_3)

    def update(self):
        self.input()
        self.grid.update()
    
    def late_update(self):
        self.grid.late_update()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.update()
            self.draw()
            self.manager.update(dt)
            self.manager.draw_ui(self.screen)
            pygame.display.update()
            self.late_update()
        pygame.quit()