"""PyBoy wrapper for MCP server."""

import base64
import io
import time
from pathlib import Path
from typing import Dict

from PIL import Image
from pyboy import PyBoy


class GameBoyEmulator:
    """Wrapper class for PyBoy emulator."""

    def __init__(self, rom_path: str):
        """Initialize the emulator with a ROM.

        Args:
            rom_path: Path to the ROM file
        """
        self.rom_path = Path(rom_path)
        self.pyboy = PyBoy(
            str(rom_path),
            window="null",  # Headless mode
            debug=False,
            bootrom=None,
        )
        self.pyboy.set_emulation_speed(0)  # Run at max speed
        self.save_states: Dict[int, bytes] = {}
        self._start_time = time.monotonic()
        self._last_fps_time = self._start_time
        self._last_fps_frame = 0

    def tick(self, frames: int = 1) -> None:
        """Advance emulation by specified frames.

        Args:
            frames: Number of frames to advance
        """
        self.pyboy.tick(frames)

    def press_button(self, button: str) -> None:
        """Press a button.

        Args:
            button: Button name (a, b, start, select, up, down, left, right)
        """
        self.pyboy.button_press(button)

    def release_button(self, button: str) -> None:
        """Release a button.

        Args:
            button: Button name (a, b, start, select, up, down, left, right)
        """
        self.pyboy.button_release(button)

    def get_screen_image(self) -> str:
        """Get current screen as base64-encoded PNG.

        Returns:
            Base64-encoded PNG image data
        """
        # screen.image shares the backing buffer; copy to snapshot the current frame
        screen_image = self.pyboy.screen.image.copy()

        # Scale up for better visibility (Game Boy is 160x144)
        scaled_image = screen_image.resize((320, 288), Image.NEAREST)

        buffer = io.BytesIO()
        scaled_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def save_state(self, slot: int) -> None:
        """Save current state to slot.

        Args:
            slot: Save slot number (0-9)
        """
        state_file = io.BytesIO()
        self.pyboy.save_state(state_file)
        self.save_states[slot] = state_file.getvalue()

    def load_state(self, slot: int) -> None:
        """Load state from slot.

        Args:
            slot: Save slot number (0-9)
        """
        if slot not in self.save_states:
            raise ValueError(f"No save state in slot {slot}")

        state_file = io.BytesIO(self.save_states[slot])
        self.pyboy.load_state(state_file)

    @property
    def cartridge_title(self) -> str:
        """Get the game title from ROM header.

        Falls back to ROM filename stem when the cartridge header has no title.
        """
        title = (self.pyboy.cartridge_title or "").strip()
        return title or self.rom_path.stem

    def get_memory(self, address: int) -> int:
        """Read a byte from memory."""
        return self.pyboy.memory[address]

    def set_memory(self, address: int, value: int) -> None:
        """Write a byte to memory."""
        self.pyboy.memory[address] = value

    def get_memory_range(self, start: int, length: int) -> list[int]:
        """Read multiple bytes from memory."""
        values = self.pyboy.memory[start : start + length]
        return list(values)

    def save_screenshot(self, filename: str) -> str:
        """Save current screen to a PNG file.

        Args:
            filename: Name of the file to save

        Returns:
            Full path to the saved file
        """
        screen_image = self.pyboy.screen.image.copy()
        scaled_image = screen_image.resize((320, 288), Image.NEAREST)

        path = Path(filename).resolve()
        scaled_image.save(path, format="PNG")

        return str(path)

    def set_emulation_speed(self, speed: int) -> None:
        """Set emulation speed.

        Args:
            speed: 0 for unlimited, 1 for normal, 2+ for faster
        """
        self.pyboy.set_emulation_speed(speed)

    def get_sprite(self, sprite_index: int) -> dict:
        """Get sprite information.

        Args:
            sprite_index: Sprite index (0-39)

        Returns:
            Dict with sprite information
        """
        sprite = self.pyboy.get_sprite(sprite_index)
        return {
            "x": sprite.x,
            "y": sprite.y,
            "tile_identifier": sprite.tile_identifier,
            "on_screen": sprite.on_screen,
            "x_flip": sprite.attr_x_flip,
            "y_flip": sprite.attr_y_flip,
            "palette": sprite.attr_palette_number,
            "bg_priority": sprite.attr_obj_bg_priority,
        }

    def get_tile(self, tile_id: int) -> str:
        """Get tile data as base64.

        Args:
            tile_id: Tile identifier (0-383)

        Returns:
            Base64 encoded tile image
        """
        tile = self.pyboy.get_tile(tile_id)
        buffer = io.BytesIO()
        tile.image().save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    @property
    def frame_count(self) -> int:
        """Total number of frames the emulator has advanced."""
        return self.pyboy.frame_count

    @property
    def current_fps(self) -> float:
        """FPS measured between successive calls; falls back to lifetime average."""
        now = time.monotonic()
        current_frame = self.pyboy.frame_count
        dt = now - self._last_fps_time
        df = current_frame - self._last_fps_frame

        if dt >= 0.05 and df > 0:
            fps = df / dt
            self._last_fps_time = now
            self._last_fps_frame = current_frame
            return fps

        lifetime = now - self._start_time
        return current_frame / lifetime if lifetime > 0 else 0.0

    def __del__(self):
        """Clean up PyBoy instance."""
        if hasattr(self, "pyboy"):
            self.pyboy.stop()
