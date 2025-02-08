import random
from setting import *
from cell import *
from enum import Enum
import time
class Game_State(Enum):
    WAIT_BLACK = 0
    WAIT_WHITE = 1
    BLACK_WIN = 2
    WHITE_WIN = 3
    DRAW = 4
class Evaluate_Sequence(Enum):
    BLACK_5_2 = 300_000_000
    BLACK_5_1 = 200_000_000
    BLACK_5_0 = 100_000_000
    BLACK_4 = 1_000_000
    BLACK_3 = 100_000
    BLACK_2 = 1_000
    BLACK_1 = 10
    COEFFICIENT = 1.5

class Grid:
    def __init__(self, screen, grid_size=(10, 10), cell_size=(50, 50), position=(300, 300)):
        self.screen = screen
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid_surf = pygame.Surface((grid_size[0] * cell_size[0], grid_size[1] * cell_size[1]))
        self.position = position
        self.grid_rect = self.grid_surf.get_frect(center=self.position) 
        self.cells = []
        for row in range(grid_size[0]):
            cells_in_row = []
            for col in range(grid_size[1]):
                cells_in_row.append(Cell(self, (row,col), self.cell_size, 0))
            self.cells.append(cells_in_row)
        self.state = Game_State.WAIT_BLACK
        self.last_move = {"position":(-1, -1), "type": Cell_Type.WHITE, "number": 0} 
        self.white_AI = False
        self.black_AI = False
        self.AI_start_solving = False
        self.potential_cells = []
    def reset_grid(self):
        for cell in self.potential_cells:
            self.cells[cell[0]][cell[1]].is_potential = False
        self.potential_cells = []
        self.last_move = {"position":(-1, -1), "type": Cell_Type.WHITE, "number": 0} 
        self.state = Game_State.WAIT_BLACK
        for row in self.cells:
            for cell in row:
                cell.type = Cell_Type.EMPTY

    def play_at(self, grid_position):
        current_play = Cell_Type.EMPTY
        if self.state is Game_State.WAIT_BLACK:
            current_play = Cell_Type.BLACK
        elif self.state is Game_State.WAIT_WHITE:
            current_play = Cell_Type.WHITE
        if current_play is Cell_Type.EMPTY:
            return
        if current_play is Cell_Type.WHITE:
            if self.white_AI:
                print("#AI played white")
            else:
                print("#Human played white")
        elif current_play is Cell_Type.BLACK:
            if self.black_AI:
                print("#AI played black")
            else:
                print("#Human played black")
        self.cells[grid_position[0]][grid_position[1]].type = current_play
        self.cells[grid_position[0]][grid_position[1]].number = self.last_move['number'] + 1
        self.cells[grid_position[0]][grid_position[1]].is_potential = False
        cell_data = [[cell.type for cell in row] for row in self.cells]
        self.last_move = {"position" : (grid_position[0], grid_position[1]),
                           "type": current_play, 
                           "number": self.last_move['number'] + 1}
        check_ending = check_ending_move(cell_data, self.last_move)
        self.state = check_ending['state']
        value = 0
        if check_ending['result'] == True:
            value = check_ending['value']
        else:
            value = evaluate_grid(cell_data, self.last_move)
        print(f'current value of grid: {value}')
        self.potential_cells = update_potential_cells_around(cell_data, grid_position, self.potential_cells)
        #Show potential cells
        for cell in self.potential_cells:
            if self.cells[cell[0]][cell[1]].type is Cell_Type.BLACK or self.cells[cell[0]][cell[1]].type is Cell_Type.WHITE:
                print("Something wrong with potential cells")
            else:
                self.cells[cell[0]][cell[1]].is_potential = True   

    def handle_AI(self):
        ai_play = Cell_Type.EMPTY
        if self.state == Game_State.WAIT_BLACK:
            ai_play = Cell_Type.BLACK
        elif self.state == Game_State.WAIT_WHITE:
            ai_play = Cell_Type.WHITE
        if ai_play is Cell_Type.EMPTY:
            return
        if ai_play is Cell_Type.WHITE:
            if self.white_AI:
                print("#AI-white is choosing the best move....")
                grid = [[cell.type for cell in row] for row in self.cells]
                start_time = time.time()
                result = minimax_alpha_beta_pruning(level=4,
                                                    alpha=-Evaluate_Sequence.BLACK_5_2.value*4,
                                                    beta=Evaluate_Sequence.BLACK_5_2.value*4,
                                                    grid=grid,
                                                    last_move=self.last_move,
                                                    potential_cells=self.potential_cells)
                end_time = time.time()
                thinking_time = end_time - start_time
                print(f'Thinking time: {thinking_time:.4f}')
                print(result)
                self.play_at(result['move'][0])
        elif ai_play is Cell_Type.BLACK:
            if self.black_AI:
                print("#AI-black is choosing the best move....")
                grid = [[cell.type for cell in row] for row in self.cells]
                start_time = time.time()
                result = minimax_alpha_beta_pruning(level=4,
                                                    alpha=-Evaluate_Sequence.BLACK_5_2.value*4,
                                                    beta=Evaluate_Sequence.BLACK_5_2.value*4,
                                                    grid=grid,
                                                    last_move=self.last_move,
                                                    potential_cells=self.potential_cells)
                end_time = time.time()
                thinking_time = end_time - start_time
                print(f'Thinking time: {thinking_time:.4f}')
                print(result)
                self.play_at(result['move'][0])

    def draw(self):
        self.grid_surf.fill((135,62,35))
        for row in self.cells:
            for cell in row:
                cell.draw()
        self.screen.blit(self.grid_surf, self.grid_rect)

    def update(self):
        for row in self.cells:
            for cell in row:
                cell.update()
        #Check AI next move
    def late_update(self):
        if (self.black_AI and self.state == Game_State.WAIT_BLACK) or (self.white_AI and self.state == Game_State.WAIT_WHITE):
            last_position = self.last_move['position']
            is_drawn_last_move = self.cells[last_position[0]][last_position[1]].is_drawn == 1
            if not self.AI_start_solving and is_drawn_last_move:
                self.AI_start_solving = True
                self.handle_AI()
                self.AI_start_solving = False

