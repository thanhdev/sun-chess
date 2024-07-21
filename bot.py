import copy
import random
import time

from main import RED, BLACK


class Bot:
    def __init__(self):
        self.color = random.choice([RED, BLACK])
        self.time_limit = 5  # 5 seconds time limit
        self.sun_capture_value = 1000000  # A very high value for capturing the Sun

    def get_move(self, board):
        start_time = time.time()
        best_move = None
        depth = 1

        valid_moves = self.get_all_valid_moves(board)
        if not valid_moves:
            return None  # Return None if no valid moves are available

        while time.time() - start_time < self.time_limit:
            try:
                move = self.iterative_deepening(board, depth, start_time)
                if move:
                    best_move = move
                depth += 1
            except TimeoutError:
                break

        return best_move

    def iterative_deepening(self, board, depth, start_time):
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        for piece, move in self.get_all_valid_moves(board):
            if time.time() - start_time > self.time_limit:
                raise TimeoutError

            temp_board = self.simulate_move(board, piece, move)
            score = self.minimax(temp_board, depth - 1, False, alpha, beta, start_time)
            if score > best_score:
                best_score = score
                best_move = (piece, move)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_move

    def minimax(self, board, depth, is_maximizing, alpha, beta, start_time):
        if time.time() - start_time > self.time_limit:
            raise TimeoutError

        if depth == 0 or board.winner:
            return self.evaluate_board(board)

        if is_maximizing:
            best_score = float("-inf")
            for piece, move in self.get_all_valid_moves(board):
                temp_board = self.simulate_move(board, piece, move)
                score = self.minimax(
                    temp_board, depth - 1, False, alpha, beta, start_time
                )
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float("inf")
            for piece, move in self.get_all_valid_moves(board, opponent=True):
                temp_board = self.simulate_move(board, piece, move)
                score = self.minimax(
                    temp_board, depth - 1, True, alpha, beta, start_time
                )
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score

    def evaluate_board(self, board):
        if board.winner:
            color = "Red" if self.color == RED else "Black"
            return (
                self.sun_capture_value
                if board.winner == f"{color} wins!"
                else -self.sun_capture_value
            )

        bot_sum = 0
        opponent_sum = 0
        bot_has_sun = False
        opponent_has_sun = False

        for row in board.board:
            for piece in row:
                if piece != 0:
                    if piece.color == self.color:
                        if piece.value == 0:  # Sun piece
                            bot_has_sun = True
                            bot_sum += 50  # Give a higher value to having the Sun
                        else:
                            bot_sum += piece.value
                    else:
                        if piece.value == 0:  # Sun piece
                            opponent_has_sun = True
                            opponent_sum += 50
                        else:
                            opponent_sum += piece.value

        # If the opponent doesn't have a Sun, return a very high score
        if not opponent_has_sun:
            return self.sun_capture_value

        # If the bot doesn't have a Sun, return a very low score
        if not bot_has_sun:
            return -self.sun_capture_value

        # Return the difference in piece values, with a bonus for having more pieces
        return (bot_sum - opponent_sum) + (
            len(self.get_all_pieces(board))
            - len(self.get_all_pieces(board, opponent=True))
        ) * 10

    def get_all_valid_moves(self, board, opponent=False):
        valid_moves = []
        for piece in self.get_all_pieces(board, opponent):
            moves = board.get_valid_moves(piece)
            valid_moves.extend([(piece, move) for move in moves])
        return valid_moves

    def get_all_pieces(self, board, opponent=False):
        pieces = []
        color = self.color if not opponent else (RED if self.color == BLACK else BLACK)
        for row in board.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def simulate_move(self, board, piece, move):
        temp_board = copy.deepcopy(board)
        temp_piece = next(
            p
            for row in temp_board.board
            for p in row
            if p != 0 and p.row == piece.row and p.col == piece.col
        )
        row, col = move
        temp_board.board[temp_piece.row][temp_piece.col] = 0
        temp_piece.move(row, col)
        temp_board.board[row][col] = temp_piece
        temp_board.change_turn()
        temp_board.check_win()
        return temp_board
