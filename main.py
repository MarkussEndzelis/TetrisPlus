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

SPECIAL_PIECES = [
    {'type': 'bomb', 'shape': [[1]], 'color': (255, 80, 80)},
    {'type': 'lightning', 'shape': [[1]], 'color': (255, 255, 0)},
    {'type': 'crystal', 'shape': [[1]], 'color': (0, 200, 255)},
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
    if random.randint(1, 8) == 1:
        sp = random.choice(SPECIAL_PIECES)
        return {
            'shape': sp['shape'],
            'color': sp['color'],
            'type': sp['type'],
            'x': COLS // 2,
            'y': 0
        }
    idx = random.randint(0, len(PIECES) - 1)
    return {
        'shape': PIECES[idx],
        'color': COLORS[idx],
        'type': 'normal',
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
    screen.blit(font.render(f"SCORE", True, WHITE), (370, 220))
    screen.blit(font_big.render(str(score), True, WHITE), (370, 240))
    screen.blit(font.render(f"LEVEL", True, WHITE), (370, 300))
    screen.blit(font_big.render(str(level), True, WHITE), (370, 320))
    screen.blit(font.render(f"LINES", True, WHITE), (370, 370))
    screen.blit(font_big.render(str(lines), True, WHITE), (370, 390))
    screen.blit(font.render("← → move", True, (180, 180, 180)), (370, 450))
    screen.blit(font.render("↑ rotate", True, (180, 180, 180)), (370, 472))
    screen.blit(font.render("↓ soft drop", True, (180, 180, 180)), (370, 494))
    screen.blit(font.render("SPACE hard drop", True, (180, 180, 180)), (370, 516))
    screen.blit(font.render("C - hold", True, (180, 180, 180)), (370, 538))

def draw_mode_ui(mode, lines_total, elapsed, blitz_time):
    if mode == 'sprint':
        remaining = f"Lines left: {max(0, 40 - lines_total)}"
        screen.blit(font.render(remaining, True, (0, 240, 0)), (370, 600))
    elif mode == 'blitz':
        secs = max(0, (blitz_time - elapsed) // 1000)
        timer = f"Time: {secs}s"
        color = (240, 60, 60) if secs <= 10 else (240, 160, 0)
        screen.blit(font.render(timer, True, color), (370, 600))

def draw_special_hint(piece):
    if piece['type'] != 'normal':
        hints = {
            'bomb': ('BOMB', '3x3 explosion', (255, 80, 80)),
            'lightning': ('LIGHTNING', 'clears column', (255, 255, 0)),
            'crystal': ('CRYSTAL', 'clears row', (0, 200, 255)),
        }
        name, desc, color = hints[piece['type']]
        label = font.render(f"SPECIAL: {name}", True, color)
        sub = font.render(desc, True, (180, 180, 180))
        screen.blit(label, (370, 550))
        screen.blit(sub, (370, 575))

def explode_bomb(board, px, py):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            ny, nx = py + dy, px + dx
            if 0 <= ny < ROWS and 0 <= nx < COLS:
                board[ny][nx] = None

def explode_lightning(board, px):
    for y in range(ROWS):
        board[y][px] = None

def explode_crystal(board, py):
    for x in range(COLS):
        board[py][x] = None

def activate_special(board, piece):
    px = piece['x']
    py = piece['y']
    t = piece['type']
    if t == 'bomb':
        explode_bomb(board, px, py)
    elif t == 'lightning':
        explode_lightning(board, px)
    elif t == 'crystal':
        explode_crystal(board, py)

def draw_hold(piece):
    label = font.render("HOLD", True, WHITE)
    screen.blit(label, (370, 150))
    if piece:
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'],
                                     (370 + x * BLOCK, 175 + y * BLOCK, BLOCK - 1, BLOCK - 1))


def mode_select():
    selected = None
    while selected is None:
        screen.fill(DARK)
        title = font_big.render("TETRIS+", True, (0, 240, 240))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        modes = [
            ("ENDLESS", "classic tetris, no limit", (0, 240, 240)),
            ("SPRINT", "clear 40 lines, fastest time", (0, 240, 0)),
            ("BLITZ", "2 minutes, max score", (240, 160, 0)),
        ]

        for i, (name, desc, color) in enumerate(modes):
            y = 200 + i * 120
            pygame.draw.rect(screen, (30, 30, 50), (150, y, 400, 80), border_radius=10)
            pygame.draw.rect(screen, color, (150, y, 400, 80), 2, border_radius=10)
            label = font_big.render(name, True, color)
            screen.blit(label, (170, y + 10))
            sub = font.render(desc, True, (180, 180, 180))
            screen.blit(sub, (170, y + 48))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, (name, _, _) in enumerate(modes):
                    y = 200 + i * 120
                    if 150 <= mx <= 550 and y <= my <= y + 80:
                        selected = name.lower()
        
        pygame.display.flip()
        clock.tick(60)
    return selected

def main(mode='endless'):
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
    sprint_done = False
    blitz_time = 120000
    elapsed = 0
    held_piece = None
    can_hold = True

    while running:
        screen.fill(DARK)
        dt = clock.tick(60)
        fall_time += dt
        if mode == 'blitz':
            elapsed += dt
            if elapsed >= blitz_time:
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        board = [[None] * COLS for _ in range(ROWS)]
                        piece = new_piece()
                        next_piece = new_piece()
                        score = 0
                        level = 1
                        lines_total = 0
                        fall_time = 0
                        fall_speed = 500
                        game_over = False
                    if event.key == pygame.K_m:
                        return
                else:

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
                    if event.key == pygame.K_c and can_hold:
                        if held_piece is None:
                            held_piece = new_piece()
                            held_piece['shape'] = piece['shape']
                            held_piece['color'] = piece['color']
                            held_piece['type'] = piece['type']
                            piece = next_piece
                            next_piece = new_piece()
                        else:
                            piece, held_piece = held_piece, piece
                            piece['x'] = COLS // 2 - len(piece['shape'][0]) // 2
                            piece['y'] = 0
                        can_hold = False
        
        if not game_over and fall_time > fall_speed:
            fall_time = 0
            if valid(board, piece, oy=1):
                piece['y'] += 1
            else:
                if piece['type'] == 'normal':
                    place(board, piece)
                else:
                    activate_special(board, piece)
                cleared = clear_lines(board)
                lines_total += cleared
                if mode == 'sprint' and lines_total >= 40:
                    game_over = True
                    sprint_done = True
                score += [0, 100, 300, 500, 800][cleared] * level
                level = lines_total // 10 + 1
                fall_speed = max(100, 500 - (level - 1) * 40)
                piece = next_piece
                can_hold = True
                next_piece = new_piece()
                if not valid(board, piece):
                    game_over = True

        draw_board(board)
        draw_ghost(board, piece)
        draw_piece(piece)
        draw_next(next_piece)
        draw_special_hint(next_piece)
        draw_ui(score, level, lines_total)
        draw_mode_ui(mode, lines_total, elapsed, blitz_time)
        draw_hold(held_piece)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            over = font_big.render("GAME OVER", True, (240, 60, 60))
            shadow = font_big.render("GAME OVER", True, (0, 0, 0))
            screen.blit(shadow, (WIDTH // 2 - over.get_width() // 2 + 2, HEIGHT // 2 - 52))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 54))

            score_text = font.render(f"Score: {score} | Lines: {lines_total} | Level: {level}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

            sub = font.render("Press R to restart  M - main menu", True, (180, 180, 180))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

while True:
    mode = mode_select()
    main(mode)