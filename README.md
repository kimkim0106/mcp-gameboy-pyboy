# mcp-gameboy-pyboy

MCP server that exposes a [PyBoy](https://github.com/Baekalfen/PyBoy) Game Boy emulator to an MCP client.

## Features

- Load `.gb` / `.gbc` ROMs, drive input, advance frames
- Capture the screen (inline PNG or file) and inspect sprites / tiles
- Read & write Game Boy memory, save / load state slots

## Install

```bash
uv sync
```

## Use

Point your MCP client at `uv run` so dependencies stay in sync automatically:

```json
{
  "mcpServers": {
    "gameboy-pyboy": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-gameboy-pyboy", "run", "mcp-gameboy-pyboy"],
      "cwd": "/path/to/mcp-gameboy-pyboy"
    }
  }
}
```

Or with Claude Code:

```bash
claude mcp add gameboy-pyboy -- uv --directory /path/to/mcp-gameboy-pyboy run mcp-gameboy-pyboy
```

Tool schemas are published over MCP — no manual tool reference needed here.

## Test

```bash
uv sync --group dev
uv run pytest
```

Tests use PyBoy's bundled `default_rom.gb`; no ROM is committed to this repo.

## License

MIT — see [LICENSE](LICENSE).

This project depends on [PyBoy](https://github.com/Baekalfen/PyBoy) (**LGPL-3.0-only**), installed as a separate pip dependency. Other runtime deps: `mcp` (MIT), `pillow` (MIT-CMU).
