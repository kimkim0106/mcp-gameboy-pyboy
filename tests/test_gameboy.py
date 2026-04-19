"""Tests for the GameBoyEmulator wrapper around PyBoy."""

import base64
import io

import pytest
from PIL import Image

from mcp_gameboy.gameboy import GameBoyEmulator


def _decode_png(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def test_cartridge_title_not_empty(emu: GameBoyEmulator):
    title = emu.cartridge_title
    assert title and title.strip(), "cartridge_title should fall back to ROM stem when header empty"


def test_cartridge_title_fallback_on_blank_header(rom_path: str):
    emu = GameBoyEmulator(rom_path)

    class _StubPyBoy:
        cartridge_title = "   "

        def stop(self):
            pass

    emu.pyboy.stop()
    emu.pyboy = _StubPyBoy()
    assert emu.cartridge_title == emu.rom_path.stem


def test_tick_advances_frame_count(emu: GameBoyEmulator):
    before = emu.frame_count
    emu.tick(60)
    assert emu.frame_count == before + 60


def test_current_fps_positive_after_ticks(emu: GameBoyEmulator):
    emu.tick(120)
    # Force a measurable dt between the two calls used internally.
    import time

    time.sleep(0.05)
    emu.tick(10)
    fps = emu.current_fps
    assert fps > 0


def test_memory_read_write_roundtrip(emu: GameBoyEmulator):
    # 0xC000 is WRAM - freely writable
    emu.set_memory(0xC000, 0x42)
    assert emu.get_memory(0xC000) == 0x42

    emu.set_memory(0xC000, 0xFF)
    assert emu.get_memory(0xC000) == 0xFF


def test_memory_range_length(emu: GameBoyEmulator):
    values = emu.get_memory_range(0xC000, 16)
    assert isinstance(values, list)
    assert len(values) == 16
    assert all(0 <= v <= 0xFF for v in values)


def test_memory_range_reflects_writes(emu: GameBoyEmulator):
    for i in range(8):
        emu.set_memory(0xC100 + i, i * 0x11)
    values = emu.get_memory_range(0xC100, 8)
    assert values == [0, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77]


def test_get_screen_image_is_valid_png(emu: GameBoyEmulator):
    emu.tick(60)
    b64 = emu.get_screen_image()
    img = _decode_png(b64)
    # Wrapper scales Game Boy 160x144 up by 2x
    assert img.size == (320, 288)
    assert img.format == "PNG"


def test_get_screen_changes_between_frames(emu: GameBoyEmulator):
    emu.tick(30)
    first = emu.get_screen_image()
    emu.tick(120)
    second = emu.get_screen_image()
    # PyBoy's default ROM animates, so successive screens should differ.
    assert first != second, "Screen capture looks cached between ticks"


def test_save_and_load_state_restore_memory(emu: GameBoyEmulator):
    emu.tick(60)
    emu.set_memory(0xC200, 0xAB)
    emu.save_state(0)

    emu.tick(60)
    emu.set_memory(0xC200, 0xCD)
    assert emu.get_memory(0xC200) == 0xCD

    emu.load_state(0)
    assert emu.get_memory(0xC200) == 0xAB


def test_load_state_missing_slot_raises(emu: GameBoyEmulator):
    with pytest.raises(ValueError):
        emu.load_state(5)


def test_save_screenshot_writes_png(emu: GameBoyEmulator, tmp_path):
    emu.tick(60)
    out = tmp_path / "screen.png"
    returned = emu.save_screenshot(str(out))
    assert out.exists()
    assert str(out.resolve()) == returned
    with Image.open(out) as img:
        assert img.format == "PNG"
        assert img.size == (320, 288)


def test_get_sprite_fields(emu: GameBoyEmulator):
    emu.tick(60)
    info = emu.get_sprite(0)
    assert set(info.keys()) == {
        "x",
        "y",
        "tile_identifier",
        "on_screen",
        "x_flip",
        "y_flip",
        "palette",
        "bg_priority",
    }
    assert isinstance(info["on_screen"], bool)
    assert isinstance(info["x_flip"], bool)


def test_get_tile_is_valid_png(emu: GameBoyEmulator):
    emu.tick(60)
    b64 = emu.get_tile(0)
    img = _decode_png(b64)
    assert img.size == (8, 8)
    assert img.format == "PNG"


def test_set_emulation_speed_accepts_zero(emu: GameBoyEmulator):
    # Should not raise for the documented "unlimited" speed.
    emu.set_emulation_speed(0)
    emu.set_emulation_speed(1)
    emu.tick(10)