def update_potential_cells_around(grid, grid_position, potential_cells):
    surrounding_cells = [top_cell(grid_position,1),
                        right_cell(grid_position,1),
                        bottom_cell(grid_position,1),
                        left_cell(grid_position,1),
                        top_left_cell(grid_position,1),
                        top_right_cell(grid_position,1),
                        bottom_right_cell(grid_position,1),
                        bottom_left_cell(grid_position,1)]
    new_potential_cells = [cell for cell in potential_cells if (cell not in surrounding_cells and grid_position != cell)]
    for cell in surrounding_cells:
        if is_valid_cell(cell):
            if grid[cell[0]][cell[1]] is Cell_Type.EMPTY:
                new_potential_cells.append(cell)
    return new_potential_cells
def minimax_alpha_beta_pruning(level, alpha, beta, grid, last_move, potential_cells):
    ai_play = Cell_Type.EMPTY
    if last_move['type'] == Cell_Type.BLACK:
        ai_play = Cell_Type.WHITE
    elif last_move['type'] == Cell_Type.WHITE:
        ai_play = Cell_Type.BLACK
    else:
        print("Something wrong in minimax algorithm")
    check_ending = check_ending_move(grid,last_move)
    if check_ending['result'] == True:
        return {"value":check_ending['value'] * level, "move":None}
    if level == 1:
        return {"value":evaluate_grid(grid, last_move), "move":None}
    if ai_play == Cell_Type.BLACK:
        best_value = -Evaluate_Sequence.BLACK_5_2.value*level-1
        best_move = []
        for potential_cell in potential_cells:
            child_grid = [[cell for cell in row] for row in grid]
            child_grid[potential_cell[0]][potential_cell[1]] = ai_play
            child_potential_cells = [cell for cell in potential_cells]
            child_potential_cells = update_potential_cells_around(child_grid,potential_cell,child_potential_cells)
            child_last_move = {"position":potential_cell,"type":ai_play,"number":last_move['number']+1}
            child_result = minimax_alpha_beta_pruning(level - 1, alpha, beta, child_grid, 
                                                            child_last_move, child_potential_cells)
            if child_result['value'] > best_value:
                best_value = child_result['value']
                best_move = [potential_cell]
                if child_result["move"] != None:
                    for move in child_result['move']:
                        best_move.append(move)
            # elif child_result['value'] == best_value:
            #     best_move.append(potential_cell)
            alpha = max(alpha,best_value)
            if beta <= alpha:
                break
        return {"value":best_value,"move":best_move}
    elif ai_play == Cell_Type.WHITE:
        best_value = Evaluate_Sequence.BLACK_5_2.value*level+1
        best_move = []
        for potential_cell in potential_cells:
            child_grid = [[cell for cell in row] for row in grid]
            child_grid[potential_cell[0]][potential_cell[1]] = ai_play
            child_potential_cells = [cell for cell in potential_cells]
            child_potential_cells = update_potential_cells_around(child_grid,potential_cell,child_potential_cells)
            child_last_move = {"position":potential_cell,"type":ai_play,"number":last_move['number']+1}
            child_result = minimax_alpha_beta_pruning(level - 1, alpha, beta, child_grid, 
                                                            child_last_move, child_potential_cells)
            if child_result['value'] < best_value:
                best_value = child_result['value']
                best_move = [potential_cell]
                if child_result["move"] != None:
                    for move in child_result['move']:
                        best_move.append(move)
            # elif child_result['value'] == best_value:
            #     best_move.append(potential_cell)
            beta = min(beta,best_value)
            if beta <= alpha:
                break
        return {"value":best_value,"move":best_move}

