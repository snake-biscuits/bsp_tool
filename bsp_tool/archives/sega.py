"""Dreamcast 'Giga-Disc' Handler"""
# https://multimedia.cx/eggs/understanding-the-dreamcast-gd-rom-layout/

from __future__ import annotations
import io
import os
from typing import List

from .. import external
from . import alcohol
from . import base
from . import cdrom
from . import golden_hawk
from . import mame
from . import padus


class Gdi(base.DiscImage):
    ext = "*.gdi"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Gdi:
        out = cls()
        num_tracks = int(stream.readline().decode())
        modes = {
            "0": base.TrackMode.AUDIO,
            "4": base.TrackMode.BINARY_1}
        for i, line in enumerate(stream):
            line = line.decode().rstrip()
            assert line.count(" ") == 5
            track_number, start_lba, mode, sector_size, name, zero = line.split(" ")
            assert int(track_number) == i + 1
            assert zero == "0"
            mode = modes[mode]
            sector_size = int(sector_size)
            start_lba = int(start_lba)
            # NOTE: length of -1 means we get it from filesize
            out.tracks.append(base.Track(mode, sector_size, start_lba, -1, name))
        assert len(out.tracks) == num_tracks
        return out


# Boot Header
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
    peripherals: str  # TODO: use Peripherals class
    product_number: str
    version: str
    release_date: str  # TODO: Date class
    boot_file: str
    developer: str
    game: str

    def __repr__(self) -> str:
        descriptor = f"{self.product_number} {self.game!r} {self.version}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_header: bytes) -> Header:
        return cls.from_stream(io.BytesIO(raw_header))

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
        out.product_number = stream.read(10).decode().rstrip(" ")
        out.version = stream.read(6).decode().rstrip(" ")  # TODO: class
        out.release_date = stream.read(16).decode().rstrip(" ")  # TODO: class
        out.boot_file = stream.read(16).decode().rstrip(" ")  # "Boot Filename"
        out.developer = stream.read(16).decode().rstrip(" ")  # "Software Maker Name"
        out.game = stream.read(16).decode().rstrip(" ")  # "Game Title"
        return out


disc_classes = {
    ".cdi": padus.Cdi,
    ".chd": mame.Chd,
    ".cue": golden_hawk.Cue,
    ".gdi": Gdi,
    ".mds": alcohol.Mds}
# NOTE: currently using GDRom


class GDRom(base.Archive):
    """DiscImage wrapper for GD-ROM filesystems"""
    ext = "*.gdi"
    exts = ["*.cdi", "*.chd", "*.cue", "*.gdi", "*.mds"]
    # NOTE: also raw *.iso disc images
    disc: base.DiscImage
    cd_rom: cdrom.Iso  # CD-ROM filesystem @ lba 0
    gd_rom: cdrom.Iso  # GD-ROM filesystem @ lba 45000
    # TODO: filesystems: List[cdrom.Iso]  # sometimes you get 3
    header: Header

    # TODO: __init__ w/ defaults (equivalent to a blank GD-ROM)

    def __repr__(self):
        descriptor = " ".join(
            getattr(self.header, attr)
            for attr in ("product_number", "game", "version"))
        return f"<GDRom {descriptor} @ 0x{id(self):016X}>"

    def listdir(self, search_folder: str) -> List[str]:
        return self.gd_rom.listdir(search_folder)

    def namelist(self) -> List[str]:
        return self.gd_rom.namelist()

    def read(self, filename: str) -> bytes:
        return self.gd_rom.read(filename)

    @classmethod
    def from_archive(cls, parent_archive: base.Archive, filename: str) -> GDRom:
        ext = os.path.splitext(filename.lower())[-1]
        if ext == ".cdi":
            cdi = padus.Cdi.from_archive(parent_archive, filename)
            return cls.from_cdi(cdi)
        elif ext in disc_classes:
            disc = disc_classes[ext].from_archive(parent_archive, filename)
            return cls.from_disc(disc)
        else:
            raise RuntimeError(f"Unsupported file extension: {ext}")

    @classmethod
    def from_bytes(cls, raw_gdrom: bytes) -> GDRom:
        disc = base.DiscImage()
        disc.extras = {":memory:": external.File.from_bytes(":memory:", raw_gdrom)}
        assert disc.extras[":memory:"].size % 2048 == 0, "unexpected EOF"
        length = disc.extras[":memory:"].size // 2048
        disc.tracks = [base.Track(base.TrackMode.BINARY_1, 2048, 0, length, ":memory:")]
        return cls.from_disc(disc)

    @classmethod
    def from_cdi(cls, cdi: padus.Cdi) -> GDRom:
        # DEBUG: the 1 .cdi I'm testing doesn't start the GD-ROM area @ 45000
        assert "Session 02 Track 01" in cdi.extras
        # NOTE: should be 2 sessions (cd_rom & gd_rom)
        data_track = {track.name: track for track in cdi.tracks}["Session 02 Track 01"]
        assert data_track.mode != base.TrackMode.AUDIO
        # build the GD-ROM
        out = cls()
        out.disc = cdi
        # TODO: check for a binary track at the start of the cd_rom sectors
        out.cd_rom = None
        out.gd_rom = cdrom.Iso.from_disc(out.disc, data_track.start_lba + 16)
        out.disc.sector_seek(data_track.start_lba)  # boot header
        out.header = Header.from_bytes(out.disc.read(0x90))
        return out

    @classmethod
    def from_disc(cls, disc: base.DiscImage) -> GDRom:
        out = cls()
        out.disc = disc
        # NOTE: cd_rom filesystem may not be present
        out.cd_rom = cdrom.Iso.from_disc(out.disc, 16)
        # NOTE: gd_rom filesystem & header might not start at 45000
        out.gd_rom = cdrom.Iso.from_disc(out.disc, 45016)
        # NOTE: might also have a header @ lba 0
        out.disc.sector_seek(45000)  # boot header
        out.header = Header.from_bytes(out.disc.read(0x90))
        return out

    @classmethod
    def from_file(cls, filename: str) -> GDRom:
        ext = os.path.splitext(filename.lower())[-1]
        if ext == ".cdi":
            cdi = padus.Cdi.from_file(filename)
            return cls.from_cdi(cdi)
        elif ext in disc_classes:
            disc = disc_classes[ext].from_file(filename)
            return cls.from_disc(disc)
        else:
            raise RuntimeError(f"Unsupported file extension: {ext}")

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GDRom:
        return cls.from_bytes(stream.read())
