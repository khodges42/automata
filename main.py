import sys
import pygame
import json
from pygame.locals import *
import pygame.freetype


# I got the conways cell functions from https://github.com/000Nobody

run = __name__ == '__main__'
clock = pygame.time.Clock()

WINDOW_SIZE = (1000, 1000) # (width, height)
CELL_SIZE = 10 # pixels
FPS = 2 # number of generations per second todo this might be good to vary

with open('levels.json', 'r') as levels_file:
    df = levels_file.read()

difficulties = json.loads(df)

screen = pygame.display.set_mode(WINDOW_SIZE)
display = pygame.Surface(WINDOW_SIZE)

cells = []
setting_up = True
lmousedown = False
rmousedown = False
show_grid = False
columns = WINDOW_SIZE[0] // CELL_SIZE
rows = WINDOW_SIZE[1] // CELL_SIZE


class Player():
    def __init__(self):
        self.level = 0
        self.cells = difficulties[self.level]["start_cell_count"]
        self.win_cell_count = difficulties[self.level]["win_cell_count"]
        self.year_goal = difficulties[self.level]["year_goal"]
        self.starting_cells = difficulties[self.level]["start_cell_count"]
        self.years = 0
        self.cells_alive = 0
        self.win = False
        self.game_is_over = False

    def check_win(self):
        if self.win is True:
            return True
        if self.cells_alive >= self.win_cell_count and self.check_loss() is False:
            self.win = True
            self.game_is_over = True
            return True
        return False

    def level_up(self):
        if self.level < len(difficulties):
            self.level += 1
            self.reset()
            self.cells = difficulties[self.level]["start_cell_count"]
            self.win_cell_count = difficulties[self.level]["win_cell_count"]
            self.year_goal = difficulties[self.level]["year_goal"]

    def check_loss(self):
        if self.win is True:
            return False
        if self.years > self.year_goal:
            self.game_is_over = True
            return True
        return False

    def reset(self):
        self.win = False
        self.cells = self.starting_cells
        self.years = 0
        self.cells_alive = 0
        self.game_is_over = False


class Cell():
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.living = False
        self.x_coord = self.x // size
        self.y_coord = self.y // size
        self.rect = pygame.Rect(x, y, size, size)
        self.innerrect = pygame.Rect(x+1, y+1, size-2, size-2)

    def getNeighbors(self, cells):
        # Translates the cells position in the 2d array in
        # 8 directions to find the neighboring cells
        neighbors = []
        translate_directions = [
            [0, 1],
            [1, 0],
            [0,-1],
            [-1,0],
            [1,-1],
            [-1,1],
            [1, 1],
            [-1,-1],
        ]
        for translation in translate_directions:
            x = self.x_coord + translation[0]
            y = self.y_coord + translation[1]
            # check if neighbor exists
            if x < 0 or y < 0 or x >= len(cells[0]) or y >= len(cells):
                continue
            neighbors.append(cells[y][x])
        return neighbors

    def update(self):
        living_neigbhors = 0
        for neighbor in self.neighbors:
            if neighbor.living:
                living_neigbhors += 1

        if self.living:
            if living_neigbhors < 2:
                self.lives_next_round = False
            elif living_neigbhors > 3:
                self.lives_next_round = False
            else:
                self.lives_next_round = True
        else:
            if living_neigbhors == 3:
                self.lives_next_round = True
            else:
                self.lives_next_round = False
        # Setting self.lives_next_round instead of self.living so that all cells can update their state at the same time

    def draw(self, display):
        if self.living:
            pygame.draw.rect(display, (4, 255, 4), self.rect)
            pygame.draw.rect(display, (255, 4, 255), self.innerrect)



        else:
            if show_grid:
                pygame.draw.rect(display, (150, 150, 150), self.rect, 1)

# Creating cells and storing them in a 2d array
# todo put this in a function
for i in range(rows):
    cells.append([Cell(j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE) for j in range(columns)])

# Once all cells are created, find all of their neighbors
for row in cells:
    for cell in row:
        cell.neighbors = cell.getNeighbors(cells)

player = Player() # todo placing this here is silly u r a silly goose

pygame.init()
GAME_FONT = pygame.freetype.Font(None, 20)

