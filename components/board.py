import pygame

from components.piece import Piece
from constants import (
    ROWS,
    COLS,
    RED,
    BLACK,
    YELLOW,
    SQUARE_SIZE,
    BLUE,
    GREEN,
    GOLD,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)


class Board:
    def __init__(self):
        self.board = []
        self.selected_piece = None
        self.red_turn = True
        self.valid_moves = []
        self.winner = None
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row < 2 or row > 4:
                    color = RED if row < 2 else BLACK
                    if row == 0 or row == 6:
                        value = [4, 3, 2, 0, 2, 3, 4][col]
                    elif row == 1 or row == 5:
                        value = [1, 2, 3, 4, 3, 2, 1][col]
                    else:
                        continue
                    self.board[row].append(Piece(row, col, value, color))
                else:
                    self.board[row].append(0)

    def draw(self, _screen):
        for row in range(ROWS):
            for col in range(COLS):
                # Draw yellow square
                pygame.draw.rect(
                    _screen,
                    YELLOW,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )
                # Draw black border
                pygame.draw.rect(
                    _screen,
                    BLACK,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    1,
                )

                # Draw piece if exists
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(_screen)

        # Highlight selected piece
        if self.selected_piece:
            x = self.selected_piece.col * SQUARE_SIZE
            y = self.selected_piece.row * SQUARE_SIZE
            pygame.draw.rect(_screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

        # Draw valid moves
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(
                _screen,
                GREEN,
                (
                    col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2,
                ),
                15,
            )

        # Draw gold border around the entire board
        pygame.draw.rect(_screen, GOLD, (0, 0, BOARD_WIDTH, BOARD_HEIGHT), 4)

    def select(self, row, col):
        if self.selected_piece:
            result = self._move(row, col)
            if not result:
                self.selected_piece = None
                self.select(row, col)
            return result

        piece = self.board[row][col]
        if piece != 0 and piece.color == (RED if self.red_turn else BLACK):
            self.selected_piece = piece
            self.valid_moves = self.get_valid_moves(piece)
            return False

        return False

    def _move(self, row, col):
        if self.selected_piece and (row, col) in self.valid_moves:
            self.board[self.selected_piece.row][self.selected_piece.col] = 0
            self.selected_piece.move(row, col)
            self.board[row][col] = self.selected_piece
            self.change_turn()
            return True
        return False

    def change_turn(self):
        self.red_turn = not self.red_turn
        self.valid_moves = []
        self.selected_piece = None

    def get_valid_moves(self, piece):
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.is_valid_move(piece, r, c):
                    moves.append((r, c))
        return moves

    def is_valid_move(self, piece, row, col):
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return False

        # Check if the move is in a straight line
        row_diff = row - piece.row
        col_diff = col - piece.col

        # Check if the move distance matches the piece's value
        # Special case for Sun (value 0): it moves like a piece with value 1
        if piece.value == 0:
            distance = max(abs(row_diff), abs(col_diff))
            if distance != 1:
                return False
        else:
            distance = max(abs(row_diff), abs(col_diff))
            if distance != piece.value:
                return False

        # Check if the move is in a straight line (horizontal, vertical, or diagonal)
        if row_diff != 0 and col_diff != 0:
            if abs(row_diff) != abs(col_diff):
                return False

        # Check if the destination is empty or contains an opponent's piece
        target = self.board[row][col]
        if target == 0 or target.color != piece.color:
            return True

        return False

    def check_win(self):
        red_sun = black_sun = False
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.value == 0:
                    if piece.color == RED:
                        red_sun = True
                    else:
                        black_sun = True

        if not red_sun:
            self.winner = "Black wins!"
        elif not black_sun:
            self.winner = "Red wins!"

        return self.winner
