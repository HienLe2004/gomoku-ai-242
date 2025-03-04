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
    FIVE_0 = 100_000_000
    FIVE_1 = 200_000_000
    FIVE_2 = 300_000_000
    FOUR_1 = 100_000
    FOUR_2 = 300_000
    FOUR_3 = 240_000
    THREE_2_1 = 4_000
    THREE_2_2 = 3_000
    THREE_3_1 = 12_000
    THREE_3_2 = 9_000
    THREE_4 = 20_000
    TWO_3_1 = 3_000
    TWO_3_2 = 1_500
    ONE_4_1 = 20
    ONE_4_2 = 12
    COEFFICIENT = 4
HIGHEST_TREE_LEVEL = 4
UNLOCKED_AI_DISTANCE = 2
TIME_LIMIT = 60
ai_timer = 0

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
        self.state = Game_State.WAIT_WHITE
        self.last_move = {"position":(-1, -1), "type": Cell_Type.BLACK, "number": 0} 
        self.white_AI = False
        self.black_AI = False
        self.AI_start_solving = False
        self.potential_cells = []
        self.values = [0,0]
    def reset_grid(self):
        for cell in self.potential_cells:
            self.cells[cell[0]][cell[1]].is_potential = False
        self.potential_cells = []
        self.last_move = {"position":(-1, -1), "type": Cell_Type.WHITE, "number": 0} 
        self.values = [0,0]
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
                print(f"#AI played white {self.last_move['number'] + 1}")
            else:
                print(f"#Human played white {self.last_move['number'] + 1}")
        elif current_play is Cell_Type.BLACK:
            if self.black_AI:
                print(f"#AI played black {self.last_move['number'] + 1}")
            else:
                print(f"#Human played black {self.last_move['number'] + 1}")
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
        values = evaluate_grid(cell_data, self.values, grid_position)
        self.values[0] = values[0]
        self.values[1] = values[1] 
        if check_ending['result'] == True:
            value = check_ending['value']
        else:
            if self.last_move['type'] == Cell_Type.WHITE:
                value = self.values[1] + self.values[0] * Evaluate_Sequence.COEFFICIENT.value
            else:
                value = self.values[1] * Evaluate_Sequence.COEFFICIENT.value + self.values[0]
        print(self.values)
        print(f'Grid\'s value: {value}')
        self.potential_cells = update_potential_cells_around(cell_data, grid_position, self.potential_cells)
        #Show potential cells
        for cell in self.potential_cells:
            if self.cells[cell[0]][cell[1]].type is Cell_Type.BLACK or self.cells[cell[0]][cell[1]].type is Cell_Type.WHITE:
                print("Something wrong with potential cells")
            else:
                self.cells[cell[0]][cell[1]].is_potential = True   

    def handle_AI(self):
        global ai_timer
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
                ai_timer = time.time()
                start_time = time.time()
                check_ending_result = check_ending_move_multiple_cells(grid, self.last_move, self.potential_cells)
                temp_last_move = {"position": self.last_move['position'], 
                                  "number": self.last_move['number'],
                                  "type": Cell_Type.WHITE}
                check_defend_result = check_ending_move_multiple_cells(grid, temp_last_move, self.potential_cells)
                move = None
                if check_ending_result['result'] == True:
                    move = check_ending_result['move']
                elif check_defend_result['result'] == True:
                    move = check_defend_result['move']
                else:
                    result = minimax_alpha_beta_pruning(level=HIGHEST_TREE_LEVEL,
                                                        alpha=-Evaluate_Sequence.FIVE_2.value*HIGHEST_TREE_LEVEL,
                                                        beta=Evaluate_Sequence.FIVE_2.value*HIGHEST_TREE_LEVEL,
                                                        grid=grid,
                                                        values=self.values,
                                                        last_move=self.last_move,
                                                        potential_cells=self.potential_cells)
                    print(result)
                    move = result['move'][0]
                end_time = time.time()
                thinking_time = end_time - start_time
                print(f'Thinking time: {thinking_time:.4f}')
                self.play_at(move)
        elif ai_play is Cell_Type.BLACK:
            if self.black_AI:
                print("#AI-black is choosing the best move....")
                grid = [[cell.type for cell in row] for row in self.cells]
                ai_timer = time.time()
                start_time = time.time()
                check_ending_result = check_ending_move_multiple_cells(grid, self.last_move, self.potential_cells)
                temp_last_move = {"position": self.last_move['position'], 
                                  "number": self.last_move['number'],
                                  "type": Cell_Type.BLACK}
                check_defend_result = check_ending_move_multiple_cells(grid, temp_last_move, self.potential_cells)
                move = None
                if check_ending_result['result'] == True:
                    move = check_ending_result['move']
                elif check_defend_result['result'] == True:
                    move = check_defend_result['move']
                else:
                    result = minimax_alpha_beta_pruning(level=HIGHEST_TREE_LEVEL,
                                                        alpha=-Evaluate_Sequence.FIVE_2.value*HIGHEST_TREE_LEVEL,
                                                        beta=Evaluate_Sequence.FIVE_2.value*HIGHEST_TREE_LEVEL,
                                                        grid=grid,
                                                        values=self.values,
                                                        last_move=self.last_move,
                                                        potential_cells=self.potential_cells)
                    print(result)
                    move = result['move'][0]
                end_time = time.time()
                thinking_time = end_time - start_time
                print(f'Thinking time: {thinking_time:.4f}')
                self.play_at(move)

    def draw(self):
        self.grid_surf.fill((255,170,100))
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
    # print(f"Before {len(potential_cells)}")
    surrounded_cells = get_surrounded_cells(grid_position, UNLOCKED_AI_DISTANCE)
    # print(f"Get {len(surrounded_cells)} surrounded cells")
    new_potential_cells = [cell for cell in potential_cells if (cell not in surrounded_cells and grid_position != cell)]
    for cell in surrounded_cells:
        if is_valid_cell(cell):
            if grid[cell[0]][cell[1]] == Cell_Type.EMPTY:
                new_potential_cells.append(cell)
    sorted_potential_cells = sorted(new_potential_cells, 
                                    key=lambda cell: max(abs(cell[0]-grid_position[0]),
                                                         abs(cell[1]-grid_position[1])))
    # print(f'After sorted {len(sorted_potential_cells)} {sorted_potential_cells}')
    return sorted_potential_cells
