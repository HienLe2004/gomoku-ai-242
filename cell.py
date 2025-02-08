from setting import *
from enum import Enum
class Cell_Type(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class Cell:
    black_color = (20, 20, 20)
    white_color = (250, 250, 250)
    highlight_color = (255, 0, 0)
    grid_color = (0, 0, 0)
    def __init__(self, grid, grid_position=(0, 0), size=(50, 50), value=0):
        self.size = size
        self.grid = grid
        self.grid_position = grid_position
        self.position = ((self.grid_position[1] + 0.5)*self.size[0], (self.grid_position[0] + 0.5)*self.size[1])
        self.value = value
        self.cell_surf = pygame.Surface(self.size)
        self.cell_rect = self.cell_surf.get_frect(center=self.position)
        self.is_hovered = False
        self.type = Cell_Type.EMPTY
        self.is_potential = False
        self.number = 0
        self.is_drawn = 0

    def input(self):
        mouse_pos = pygame.mouse.get_pos()
        modified_mouse_pos = (mouse_pos[0] - self.grid.grid_rect.left, mouse_pos[1] - self.grid.grid_rect.top)
        mouse_buttons = pygame.mouse.get_just_released()
        self.is_hovered = self.cell_rect.collidepoint(modified_mouse_pos)
        if self.is_hovered and (self.type == Cell_Type.EMPTY):
            if mouse_buttons[0]:
                self.grid.play_at(self.grid_position)

    def draw(self):
        pygame.draw.rect(surface=self.grid.grid_surf, color=self.grid_color, rect=self.cell_rect.scale_by(1, 0.05))
        pygame.draw.rect(surface=self.grid.grid_surf, color=self.grid_color, rect=self.cell_rect.scale_by(0.05, 1))
        if self.type == Cell_Type.BLACK:
            pygame.draw.circle(surface=self.grid.grid_surf, color=self.black_color, center=self.position, radius=self.size[0] * 0.3)
            font = pygame.font.Font('freesansbold.ttf', int(self.size[0]*0.2))
            text_color = Cell.white_color
            if self.grid.last_move['position'] == self.grid_position:
                text_color = Cell.highlight_color
            text = font.render(str(self.number), True, text_color)
            text_rect = text.get_frect(center=self.position)
            self.grid.grid_surf.blit(text, text_rect)
            self.is_drawn = 1    
        elif self.type == Cell_Type.WHITE:
            pygame.draw.circle(surface=self.grid.grid_surf, color=self.white_color, center=self.position, radius=self.size[0] * 0.3)
            font = pygame.font.Font('freesansbold.ttf', int(self.size[0]*0.2))
            text_color = Cell.black_color
            if self.grid.last_move['position'] == self.grid_position:
                text_color = Cell.highlight_color
            text = font.render(str(self.number), True, text_color)
            text_rect = text.get_frect(center=self.position)
            self.grid.grid_surf.blit(text, text_rect)
            self.is_drawn = 1    
        if self.is_potential:
            pygame.draw.circle(surface=self.grid.grid_surf, color=(100,100,100), center=self.position, radius=self.size[0] * 0.3)

    def update(self):
        self.input()