def check_ending_move(grid, last_move):
    final_result = {'result': None, 'state': None, 'value': None}
    #vertival
    vertical_count = 1
    empty = 0
    for i in range(1, 6):
        temp = top_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                vertical_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    for i in range(1, 6):
        temp = bottom_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                vertical_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    if vertical_count >= 5:
        # print('/win vertical')
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if vertical_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_0.value
        elif vertical_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_2.value
        return final_result
    #horizontal
    horizontal_count = 1
    empty = 0
    for i in range(1, 6):
        temp = left_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                horizontal_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    for i in range(1, 6):
        temp = right_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                horizontal_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    if horizontal_count >= 5:
        # print('/win horizontal')
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if horizontal_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_0.value
        elif horizontal_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_2.value
        return final_result
    #top_left
    top_left_count = 1
    empty = 0
    for i in range(1, 6):
        temp = top_left_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                top_left_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    for i in range(1, 6):
        temp = bottom_right_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                top_left_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    if top_left_count >= 5:
        # print('/win top_left')
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if top_left_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_0.value
        elif top_left_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_2.value
        return final_result
    #top_right
    top_right_count = 1
    empty = 0
    for i in range(1, 6):
        temp = top_right_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                top_right_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    for i in range(1, 6):
        temp = bottom_left_cell(last_move['position'], i)
        if is_valid_cell(temp):
            if grid[temp[0]][temp[1]] is last_move['type']:
                top_right_count += 1
            elif grid[temp[0]][temp[1]] == Cell_Type.EMPTY:
                empty += 1
                break
            else:
                break
    if top_right_count >= 5:
        # print('/win top_right')
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if top_right_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_0.value
        elif top_right_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.BLACK_5_2.value
        return final_result
    #no winning state
    if is_full(last_move):
        # print("draw")
        final_result['result'] = True
        final_result['state'] = Game_State.DRAW
        final_result['value'] = 0
        return final_result
    final_result['result'] = False
    if last_move['type'] is Cell_Type.BLACK:
        final_result['state'] = Game_State.WAIT_WHITE
    elif last_move['type'] is Cell_Type.WHITE:
        final_result['state'] = Game_State.WAIT_BLACK
    return final_result


