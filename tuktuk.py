import pygame
import platform
import asyncio
from src.game_logic import main

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init(frequency=44100, buffer=512)
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())