def draw():
    if player.check_win():
        # todo this is window size minus strlen or something but we are lazy
        display.fill((207, 181, 59))
        for row in cells:
            for cell in row:
                if cell.living:
                    player.cells_alive += 1
                cell.draw(display)
        screen.blit(display, (0, 0))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2), "U R A WINRAR", (255, 255, 255))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] / 2)+50), "press any key to start next level!", (255, 255, 255))

        pygame.display.update()

    elif player.check_loss():
        # todo this is window size minus strlen or something but we are lazy
        display.fill((200, 0, 0))
        for row in cells:
            for cell in row:
                if cell.living:
                    player.cells_alive += 1
                cell.draw(display)
        screen.blit(display, (0, 0))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2), "o no u lost", (255, 255, 255))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] / 2) + 50),
                            "press any key to start a new game", (255, 255, 255))
        pygame.display.update()

    else:  #todo fuck this
        player.cells_alive = 0
        if setting_up:
            display.fill((50, 50, 50))
        else:
            display.fill((20, 70, 20))
            player.years += 1

        for row in cells:
            for cell in row:
                if cell.living:
                    player.cells_alive += 1
                cell.draw(display)



        screen.blit(display, (0, 0))
        if setting_up:
           GAME_FONT.render_to(screen, (0, WINDOW_SIZE[1] - 100), "Setting Up. Hit Space to Unpause", (255, 255, 255))
        else:
            GAME_FONT.render_to(screen, (0, WINDOW_SIZE[1] - 100), "Running! Hit Space to Pause", (255, 255, 255))

        GAME_FONT.render_to(screen, (0, 0), "Cells in Storage: {}".format(player.cells), (255, 255, 255))
        GAME_FONT.render_to(screen, (0, 20), "Cells Alive: {}".format(player.cells_alive), (255, 255, 255))

        GAME_FONT.render_to(screen, (0, 40),
                            "{} goal, {} needed to win".format(player.win_cell_count, (player.win_cell_count - player.cells_alive)),
                            (255, 255, 255))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0]/2, 0), "Current Year: {}".format(player.years),(255, 255, 255))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[0] / 2, 20), "Years Remaining: {}".format(player.year_goal - player.years), (255, 255, 255))
        GAME_FONT.render_to(screen, (WINDOW_SIZE[1]/2, WINDOW_SIZE[0]-30), "Difficulty:{}".format(difficulties[player.level]["name"]), (255, 255, 255))

        pygame.display.update()

while run:

    if not setting_up:
        clock.tick(FPS)

    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_g:
                show_grid = not show_grid

        if setting_up:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmousedown = True
                if event.button == 3:
                    rmousedown = True

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    lmousedown = False
                if event.button == 3:
                    rmousedown = False                    

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    setting_up = False
                if event.key == K_c: # todo this doesnt need to be here
                    for row in cells:
                        for cell in row:
                            cell.living = False

            if lmousedown:
                if player.cells > 0:
                    try:
                        if cells[my // CELL_SIZE][mx // CELL_SIZE].living is False:
                            cells[my//CELL_SIZE][mx//CELL_SIZE].living = True
                            player.cells -= 1

                    except IndexError:
                        pass
            if rmousedown:
                try:
                    if cells[my//CELL_SIZE][mx//CELL_SIZE].living is True:
                        player.cells += 1
                        cells[my//CELL_SIZE][mx//CELL_SIZE].living = False
                except IndexError:
                    pass
        else:
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                if player.game_is_over:
                    if player.win:
                        if player.level < len(difficulties):

                            player.level_up()
                    else:
                        player.reset()

                    cells = []
                    # Creating cells and storing them in a 2d array
                    for i in range(rows):
                        cells.append([Cell(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE) for j in range(columns)])

                    # Once all cells are created, find all of their neighbors
                    for row in cells:
                        for cell in row:
                            cell.neighbors = cell.getNeighbors(cells)

                    setting_up = True

                else: # todo this is requiring keydown/space again, i should probably rewrite this
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            setting_up = True

    if not setting_up and not player.game_is_over:
        for row in cells:
            for cell in row:
                cell.update()

        for row in cells:
            for cell in row:
                cell.living = cell.lives_next_round

    draw()