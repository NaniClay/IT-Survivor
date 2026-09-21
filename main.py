import pygame
from settings import *
from src.player import Player
from src.enemy import Enemy


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player((WIDTH // 2, HEIGHT // 2))
    enemies = pygame.sprite.Group(Enemy((100, 100), player))
    all_sprites = pygame.sprite.Group(player, *enemies)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # segundos desde el frame anterior

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        all_sprites.update(dt)

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()