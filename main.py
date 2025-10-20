import pygame
import random
import sys
from pygame.locals import *
 
pygame.init()


scrn_width = 300
scrn_height = 600
blck_sz = 30
rows = 20
cols = 10
title_font = pygame.font.SysFont("comic sans", 20)
small_font = pygame.font.SysFont("verdana", 12)


win = pygame.display.set_mode((scrn_width + 200, scrn_height))
pygame.display.set_caption("LANKEN TETRIS")


white = (255, 255, 255)
gray = (100, 100, 100)
blk = (0, 0, 0)
clr_lst = [
    (0, 255, 255),
    (255, 100, 100),
    (100, 255, 100),
    (255, 255, 100),
    (255, 165, 0),
    (100, 100, 255),
    (160, 32, 240),
]


shapes = [
    [[1, 1, 1, 1,]], # I
    [[1, 1, 0], [0, 1, 1,]], # Z
    [[0, 1, 1,], [1, 1, 0]], # S
    [[1, 1,], [1, 1]], # O
    [[1, 0, 0], [1, 1, 1]], #J
    [[0, 1, 0,], [1, 1, 1]] #T
]



class Tetpiece:
    def __init__(self, x_pos, y_pos, type_idx):
        self.x = x_pos
        self.y = y_pos
        self.typ = type_idx
        self.shape = shapes[type_idx]
        self.colr = clr_lst[type_idx]
        self.rot = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        self.rot = (self.rot + 1) % 4


def build_grid(locked_blocks={}):
    board = [[blk for _ in range(cols)] for _ in range(rows)]
    for y in range(rows):
        for x in range(cols):
            if (x, y) in locked_blocks: 
                    board[y][x] = locked_blocks[(x, y)] 
    return board  

         
def draw_grid(screen, grid_data):
    for y in range(rows):
           for x in range(cols):
             pygame.draw.rect(screen, grid_data[y][x], (x*blck_sz, y*blck_sz, blck_sz, blck_sz), 0)

    for y in range(rows):
                    pygame.draw.line (screen, gray, (0, y*blck_sz), (scrn_width, y*blck_sz))
    for x in range (cols):
            pygame.draw.line(screen, gray, (x*blck_sz, 0), (x*blck_sz, scrn_height))   

def covert_piece (piece_obj):      
      covert = []
      for i, row in enumerate(piece_obj.shape):
        for j, cell in enumerate(row): 
          if cell:
               covert.append((piece_obj.x + j, piece_obj.y + i))
      return covert


def valid_move(shape_coords, grid):
    for x, y in shape_coords:
        if x < 0 or x >= cols or y >= rows:
            return False
        if y >= 0 and grid[y][x] != blk:
            return False
    return True

def clear_full_rows(grid, locked_pos):
    cleared = 0
    for y in range(rows -1, -1, -1):    
        if blk not in grid[y]:
            cleared += 1
            ind = y 
            for x in range(cols):
                try:
                    del locked_pos[(x, y)]
                except:
                    continue
    if cleared > 0:
        for key in sorted(list(locked_pos), key=lambda a: a[1])[:: -1]:
            x, y = key
            if y < ind:
                newkey = (x, y + cleared)
                locked_pos[newkey] = locked_pos.pop(key)
    return cleared

def draw_window(scrn, grid, score=0):
    scrn.fill((0, 0, 0))
    draw_grid(scrn, grid)

    label = small_font.render("SCORE: " + str(score), 1, white)
    scrn.blit (label, (scrn_width + 20, 50))

    title_ibi = title_font.render("LANKEN TETRIS: " , 1, white)
    scrn.blit(title_ibi, (scrn_width + 10, 2))

    pygame.display.update()

def get_rand_piece():
    idx = random.randint(0, len(shapes) -1)
    return Tetpiece(3, 0, idx)

def game_over(position):
    for p in position:
        x,y = p
        if y < 1:
            return True
    return False


def temp_logger(text):
    with open ("temp_log.txt", "a") as logf:
        logf.write(text + "\n")

class RandomObject:
    def _init_(self):
        self.x = 1
        self.y= 2
    def dummy(self):
        return self.x + self.y
        
def main_game():
    locked_position = {}
    grid = build_grid(locked_position)    

    change_piece = False
    run_game = True
    current_piece = get_rand_piece()
    next_piece = get_rand_piece()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    dummy_counter = 0

    while run_game:
        grid = build_grid(locked_position) # type: ignore
        fall_time += clock.get_rawtime()
        clock.tick()


        if fall_time / 1000 >= fall_speed:
            current_piece.y += 1
            if not valid_move(covert_piece(current_piece), grid):
                current_piece.y -= 1
                change_piece = True
            fall_time = 0


        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_move(covert_piece(current_piece), grid):
                        current_piece.x += 1
                elif e.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_move(covert_piece(current_piece), grid):
                        current_piece.x -= 1
                elif e.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_move(covert_piece(current_piece), grid):
                         current_piece.y -= 1
                elif e.key == pygame .K_UP:
                    current_piece.rotate()
                    if not valid_move(covert_piece(current_piece), grid):
                        for _ in range(3): current_piece.rotate()


        for x, y in covert_piece(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.colr


        if change_piece:
            for pos in covert_piece(current_piece):
                p = (pos [0], pos[1])
                locked_position[p] = current_piece.colr
            current_piece = next_piece
            next_piece = get_rand_piece()
            change_piece = False
            score += clear_full_rows(grid, locked_position)* 10
        
        draw_window(win, grid, score)

        if game_over(locked_position):
            run_game = False
            temp_logger("Game over at score: " + str(score))

    end_text = title_font.render("GAME OVER", 1,(255,0,0))
    win.blit(end_text, (scrn_width // 2 - 80, scrn_height // 2 - 30))
    pygame.display.update()
    pygame.time.delay(2500)

if __name__ == "__main__":
    main_game()
