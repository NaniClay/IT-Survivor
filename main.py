import pygame
from settings import *
from src.player import Player
from src.spawner import Spawner
from src.ui import UI


def new_game():
    player = Player((WIDTH // 2, HEIGHT // 2))
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    spawner = Spawner(player, enemies, all_sprites)
    return player, enemies, all_sprites, spawner


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    ui = UI()

    player, enemies, all_sprites, spawner = new_game()
    elapsed = 0
    game_over = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    player, enemies, all_sprites, spawner = new_game()
                    elapsed = 0
                    game_over = False

        if not game_over:
            elapsed += dt
            spawner.update(dt)
            all_sprites.update(dt)

            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                if player.take_damage(ENEMY_DAMAGE):
                    enemy.kill()   # el bug se "gasta" al pegarte

            if player.hp <= 0:
                game_over = True

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        ui.draw_hud(screen, player, elapsed)
        if game_over:
            ui.draw_game_over(screen, elapsed)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()