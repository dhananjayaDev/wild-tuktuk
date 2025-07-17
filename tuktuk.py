import pygame
import platform
import asyncio
from src.game_logic import main
import os

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init(frequency=44100, buffer=512)
    icon_path = "assets/tuktuk.png"
    if os.path.exists(icon_path):
        icon_surface = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_surface)
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())