"""Dreamcast 'Giga-Disc' Handler"""
# https://multimedia.cx/eggs/understanding-the-dreamcast-gd-rom-layout/

from __future__ import annotations
import enum
import io
import os
from typing import List

from . import base
from . import cdrom
from . import padus


# *.gdi files
class GdiTrackType(enum.Enum):
    AUDIO = 0
    BINARY = 4


class GdiTrack:
    track_number: int  # starts at 1
    start_lba: int
    type: GdiTrackType
    sector_size: int
    filename: str

    def __init__(self, track_number, start_lba, type_, sector_size, filename):
        self.track_number = track_number
        self.start_lba = start_lba
        self.type = type_
        self.sector_size = sector_size
        self.filename = filename

    def __repr__(self) -> str:
        descriptor = f"{self.track_number:02d} {self.filename!r} ({self.type.name})"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_line(cls, line: str) -> GdiTrack:
        line = line.rstrip()  # no trailing whitespace or newline
        assert line.count(" ") == 5
        track_number, start_lba, type_, sector_size, filename, zero = line.split(" ")
        assert zero == "0", f"{zero!r}"
        track_number = int(track_number)
        start_lba = int(start_lba)
        type_ = GdiTrackType(int(type_))
        sector_size = int(sector_size)
        return cls(track_number, start_lba, type_, sector_size, filename)


class Gdi(base.Archive):
    ext = "*.gdi"
    folder: str
    filename: str
    tracks: List[GdiTrack]

    def __init__(self, filename: str = None):
        self.tracks = list()
        if filename is not None:
            self.folder, self.filename = os.path.split(filename)

    def __repr__(self) -> str:
        descriptor = f"{self.filename!r} {len(self.tracks)} tracks"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return [track.filename for track in self.tracks]

    def read(self, filename: str) -> bytes:
        assert filename in self.namelist()
        track = {track.filename: track for track in self.tracks}[filename]
        with open(os.path.join(self.folder, filename), "rb") as track_file:
            if track.type == GdiTrackType.BINARY:
                # based on sector conversion code from padus.Cdi.read
                sectors = list()
                # NOTE: Mode1 2352, not Mode2 like in .cdi?
                header_length_for_size = {2048: 0, 2352: 16}
                header_length = header_length_for_size[track.sector_size]
                raw_sector = track_file.read(track.sector_size)
                while len(raw_sector) != 0:
                    assert len(raw_sector) == track.sector_size
                    sector = raw_sector[header_length:]
                    sector = sector[:2048]
                    sectors.append(sector)
                    raw_sector = track_file.read(track.sector_size)
                return b"".join(sectors)
            else:
                return track_file.read()

    @classmethod
    def from_file(cls, filename: str) -> Gdi:
        out = cls(filename)
        with open(filename, "r") as gdi_file:
            num_tracks = int(gdi_file.readline())
            for line in gdi_file:
                track = GdiTrack.from_line(line)
                out.tracks.append(track)
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


# Universal GDRom wrapper
class GDRom(base.Archive):
    ext = "*.gdi"
    exts = ["*.cdi", "*.chd", "*.cue", "*.gdi"]
    header: Header
    data_area: cdrom.Iso  # GD-ROM Data Area

    # TODO: __init__ w/ defaults (equivalent to a blank GD-ROM)

    def __repr__(self):
        descriptor = " ".join(
            getattr(self.header, attr)
            for attr in ("product_number", "game", "version"))
        return f"<GDRom {descriptor} @ 0x{id(self):016X}>"

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
    def from_gdi(cls, gdi: Gdi) -> GDRom:
        data_track = gdi.tracks[-1]
        # validate our assumptions
        assert data_track.type == GdiTrackType.BINARY
        out = cls()
        # NOTE: .gdi files might break up the data area into multiple tracks
        # -- maybe we can add controls for merging tracks in that case?
        out.data_area = cdrom.Iso.from_bytes(gdi.read(data_track.filename), 0x8000, -data_track.start_lba)
        # NOTE: we assuming there's a PVD at the default address (seaching for a PVD is slow)
        # -- other PVDs might be present
        # -- quakeiii.cdi has a 2nd PVD (thinks it starts at LBA 16 like a normal CD)
        # -- iso_2 = cdrom.Iso.from_bytes(cdi.read("1.0.iso"), 0x9B000, (0x9B000 // 0x800) - 16)
        out.data_area.disc.seek(0)  # boot header
        out.header = Header.from_stream(out.data_area.disc)
        out.gdi = gdi  # DEBUG
        # TODO: save all audio tracks to self.soundtrack or something & discard the Gdi
        # -- if Gdi.tracks[0].type == GdiTrackType.BINARY: get audio track filenames from Iso
        return out

    @classmethod
    def from_file(cls, filename: str) -> GDRom:
        ext = os.path.splitext(filename.lower())[-1]
        if ext == ".cdi":
            return cls.from_cdi(padus.Cdi(filename))
        elif ext == ".chd":
            # TODO: mame.Chd
            raise NotImplementedError()
        elif ext == ".cue":
            raise NotImplementedError()
        elif ext == ".gdi":
            return cls.from_gdi(Gdi.from_file(filename))
        else:
            raise RuntimeError(f"Unsupported file extension: {ext}")
