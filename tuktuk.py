import pygame
import random
import platform
import asyncio
import os

# Initialize Pygame with optimized sound settings
pygame.init()
pygame.mixer.init(frequency=44100, buffer=512)  # Better sound performance

# ========== GAME CONSTANTS ==========
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ROAD_WIDTH = 360
ROAD_X = (WINDOW_WIDTH - ROAD_WIDTH) // 2
LANE_WIDTH = ROAD_WIDTH // 4
FPS = 60
DASH_LENGTH = 20
DASH_GAP = 20

# Vehicle dimensions
TUKTUK_WIDTH = 60
TUKTUK_HEIGHT = 100
VEHICLE_WIDTH = 60
VEHICLE_HEIGHT = 100

# Speeds
TUKTUK_SPEED = 5
BASE_VEHICLE_SPEED = 3

# Gameplay settings
COLLISION_DISTANCE = 150  # Distance for AI vehicles to honk at player
HONK_KEY = pygame.K_h  # Key for manual honking
MUSIC_TOGGLE_KEY = pygame.K_m  # Key to toggle music

# Colors
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 255, 204)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)
WHITE = (255, 255, 255)

# Sound file paths
SOUNDS = {
    'environment': 'assets/sounds/environment.mp3',
    'music': 'assets/sounds/music.mp3',
    'tuktuk_honk': 'assets/sounds/tuktuk_honk.wav',
    'vehicle_honk': 'assets/sounds/vehicle_honk.wav',
    'win': 'assets/sounds/win.mp3',
    'lose': 'assets/sounds/lose.mp3'
}

# ========== GAME SETUP ==========
# Create assets directory if it doesn't exist
if not os.path.exists('assets/sounds'):
    os.makedirs('assets/sounds')

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wrong Lane TukTuk - Progressive Levels")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 48)
medium_font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
tiny_font = pygame.font.SysFont('Arial', 18)

