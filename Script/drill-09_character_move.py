"""소년 이동 실습: 방향키를 누르는 동안 이동한다."""

from pathlib import Path

import pico2d

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
FRAME_WIDTH = 100
FRAME_HEIGHT = 100
FRAME_COUNT = 8
RESOURCE_DIR = Path(__file__).resolve().parent.parent / "Resourse"


def main():
    pico2d.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    background = pico2d.load_image(str(RESOURCE_DIR / "TUK_GROUND.png"))
    character = pico2d.load_image(str(RESOURCE_DIR / "animation_sheet.png"))
    running = True
    while running:
        for event in pico2d.get_events():
            if event.type == pico2d.SDL_QUIT:
                running = False
        pico2d.clear_canvas()
        background.draw(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        character.clip_draw(0, character.h - FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT,
                            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pico2d.update_canvas()
        pico2d.delay(0.01)
    pico2d.close_canvas()


if __name__ == "__main__":
    main()
