# Game constants
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
HONK_KEY = 104  # pygame.K_h
MUSIC_TOGGLE_KEY = 109  # pygame.K_m

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
    'tuktuk_honk': 'assets/sounds/tuktuk_honk.mp3',
    'vehicle_honk': 'assets/sounds/vehicle_honk.mp3',
    'win': 'assets/sounds/win.mp3',
    'lose': 'assets/sounds/lose.mp3'
}

# Level configurations (updated as per user request)
LEVELS = {
    1: {
        "vehicle_speed": 3,
        "spawn_frequency": 120,
        "vehicles_per_spawn": 2,
        "color": GREEN,
        "min_gap": 150,
        "required_top_reaches": 3,
        "completion_requirement": "Reach the top of the screen 3 times"
    },
    2: {
        "vehicle_speed": 4,
        "spawn_frequency": 80,
        "vehicles_per_spawn": 3,
        "color": YELLOW,
        "min_gap": 120,
        "required_top_reaches": 5,
        "completion_requirement": "Reach the top of the screen 5 times"
    },
    3: {
        "vehicle_speed": 5,
        "spawn_frequency": 50,
        "vehicles_per_spawn": 3,
        "color": RED,
        "min_gap": 90,
        "required_top_reaches": 20,
        "completion_requirement": "Reach the top of the screen 20 times (win)"
    }
}