# ========== SOUND MANAGER ==========
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_on = False
        self.environment_on = True
        
        # Load all sounds with error handling
        for name, path in SOUNDS.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {path}")
                else:
                    print(f"Missing sound file: {path}")
                    # Create silent fallback
                    silent_sound = pygame.mixer.Sound(buffer=bytes([0]*1024))
                    silent_sound.set_volume(0)
                    self.sounds[name] = silent_sound
            except Exception as e:
                print(f"Error loading sound {name}: {e}")
                silent_sound = pygame.mixer.Sound(buffer=bytes([0]*1024))
                silent_sound.set_volume(0)
                self.sounds[name] = silent_sound
        
        # Set volumes
        self.set_volume('environment', 0.3)
        self.set_volume('music', 0.5)
        self.set_volume('tuktuk_honk', 0.7)
        self.set_volume('vehicle_honk', 0.6)
        self.set_volume('win', 1.0)
        self.set_volume('lose', 1.0)
        
        # Start ambient sound
        self.play('environment', loops=-1)

    def play(self, sound_name, loops=0):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play(loops)
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")

    def stop(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def set_volume(self, sound_name, volume):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.play('music', loops=-1)
        else:
            self.stop('music')

# ========== GAME STATE ==========
class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.game_over = False
        self.paused = False
        self.level = 1
        self.times_reached_top = 0
        self.high_score = 0
        self.show_instructions = True
        self.won = False

game_state = GameState()
sound_manager = SoundManager()

# ========== LEVEL CONFIGURATIONS ==========
LEVELS = {
    1: {
        "vehicle_speed": BASE_VEHICLE_SPEED,
        "spawn_frequency": 120,
        "vehicles_per_spawn": 2,
        "color": GREEN,
        "min_gap": 150,
        "required_top_reaches": 3
    },
    2: {
        "vehicle_speed": BASE_VEHICLE_SPEED + 1,
        "spawn_frequency": 80,
        "vehicles_per_spawn": 3,
        "color": YELLOW,
        "min_gap": 120,
        "required_top_reaches": 5
    },
    3: {
        "vehicle_speed": BASE_VEHICLE_SPEED + 2,
        "spawn_frequency": 50,
        "vehicles_per_spawn": 3,
        "color": RED,
        "min_gap": 90,
        "required_top_reaches": 999
    }
}

# ========== GAME OBJECTS ==========
class TukTuk:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.width = TUKTUK_WIDTH
        self.height = TUKTUK_HEIGHT
        self.x = ROAD_X + 2 * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = WINDOW_HEIGHT - self.height - 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_moving = False
        self.image = self.load_image()

    def load_image(self):
        try:
            path = os.path.join("assets", "tuktuk.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Error loading tuktuk image: {e}")
        return None

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(ROAD_X, min(self.x, ROAD_X + ROAD_WIDTH - self.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
        self.rect.x = self.x
        self.rect.y = self.y
        self.is_moving = dx != 0 or dy != 0

    def draw(self):
        if self.image:
            screen.blit(self.image, (self.rect))
        else:
            pygame.draw.rect(screen, GREEN, self.rect)

class Vehicle:
    def __init__(self, lane, speed, y=None):
        self.width = VEHICLE_WIDTH
        self.height = VEHICLE_HEIGHT
        self.lane = lane % 4
        self.x = ROAD_X + self.lane * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = -self.height if y is None else y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = speed
        self.last_honk_time = 0
        self.image = self.load_image()
        
    def load_image(self):
        try:
            car_num = random.randint(1, 6)
            path = os.path.join("assets", f"car{car_num:02d}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Error loading car image: {e}")
        return None

    def move(self):
        self.y += self.speed
        self.rect.y = self.y

    def check_honk(self, tuktuk):
        if (abs(self.x - tuktuk.x) < 30 and 0 < self.y - tuktuk.y < COLLISION_DISTANCE):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_honk_time > 2000:  # 2 second cooldown
                sound_manager.play('vehicle_honk')
                self.last_honk_time = current_time

    def draw(self):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)

    def off_screen(self):
        return self.y > WINDOW_HEIGHT

# ========== GAME FUNCTIONS ==========
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
    # Level and score info
    level_text = small_font.render(f"Level: {game_state.level}", True, DARK_GRAY)
    screen.blit(level_text, (10, 10))
    
    progress_text = small_font.render(
        f"Reaches: {game_state.times_reached_top}/{LEVELS[game_state.level]['required_top_reaches']}", 
        True, DARK_GRAY
    )
    screen.blit(progress_text, (10, 50))
    
    high_score_text = small_font.render(f"High Score: {game_state.high_score}", True, DARK_GRAY)
    screen.blit(high_score_text, (10, 90))
    
    # Level indicator
    level_indicator = pygame.Rect(WINDOW_WIDTH - 30, 10, 20, 20)
    pygame.draw.rect(screen, LEVELS[game_state.level]["color"], level_indicator)
    
    # Controls hint
    controls_text = tiny_font.render("H: Honk | M: Music | P: Pause | Q: Quit | R: Restart", True, DARK_GRAY)
    screen.blit(controls_text, (WINDOW_WIDTH - controls_text.get_width() - 10, 
                              WINDOW_HEIGHT - controls_text.get_height() - 10))

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

# ========== MAIN GAME LOOP ==========
async def main():
    global tuktuk, vehicles, spawn_timer
    
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
        
        # Draw the road and vehicles
        screen.fill(BORDER_COLOR)
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_X, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        draw_dashed_line(offset)
        
        if not game_state.show_instructions:
            tuktuk.draw()
            for vehicle in vehicles:
                vehicle.draw()
                vehicle.check_honk(tuktuk)
        
        draw_ui()
        
        if game_state.show_instructions:
            draw_instructions()
        elif game_state.paused or game_state.game_over or game_state.won:
            draw_game_state()
        elif not game_state.paused and not game_state.game_over and not game_state.won:
            # Game logic
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

# ========== RUN THE GAME ==========
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())