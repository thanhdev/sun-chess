import pygame

from constants import SQUARE_SIZE, YELLOW, RED


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

    def draw(self, _screen):
        radius = SQUARE_SIZE // 2 - 10
        pygame.draw.circle(_screen, self.color, (self.x, self.y), radius)

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
            pygame.draw.polygon(_screen, YELLOW, points)
        else:  # Number piece
            font = pygame.font.Font(None, 36)
            text = font.render(
                str(self.value), True, YELLOW if self.color == RED else RED
            )
            text_rect = text.get_rect(center=(self.x, self.y))
            _screen.blit(text, text_rect)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()
