"""소년 이동 실습: 방향키를 누르는 동안 이동한다."""

import pico2d

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024


def main():
    pico2d.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    running = True
    while running:
        for event in pico2d.get_events():
            if event.type == pico2d.SDL_QUIT:
                running = False
        pico2d.clear_canvas()
        pico2d.update_canvas()
        pico2d.delay(0.01)
    pico2d.close_canvas()


if __name__ == "__main__":
    main()