def is_valid_cell(grid_position):
    if grid_position[0] < 0 or grid_position[0] > 15 - 1:
        return False
    if grid_position[1] < 0 or grid_position[1] > 15 - 1:
        return False
    return True

def is_full(last_move):
    return last_move['number'] == 15 * 15

def top_cell(grid_position, step):
    return (grid_position[0] - step, grid_position[1])
def right_cell(grid_position, step):
    return (grid_position[0], grid_position[1] + step)
def bottom_cell(grid_position, step):
    return (grid_position[0] + step, grid_position[1])
def left_cell(grid_position, step):
    return (grid_position[0], grid_position[1] - step)
def top_left_cell(grid_position, step):
    return (grid_position[0] - step, grid_position[1] - step)
def top_right_cell(grid_position, step):
    return (grid_position[0] - step, grid_position[1] + step)
def bottom_right_cell(grid_position, step):
    return (grid_position[0] + step, grid_position[1] + step)
def bottom_left_cell(grid_position, step):
    return (grid_position[0] + step, grid_position[1] - step)

def evaluate_grid(grid, last_move):
    value = 0
    horizontal_value = evaluate_horizontal(grid, last_move)
    vertical_value = evaluate_vertical(grid, last_move)
    top_left_value = evaluate_top_left(grid, last_move)
    top_right_value = evaluate_top_right(grid, last_move)
    # print(f"(hor,ver,tle,tri) value ({horizontal_value},{vertical_value},{top_left_value},{top_right_value})")
    value = horizontal_value + vertical_value + top_left_value + top_right_value
    return value
def evaluate_horizontal (grid, last_move):
    value = 0
    for row in range(15):
        count = {Cell_Type.BLACK: 0, Cell_Type.WHITE: 0, Cell_Type.EMPTY: 0}
        pattern = []
        for col in range(4):
            pattern.append(grid[row][col])
            count[grid[row][col]] = count[grid[row][col]] + 1
        for col in range(4, 15):
            pattern.append(grid[row][col])
            count[grid[row][col]] = count[grid[row][col]] + 1
            modified_value = evaluate_pattern(count)
            if modified_value > 0 and last_move['type'] == Cell_Type.WHITE:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            elif modified_value < 0 and last_move['type'] == Cell_Type.BLACK:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            value += modified_value
            if len(pattern) == 5:
                removed_symbol = pattern.pop(0)
                count[removed_symbol] = count[removed_symbol] - 1
    return value
def evaluate_vertical (grid, last_move):
    value = 0
    for col in range(15):
        count = {Cell_Type.BLACK: 0, Cell_Type.WHITE: 0, Cell_Type.EMPTY: 0}
        pattern = []
        for row in range(4):
            pattern.append(grid[row][col])
            count[grid[row][col]] = count[grid[row][col]] + 1
        for row in range(4, 15):
            pattern.append(grid[row][col])
            count[grid[row][col]] = count[grid[row][col]] + 1
            modified_value = evaluate_pattern(count)
            if modified_value > 0 and last_move['type'] == Cell_Type.WHITE:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            elif modified_value < 0 and last_move['type'] == Cell_Type.BLACK:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            value += modified_value
            if len(pattern) == 5:
                removed_symbol = pattern.pop(0)
                count[removed_symbol] = count[removed_symbol] - 1
    return value 
