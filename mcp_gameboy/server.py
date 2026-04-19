"""MCP server for Game Boy emulation."""

import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent

from .gameboy import GameBoyEmulator

logger = logging.getLogger(__name__)

# Global emulator instance
emulator: Optional[GameBoyEmulator] = None

# Create MCP server
mcp = FastMCP("mcp-gameboy-pyboy")


@mcp.tool()
def load_rom(rom_path: str) -> list[TextContent]:
    """Load a Game Boy ROM file.
    
    Args:
        rom_path: Path to the ROM file (.gb or .gbc)
    """
    global emulator
    
    try:
        path = Path(rom_path).expanduser().resolve()
        if not path.exists():
            return [TextContent(type="text", text=f"ROM file not found: {rom_path}")]
        
        if path.suffix.lower() not in ['.gb', '.gbc']:
            return [TextContent(type="text", text="File must be a .gb or .gbc ROM")]
        
        emulator = GameBoyEmulator(str(path))
        return [TextContent(type="text", text=f"ROM loaded successfully: {path.name}")]
    except Exception as e:
        logger.error(f"Failed to load ROM: {e}")
        return [TextContent(type="text", text=f"Failed to load ROM: {str(e)}")]


@mcp.tool(structured_output=False)
def get_screen() -> list[TextContent | ImageContent]:
    """Get the current Game Boy screen as an image."""
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    try:
        image_data = emulator.get_screen_image()
        return [ImageContent(type="image", data=image_data, mimeType="image/png")]
    except Exception as e:
        logger.error(f"Failed to get screen: {e}")
        return [TextContent(type="text", text=f"Failed to get screen: {str(e)}")]


@mcp.tool()
def press_button(button: str) -> list[TextContent]:
    """Press a Game Boy button.
    
    Args:
        button: Button to press (a, b, start, select, up, down, left, right)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    valid_buttons = ["a", "b", "start", "select", "up", "down", "left", "right"]
    if button.lower() not in valid_buttons:
        return [TextContent(type="text", text=f"Invalid button. Must be one of: {', '.join(valid_buttons)}")]
    
    try:
        emulator.press_button(button.lower())
        return [TextContent(type="text", text=f"Pressed button: {button}")]
    except Exception as e:
        logger.error(f"Failed to press button: {e}")
        return [TextContent(type="text", text=f"Failed to press button: {str(e)}")]


@mcp.tool()
def release_button(button: str) -> list[TextContent]:
    """Release a Game Boy button.
    
    Args:
        button: Button to release (a, b, start, select, up, down, left, right)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    valid_buttons = ["a", "b", "start", "select", "up", "down", "left", "right"]
    if button.lower() not in valid_buttons:
        return [TextContent(type="text", text=f"Invalid button. Must be one of: {', '.join(valid_buttons)}")]
    
    try:
        emulator.release_button(button.lower())
        return [TextContent(type="text", text=f"Released button: {button}")]
    except Exception as e:
        logger.error(f"Failed to release button: {e}")
        return [TextContent(type="text", text=f"Failed to release button: {str(e)}")]


@mcp.tool()
def tick(frames: int = 1) -> list[TextContent]:
    """Advance the emulation by a number of frames.
    
    Args:
        frames: Number of frames to advance (default: 1)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if frames < 1:
        return [TextContent(type="text", text="Frames must be >= 1")]
    
    try:
        emulator.tick(frames)
        return [TextContent(type="text", text=f"Advanced {frames} frame(s)")]
    except Exception as e:
        logger.error(f"Failed to tick: {e}")
        return [TextContent(type="text", text=f"Failed to advance emulation: {str(e)}")]


@mcp.tool()
def save_state(slot: int = 0) -> list[TextContent]:
    """Save the current emulator state.
    
    Args:
        slot: Save state slot (0-9, default: 0)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= slot <= 9:
        return [TextContent(type="text", text="Slot must be between 0-9")]
    
    try:
        emulator.save_state(slot)
        return [TextContent(type="text", text=f"State saved to slot {slot}")]
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        return [TextContent(type="text", text=f"Failed to save state: {str(e)}")]


@mcp.tool()
def load_state(slot: int = 0) -> list[TextContent]:
    """Load a previously saved emulator state.
    
    Args:
        slot: Save state slot (0-9, default: 0)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= slot <= 9:
        return [TextContent(type="text", text="Slot must be between 0-9")]
    
    try:
        emulator.load_state(slot)
        return [TextContent(type="text", text=f"State loaded from slot {slot}")]
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return [TextContent(type="text", text=f"Failed to load state: {str(e)}")]


@mcp.tool()
def get_game_title() -> list[TextContent]:
    """Get the title of the currently loaded game."""
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    try:
        title = emulator.cartridge_title
        return [TextContent(type="text", text=f"Game title: {title}")]
    except Exception as e:
        logger.error(f"Failed to get game title: {e}")
        return [TextContent(type="text", text=f"Failed to get game title: {str(e)}")]


@mcp.tool()
def get_memory(address: int) -> list[TextContent]:
    """Read a byte from Game Boy memory.
    
    Args:
        address: Memory address (0x0000 - 0xFFFF)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= address <= 0xFFFF:
        return [TextContent(type="text", text="Address must be between 0x0000 and 0xFFFF")]
    
    try:
        value = emulator.get_memory(address)
        return [TextContent(type="text", text=f"Memory[0x{address:04X}] = 0x{value:02X} ({value})")]
    except Exception as e:
        logger.error(f"Failed to read memory: {e}")
        return [TextContent(type="text", text=f"Failed to read memory: {str(e)}")]