def minimax_alpha_beta_pruning(level, alpha, beta, grid, values, last_move, potential_cells):
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
        value = 0
        if ai_play == Cell_Type.BLACK:
            value = values[0] * Evaluate_Sequence.COEFFICIENT.value
            value += values[1]
        else:
            value = values[1] * Evaluate_Sequence.COEFFICIENT.value
            value += values[0]
        return {"value": value, "move":None}
    if ai_play == Cell_Type.BLACK:
        # best_value = -Evaluate_Sequence.BLACK_5_2.value*level-1
        best_value = -Evaluate_Sequence.FIVE_2.value*level-1
        best_move = None
        for potential_cell in potential_cells:
            child_grid = [[cell for cell in row] for row in grid]
            child_grid[potential_cell[0]][potential_cell[1]] = ai_play
            child_potential_cells = [cell for cell in potential_cells]
            child_potential_cells = update_potential_cells_around(child_grid,potential_cell,child_potential_cells)
            child_last_move = {"position":potential_cell,"type":ai_play,"number":last_move['number']+1}
            child_values = evaluate_grid(child_grid, values, potential_cell)
            # if (level == HIGHEST_TREE_LEVEL - 1):
            #     print(f"Parent {last_move['position']} {values}, child {potential_cell} {child_values}")
            child_result = minimax_alpha_beta_pruning(level - 1, alpha, beta, child_grid, child_values,
                                                            child_last_move, child_potential_cells)
            old_best_value = best_value
            best_value = max(best_value, child_result['value'])
            alpha = max(alpha,best_value)
            #Get last best result each level
            if child_result['value'] > old_best_value:
                best_move = [potential_cell]
                if child_result["move"] != None:
                    for move in child_result['move']:
                        best_move.append(move)
            if beta <= alpha:
                break
            #time_limit break
            if time.time() - ai_timer >= TIME_LIMIT:
                break
        # if (level == HIGHEST_TREE_LEVEL - 1):
        #     print(f"Last move at {last_move['position']}, best black move {best_move}, value {best_value}")
        return {"value":best_value,"move":best_move}
    elif ai_play == Cell_Type.WHITE:
        # best_value = Evaluate_Sequence.BLACK_5_2.value*level+1
        best_value = Evaluate_Sequence.FIVE_2.value*level+1
        best_move = None
        for potential_cell in potential_cells:
            child_grid = [[cell for cell in row] for row in grid]
            child_grid[potential_cell[0]][potential_cell[1]] = ai_play
            child_potential_cells = [cell for cell in potential_cells]
            child_potential_cells = update_potential_cells_around(child_grid,potential_cell,child_potential_cells)
            child_last_move = {"position":potential_cell,"type":ai_play,"number":last_move['number']+1}
            child_values = evaluate_grid(child_grid, values, potential_cell)
            if (level == HIGHEST_TREE_LEVEL - 1):
                print(f"Parent {last_move['position']} {values}, child {potential_cell} {child_values}")
            child_result = minimax_alpha_beta_pruning(level - 1, alpha, beta, child_grid, child_values,
                                                            child_last_move, child_potential_cells)
            old_best_value = best_value
            best_value = min(best_value,child_result['value'])
            beta = min(beta,best_value)
            #Get last best result each level
            # print(f"Old {old_best_value} new {best_value}")
            if child_result['value'] < old_best_value:
                best_move = [potential_cell]
                if child_result["move"] != None:
                    for move in child_result['move']:
                        best_move.append(move)
            # print(f"Move {best_move}")
            if beta <= alpha:
                break
            #time_limit break
            if time.time() - ai_timer >= TIME_LIMIT:
                break
        if (level == HIGHEST_TREE_LEVEL - 1):
            print(f"Last move at {last_move['position']}, best white move {best_move}, value {best_value}")
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
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if vertical_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_0.value
        elif vertical_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_2.value
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
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if horizontal_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_0.value
        elif horizontal_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_2.value
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
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if top_left_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_0.value
        elif top_left_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_2.value
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
        final_result['result'] = True
        if last_move['type'] is Cell_Type.BLACK:
            final_result['state'] = Game_State.BLACK_WIN
            final_result['value'] = 1
        elif last_move['type'] is Cell_Type.WHITE:
            final_result['state'] = Game_State.WHITE_WIN
            final_result['value'] = -1
        if top_right_count - 5 + empty == 0:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_0.value
        elif top_right_count - 5 + empty == 1:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_1.value
        else:
            final_result['value'] = final_result['value'] * Evaluate_Sequence.FIVE_2.value
        return final_result
    #no winning state
    if is_full(last_move):
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
def check_ending_move_multiple_cells(grid, last_move, cells):
    temp_last_move = {"number": last_move['number'] + 1}
    if last_move['type'] == Cell_Type.BLACK:
        temp_last_move['type'] = Cell_Type.WHITE
    else:
        temp_last_move['type'] = Cell_Type.BLACK
    for cell in cells:
        temp_last_move['position'] = cell
        temp_grid = [[c for c in row] for row in grid]
        temp_grid[cell[0]][cell[1]] = temp_last_move['type']
        temp_result = check_ending_move(temp_grid, temp_last_move)
        if temp_result['result'] == True:
            return {"result": True, "move": cell}
    return {"result": False}

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
def get_surrounded_cells(grid_position, distance):
    cells = []
    for layer in range(1, distance + 1):
        cells.append(top_left_cell(grid_position, layer))
        cells.append(top_right_cell(grid_position, layer))
        cells.append(bottom_right_cell(grid_position, layer))
        cells.append(bottom_left_cell(grid_position, layer))
        cells.append(top_cell(grid_position, layer))
        cells.append(right_cell(grid_position, layer))
        cells.append(bottom_cell(grid_position, layer))
        cells.append(left_cell(grid_position, layer))
    return cells

