import io
import re


def xxd(data: bytes, cols: int = 32, show_address: bool = False) -> str:
    """view a binary file like with a certain hex editor"""
    data = io.BytesIO(data)
    allowed_chars = re.compile(r"[a-zA-Z0-9/\\]")
    address, bytes_ = 0, data.read(cols)
    while bytes_ != b"":
        hex_ = " ".join([f"{b:02X}" for b in bytes_])
        if len(hex_) < 3 * cols:  # last line needs padding
            hex_ += " " * (3 * cols - len(hex_))
        ascii_ = "".join([c if allowed_chars.match(c) else "." for c in map(chr, bytes_)])
        if show_address:
            yield f"0x{address:08X}:  {hex_}  {ascii_}\n"
        else:
            yield f"{hex_} {ascii_}\n"
        address, bytes_ = address + cols, data.read(cols)
