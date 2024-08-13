"""Dreamcast 'Giga-Disc' Handler"""
# https://multimedia.cx/eggs/understanding-the-dreamcast-gd-rom-layout/

from __future__ import annotations
import io
from typing import List

from . import cdrom
from . import padus


class Region:  # string-based flags
    symbols: str
    JPN = 0
    USA = 1
    EUR = 2

    def __init__(self, area_symbols: str):
        assert area_symbols[self.JPN] in "J "
        assert area_symbols[self.USA] in "U "
        assert area_symbols[self.EUR] in "E "
        self.symbols = area_symbols

    def __repr__(self) -> str:
        regions = [
            name
            for i, name in enumerate(("JPN", "USA", "EUR"))
            if self.symbols[i] != " "]
        return f"<Region {'|'.join(regions)}>"


# TODO: Peripherals string-based flags


class Header:
    # https://github.com/KallistiOS/KallistiOS/blob/master/utils/makeip/src/field.c#L36
    device: str  # GD-ROM1/1 etc.
    region: Region

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Header:
        out = cls()
        assert stream.read(16) == b"SEGA SEGAKATANA "  # Hardware ID
        assert stream.read(16) == b"SEGA ENTERPRISES"  # Maker ID
        out.device = stream.read(16).decode().rstrip(" ")
        area_symbols = stream.read(8).decode()
        assert area_symbols[3:] == " " * 5, area_symbols
        out.region = Region(area_symbols[:3])  # :3
        out.peripherals = stream.read(8).decode().rstrip(" ")  # TODO: class
        out.product_num = stream.read(10).decode().rstrip(" ")
        out.version = stream.read(6).decode().rstrip(" ")  # TODO: class
        out.release_date = stream.read(16).decode().rstrip(" ")  # TODO: class
        out.boot_file = stream.read(16).decode().rstrip(" ")  # "Boot Filename"
        out.developer = stream.read(16).decode().rstrip(" ")  # "Software Maker Name"
        out.game = stream.read(16).decode().rstrip(" ")  # "Game Title"
        return out


class GDRom:
    header: Header
    data_area: cdrom.Iso  # GD-ROM Data Area

    def __init__(self):
        self.pvd = list()
        self.path_table = list()

    def __repr__(self):
        id_ = " ".join(
            getattr(self.header, attr)
            for attr in ("product_num", "game", "version"))
        return f"<GDRom {id_} @ 0x{id(self):016X}>"

    def listdir(self, search_folder: str) -> List[str]:
        return self.data_area.listdir(search_folder)

    def namelist(self) -> List[str]:
        return self.data_area.namelist()

    def read(self, filename: str) -> bytes:
        return self.data_area.read(filename)

    @classmethod
    def from_cdi(cls, cdi: padus.Cdi) -> GDRom:
        # validate our assumptions
        assert len(cdi.sessions) == 2  # CD area (soundtrack), GD area (game)
        assert len(cdi.sessions[1]) == 1  # 1 Track
        data_track = cdi.sessions[1][0]
        assert data_track.mode == padus.TrackMode.Mode2  # binary data (.iso)
        # Session 2 - Track 1 is the GD Area
        out = cls()
        out.data_area = cdrom.Iso.from_bytes(cdi.read("1.0.iso"), 0x8000, -data_track.start_lba)
        # NOTE: we assuming there's a PVD at the default address (seaching for a PVD is slow)
        # -- other PVDs might be present
        # -- quakeiii.cdi has a 2nd PVD (thinks it starts at LBA 16 like a normal CD)
        # -- iso_2 = cdrom.Iso.from_bytes(cdi.read("1.0.iso"), 0x9B000, (0x9B000 // 0x800) - 16)
        out.data_area.disc.seek(0)  # boot header
        out.header = Header.from_stream(out.data_area.disc)
        out.cdi = cdi  # DEBUG
        # TODO: save session[0]'s tracks to self.soundtrack or something & discard the Cdi
        return out

    @classmethod
    def from_file(cls, filename: str) -> GDRom:
        # TODO: support multiple source file formats:
        # -- .cdi .gdi+.bin/.raw .cue+.bin/.raw
        assert filename.lower().endswith(".cdi")
        return cls.from_cdi(padus.Cdi(filename))