@mcp.tool()
def set_memory(address: int, value: int) -> list[TextContent]:
    """Write a byte to Game Boy memory.
    
    Args:
        address: Memory address (0x0000 - 0xFFFF)
        value: Byte value to write (0-255)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= address <= 0xFFFF:
        return [TextContent(type="text", text="Address must be between 0x0000 and 0xFFFF")]
    
    if not 0 <= value <= 255:
        return [TextContent(type="text", text="Value must be between 0 and 255")]
    
    try:
        emulator.set_memory(address, value)
        return [TextContent(type="text", text=f"Memory[0x{address:04X}] = 0x{value:02X}")]
    except Exception as e:
        logger.error(f"Failed to write memory: {e}")
        return [TextContent(type="text", text=f"Failed to write memory: {str(e)}")]


@mcp.tool()
def get_memory_range(start: int, length: int) -> list[TextContent]:
    """Read multiple bytes from Game Boy memory.
    
    Args:
        start: Starting memory address (0x0000 - 0xFFFF)
        length: Number of bytes to read (1-256)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= start <= 0xFFFF:
        return [TextContent(type="text", text="Start address must be between 0x0000 and 0xFFFF")]
    
    if not 1 <= length <= 256:
        return [TextContent(type="text", text="Length must be between 1 and 256")]
    
    if start + length > 0x10000:
        return [TextContent(type="text", text="Range exceeds memory boundary (0xFFFF)")]
    
    try:
        values = emulator.get_memory_range(start, length)
        hex_values = " ".join(f"{v:02X}" for v in values)
        return [TextContent(type="text", text=f"Memory[0x{start:04X}..0x{start+length-1:04X}]: {hex_values}")]
    except Exception as e:
        logger.error(f"Failed to read memory range: {e}")
        return [TextContent(type="text", text=f"Failed to read memory range: {str(e)}")]


@mcp.tool()
def save_screenshot(filename: str) -> list[TextContent]:
    """Save the current screen as a PNG file.
    
    Args:
        filename: Name of the file to save (will be saved in current directory)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    try:
        # Ensure filename ends with .png
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Save screenshot
        saved_path = emulator.save_screenshot(filename)
        return [TextContent(type="text", text=f"Screenshot saved to: {saved_path}")]
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        return [TextContent(type="text", text=f"Failed to save screenshot: {str(e)}")]


@mcp.tool()
def set_emulation_speed(speed: int) -> list[TextContent]:
    """Set emulation speed.
    
    Args:
        speed: 0 for unlimited, 1 for normal, 2+ for faster
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if speed < 0:
        return [TextContent(type="text", text="Speed must be >= 0")]
    
    try:
        emulator.set_emulation_speed(speed)
        speed_text = "unlimited" if speed == 0 else f"{speed}x"
        return [TextContent(type="text", text=f"Emulation speed set to: {speed_text}")]
    except Exception as e:
        logger.error(f"Failed to set emulation speed: {e}")
        return [TextContent(type="text", text=f"Failed to set emulation speed: {str(e)}")]


@mcp.tool()
def get_sprite(sprite_index: int) -> list[TextContent]:
    """Get sprite information.
    
    Args:
        sprite_index: Sprite index (0-39)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= sprite_index <= 39:
        return [TextContent(type="text", text="Sprite index must be between 0 and 39")]
    
    try:
        sprite_info = emulator.get_sprite(sprite_index)
        text = (
            f"Sprite {sprite_index}: x={sprite_info['x']}, y={sprite_info['y']}, "
            f"tile={sprite_info['tile_identifier']}, on_screen={sprite_info['on_screen']}, "
            f"x_flip={sprite_info['x_flip']}, y_flip={sprite_info['y_flip']}, "
            f"palette={sprite_info['palette']}, bg_priority={sprite_info['bg_priority']}"
        )
        return [TextContent(type="text", text=text)]
    except Exception as e:
        logger.error(f"Failed to get sprite: {e}")
        return [TextContent(type="text", text=f"Failed to get sprite: {str(e)}")]


@mcp.tool(structured_output=False)
def get_tile(tile_id: int) -> list[TextContent | ImageContent]:
    """Get tile image data.
    
    Args:
        tile_id: Tile identifier (0-383)
    """
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    if not 0 <= tile_id <= 383:
        return [TextContent(type="text", text="Tile ID must be between 0 and 383")]
    
    try:
        tile_data = emulator.get_tile(tile_id)
        return [ImageContent(type="image", data=tile_data, mimeType="image/png")]
    except Exception as e:
        logger.error(f"Failed to get tile: {e}")
        return [TextContent(type="text", text=f"Failed to get tile: {str(e)}")]


@mcp.tool()
def get_fps() -> list[TextContent]:
    """Get current emulation FPS."""
    if not emulator:
        return [TextContent(type="text", text="No ROM loaded. Use load_rom first.")]
    
    try:
        fps = emulator.current_fps
        return [TextContent(type="text", text=f"Current FPS: {fps:.1f}")]
    except Exception as e:
        logger.error(f"Failed to get FPS: {e}")
        return [TextContent(type="text", text=f"Failed to get FPS: {str(e)}")]


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()