import pygame
import random
import sys

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK = (20, 20, 30)

COLORS = [
    (0, 240, 240),
    (240, 240, 0),
    (160, 0, 240),
    (0, 240, 0),
    (240, 0, 0),
    (0, 0, 240),
    (240, 160, 0),
]

PIECES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[0,1,1],[1,1,0]],
    [[1,1,0],[0,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
]

BLOCK = 30
COLS = 10
ROWS = 20
WIDTH = 700
HEIGHT = 660

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris+")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20, bold=True)
font_big = pygame.font.SysFont("Arial", 36, bold=True)

def new_piece():
    idx = random.randint(0, len(PIECES) - 1)
    return {
        'shape': PIECES[idx],
        'color': COLORS[idx],
        'x': COLS // 2 - len(PIECES[idx][0]) // 2,
        'y': 0
    }

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def valid(board, piece, ox=0, oy=0):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                nx = piece['x'] + x + ox
                ny = piece['y'] + y + oy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def place(board, piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                board[piece['y'] + y][piece['x'] + x] = piece['color']

def clear_lines(board):
    full = [i for i, row in enumerate(board) if all(row)]
    for i in full:
        board.pop(i)
        board.insert(0, [None] * COLS)
    return len(full)

def draw_board(board, offset_x=20, offset_y=20):
    pygame.draw.rect(screen, GRAY, (offset_x - 2, offset_y - 2, COLS * BLOCK + 4, ROWS * BLOCK + 4), 2)
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pygame.draw.rect(screen, board[y][x], (offset_x + x * BLOCK, offset_y + y * BLOCK, BLOCK - 1, BLOCK - 1))
            else:
                pygame.draw.rect(screen, GRAY, (offset_x + x * BLOCK, offset_y + y * BLOCK, BLOCK - 1, BLOCK - 1), 1)

def draw_piece(piece, offset_x=20, offset_y=20):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece['color'],
                                 (offset_x + (piece['x'] + x) * BLOCK,
                                  offset_y + (piece['y'] + y) * BLOCK,
                                  BLOCK - 1, BLOCK - 1))
                
def draw_ghost(board, piece, offset_x=20, offset_y=20):
    ghost = dict(piece)
    ghost['shape'] = [row[:] for row in piece['shape']]
    while valid(board, ghost, oy=1):
        ghost['y'] += 1
    for y, row in enumerate(ghost['shape']):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, (80, 80, 80),
                                 (offset_x + (ghost['x'] + x) * BLOCK,
                                  offset_y + (ghost['y'] + y) * BLOCK,
                                  BLOCK - 1, BLOCK - 1), 2)
                
def draw_next(piece):
    label = font.render("NEXT", True, WHITE)
    screen.blit(label, (370, 30))
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece['color'],
                                 (370 + x * BLOCK, 60 + y * BLOCK, BLOCK - 1, BLOCK - 1))
                
def draw_ui(score, level, lines):
    screen.blit(font.render(f"SCORE", True, WHITE), (370, 180))
    screen.blit(font_big.render(str(score), True, WHITE), (370, 200))
    screen.blit(font.render(f"LEVEL", True, WHITE), (370, 260))
    screen.blit(font_big.render(str(level), True, WHITE), (370, 280))
    screen.blit(font.render(f"LINES", True, WHITE), (370, 340))
    screen.blit(font_big.render(str(lines), True, WHITE), (370, 360))
    screen.blit(font.render("← → move", True, GRAY), (370, 430))
    screen.blit(font.render("↑ rotate", True, GRAY), (370, 455))
    screen.blit(font.render("↓ soft drop", True, GRAY), (370, 480))
    screen.blit(font.render("SPACE hard drop", True, GRAY), (370, 505))

def main():
    board = [[None] * COLS for _ in range(ROWS)]
    piece = new_piece()
    next_piece = new_piece()
    score = 0
    level = 1
    lines_total = 0
    fall_time = 0
    fall_speed = 500

    running = True
    game_over = False

    while running:
        screen.fill(DARK)
        dt = clock.tick(60)
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and valid(board, piece, ox=-1):
                    piece['x'] -= 1
                if event.key == pygame.K_RIGHT and valid(board, piece, ox=1):
                    piece['x'] += 1
                if event.key == pygame.K_UP:
                    rotated = rotate(piece['shape'])
                    if valid(board, {'shape': rotated, 'x': piece['x'], 'y': piece['y']}):
                        piece['shape'] = rotated
                if event.key == pygame.K_DOWN and valid(board, piece, oy=1):
                    piece['y'] += 1
                if event.key == pygame.K_SPACE:
                    while valid(board, piece, oy=1):
                        piece['y'] += 1
                if event.key == pygame.K_r and game_over:
                    main()
        
        if not game_over and fall_time > fall_speed:
            fall_time = 0
            if valid(board, piece, oy=1):
                piece['y'] += 1
            else:
                place(board, piece)
                cleared = clear_lines(board)
                lines_total += cleared
                score += [0, 100, 300, 500, 800][cleared] * level
                level = lines_total // 10 + 1
                fall_speed = max(100, 500 - (level - 1) * 40)
                piece = next_piece
                next_piece = new_piece()
                if not valid(board, piece):
                    game_over = True

        draw_board(board)
        draw_ghost(board, piece)
        draw_piece(piece)
        draw_next(next_piece)
        draw_ui(score, level, lines_total)

        if game_over:
            over = font_big.render("GAME OVER", True, (240, 0, 0))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 20))
            sub = font.render("Press R to restart", True, WHITE)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 30))

        pygame.display.flip()

main()