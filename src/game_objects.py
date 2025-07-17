import pygame
import os
import random
from src.constants import (
    TUKTUK_WIDTH, TUKTUK_HEIGHT, VEHICLE_WIDTH, VEHICLE_HEIGHT,
    ROAD_X, LANE_WIDTH, WINDOW_HEIGHT, ROAD_WIDTH, GREEN, RED, COLLISION_DISTANCE
)
from src.utils import resource_path

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
            path = resource_path(os.path.join("assets", "tuktuk.png"))
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

    def draw(self, screen):
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
            path = resource_path(os.path.join("assets", f"car{car_num:02d}.png"))
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Error loading car image: {e}")
        return None

    def move(self):
        self.y += self.speed
        self.rect.y = self.y

    def check_honk(self, tuktuk, sound_manager):
        # Honk when TukTuk is in front of the vehicle (vehicle is approaching TukTuk)
        if (abs(self.x - tuktuk.x) < 30 and 0 < tuktuk.y - self.y < COLLISION_DISTANCE):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_honk_time > 2000:  # 2 second cooldown
                sound_manager.play('vehicle_honk')
                self.last_honk_time = current_time

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)

    def off_screen(self):
        return self.y > WINDOW_HEIGHT
