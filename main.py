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
can_move[1][1] = 1
can_move[4][4] = 1

board = chess.Board()

def update_board_grid():
	for i in range(8):
		for j in range(8):
			board_grid[i][j] = eval(f"board.piece_at(chess.{chr(ord('A') + j)}{8 - i})")

SQUARE_WIDTH = 70

dragging_piece = (-1, -1)

class BoardSquare(pg.sprite.Sprite):
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
		if (self.row + self.col) % 2 == 0:
			self.image.fill(COLOR_LIGHT_YELLOW)
		else:
			self.image.fill(COLOR_BROWN)
		if dragging_piece != (self.row, self.col):
			img = symbol_to_image(board_grid[self.row][self.col])
			if img != None:
				self.image.blit(img, (SQUARE_WIDTH // 2 - img.get_width() // 2, SQUARE_WIDTH // 2 - img.get_height() // 2))

CIRCLE_RADIUS = 15

class BoardCircle(pg.sprite.Sprite):
	def __init__(self, row, col):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.Surface((SQUARE_WIDTH, SQUARE_WIDTH))
		self.image.set_colorkey(COLOR_BLACK)
		self.image.set_alpha(0)
		self.row = row
		self.col = col
		self.rect = self.image.get_rect()
		self.rect.x = 50 + col * SQUARE_WIDTH
		self.rect.y = 50 + row * SQUARE_WIDTH
		pg.draw.circle(self.image, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), CIRCLE_RADIUS)

	def update(self):
		self.image.fill(COLOR_BLACK)
		if can_move[self.row][self.col]:
			self.image.set_alpha(150)
			if board_grid[self.row][self.col] == None:
				pg.draw.circle(self.image, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), CIRCLE_RADIUS)
			else:
				pg.draw.circle(self.image, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), SQUARE_WIDTH // 2)
				pg.draw.circle(self.image, COLOR_BLACK, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), (SQUARE_WIDTH - CIRCLE_RADIUS) // 2)
		else:
			self.image.set_alpha(0)
			pg.draw.circle(self.image, COLOR_GRAY, (SQUARE_WIDTH // 2, SQUARE_WIDTH // 2), CIRCLE_RADIUS)

pieces = pg.sprite.Group()
circles = pg.sprite.Group()

for i in range(8):
	for j in range(8):
		pieces.add(BoardSquare(i, j))
		circles.add(BoardCircle(i, j))

MOUSE_LEFT, MOUSE_RIGHT = 1, 3

while True:
	clock.tick(FPS)
	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			quit()
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
			print("You pressed the left mouse button at (%d, %d)", event.pos)
			pos = pg.mouse.get_pos()
			clicked_sprites = [s for s in pieces if s.rect.collidepoint(pos)]
			if len(clicked_sprites) > 0:
				print(clicked_sprites[0].row, clicked_sprites[0].col)
				dragging_piece = (clicked_sprites[0].row, clicked_sprites[0].col)
		elif event.type == pg.MOUSEBUTTONUP and event.button == MOUSE_LEFT:
			print("You released the left mouse button at (%d, %d)", event.pos)
			dragging_piece = (-1, -1)
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == MOUSE_RIGHT:
			print("You pressed the right mouse button at (%d, %d)", event.pos)
		elif event.type == pg.MOUSEBUTTONUP and event.button == MOUSE_RIGHT:
			print("You released the right mouse button at (%d, %d)", event.pos)

	update_board_grid()
	pieces.update()
	circles.update()

	screen.fill(COLOR_WHITE)
	pieces.draw(screen)
	circles.draw(screen)
	if dragging_piece != (-1, -1):
		img = symbol_to_image(board_grid[dragging_piece[0]][dragging_piece[1]])
		if img != None:
			pos = pg.mouse.get_pos()
			pos = (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2)
			screen.blit(img, pos)
	pg.display.update()
