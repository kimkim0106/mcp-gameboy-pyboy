# MCP Game Boy PyBoy Server

An MCP (Model Context Protocol) server that provides Game Boy emulation capabilities using PyBoy.

## Features

- Load Game Boy ROM files (.gb, .gbc)
- Control emulation (button presses, frame advancement)
- Capture screen images
- Save and load emulator states
- Get game information

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kimkim0106/mcp-gameboy-pyboy.git
cd mcp-gameboy-pyboy
```

2. Install the package and dependencies:
```bash
pip install -e .
```

### Claude Desktop Configuration

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gameboy-pyboy": {
      "command": "python3",
      "args": ["-m", "mcp_gameboy.server"],
      "cwd": "/path/to/mcp-gameboy-pyboy",
      "env": {
        "PYTHONPATH": "/path/to/mcp-gameboy-pyboy"
      }
    }
  }
}
```

**Note**: Replace `/path/to/mcp-gameboy-pyboy` with the actual path to this project directory.

For Python environments managed by tools like asdf or pyenv, use the full path to the Python executable:
```json
{
  "mcpServers": {
    "gameboy-pyboy": {
      "command": "/full/path/to/python3",
      "args": ["-m", "mcp_gameboy.server"],
      "cwd": "/path/to/mcp-gameboy-pyboy",
      "env": {
        "PYTHONPATH": "/path/to/mcp-gameboy-pyboy"
      }
    }
  }
}
```

After updating the configuration, restart Claude Desktop to load the server.

### Claude Code Configuration

To use this server with Claude Code, first navigate to the project directory and use the `claude mcp add` command:

```bash
cd /path/to/mcp-gameboy-pyboy
claude mcp add gameboy-pyboy python3 -- -m mcp_gameboy.server
```

For Python environments managed by tools like asdf or pyenv, use the full path to the Python executable:
```bash
cd /path/to/mcp-gameboy-pyboy
claude mcp add gameboy-pyboy /full/path/to/python3 -- -m mcp_gameboy.server
```

**Note**: The `--` is important to separate the claude command options from the Python arguments.

To verify the server is added:
```bash
claude mcp list
```

To remove the server:
```bash
claude mcp remove gameboy-pyboy
```

## Available Tools

### `load_rom`
Load a Game Boy ROM file.
- `rom_path`: Path to the ROM file (.gb or .gbc)

### `get_screen`
Get the current Game Boy screen as an image.

### `press_button`
Press a Game Boy button.
- `button`: Button to press (a, b, start, select, up, down, left, right)

### `release_button`
Release a Game Boy button.
- `button`: Button to release (a, b, start, select, up, down, left, right)

### `tick`
Advance the emulation by a number of frames.
- `frames`: Number of frames to advance (default: 1)

### `save_state`
Save the current emulator state.
- `slot`: Save state slot (0-9, default: 0)

### `load_state`
Load a previously saved emulator state.
- `slot`: Save state slot (0-9, default: 0)

### `get_game_title`
Get the title of the currently loaded game.

## Usage Example

```python
# Load a ROM
await load_rom("~/games/pokemon_red.gb")

# Get game title
await get_game_title()

# Press start button
await press_button("start")
await tick(60)  # Advance 1 second (60 fps)
await release_button("start")

# Capture screen
await get_screen()

# Save state
await save_state(0)

# Play for a bit
await press_button("a")
await tick(30)
await release_button("a")

# Load previous state
await load_state(0)
```

## Development

Run the server:
```bash
python -m mcp_gameboy.server
```

## License

MIT# mcp-gameboy-pyboy
