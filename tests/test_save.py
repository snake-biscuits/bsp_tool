import difflib
import fnmatch
import os
import re
import shutil

from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2

import pytest


def map_dir_to_test(map_dir: str):
    """decorator for sourcing test maps"""
    # TODO: multiple map_dirs
    maps = fnmatch.filter(os.listdir(os.path.join("tests/maps", map_dir)), "*.bsp")
    map_names = [os.path.join(map_dir, m) for m in maps]
    map_paths = [os.path.join("tests/maps", m) for m in map_names]

    def decorator(test_function):
        """parametrize test for better logging & handle cleanup of files"""

        @pytest.mark.parametrize("map_path", map_paths, ids=map_names)
        def wrapped_test_function(map_path: str):
            shutil.copy(map_path, map_path + ".bak")
            try:
                test_function(map_path)
            except Exception as exc:  # restore the backup when the test fails
                shutil.move(map_path + ".bak", map_path)
                raise exc
            shutil.move(map_path + ".bak", map_path)  # cleanup
        return wrapped_test_function

    return decorator


def xxd(filename: str, width: int = 32) -> str:
    """view a binary file like with a certain hex editor"""
    allowed_chars = re.compile(r"[a-zA-Z0-9/\\]")
    with open(filename, "rb") as binary_file:
        i, bytes_ = 0, binary_file.read(width)
        while bytes_ != b"":
            address = f"0x{i * width:08X}"
            hex_ = " ".join([f"{b:02X}" for b in bytes_])
            if len(hex_) < 3 * width:  # pad last line of hex with spaces
                hex_ += " " * (3 * width - len(hex_))
            ascii_ = "".join([chr(b) if allowed_chars.match(chr(b)) else "." for b in bytes_])
            yield f"{address}:  {hex_}  {ascii_}\n"
            i, bytes_ = binary_file.read(width), i + 1


@pytest.mark.xfail
@map_dir_to_test("Titanfall 2")
def test_save_RespawnBsp(map_path: str):
    bsp = RespawnBsp(titanfall2, map_path)
    bsp.save()
    short_name = bsp.filename
    del bsp  # close the bsp file
    diff_lines = difflib.unified_diff(xxd(f"{map_path}.bak"), xxd(map_path),
                                      f"{short_name}.bak", short_name)
    diff_text = "".join(diff_lines)
    assert len(diff_text) == 0, "not a perfect match"
