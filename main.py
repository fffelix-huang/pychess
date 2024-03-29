import pygame as pg
from pygame.locals import *
import sys
import chess

### Colors ###

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

### Images ###

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

### Screen ###

FPS = 60

pg.init()
pg.display.set_caption("pychess")
pg.display.set_icon(WHITE_KNIGHT_IMG)

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 670
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

### Font ###

font = pg.font.SysFont("arial", 20)

### Clock ###

clock = pg.time.Clock()

board_grid = [[chess.Piece.from_symbol('k')] * 8 for _ in range(8)]
can_move = [[0] * 8 for _ in range(8)]

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
	can_move = [[0] * 8 for _ in range(8)]
	for m in legal_moves:
		(row, col) = uci_to_coordinate(m[0:2])

		if dragging_piece == (row, col):
			(row2, col2) = uci_to_coordinate(m[2:4])
			can_move[row2][col2] = 1

def draw_dragging_piece(dragging_piece):
	if dragging_piece != (-1, -1):
		img = symbol_to_image(board_grid[dragging_piece[0]][dragging_piece[1]])

		if img != None:
			pos = pg.mouse.get_pos()
			pos = (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2)
			screen.blit(img, pos)

dragging_piece = (-1, -1)
touching_piece = (-1, -1)
last_move = (-1, -1)

selecting_promotion = False
promotion_move = 'a1a1'
promotion_options = [[None] * 8 for _ in range(8)]

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
		# Handle promotion option button
		if selecting_promotion and promotion_options[self.row][self.col] != None:
			self.image.fill(COLOR_WHITE)
			img = symbol_to_image(promotion_options[self.row][self.col])
			self.image.blit(img, (SQUARE_WIDTH // 2 - img.get_width() // 2, SQUARE_WIDTH // 2 - img.get_height() // 2))
			return

		# Get tile color
		color = COLOR_WHITE
		if (self.row, self.col) == last_move[0] or (self.row, self.col) == last_move[1]:
			color = COLOR_YELLOW
		else:
			if (self.row + self.col) % 2 == 0:
				color = COLOR_LIGHT_YELLOW
			else:
				color = COLOR_BROWN

		# Draw margin and square
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

class Result(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.Surface((0, 0))
		self.rect = self.image.get_rect()
		self.terminate = False

	def update(self):
		# Update game status
		text = ""
		bar_color = COLOR_WHITE
		text_color = COLOR_BLACK
		if board.is_checkmate():
			self.terminate = True
			if board.fen().split()[1] == 'w':
				text = "Black wins by checkmate"
				bar_color, text_color = text_color, bar_color
			else:
				text = "White wins by checkmate"
		elif board.is_stalemate():
			self.terminate = True
			text = "Draw by stalemate"
		elif board.is_insufficient_material():
			self.terminate = True
			text = "Draw by insufficient material"
		elif board.can_claim_threefold_repetition():
			self.terminate = True
			text = "Draw by threefold repetition"
		elif board.can_claim_fifty_moves():
			self.terminate = True
			text = "Draw by fifty moves rule"
		else:
			return

		# Render text and draw
		text = font.render(text, True, text_color)
		self.image = pg.Surface((text.get_width() + 10, text.get_height() + 10))
		self.image.fill(bar_color)
		self.image.blit(text, dest=(5, 5))
		side_width = SCREEN_WIDTH - (50 + SQUARE_WIDTH * 8)
		margin = (side_width - self.image.get_width()) // 2
		self.rect.x = 50 + SQUARE_WIDTH * 8 + margin
		self.rect.y = 100

sprites = pg.sprite.Group()

for i in range(8):
	for j in range(8):
		sprites.add(Square(i, j))

result = Result()
sprites.add(result)

# Constant for pygame event
MOUSE_LEFT, MOUSE_RIGHT = 1, 3

while True:
	# Set fps
	clock.tick(FPS)

	# Get legal moves
	if result.terminate == False:
		legal_moves = list(str(list(board.legal_moves))[1:-1].replace("Move.from_uci(\'", "").replace("\')", "").split(","))
		legal_moves = [s.strip() for s in legal_moves if len(s) > 0]

	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			quit()
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
			dragging_piece = touching_piece
		elif event.type == pg.MOUSEBUTTONUP and event.button == MOUSE_LEFT:
			if selecting_promotion == False:
				# Not selecting pawn promotion
				move = coordinate_to_uci(dragging_piece) + coordinate_to_uci(touching_piece)
				moves = [s for s in legal_moves if s[0:4] == move]

				if len(moves) > 0:
					if len(moves) == 4:
						# Pawn promotion
						selecting_promotion = True
						promotion_move = move
						col = touching_piece[1]

						if touching_piece[0] == 0:
							# White side
							promotion_options[0][col] = chess.Piece.from_symbol('Q')
							promotion_options[1][col] = chess.Piece.from_symbol('N')
							promotion_options[2][col] = chess.Piece.from_symbol('R')
							promotion_options[3][col] = chess.Piece.from_symbol('B')
						else:
							# Black side
							promotion_options[7][col] = chess.Piece.from_symbol('q')
							promotion_options[6][col] = chess.Piece.from_symbol('n')
							promotion_options[5][col] = chess.Piece.from_symbol('r')
							promotion_options[4][col] = chess.Piece.from_symbol('b')

					board.push(chess.Move.from_uci(move))

					if len(moves) == 1:
						last_move = (uci_to_coordinate(move[0:2]), uci_to_coordinate(move[2:4]))
			else:
				board.pop()

				# Select a promotion
				if promotion_options[touching_piece[0]][touching_piece[1]] != None:
					promotion_type = str(promotion_options[touching_piece[0]][touching_piece[1]])
					promotion_move = (promotion_move + promotion_type).lower()
					board.push(chess.Move.from_uci(promotion_move))
					last_move = (uci_to_coordinate(promotion_move[0:2]), uci_to_coordinate(promotion_move[2:4]))

				selecting_promotion = False
				promotion_options = [[None] * 8 for _ in range(8)]

			dragging_piece = (-1, -1)

	# Update touching_piece
	touching_piece = (-1, -1)
	for s in sprites:
		if s.rect.collidepoint(pg.mouse.get_pos()):
			touching_piece = (s.row, s.col)

	update_board_grid()
	update_can_move(legal_moves, dragging_piece)
	sprites.update()

	# Draw
	screen.fill(COLOR_GRAY)
	sprites.draw(screen)
	draw_dragging_piece(dragging_piece)
	pg.display.update()
