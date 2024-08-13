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
    data_area: io.BytesIO  # GD-ROM Data Area
    pvd: cdrom.PrimaryVolumeDescriptor
    path_table: List[cdrom.PathTableEntry]

    def __init__(self):
        self.pvd = list()
        self.path_table = list()

    def __repr__(self):
        id_ = " ".join(
            getattr(self.header, attr)
            for attr in ("product_num", "game", "version"))
        return f"<GDRom {id_} @ 0x{id(self):016X}>"

    def full_path(self, path_table_index: int) -> str:
        if path_table_index == 0:
            return "/"
        path = self.path_table[path_table_index]
        names = [path.name]
        while path.parent_index != 1:
            path = self.path_table[path.parent_index - 1]
            names.append(path.name)
        return "/" + "/".join(reversed(names)) + "/"

    def path_records(self, path_index: int) -> List[cdrom.Directory]:
        path = self.path_table[path_index]
        lba = path.extent_lba - self.data_area_lba
        self.data_area.seek(lba * self.pvd.block_size)
        # grab Directory records at top of the path extent
        # NOTE: it might be possible to get the number or files
        # -- instead of depending on hitting null bytes
        directory = cdrom.Directory.from_stream(self.data_area)
        records = list()
        while directory is not None:
            records.append(directory)
            directory = cdrom.Directory.from_stream(self.data_area)
        return records

    def listdir(self, search_folder: str) -> List[str]:
        # NOTE: search_folder is case sensitive
        search_folder.replace("\\", "/")
        search_folder = f"/{search_folder}/"
        search_folder = search_folder.replace("//", "/")  # eliminate doubles
        folders = [self.full_path(i) for i, path in enumerate(self.path_table)]
        assert search_folder in folders, "path not found"
        path_index = folders.index(search_folder)
        records = self.path_records(path_index)
        assert records[0].name == "."
        assert records[1].name == ".."
        # NOTE: we could add a "/" to the end of a name if it's not a file
        return [f.name for f in records[2:]]

    def namelist(self) -> List[str]:
        filenames = set()
        for i, path in enumerate(self.path_table):
            path_name = self.full_path(i).lstrip("/")
            for record in self.folder_contents(i):
                if record.is_file:
                    filenames.add(path_name + record.name)
        return sorted(filenames)

    def tree(self, head=1, depth=0):
        # NOTE: folders only
        for path in self.path_table[1:]:
            if path.parent_index == head:
                print(f"{'  ' * depth}{path.name}/")
                self.tree(self.path_table.index(path) + 1, depth + 1)

    @classmethod
    def from_cdi(cls, cdi: padus.Cdi) -> GDRom:
        # validate our assumptions
        assert len(cdi.sessions) == 2  # CD area (soundtrack), GD area (game)
        assert len(cdi.sessions[1]) == 1  # 1 Track
        assert cdi.sessions[1][0].mode == padus.TrackMode.Mode2  # binary data (.iso)
        # Session 2 - Track 1 is the GD Area
        data_area_bytes = cdi.read("1.0.iso")
        data_area_lba = cdi.sessions[1][0].start_lba
        out = cls.from_data_area(data_area_bytes, data_area_lba)
        out.cdi = cdi  # DEBUG
        # TODO: we shouldn't have to keep the CDI
        # -- for not it's handy for checking things & grabbing other tracks
        # -- in future we need to map the WHOLE GD-ROM on our own
        return out

    @classmethod
    def from_data_area(cls, data_area_bytes: bytes, data_area_lba: int = 0) -> GDRom:
        # NOTE: if data_area_lba = 0 we've got the entire 1GB+ disc in memory
        # -- and the main PVD definitely isn't going to be @ 0x8000
        # NOTE: using data_area_bytes because of how we locate PVDs
        # -- io.BytesIO would be nicer
        out = cls()
        out.data_area_lba = data_area_lba
        out.data_area = io.BytesIO(data_area_bytes)
        # boot header
        out.header = Header.from_stream(out.data_area)
        # 1st PVD filesystem
        pvd_addresses = binary.find_all(data_area_bytes, b"\x01CD001")
        assert len(pvd_addresses) > 0, "no PrimaryVolumeDescriptor found in GD Area"
        assert pvd_addresses[0] == 0x8000
        # NOTE: there should be a 2nd PVD @ 0x9800 or so
        # -- we're skipping that one for now; LBA correction put it's address in the negatives
        out.data_area.seek(0x8000)  # 1st PVD
        out.pvd = cdrom.PrimaryVolumeDescriptor.from_stream(out.data_area)
        # NOTE: it should be possible to navigate via pvd.root_directory
        # -- rather than via the path table
        # -- but it would be nice for both ways to work
        # -- that way we can check for discrepancies between the two
        # path table
        path_table_lba = out.pvd.path_table_le_lba - out.data_area_lba
        out.data_area.seek(path_table_lba * out.pvd.block_size)
        raw_path_table = out.data_area.read(out.pvd.path_table_size)
        path_table_stream = io.BytesIO(raw_path_table)
        out.path_table = list()
        while path_table_stream.tell() < out.pvd.path_table_size:
            entry = cdrom.PathTableEntry.from_stream(path_table_stream)
            out.path_table.append(entry)
        assert path_table_stream.tell() == out.pvd.path_table_size
        # NOTE: we're ignoring the optional path table, and the big-endian stuff too
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
        # -- .cdi .gdi+.bin/.raw .cue+.bin/.raw
        assert filename.lower().endswith(".cdi")
        return cls.from_cdi(padus.Cdi(filename))
