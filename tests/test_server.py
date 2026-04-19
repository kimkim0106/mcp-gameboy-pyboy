"""Tests for the MCP server tools, exercised through FastMCP's call_tool."""

import asyncio
import base64

import pytest

from mcp.types import ImageContent, TextContent

import mcp_gameboy.server as server


@pytest.fixture(autouse=True)
def reset_emulator():
    """Ensure each test starts without a loaded ROM."""
    server.emulator = None
    yield
    server.emulator = None


def run(coro):
    return asyncio.run(coro)


def _unwrap(result):
    """FastMCP returns either ``content`` or ``(content, structured)`` depending
    on whether an output_schema is present. Normalize to the content list."""
    if isinstance(result, tuple):
        return result[0]
    return result


def test_load_rom_returns_success_text(rom_path: str):
    content = _unwrap(run(server.mcp.call_tool("load_rom", {"rom_path": rom_path})))
    assert len(content) == 1
    assert isinstance(content[0], TextContent)
    assert "loaded successfully" in content[0].text


def test_load_rom_missing_file_returns_error_text(tmp_path):
    missing = tmp_path / "nope.gb"
    content = _unwrap(
        run(server.mcp.call_tool("load_rom", {"rom_path": str(missing)}))
    )
    assert isinstance(content[0], TextContent)
    assert "not found" in content[0].text.lower()


def test_tool_without_loaded_rom_returns_guidance():
    content = _unwrap(run(server.mcp.call_tool("get_screen", {})))
    assert isinstance(content[0], TextContent)
    assert "load_rom" in content[0].text


def test_get_screen_returns_unstructured_image_only(rom_path: str):
    """Regression guard: ``structured_output=False`` must stay on ``get_screen``
    so the base64 PNG isn't duplicated into a structuredContent envelope that
    some clients mis-render as a blank image."""
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("tick", {"frames": 60}))
    raw = run(server.mcp.call_tool("get_screen", {}))

    assert not isinstance(raw, tuple), (
        "get_screen must not emit structuredContent — that triggers the blank-PNG bug"
    )
    assert len(raw) == 1
    assert isinstance(raw[0], ImageContent)
    assert raw[0].mimeType == "image/png"
    # PNG signature check on the decoded bytes
    assert base64.b64decode(raw[0].data).startswith(b"\x89PNG\r\n\x1a\n")


def test_get_screen_changes_after_tick(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("tick", {"frames": 30}))
    first = _unwrap(run(server.mcp.call_tool("get_screen", {})))[0].data

    run(server.mcp.call_tool("tick", {"frames": 120}))
    second = _unwrap(run(server.mcp.call_tool("get_screen", {})))[0].data

    assert first != second


def test_get_tile_returns_unstructured_image_only(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    raw = run(server.mcp.call_tool("get_tile", {"tile_id": 0}))
    assert not isinstance(raw, tuple)
    assert isinstance(raw[0], ImageContent)


def test_get_memory_formats_hex(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("set_memory", {"address": 0xC000, "value": 0x7A}))
    content = _unwrap(run(server.mcp.call_tool("get_memory", {"address": 0xC000})))
    assert "0xC000" in content[0].text
    assert "0x7A" in content[0].text


def test_get_memory_rejects_out_of_range(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    content = _unwrap(
        run(server.mcp.call_tool("get_memory", {"address": 0x10000}))
    )
    assert "between" in content[0].text.lower()


def test_get_memory_range_formats_all_bytes(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    for i in range(4):
        run(
            server.mcp.call_tool(
                "set_memory", {"address": 0xC300 + i, "value": i + 1}
            )
        )
    content = _unwrap(
        run(server.mcp.call_tool("get_memory_range", {"start": 0xC300, "length": 4}))
    )
    text = content[0].text
    assert "01 02 03 04" in text


def test_press_and_release_button_accept_valid_names(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    press = _unwrap(run(server.mcp.call_tool("press_button", {"button": "a"})))
    release = _unwrap(run(server.mcp.call_tool("release_button", {"button": "a"})))
    assert "Pressed" in press[0].text
    assert "Released" in release[0].text


def test_press_button_rejects_invalid(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    content = _unwrap(
        run(server.mcp.call_tool("press_button", {"button": "x"}))
    )
    assert "Invalid button" in content[0].text


def test_save_and_load_state_through_tools(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("tick", {"frames": 30}))
    saved = _unwrap(run(server.mcp.call_tool("save_state", {"slot": 0})))
    assert "saved to slot 0" in saved[0].text

    loaded = _unwrap(run(server.mcp.call_tool("load_state", {"slot": 0})))
    assert "loaded from slot 0" in loaded[0].text


def test_save_screenshot_creates_file(rom_path: str, tmp_path):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("tick", {"frames": 30}))
    out = tmp_path / "shot.png"
    content = _unwrap(
        run(server.mcp.call_tool("save_screenshot", {"filename": str(out)}))
    )
    assert out.exists()
    assert str(out) in content[0].text


def test_get_fps_returns_text(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    run(server.mcp.call_tool("tick", {"frames": 60}))
    content = _unwrap(run(server.mcp.call_tool("get_fps", {})))
    assert "FPS" in content[0].text


def test_get_game_title_returns_non_empty(rom_path: str):
    run(server.mcp.call_tool("load_rom", {"rom_path": rom_path}))
    content = _unwrap(run(server.mcp.call_tool("get_game_title", {})))
    text = content[0].text.replace("Game title:", "").strip()
    assert text, "title should never be empty (falls back to ROM stem)"
