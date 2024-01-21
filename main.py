import pygame as pg
import sys
import numpy as np
from pygame.locals import *
import chess

### colors ###

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (150, 150, 150)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_LIGHT_YELLOW = (240, 240, 200)
COLOR_PINK = (255, 0, 255)
COLOR_PURPLE = (150, 0, 200)
COLOR_ORANGE = (255, 150, 0)
COLOR_BROWN = (115, 70, 42)

### images ###

WHITE_PAWN_IMG   = pg.image.load("resources/white_pawn.png")
WHITE_ROOK_IMG   = pg.image.load("resources/white_rook.png")
WHITE_KNIGHT_IMG = pg.image.load("resources/white_knight.png")
WHITE_BISHOP_IMG = pg.image.load("resources/white_bishop.png")
WHITE_QUEEN_IMG  = pg.image.load("resources/white_queen.png")
WHITE_KING_IMG   = pg.image.load("resources/white_king.png")
BLACK_PAWN_IMG   = pg.image.load("resources/black_pawn.png")
BLACK_ROOK_IMG   = pg.image.load("resources/black_rook.png")
BLACK_KNIGHT_IMG = pg.image.load("resources/black_knight.png")
BLACK_BISHOP_IMG = pg.image.load("resources/black_bishop.png")
BLACK_QUEEN_IMG  = pg.image.load("resources/black_queen.png")
BLACK_KING_IMG   = pg.image.load("resources/black_king.png")

def symbol_to_image(symbol):
	img = None
	if symbol != None:
		if symbol == chess.Piece.from_symbol('P'):
			img = WHITE_PAWN_IMG
		elif symbol == chess.Piece.from_symbol('R'):
			img = WHITE_ROOK_IMG
		elif symbol == chess.Piece.from_symbol('N'):
			img = WHITE_KNIGHT_IMG
		elif symbol == chess.Piece.from_symbol('B'):
			img = WHITE_BISHOP_IMG
		elif symbol == chess.Piece.from_symbol('Q'):
			img = WHITE_QUEEN_IMG
		elif symbol == chess.Piece.from_symbol('K'):
			img = WHITE_KING_IMG
		elif symbol == chess.Piece.from_symbol('p'):
			img = BLACK_PAWN_IMG
		elif symbol == chess.Piece.from_symbol('r'):
			img = BLACK_ROOK_IMG
		elif symbol == chess.Piece.from_symbol('n'):
			img = BLACK_KNIGHT_IMG
		elif symbol == chess.Piece.from_symbol('b'):
			img = BLACK_BISHOP_IMG
		elif symbol == chess.Piece.from_symbol('q'):
			img = BLACK_QUEEN_IMG
		elif symbol == chess.Piece.from_symbol('k'):
			img = BLACK_KING_IMG
		else:
			assert False
	return img

### screen ###

FPS = 60

pg.init()
pg.display.set_caption("pychess")

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 670
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

### clock ###

clock = pg.time.Clock()

board_grid = [[chess.Piece.from_symbol('k')] * 8 for _ in range(8)]
can_move = np.zeros((8, 8))

board = chess.Board()

def uci_to_coordinate(s):
	row = 7 - (ord(s[1]) - ord('1'))
	col = ord(s[0]) - ord('a')
	return (row, col)

def coordinate_to_uci(c, upper=False):
	x = chr(ord('a') + c[1])
	y = chr(ord('0') + (8 - c[0]))
	s = x + y
	if upper:
		s = s.upper()
	return s

def update_board_grid():
	for i in range(8):
		for j in range(8):
			board_grid[i][j] = eval(f"board.piece_at(chess.{coordinate_to_uci((i, j), upper=True)})")

def update_can_move(legal_moves, dragging_piece):
	global can_move
	can_move = np.zeros((8, 8))
	for m in legal_moves:
		(row, col) = uci_to_coordinate(m[0:2])
		if dragging_piece == (row, col):
			(row2, col2) = uci_to_coordinate(m[2:4])
			can_move[row2][col2] = 1

