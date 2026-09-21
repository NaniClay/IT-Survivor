import pygame
from settings import *
from src.player import Player
from src.spawner import Spawner


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player((WIDTH // 2, HEIGHT // 2))
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    spawner = Spawner(player, enemies, all_sprites)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        spawner.update(dt)
        all_sprites.update(dt)

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()