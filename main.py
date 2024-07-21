import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
BOARD_WIDTH, BOARD_HEIGHT = 700, 700
PANEL_WIDTH = 200
ROWS, COLS = 7, 7
SQUARE_SIZE = BOARD_WIDTH // COLS
TOTAL_WIDTH = BOARD_WIDTH + PANEL_WIDTH
TOTAL_HEIGHT = BOARD_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Create the screen
screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption("Sun Chess")


class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 32)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Piece:
    def __init__(self, row, col, value, color):
        self.row = row
        self.col = col
        self.value = value
        self.color = color
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def draw(self, screen):
        radius = SQUARE_SIZE // 2 - 10
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)

        if self.value == 0:  # Sun piece
            points = []
            for i in range(8):
                angle = i * 45
                x = self.x + int(
                    radius * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).x
                )
                y = self.y + int(
                    radius * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).y
                )
                points.append((x, y))
            pygame.draw.polygon(screen, YELLOW, points)
        else:  # Number piece
            font = pygame.font.Font(None, 36)
            text = font.render(
                str(self.value), True, YELLOW if self.color == RED else RED
            )
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()


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
                    self.board[row].append(Piece(row, col, value, color))
                else:
                    self.board[row].append(0)

    def draw(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                # Draw yellow square
                pygame.draw.rect(
                    screen,
                    YELLOW,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )
                # Draw black border
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    1,
                )

                # Draw piece if exists
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(screen)

        # Highlight selected piece
        if self.selected_piece:
            x = self.selected_piece.col * SQUARE_SIZE
            y = self.selected_piece.row * SQUARE_SIZE
            pygame.draw.rect(screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

        # Draw valid moves
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(
                screen,
                GREEN,
                (
                    col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2,
                ),
                15,
            )

        # Draw gold border around the entire board
        pygame.draw.rect(screen, GOLD, (0, 0, BOARD_WIDTH, BOARD_HEIGHT), 4)

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


def draw_info_panel(
    screen, board, new_game_button, exit_button, player_color, bot_color
):
    # Draw panel background
    pygame.draw.rect(screen, GRAY, (BOARD_WIDTH, 0, PANEL_WIDTH, TOTAL_HEIGHT))

    # Draw turn information or winner
    font = pygame.font.Font(None, 36)
    if board.winner:
        info_text = board.winner
        text_color = RED if board.winner.startswith("Red") else BLACK
    else:
        current_turn = "Red" if board.red_turn else "Black"
        info_text = f"{current_turn}'s Turn"
        text_color = RED if board.red_turn else BLACK

    info_surface = font.render(info_text, True, text_color)
    screen.blit(info_surface, (BOARD_WIDTH + 20, 50))

    # Draw player and bot color information
    player_text = f"Player: {'Red' if player_color == RED else 'Black'}"
    bot_text = f"Bot: {'Red' if bot_color == RED else 'Black'}"
    player_surface = font.render(player_text, True, BLACK)
    bot_surface = font.render(bot_text, True, BLACK)
    screen.blit(player_surface, (BOARD_WIDTH + 20, 100))
    screen.blit(bot_surface, (BOARD_WIDTH + 20, 140))

    # Draw buttons
    new_game_button.draw(screen)
    exit_button.draw(screen)


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def handle_events(board, new_game_button, exit_button, player_color):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, False  # Signal to exit the game

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[0] < BOARD_WIDTH:  # Click is on the game board
                if not board.winner and board.red_turn == (player_color == RED):
                    row, col = get_row_col_from_mouse(pos)
                    move_made = board.select(row, col)
                    if move_made:
                        return (
                            True,
                            True,
                        )  # Signal that a move was made and it's bot's turn
            else:  # Click is on the info panel
                if new_game_button.is_clicked(pos):
                    return True, None  # Signal to start a new game
                elif exit_button.is_clicked(pos):
                    return False, False  # Signal to exit the game

    return True, False  # Continue game, no special action needed


def main():
    board = Board()
    new_game_button = Button(BOARD_WIDTH + 20, 200, 160, 50, "New Game", GREEN, BLACK)
    exit_button = Button(BOARD_WIDTH + 20, 270, 160, 50, "Exit", RED, WHITE)
    from bot import Bot

    bot = Bot()  # Create a bot with random color
    player_color = RED if bot.color == BLACK else BLACK

    running = True
    bot_turn = bot.color == RED  # Start with bot's turn if it's red

    while running:
        if not bot_turn:
            running, bot_turn = handle_events(
                board, new_game_button, exit_button, player_color
            )
            if bot_turn is None:  # New game requested
                board = Board()
                bot = Bot()  # Create a new bot with random color
                player_color = RED if bot.color == BLACK else BLACK
                bot_turn = bot.color == RED
                continue

        if bot_turn and not board.winner:
            # Display "Bot is thinking..." message
            screen.fill(WHITE)
            board.draw(screen)
            font = pygame.font.Font(None, 36)
            text = font.render("Bot is thinking...", True, BLACK)
            text_rect = text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
            screen.blit(text, text_rect)
            draw_info_panel(
                screen, board, new_game_button, exit_button, player_color, bot.color
            )
            pygame.display.flip()

            # Let the bot make its move
            bot_move = bot.get_move(board)
            if bot_move is not None:
                bot_piece, bot_move_coords = bot_move
                board.select(bot_piece.row, bot_piece.col)
                board.select(bot_move_coords[0], bot_move_coords[1])
            else:
                # Bot has no valid moves, end the game
                board.winner = f"{'Red' if player_color == RED else 'Black'} wins!"
            bot_turn = False

        screen.fill(WHITE)
        board.draw(screen)

        if not board.winner:
            board.check_win()
        else:
            # Game has ended, display winner
            font = pygame.font.Font(None, 72)
            if (board.winner == "Red wins!" and player_color == RED) or (
                board.winner == "Black wins!" and player_color == BLACK
            ):
                text = font.render("You Win!", True, player_color)
            else:
                text = font.render("Bot Wins!", True, bot.color)
            text_rect = text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
            screen.blit(text, text_rect)

        draw_info_panel(
            screen, board, new_game_button, exit_button, player_color, bot.color
        )
        pygame.display.flip()

        # Add a small delay to reduce CPU usage
        pygame.time.delay(50)

        # Handle events during bot's turn (only for quitting or new game)
        if bot_turn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if new_game_button.is_clicked(pos):
                        board = Board()
                        bot = Bot()
                        player_color = RED if bot.color == BLACK else BLACK
                        bot_turn = bot.color == RED
                    elif exit_button.is_clicked(pos):
                        running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
