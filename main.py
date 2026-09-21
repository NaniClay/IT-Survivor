import pygame
from settings import *
from src.player import Player
from src.spawner import Spawner
from src.weapons import AutoShooter
from src.abilities import CoffeeBoost, GitRollback, Refactor
from src import leaderboard
from src.ui import UI


def new_game():
    player = Player((WIDTH // 2, HEIGHT // 2))
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    spawner = Spawner(player, enemies, all_sprites)
    shooter = AutoShooter(player, enemies, bullets, all_sprites)
    coffee = CoffeeBoost()
    rollback = GitRollback()
    refactor = Refactor()
    return (player, enemies, bullets, all_sprites,
            spawner, shooter, coffee, rollback, refactor)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    ui = UI()

    (player, enemies, bullets, all_sprites,
     spawner, shooter, coffee, rollback, refactor) = new_game()
    elapsed = 0
    bugs_fixed = 0
    game_over = False
    entering_name = False
    name_text = ""
    score = 0
    entries = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --- escribiendo el nombre para el leaderboard ---
                if game_over and entering_name:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        entries = leaderboard.add_entry(name_text.strip(), score, elapsed, bugs_fixed)
                        entering_name = False
                    elif event.key == pygame.K_ESCAPE:
                        entries = leaderboard.load()
                        entering_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(name_text) < NAME_MAX_LEN:
                        name_text += event.unicode

                # --- controles normales ---
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game_over:
                    coffee.activate()
                elif event.key == pygame.K_g and not game_over:
                    rollback.activate(player)
                elif event.key == pygame.K_e and not game_over:
                    bugs_fixed += refactor.activate(player, enemies)
                elif event.key == pygame.K_r and game_over:
                    (player, enemies, bullets, all_sprites,
                     spawner, shooter, coffee, rollback, refactor) = new_game()
                    elapsed = 0
                    bugs_fixed = 0
                    game_over = False
                    entering_name = False
                    name_text = ""

        if not game_over:
            elapsed += dt

            coffee.update(dt)
            refactor.update(dt)
            player.speed_mult = COFFEE_SPEED_MULT if coffee.active else 1
            player.boosted = coffee.active
            shooter.fire_mult = COFFEE_FIRE_MULT if coffee.active else 1

            spawner.update(dt)
            shooter.update(dt)
            all_sprites.update(dt)
            rollback.update(dt, player)

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
                score = leaderboard.calc_score(elapsed, bugs_fixed)
                if leaderboard.qualifies(score):
                    entering_name = True
                    name_text = ""
                else:
                    entries = leaderboard.load()

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        ui.draw_hud(screen, player, elapsed, bugs_fixed)
        ui.draw_coffee(screen, coffee)
        ui.draw_rollback(screen, rollback)
        ui.draw_refactor(screen, refactor)
        if game_over:
            ui.draw_game_over(screen, elapsed, bugs_fixed, score,
                              entering_name, name_text, entries)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()