"""소년 이동 실습: 방향키를 누르는 동안 이동한다."""

from dataclasses import dataclass
from pathlib import Path

import pico2d

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
FRAME_WIDTH = 100
FRAME_HEIGHT = 100
FRAME_COUNT = 8
ARROW_KEYS = {pico2d.SDLK_LEFT, pico2d.SDLK_RIGHT, pico2d.SDLK_UP, pico2d.SDLK_DOWN}
RESOURCE_DIR = Path(__file__).resolve().parent.parent / "Resourse"


@dataclass
class CharacterState:
    x: float = SCREEN_WIDTH / 2
    y: float = SCREEN_HEIGHT / 2
    facing: str = "RIGHT"


def main():
    pico2d.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    try:
        background = pico2d.load_image(str(RESOURCE_DIR / "TUK_GROUND.png"))
        character = pico2d.load_image(str(RESOURCE_DIR / "animation_sheet.png"))
        state = CharacterState()
        pressed_keys = set()
        running = True
        while running:
            for event in pico2d.get_events():
                if event.type == pico2d.SDL_QUIT:
                    running = False
                elif event.type == pico2d.SDL_KEYDOWN and event.key in ARROW_KEYS:
                    pressed_keys.add(event.key)
                elif event.type == pico2d.SDL_KEYUP:
                    pressed_keys.discard(event.key)
            pico2d.clear_canvas()
            background.draw(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
            character.clip_draw(0, character.h - FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT,
                                state.x, state.y)
            pico2d.update_canvas()
            pico2d.delay(0.01)
    finally:
        pico2d.close_canvas()


if __name__ == "__main__":
    main()
