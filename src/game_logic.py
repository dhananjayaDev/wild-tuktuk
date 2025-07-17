import pygame
import asyncio
import random
from src.constants import *
from src.game_state import GameState
from src.sound_manager import SoundManager
from src.game_objects import TukTuk, Vehicle

# Global game objects
screen = None
clock = None
font = None
medium_font = None
small_font = None
tiny_font = None
game_state = None
sound_manager = None
tuktuk = None
vehicles = []
spawn_timer = 0

def init_globals():
    global screen, clock, font, medium_font, small_font, tiny_font, game_state, sound_manager
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Wrong Lane TukTuk - Progressive Levels")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 48)
    medium_font = pygame.font.SysFont('Arial', 32)
    small_font = pygame.font.SysFont('Arial', 24)
    tiny_font = pygame.font.SysFont('Arial', 18)
    game_state = GameState()
    sound_manager = SoundManager()

def setup():
    global tuktuk, vehicles, spawn_timer
    game_state.reset()
    tuktuk = TukTuk()
    vehicles = []
    spawn_timer = 0
    sound_manager.stop('win')
    sound_manager.stop('lose')
    sound_manager.play('environment', loops=-1)

def spawn_vehicle():
    global spawn_timer
    current_level = LEVELS[game_state.level]
    spawn_timer += 1
    if spawn_timer >= current_level["spawn_frequency"]:
        spawn_timer = 0
        y_position = -VEHICLE_HEIGHT
        lanes = [0, 1, 2, 3]
        random.shuffle(lanes)
        blocked = lanes[:current_level["vehicles_per_spawn"]]
        for lane in blocked:
            vehicles.append(Vehicle(lane, current_level["vehicle_speed"], y_position))
            y_position -= current_level["min_gap"]

def check_level_progression():
    current_level = LEVELS[game_state.level]
    if game_state.times_reached_top >= current_level["required_top_reaches"]:
        if game_state.level < 3:
            game_state.level += 1
            game_state.times_reached_top = 0
            sound_manager.play('win')
        else:
            game_state.won = True
            sound_manager.play('win')

def draw_dashed_line(offset):
    y = offset % (DASH_LENGTH + DASH_GAP)
    while y < WINDOW_HEIGHT:
        for i in range(1, 4):
            pygame.draw.line(screen, LINE_COLOR,
                           (ROAD_X + i * LANE_WIDTH, y),
                           (ROAD_X + i * LANE_WIDTH, y + DASH_LENGTH), 5)
        y += DASH_LENGTH + DASH_GAP

def draw_ui():
    level_text = small_font.render(f"Level: {game_state.level}", True, DARK_GRAY)
    screen.blit(level_text, (10, 10))
    progress_text = small_font.render(
        f"Reaches: {game_state.times_reached_top}/{LEVELS[game_state.level]['required_top_reaches']}", 
        True, DARK_GRAY
    )
    screen.blit(progress_text, (10, 50))
    high_score_text = small_font.render(f"High Score: {game_state.high_score}", True, DARK_GRAY)
    screen.blit(high_score_text, (10, 90))
    level_indicator = pygame.Rect(WINDOW_WIDTH - 30, 10, 20, 20)
    pygame.draw.rect(screen, LEVELS[game_state.level]["color"], level_indicator)
    controls_text = tiny_font.render("H: Honk | M: Music | P: Pause | Q: Quit | R: Restart", True, DARK_GRAY)
    # Place controls hint to the right of the road, with padding
    controls_x = ROAD_X + ROAD_WIDTH + 20
    controls_y = WINDOW_HEIGHT - controls_text.get_height() - 20
    screen.blit(controls_text, (controls_x, controls_y))

def draw_instructions():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    title = medium_font.render("WRONG LANE TUKTUK", True, WHITE)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
    instructions = [
        "Drive your tuk-tuk against traffic!",
        "Use arrow keys to move",
        "H to honk, M to toggle music",
        "Avoid hitting other vehicles",
        "Reach the top to progress",
        "",
        "Press any arrow key to start",
        "Or R to restart later",
        "Q to quit"
    ]
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, WHITE)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 180 + i*30))

def draw_game_state():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    if game_state.game_over:
        msg = medium_font.render("GAME OVER", True, RED)
        restart_msg = small_font.render("Press R to restart or Q to quit", True, WHITE)
    elif game_state.won:
        msg = medium_font.render("YOU WIN!", True, GREEN)
        restart_msg = small_font.render("Press R to restart or Q to quit", True, WHITE)
    else:
        msg = medium_font.render("PAUSED", True, YELLOW)
        restart_msg = small_font.render("Press P to continue or Q to quit", True, WHITE)
    screen.blit(msg, (WINDOW_WIDTH//2 - msg.get_width()//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(restart_msg, (WINDOW_WIDTH//2 - restart_msg.get_width()//2, WINDOW_HEIGHT//2 + 10))

async def main():
    global tuktuk, vehicles, spawn_timer
    init_globals()
    setup()
    offset = 0
    spawn_timer = 0
    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_state.game_over or game_state.paused or game_state.show_instructions or game_state.won):
                    setup()
                elif event.key == pygame.K_p and not game_state.game_over and not game_state.show_instructions:
                    game_state.paused = not game_state.paused
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return
                elif event.key == HONK_KEY:
                    sound_manager.play('tuktuk_honk')
                elif event.key == MUSIC_TOGGLE_KEY:
                    sound_manager.toggle_music()
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT) and game_state.show_instructions:
                    game_state.show_instructions = False
        screen.fill(BORDER_COLOR)
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_X, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        draw_dashed_line(offset)
        if not game_state.show_instructions:
            tuktuk.draw(screen)
            for vehicle in vehicles:
                vehicle.draw(screen)
                vehicle.check_honk(tuktuk, sound_manager)
        draw_ui()
        if game_state.show_instructions:
            draw_instructions()
        elif game_state.paused or game_state.game_over or game_state.won:
            draw_game_state()
        elif not game_state.paused and not game_state.game_over and not game_state.won:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT]:
                dx -= TUKTUK_SPEED
            if keys[pygame.K_RIGHT]:
                dx += TUKTUK_SPEED
            if keys[pygame.K_UP]:
                dy -= TUKTUK_SPEED
            if keys[pygame.K_DOWN]:
                dy += TUKTUK_SPEED
            tuktuk.move(dx, dy)
            spawn_vehicle()
            to_remove = []
            for vehicle in vehicles:
                vehicle.move()
                if vehicle.off_screen():
                    to_remove.append(vehicle)
                if tuktuk.rect.colliderect(vehicle.rect):
                    game_state.game_over = True
                    game_state.high_score = max(game_state.high_score, game_state.times_reached_top)
                    sound_manager.play('lose')
            if tuktuk.y <= 0:
                game_state.times_reached_top += 1
                tuktuk.y = WINDOW_HEIGHT - tuktuk.height - 20
                check_level_progression()
            for v in to_remove:
                vehicles.remove(v)
        pygame.display.flip()
        clock.tick(FPS)
        if not game_state.show_instructions and not game_state.paused and not game_state.game_over and not game_state.won:
            offset += LEVELS[game_state.level]["vehicle_speed"]
        await asyncio.sleep(0)
