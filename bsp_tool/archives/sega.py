"""Dreamcast 'Giga-Disc' Handler"""
# https://multimedia.cx/eggs/understanding-the-dreamcast-gd-rom-layout/

from __future__ import annotations
import io
from typing import List

from . import cdrom
from . import padus
from ..utils import binary


# TODO: grab files inside a .zip, convert to disc image, then GDRom


class Region:
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


# TODO: peripherals string enum


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
        out.region = Region(area_symbols)
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
    pvd: cdrom.PrimaryVolumeDescriptor
    path_table: bytes

    def __init__(self):
        self.pvd = list()
        self.path_table = list()

    def __repr__(self):
        id_ = " ".join(
            getattr(self.header, attr)
            for attr in ("product_num", "game", "version"))
        return f"<GDRom {id_} @ 0x{id(self):016X}>"

    @classmethod
    def from_cdi(cls, cdi: padus.Cdi) -> GDRom:
        out = cls()
        out.cdi = cdi  # DEBUG
        # TODO: we shouldn't be tied to built from
        # -- we need to map the WHOLE GD-ROM on our own
        start_lba = cdi.sessions[1][0].start_lba  # GD Area PVD correction
        out.disc_image = cdi.read("1.0.iso")  # session 2; track 1
        stream = io.BytesIO(out.disc_image)
        # boot header
        out.header = Header.from_stream(stream)
        # disc filesystem
        pvd_addresses = binary.find_all(out.disc_image, b"\x01CD001")
        assert len(pvd_addresses) > 0, "no PrimaryVolumeDescriptor found in GD Area"
        assert pvd_addresses[0] == 0x8000
        # NOTE: there should be a 2nd PVD @ 0x9800 or so
        # -- we're skipping that one for now; LBA correction put it's address in the negatives
        stream.seek(0x8000)  # 1st PVD
        out.pvd = cdrom.PrimaryVolumeDescriptor.from_stream(stream)
        path_table_lba = out.pvd.path_table_le_lba - start_lba
        stream.seek(path_table_lba * out.pvd.block_size)
        out.path_table = stream.read(out.pvd.path_table_size)
        # NOTE: we're ignoring the optional path table, and the big-endian stuff too
        # TODO: parse the cdrom.PathTable, don't just grab the bytes
        # TODO: parse the 2nd PVD & it's PathTable
        # -- the 2nd PVD thinks it starts at LBA 16 (0x8000 on a regular CD-ROM)
        # -- e.g. LBA X is @ pvd_address + (X - 16) * block_size
        # -- there is a PathTable at this location
        ...
        # TODO: what else do we need?
        # -- filesystem(s) -> hooks for namelist & read methods
        return out

    @classmethod
    def from_file(cls, filename: str) -> GDRom:
        # TODO: support multiple source file formats:
        # -- .cdi .gdi .bin+.cue
        assert filename.lower().endswith(".cdi")
        return cls.from_cdi(padus.Cdi(filename))
