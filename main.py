import pygame
import sys

from bot import Bot
from components.board import Board
from components.button import Button
from constants import (
    PANEL_WIDTH,
    SQUARE_SIZE,
    TOTAL_WIDTH,
    TOTAL_HEIGHT,
    WHITE,
    BLACK,
    RED,
    GREEN,
    GRAY,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption("Sun Chess")


def draw_info_panel(
    _screen, board, new_game_button, exit_button, player_color, bot_color
):
    # Draw panel background
    pygame.draw.rect(_screen, GRAY, (BOARD_WIDTH, 0, PANEL_WIDTH, TOTAL_HEIGHT))

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
    _screen.blit(info_surface, (BOARD_WIDTH + 20, 50))

    # Draw player and bot color information
    player_text = f"Player: {'Red' if player_color == RED else 'Black'}"
    bot_text = f"Bot: {'Red' if bot_color == RED else 'Black'}"
    player_surface = font.render(player_text, True, BLACK)
    bot_surface = font.render(bot_text, True, BLACK)
    _screen.blit(player_surface, (BOARD_WIDTH + 20, 100))
    _screen.blit(bot_surface, (BOARD_WIDTH + 20, 140))

    # Draw buttons
    new_game_button.draw(_screen)
    exit_button.draw(_screen)


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
            text = font.render("Bot is thinking...", True, GRAY)
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
                text = font.render("You Win!", True, WHITE)
            else:
                text = font.render("Bot Wins!", True, WHITE)
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