def evaluate_top_left (grid, last_move):
    value = 0
    start_cells = []
    for row in range(15 - 4):
        start_cells.append((row,0))
    for col in range(1, 15 - 4):
        start_cells.append((0,col))

    for cell in start_cells:
        count = {Cell_Type.BLACK: 0, Cell_Type.WHITE: 0, Cell_Type.EMPTY: 0}
        pattern = []
        for index in range(4):
            pattern.append(grid[cell[0] + index][cell[1] + index])
            count[grid[cell[0] + index][cell[1] + index]] = count[grid[cell[0] + index][cell[1] + index]] + 1
        index = 4
        while cell[0] + index < 15 and cell[1] + index < 15:
            pattern.append(grid[cell[0] + index][cell[1] + index])
            count[grid[cell[0] + index][cell[1] + index]] = count[grid[cell[0] + index][cell[1] + index]] + 1
            modified_value = evaluate_pattern(count)
            if modified_value > 0 and last_move['type'] == Cell_Type.WHITE:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            elif modified_value < 0 and last_move['type'] == Cell_Type.BLACK:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            value += modified_value
            if len(pattern) == 5:
                removed_symbol = pattern.pop(0)
                count[removed_symbol] = count[removed_symbol] - 1
            index += 1
    return value  
def evaluate_top_right (grid, last_move):
    value = 0
    start_cells = []
    for row in range(15 - 4):
        start_cells.append((row,15-1))
    for col in range(4, 15 - 1):
        start_cells.append((0,col))

    for cell in start_cells:
        count = {Cell_Type.BLACK: 0, Cell_Type.WHITE: 0, Cell_Type.EMPTY: 0}
        pattern = []
        for index in range(4):
            pattern.append(grid[cell[0] + index][cell[1] - index])
            count[grid[cell[0] + index][cell[1] - index]] = count[grid[cell[0] + index][cell[1] - index]] + 1
        index = 4
        while cell[0] +index < 15 and cell[1] -index > 0:
            pattern.append(grid[cell[0] +index][cell[1] -index])
            count[grid[cell[0] +index][cell[1] -index]] = count[grid[cell[0] +index][cell[1] -index]] + 1
            modified_value = evaluate_pattern(count)
            if modified_value > 0 and last_move['type'] == Cell_Type.WHITE:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            elif modified_value < 0 and last_move['type'] == Cell_Type.BLACK:
                modified_value *= Evaluate_Sequence.COEFFICIENT.value
            value += modified_value
            if len(pattern) == 5:
                removed_symbol = pattern.pop(0)
                count[removed_symbol] = count[removed_symbol] - 1
            index += 1
    return value         
def evaluate_direction(direction, grid, last_move):
    return direction(grid, last_move)
def evaluate_pattern(pattern):
    if pattern[Cell_Type.EMPTY] == 5:
        return 0
    if pattern[Cell_Type.BLACK] != 0 and pattern[Cell_Type.WHITE] != 0:
        return 0
    if pattern[Cell_Type.BLACK] != 0:
        if pattern[Cell_Type.BLACK] == 1:
            return Evaluate_Sequence.BLACK_1.value
        elif pattern[Cell_Type.BLACK] == 2:
            return Evaluate_Sequence.BLACK_2.value
        elif pattern[Cell_Type.BLACK] == 3:
            return Evaluate_Sequence.BLACK_3.value
        elif pattern[Cell_Type.BLACK] == 4:
            return Evaluate_Sequence.BLACK_4.value
    if pattern[Cell_Type.WHITE] != 0:
        if pattern[Cell_Type.WHITE] == 1:
            return -Evaluate_Sequence.BLACK_1.value
        elif pattern[Cell_Type.WHITE] == 2:
            return -Evaluate_Sequence.BLACK_2.value
        elif pattern[Cell_Type.WHITE] == 3:
            return -Evaluate_Sequence.BLACK_3.value
        elif pattern[Cell_Type.WHITE] == 4:
            return -Evaluate_Sequence.BLACK_4.value
    return 0
  