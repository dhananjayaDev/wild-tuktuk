import pygame
import os
from src.constants import SOUNDS

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
