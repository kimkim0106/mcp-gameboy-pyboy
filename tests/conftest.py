"""Shared fixtures for the test suite.

The ROM used in these tests is ``default_rom.gb`` bundled with the ``pyboy``
package (LGPL-3.0). It is referenced from the installed package path so no
ROM binary is committed to this repository.
"""

from pathlib import Path

import pyboy
import pytest

from mcp_gameboy.gameboy import GameBoyEmulator


@pytest.fixture(scope="session")
def rom_path() -> str:
    path = Path(pyboy.__file__).parent / "default_rom.gb"
    assert path.exists(), f"Expected bundled PyBoy ROM at {path}"
    return str(path)


@pytest.fixture
def emu(rom_path: str) -> GameBoyEmulator:
    return GameBoyEmulator(rom_path)