dragging_piece = (-1, -1)
touching_piece = (-1, -1)

SQUARE_WIDTH = 70
CIRCLE_RADIUS = 10

class Square(pg.sprite.Sprite):
	def __init__(self, row, col):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.Surface((SQUARE_WIDTH, SQUARE_WIDTH))
		if (row + col) % 2 == 0:
			self.image.fill(COLOR_LIGHT_YELLOW)
		else:
			self.image.fill(COLOR_BROWN)
		self.rect = self.image.get_rect()
		self.rect.x = 50 + col * SQUARE_WIDTH
		self.rect.y = 50 + row * SQUARE_WIDTH
		self.row = row
		self.col = col

	def update(self):
		# Get tile color
		color = COLOR_WHITE
		if (self.row + self.col) % 2 == 0:
			color = COLOR_LIGHT_YELLOW
		else:
			color = COLOR_BROWN

		# Draw margin
		if touching_piece == (self.row, self.col):
			self.image.fill(COLOR_GRAY)
			pg.draw.rect(self.image, color, pg.Rect(5, 5, SQUARE_WIDTH - 10, SQUARE_WIDTH - 10))
		else:
			self.image.fill(color)

		# Draw piece
		if dragging_piece != (self.row, self.col):
			img = symbol_to_image(board_grid[self.row][self.col])
			if img != None:
				self.image.blit(img, (SQUARE_WIDTH // 2 - img.get_width() // 2, SQUARE_WIDTH // 2 - img.get_height() // 2))

		# Draw dots
		if can_move[self.row][self.col]:
			circle = pg.Surface((SQUARE_WIDTH, SQUARE_WIDTH))
			circle.set_colorkey(COLOR_BLACK)
			circle.set_alpha(150)
			if board_grid[self.row][self.col] == None:
				pg.draw.circle(circle, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), CIRCLE_RADIUS)
			else:
				pg.draw.circle(circle, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), SQUARE_WIDTH // 2)
				pg.draw.circle(circle, COLOR_BLACK, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), (SQUARE_WIDTH - CIRCLE_RADIUS) // 2)
			self.image.blit(circle, (0, 0))

sprites = pg.sprite.Group()

for i in range(8):
	for j in range(8):
		sprites.add(Square(i, j))

MOUSE_LEFT, MOUSE_RIGHT = 1, 3

while True:
	# Set fps
	clock.tick(FPS)

	# Get legal moves
	legal_moves = list(str(list(board.legal_moves))[1:-1].replace("Move.from_uci(\'", "").replace("\')", "").split(","))
	legal_moves = [s.strip() for s in legal_moves]

	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			quit()
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
			dragging_piece = touching_piece
		elif event.type == pg.MOUSEBUTTONUP and event.button == MOUSE_LEFT:
			move = coordinate_to_uci(dragging_piece) + coordinate_to_uci(touching_piece)
			if move in [s[0:4] for s in legal_moves]:
				move = chess.Move.from_uci(move)
				board.push(move)
			dragging_piece = (-1, -1)
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == MOUSE_RIGHT:
			print("You pressed the right mouse button at (%d, %d)", event.pos)
		elif event.type == pg.MOUSEBUTTONUP and event.button == MOUSE_RIGHT:
			print("You released the right mouse button at (%d, %d)", event.pos)

	touching_piece = (-1, -1)
	for s in sprites:
		if s.rect.collidepoint(pg.mouse.get_pos()):
			touching_piece = (s.row, s.col)

	update_board_grid()
	update_can_move(legal_moves, dragging_piece)
	sprites.update()

	screen.fill(COLOR_WHITE)
	sprites.draw(screen)
	if dragging_piece != (-1, -1):
		img = symbol_to_image(board_grid[dragging_piece[0]][dragging_piece[1]])
		if img != None:
			pos = pg.mouse.get_pos()
			pos = (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2)
			screen.blit(img, pos)
	pg.display.update()
