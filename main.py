import pygame
from settings import *
from src.player import Player
from src.spawner import Spawner
from src.weapons import AutoShooter
from src.ui import UI


def new_game():
    player = Player((WIDTH // 2, HEIGHT // 2))
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    spawner = Spawner(player, enemies, all_sprites)
    shooter = AutoShooter(player, enemies, bullets, all_sprites)
    return player, enemies, bullets, all_sprites, spawner, shooter


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    ui = UI()

    player, enemies, bullets, all_sprites, spawner, shooter = new_game()
    elapsed = 0
    bugs_fixed = 0
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
                    player, enemies, bullets, all_sprites, spawner, shooter = new_game()
                    elapsed = 0
                    bugs_fixed = 0
                    game_over = False

        if not game_over:
            elapsed += dt
            spawner.update(dt)
            shooter.update(dt)
            all_sprites.update(dt)

            # balas vs enemigos (la bala se destruye al pegar)
            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                enemy = hit_enemies[0]
                if enemy.take_damage(BULLET_DAMAGE):
                    enemy.kill()
                    bugs_fixed += 1

            # enemigos vs jugador
            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                 if player.take_damage(enemy.damage):
                    enemy.kill()

            if player.hp <= 0:
                game_over = True

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        ui.draw_hud(screen, player, elapsed, bugs_fixed)
        if game_over:
            ui.draw_game_over(screen, elapsed, bugs_fixed)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()