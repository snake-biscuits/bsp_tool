import re

from bsp_tool.extensions import diff

import pytest


class TestXXD:
    # TODO: test show_address=False
    @staticmethod
    def expected_line(line_number: int, bytes_: bytes, cols: int = None):
        cols = len(bytes_) if cols is None else cols
        address = f"0x{line_number * cols:08X}"
        hex_ = " ".join([f"{b:02X}" for b in bytes_])
        if len(hex_) < 3 * cols:  # padding
            hex_ += " " * (3 * cols - len(hex_))
        allowed_chars = re.compile(r"[a-zA-Z0-9/\\]")
        ascii_ = "".join([c if allowed_chars.match(c) else "." for c in map(chr, bytes_)])
        return f"{address}:  {hex_}  {ascii_}\n"

    @staticmethod
    def split(bytes_: bytes, cols: int):
        for i in range(0, len(bytes_), cols):
            yield bytes_[i:i + cols]

    samples = {"no padding needed": (b"Hello World!", 6),
               "padding required": (b"Communist Manifesto", 10),
               "every byte": (bytes(range(0xFF + 1)), 16)}

    @pytest.mark.parametrize("sample,cols", samples.values(), ids=samples.keys())
    def test_input(self, sample: bytes, cols: int):
        xxd_line = diff.core.xxd(sample, cols=cols, show_address=True)
        for i, bytes_ in enumerate(self.split(sample, cols)):
            assert next(xxd_line) == self.expected_line(i, bytes_, cols)
        with pytest.raises(StopIteration):
            next(xxd_line)