def evaluate_grid(grid, old_values, position):
    new_sub_values = [0,0]
    old_sub_values = [0,0]
    #horizontal
    line = [grid[position[0]][i] for i in range(15)]
    result = evaluate_line(line)
    new_sub_values[0] += result[0]
    new_sub_values[1] += result[1]
    line[position[1]] = Cell_Type.EMPTY
    result = evaluate_line(line)
    old_sub_values[0] += result[0]
    old_sub_values[1] += result[1]
    #vertical
    line = [grid[i][position[1]] for i in range(15)]
    result = evaluate_line(line)
    new_sub_values[0] += result[0]
    new_sub_values[1] += result[1]
    line[position[0]] = Cell_Type.EMPTY
    result = evaluate_line(line)
    old_sub_values[0] += result[0]
    old_sub_values[1] += result[1]
    #top_left
    index = 0
    while position[0] + index != 0 and position[1] + index != 0:
        index -= 1
    line = []
    position_index = -index
    while position[0] + index <= 14 and position[1] + index <= 14:
        line.append(grid[position[0] + index][position[1] + index])
        index += 1
    result = evaluate_line(line)
    new_sub_values[0] += result[0]
    new_sub_values[1] += result[1]
    line[position_index] = Cell_Type.EMPTY
    result = evaluate_line(line)
    old_sub_values[0] += result[0]
    old_sub_values[1] += result[1]
    #top_right
    index = 0
    while position[0] + index != 0 and position[1] - index != 14:
        index -= 1
    line = []
    position_index = -index
    while position[0] + index <= 14 and position[1] - index >= 0:
        line.append(grid[position[0] + index][position[1] - index])
        index += 1
    result = evaluate_line(line)
    new_sub_values[0] += result[0]
    new_sub_values[1] += result[1]

    line[position_index] = Cell_Type.EMPTY
    result = evaluate_line(line)
    old_sub_values[0] += result[0]
    old_sub_values[1] += result[1]

    new_values = [0,0]
    new_values[0] = old_values[0] - old_sub_values[0] + new_sub_values[0]
    new_values[1] = old_values[1] - old_sub_values[1] + new_sub_values[1]
    return new_values
