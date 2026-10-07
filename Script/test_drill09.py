"""실행: python -m unittest discover -s Script -p test_drill09.py -v"""

import importlib.util
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location(
    "drill09", Path(__file__).with_name("drill-09_character_move.py")
)
game = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = game
spec.loader.exec_module(game)
p = game.pico2d


class CharacterMovementTests(unittest.TestCase):
    def test_four_directions(self):
        for key, dx, dy in ((p.SDLK_RIGHT, 1, 0), (p.SDLK_LEFT, -1, 0),
                            (p.SDLK_UP, 0, 1), (p.SDLK_DOWN, 0, -1)):
            with self.subTest(key=key):
                state = game.CharacterState()
                game.update_character(state, {key}, 0.4)
                self.assertAlmostEqual(state.x, game.SCREEN_WIDTH / 2 + dx * 100)
                self.assertAlmostEqual(state.y, game.SCREEN_HEIGHT / 2 + dy * 100)
                self.assertEqual(state.mode, "MOVE")

    def test_equal_elapsed_time_gives_equal_distance(self):
        single, multiple = game.CharacterState(), game.CharacterState()
        game.update_character(single, {p.SDLK_RIGHT}, 1.0)
        for _ in range(10):
            game.update_character(multiple, {p.SDLK_RIGHT}, 0.1)
        self.assertAlmostEqual(single.x, multiple.x)

    def test_diagonal_speed_matches_single_axis(self):
        state = game.CharacterState()
        game.update_character(state, {p.SDLK_UP, p.SDLK_RIGHT}, 0.4)
        distance = math.hypot(state.x - game.SCREEN_WIDTH / 2,
                              state.y - game.SCREEN_HEIGHT / 2)
        self.assertAlmostEqual(distance, 100)

    def test_vertical_and_opposite_inputs_keep_facing(self):
        state = game.CharacterState()
        game.update_character(state, {p.SDLK_LEFT}, 0.1)
        game.update_character(state, {p.SDLK_UP}, 0.1)
        self.assertEqual(state.facing, "LEFT")
        before = (state.x, state.y)
        game.update_character(state, game.ARROW_KEYS, 0.1)
        self.assertEqual((state.x, state.y), before)
        self.assertEqual((state.mode, state.facing), ("IDLE", "LEFT"))

    def test_all_corners_and_return_from_boundary(self):
        for horizontal in (p.SDLK_LEFT, p.SDLK_RIGHT):
            for vertical in (p.SDLK_DOWN, p.SDLK_UP):
                with self.subTest(horizontal=horizontal, vertical=vertical):
                    state = game.CharacterState()
                    game.update_character(state, {horizontal, vertical}, 100)
                    expected_x = 50 if horizontal == p.SDLK_LEFT else 1230
                    expected_y = 50 if vertical == p.SDLK_DOWN else 974
                    self.assertEqual((state.x, state.y), (expected_x, expected_y))
                    self.assertEqual(state.mode, "MOVE")
                    reverse = p.SDLK_RIGHT if horizontal == p.SDLK_LEFT else p.SDLK_LEFT
                    game.update_character(state, {reverse}, 0.1)
                    self.assertNotEqual(state.x, expected_x)

    def test_idle_animation_changes_frame_without_moving(self):
        state = game.CharacterState()
        position = (state.x, state.y)
        game.update_character(state, set(), 0.25)
        game.update_animation(state, 0.25)
        self.assertEqual(state.frame, 1)
        self.assertEqual((state.x, state.y), position)
        game.update_animation(state, 1.4)
        self.assertEqual(state.frame, 0)

    def test_state_and_direction_changes_reset_animation(self):
        state = game.CharacterState(frame=5, animation_time=0.05)
        game.update_character(state, {p.SDLK_RIGHT}, 0)
        self.assertEqual((state.frame, state.animation_time), (0, 0))
        state.frame = 4
        game.update_character(state, {p.SDLK_LEFT}, 0)
        self.assertEqual(state.frame, 0)
        state.frame = 3
        game.update_character(state, set(), 0)
        self.assertEqual(state.frame, 0)

    def test_key_release_keeps_other_key_and_then_stops(self):
        keys = set()
        events = [SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_RIGHT),
                  SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_UP),
                  SimpleNamespace(type=p.SDL_KEYUP, key=p.SDLK_RIGHT)]
        with patch.object(p, "get_events", return_value=events), \
                patch.object(p, "SDL_GetKeyboardFocus", return_value=True):
            self.assertTrue(game.handle_events(keys))
        self.assertEqual(keys, {p.SDLK_UP})
        state = game.CharacterState()
        game.update_character(state, keys, 0.1)
        position = (state.x, state.y)
        with patch.object(p, "get_events", return_value=[
                SimpleNamespace(type=p.SDL_KEYUP, key=p.SDLK_UP)]), \
                patch.object(p, "SDL_GetKeyboardFocus", return_value=True):
            game.handle_events(keys)
        game.update_character(state, keys, 0.1)
        self.assertEqual((state.x, state.y), position)
        self.assertEqual(state.mode, "IDLE")

    def test_focus_loss_clears_input(self):
        keys = {p.SDLK_LEFT}
        with patch.object(p, "get_events", return_value=[]), \
                patch.object(p, "SDL_GetKeyboardFocus", return_value=None):
            game.handle_events(keys)
        self.assertEqual(keys, set())

    def test_render_selects_idle_and_move_rows_for_both_directions(self):
        background, character = Mock(), Mock(h=402)
        with patch.object(p, "clear_canvas"), patch.object(p, "update_canvas"):
            for mode, facing, source_y in (("IDLE", "RIGHT", 302),
                                           ("IDLE", "LEFT", 202),
                                           ("MOVE", "RIGHT", 102),
                                           ("MOVE", "LEFT", 2)):
                with self.subTest(mode=mode, facing=facing):
                    state = game.CharacterState(mode=mode, facing=facing, frame=7)
                    game.render(background, character, state)
                    character.clip_draw.assert_called_with(700, source_y, 100, 100,
                                                           state.x, state.y)

    def test_window_close_and_cleanup(self):
        with patch.object(p, "get_events", return_value=[SimpleNamespace(type=p.SDL_QUIT)]), \
                patch.object(p, "SDL_GetKeyboardFocus", return_value=True):
            self.assertFalse(game.handle_events(set()))
        with patch.object(p, "open_canvas"), \
                patch.object(p, "load_image", side_effect=RuntimeError("load failed")), \
                patch.object(p, "close_canvas") as close:
            with self.assertRaises(RuntimeError):
                game.main()
            close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