def evaluate_line(line):
    cell_values = [[] for _ in line]
    cell_final_values = [[0,0] for _ in line]
    #check pattern with length 5-6-7
    for pattern_len in range(5, 8):
        if len(line) < pattern_len:
            break
        pattern = []
        count = {Cell_Type.EMPTY:0, Cell_Type.BLACK:0, Cell_Type.WHITE:0}
        #create pattern with first n-1 cells
        for i in range(pattern_len - 1):
            pattern.append(line[i])
            count[line[i]] += 1
        #loop to add 1 next cell
        for i in range(pattern_len - 1, len(line)):
            pattern.append(line[i])
            count[line[i]] += 1
            #get value of pattern with length n
            value = evaluate_pattern(count, pattern)
            if value != 0:
                for j in range(pattern_len):
                    #add divided value to empty cell's value list
                    if line[i - j] == Cell_Type.EMPTY:
                        cell_values[i - j].append(value // count[Cell_Type.EMPTY])
            #remove first cell to get pattern with length n - 1
            remove_pattern = pattern.pop(0)
            count[remove_pattern] -= 1
    result = [0,0]
    for i in range(len(line)):
        value = [[],[]]
        value_len = [0,0]
        for v in cell_values[i]:
            if v > 0:
                value[0].append(v)
                value_len[0] += 1
            elif v < 0:
                value[1].append(v)
                value_len[1] += 1
        if value_len[0] != 0:
            cell_final_values[i][0] = max(value[0])
        if value_len[1] != 0:
            cell_final_values[i][1] = min(value[1])
        result[0] += cell_final_values[i][0]
        result[1] += cell_final_values[i][1]
    return result

def evaluate_pattern(count, pattern):
    if count[Cell_Type.EMPTY] >= 5:
        return 0
    if count[Cell_Type.BLACK] != 0 and count[Cell_Type.WHITE] != 0:
        return 0
    is_black = 1
    if count[Cell_Type.WHITE] != 0:
        is_black = -1
    if len(pattern) == 7:
        if pattern[0] != Cell_Type.EMPTY or pattern[6] != Cell_Type.EMPTY:
            return 0
        if count[Cell_Type(is_black)] == 4:
            if Cell_Type.EMPTY in pattern[2:5]:
                #-x-xxx-    
                #-xxx-x-
                #-xx-xx-
                return is_black * Evaluate_Sequence.FOUR_3.value
            return 0
        elif count[Cell_Type(is_black)] == 3:
            if pattern[1] == Cell_Type.EMPTY and pattern[5] == Cell_Type.EMPTY:
                #--xxx--
                return is_black * Evaluate_Sequence.THREE_4.value
            return 0
        return 0
    elif len(pattern) == 6:
        if pattern[0] != Cell_Type.EMPTY or pattern[5] != Cell_Type.EMPTY:
            return 0
        if count[Cell_Type(is_black)] == 4:
            #-xxxx-
            return is_black * Evaluate_Sequence.FOUR_2.value
        elif count[Cell_Type(is_black)] == 3:
            if pattern[1] == Cell_Type.EMPTY or pattern[4] == Cell_Type.EMPTY:
                #--xxx-
                #-xxx--
                return is_black * Evaluate_Sequence.THREE_3_1.value
            #-x-xx-
            #-xx-x-
            return is_black * Evaluate_Sequence.THREE_3_2.value
        return 0
    elif len(pattern) == 5:
        if count[Cell_Type(is_black)] == 1:
            if pattern[0] != Cell_Type.EMPTY or pattern[4] != Cell_Type.EMPTY:
                #x----
                #----x
                return is_black * Evaluate_Sequence.ONE_4_2.value
            #-x---
            #--x--
            #---x-
            return is_black * Evaluate_Sequence.ONE_4_1.value
        elif count[Cell_Type(is_black)] == 2:
            if pattern[0] == Cell_Type.EMPTY and pattern[4] == Cell_Type.EMPTY:
                #-xx--
                #--xx-
                #-x-x-
                return is_black * Evaluate_Sequence.TWO_3_1.value
            #xx---
            #x-x--
            #x--x-
            #x---x
            #-x--x
            #--x-x
            #---xx
            return is_black * Evaluate_Sequence.TWO_3_2.value
        elif count[Cell_Type(is_black)] == 3:
            if pattern[0] == Cell_Type.EMPTY:
                #-xxx-
                return is_black * Evaluate_Sequence.THREE_2_1.value
            if pattern[0] == Cell_Type.EMPTY:
                #--xxx
                #-x-xx
                #-xx-x
                return is_black * Evaluate_Sequence.THREE_2_1.value 
            if pattern[4] == Cell_Type.EMPTY:
                #xxx--
                #xx-x-
                #x-xx-
                return is_black * Evaluate_Sequence.THREE_2_1.value 
            #x-x-x
            #x--xx
            #xx--x
            return is_black * Evaluate_Sequence.THREE_2_2.value
        elif count[Cell_Type(is_black)] == 4:
            #xxxx-
            #xxx-x
            #xx-xx
            #x-xxx
            #-xxxx
            return is_black * Evaluate_Sequence.FOUR_1.value
    return 0