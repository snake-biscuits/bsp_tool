"""ISO-9660 / ECMA-119 Disc Image Format"""
# https://wiki.osdev.org/ISO_9660

from __future__ import annotations
import datetime
import enum
import io
import os
from typing import List

from ..utils import binary
from . import base


# NOTE: Logical Block Address -> Byte Address:
# -- LBA * LB_size = BA


def read_both_endian(stream: io.BytesIO, format_: str) -> int:
    """process one field at a time, don't try for multiple!"""
    little_endian = binary.read_struct(stream, f"<{format_}")
    big_endian = binary.read_struct(stream, f">{format_}")
    assert little_endian == big_endian
    return little_endian


strD = {
    *{chr(x) for x in range(ord("a"), ord("z") + 1)},
    *{chr(x) for x in range(ord("A"), ord("Z") + 1)},
    *{chr(x) for x in range(ord("0"), ord("9") + 1)},
    *"._ []"}

strA = {
    *strD,
    *"!\"%&\'()*+,-./:;<=>?"}


def read_strA(stream: io.BytesIO, length: int) -> str:
    """ASCII A-Z 0-9 & underscore"""
    raw_str = binary.read_struct(stream, f"{length}s")
    out = raw_str.decode().rstrip(" ")
    assert len(set(out).difference(strA)) == 0, f"{out!r} is not a valid strA"
    return out


def read_strD(stream: io.BytesIO, length: int) -> str:
    """ASCII A-Z 0-9 & common symbols"""
    raw_str = binary.read_struct(stream, f"{length}s")
    out = raw_str.decode().rstrip(" ")
    assert len(set(out).difference(strD)) == 0, f"{out!r} is not a valid strD"
    return out


class TimeStamp:
    year: int  # 1..9999
    month: int  # 1..12
    day: int  # 1..31
    hour: int  # 0..23
    minute: int  # 0..59
    second: int  # 0..59
    centisecond: int  # 0..99 (100ths of a second)
    # NOTE: all timezones parsed so far seem incorrect
    timezone: int  # 15 min increments from GMT
    # -48 (West) -> 52 (East)
    # GMT-12 -> GMT+13

    def __init__(self, year, month, day, hour, minute, second, centisecond, timezone):
        assert 1 <= year <= 9999, year
        self.year = year
        assert 1 <= month <= 12, month
        self.month = month
        assert 1 <= day <= 31, day
        self.day = day
        assert 0 <= hour <= 23, hour
        self.hour = hour
        assert 0 <= minute <= 59, minute
        self.minute = minute
        assert 0 <= second <= 59, second
        self.second = second
        assert 0 <= centisecond <= 99, centisecond
        self.centisecond = centisecond
        # assert 0 <= timezone <= 100, timezone  # !!! BREAKING !!!
        self.timezone = timezone

    def __repr__(self) -> str:
        try:  # some valid TimeStamps fall outside the range of valid DateTimes
            time_string = self.as_datetime().strftime("%Y/%m/%d (%a) %H:%M:%S.%f")
            return f"<{self.__class__.__name__} {time_string}>"
        except Exception:  # TODO: be more specific
            args = [
                self.year, self.month, self.day,
                self.hour, self.minute, self.second, self.centisecond,
                self.timezone]
            return f"{self.__class__.__name__}({', '.join(args)})"

    def as_datetime(self) -> datetime.datetime:
        # NOTE: year must be >= 1601
        # TODO: timezone
        return datetime.datetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second, self.centisecond * 10000)

    @classmethod
    def from_stream_ascii(cls, stream: io.BytesIO) -> TimeStamp:
        """mostly ASCII for PVD (17 bytes)"""
        year = int(read_strD(stream, 4))
        month = int(read_strD(stream, 2))
        day = int(read_strD(stream, 2))
        hour = int(read_strD(stream, 2))
        minute = int(read_strD(stream, 2))
        second = int(read_strD(stream, 2))
        centisecond = int(read_strD(stream, 2))
        timezone = binary.read_struct(stream, "B")
        if {year, month, day, hour, minute, second, centisecond, timezone} == {0}:
            return None  # valid data, but not a timestamp
        return cls(year, month, day, hour, minute, second, centisecond, timezone)

    @classmethod
    def from_stream_bytes(cls, stream: io.BytesIO) -> TimeStamp:
        """compressed form for Directories & Path Table (7 bytes)"""
        year, month, day = binary.read_struct(stream, "3B")
        hour, minute, second = binary.read_struct(stream, "3B")
        centisecond = 0
        timezone = binary.read_struct(stream, "B")
        if {year, month, day, hour, minute, second, centisecond, timezone} == {0}:
            return None  # valid data, but not a timestamp
        return cls(year, month, day, hour, minute, second, centisecond, timezone)


class FileFlag(enum.IntFlag):
    HIDDEN = 1 << 0
    DIRECTORY = 1 << 1
    ASSOCIATED = 1 << 2  # is an "Associated File", whatever that means
    FORMAT_IN_EAR = 1 << 3  # Extended Attribute Record has info on format
    PERMISSIONS_IN_EAR = 1 << 4  # Owner & Group permissions are stored in the EAR
    # NOTE: bits 5 & 6 are reserved
    NOT_FINAL_DIR = 1 << 7


class Directory:
    length: int
    ear_length: int
    data_lba: int  # LBA of data extent
    data_size: int  # size of data extent (in bytes)
    timestamp: TimeStamp
    flags: FileFlag
    interleaved_unit_size: int  # "file unit size"; 0 if not interleaved
    interleaved_gap_size: int  # 0 if not interleaved
    volume_sequence_index: int  # volume this extent is recorded on
    name: str
    is_file: bool
    extras: bytes  # unsupported bonus data; None if not present

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.name}" @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Directory:
        out = cls()
        out.length, out.ear_length = binary.read_struct(stream, "2B")
        if out.length == 0:
            return None  # for if we're at the end of a directory list
        # NOTE: ear is short for "Extended Attribute Record"
        out.data_lba = read_both_endian(stream, "I")
        out.data_size = read_both_endian(stream, "I")
        out.timestamp = TimeStamp.from_stream_bytes(stream)
        out.flags = FileFlag(binary.read_struct(stream, "B"))
        out.interleaved_unit_size = binary.read_struct(stream, "B")
        out.interleaved_gap_size = binary.read_struct(stream, "B")
        out.volume_sequence_index = read_both_endian(stream, "H")
        # name & file / directory identification
        filename_length = binary.read_struct(stream, "B")
        filename = binary.read_struct(stream, f"{filename_length}s")
        if filename_length == 1:  # special directory
            out.is_file = False
            if filename == b"\x00":  # PVD.root_directory / 1st in sequence
                out.name = "."  # local root
            elif filename == b"\x01":  # 2nd in sequence
                out.name = ".."  # parent
            else:
                raise RuntimeError(f"Unexpected File ID: {filename!r}")
        elif filename.endswith(b";1"):  # named file
            out.is_file = True
            out.name = filename.decode()[:-2]
            # verify name is valid strD ("." is also allowed)
            assert len(set(out.name).difference(strD)) == 0, "invalid strD"
        else:  # named directory
            # NOTE: haven't encountered any of these yet
            out.is_file = False  # directory
            out.name = filename.decode()
        # optional 1 byte pad (next Directory will start on an even address)
        if filename_length % 2 == 0:
            assert stream.read(1) == b"\x00"
        expected_length = 33 + filename_length + (filename_length + 1) % 2
        # TODO: got some ISO extensions, not interested in supporting those rn
        if out.length != expected_length:
            out.extras = stream.read(out.length - expected_length)
        else:
            out.extras = None
        assert out.ear_length == 0, "idk where EAR data is stored"
        return out


class PathTableEntry:
    length: int  # preserved for asserts
    ear_length: int  # preserved for asserts
    extent_lba: int  # LBA of extent containing directory data
    parent_index: int  # path table index of parent dir (65536 limit)
    # NOTE: parent index starts from 1, not 0
    # -- root is first, and indexes itself (1)
    name: str

    def __repr__(self) -> str:
        path_name = "/" if self.name is None else f"{self.name}/"
        return f"<PathTableEntry {path_name} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_entry: bytes) -> PathTableEntry:
        return cls.from_stream(io.BytesIO(raw_entry))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PathTableEntry:
        # NOTE: little-endian only
        out = cls()
        out.length, out.ear_length = binary.read_struct(stream, "2B")
        # NOTE: ear is short for "Extended Attribute Record"
        out.extent_lba = binary.read_struct(stream, "I")
        out.parent_index = binary.read_struct(stream, "H")
        name = binary.read_struct(stream, f"{out.length}s")
        if name != b"\x00":  # verify strD
            name = name.decode()
            assert len(set(name).difference(strD)) == 0, "invalid strD"
            out.name = name
        else:
            out.name = None
        # optional 1 byte pad (next entry will start on an even address)
        if out.length % 2 != 0:
            assert stream.read(1) == b"\x00"
        assert out.ear_length == 0, "idk where EAR data is stored"
        return out


class PrimaryVolumeDescriptor:
    system: str  # who can boot from the first 16 sectors of this disc
    name: str
    size_in_blocks: int  # size of volume in Logical Blocks
    num_discs: int  # in a set
    dics: int  # index of this disc in it's set
    block_size: int  # size of a Logical Block (typically 2048)
    path_table_size: int  # in bytes
    path_table_le_lba: int  # Logical Block Address of Little-Endian Path Table
    opt_path_table_le_lba: int  # Logical Block Address of Optional Little-Endian Path Table
    path_table_be_lba: int  # Logical Block Address of Big-Endian Path Table
    opt_path_table_be_lba: int  # Logical Block Address of Optional Big-Endian Path Table
    # NOTE: optinal path table addresses are 0 if absent
    root_dir: Directory
    set_name: str  # name of the set this dics belongs to
    publisher: str  # name of volume publisher (extended w/ "_" @ start)
    data_preparer: str  # who prepared data for this volume (extended w/ "_" @ start)
    application: str  # how data is recorded (extended w/ "_" @ start)
    copyright_file: str
    abstract_file: str
    bibliography_file: str
    volume_created: TimeStamp
    volume_modified: TimeStamp
    volume_expires: TimeStamp  # when obsolete; can be None
    volume_effective: TimeStamp  # release date; can be None
    application_bytes: bytes  # observed: either all ASCII whitespace or null bytes

    def __init__(self):
        self.system = "Win32"
        self.name = "Untitled"
        # TODO: more defaults

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.name}" @ 0x{id(self):016X}>'

    def __str__(self) -> str:
        # TODO: pretty printed table of various data
        raise NotImplementedError()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PrimaryVolumeDescriptor:
        out = cls()
        type_code = binary.read_struct(stream, "B")
        assert type_code == 0x01, type_code  # 0x01: Primary, 0x02: Supplementary, 0x03: Partition
        magic = binary.read_struct(stream, "5s")
        assert magic == b"CD001"
        version = binary.read_struct(stream, "H")  # technically uint8 + 1 char pad
        assert version == 0x0001
        out.system = read_strA(stream, 32)
        out.name = read_strD(stream, 32)
        assert stream.read(8) == b"\x00" * 8
        out.size_in_blocks = read_both_endian(stream, "I")
        assert stream.read(32) == b"\x00" * 32
        out.num_discs = read_both_endian(stream, "H")
        out.disc = read_both_endian(stream, "H")
        out.block_size = read_both_endian(stream, "H")
        out.path_table_size = read_both_endian(stream, "I")  # in bytes
        out.path_table_le_lba = binary.read_struct(stream, "<I")
        out.opt_path_table_le_lba = binary.read_struct(stream, "<I")
        out.path_table_be_lba = binary.read_struct(stream, ">I")
        out.opt_path_table_be_lba = binary.read_struct(stream, ">I")
        out.root_dir = Directory.from_stream(stream)
        # TODO: assert root_dir was 34 bytes long
        out.set_name = read_strD(stream, 128)
        out.publisher = read_strA(stream, 128)
        out.data_preparer = read_strA(stream, 128)
        out.application = read_strA(stream, 128)
        # filenames in root dir
        out.copyright_file = read_strD(stream, 37)
        out.abstract_file = read_strD(stream, 37)
        out.bibliography_file = read_strD(stream, 37)
        # timestamps
        out.volume_created = TimeStamp.from_stream_ascii(stream)
        out.volume_modified = TimeStamp.from_stream_ascii(stream)
        out.volume_expires = TimeStamp.from_stream_ascii(stream)  # when obsolete (can be zeroed?)
        out.volume_effective = TimeStamp.from_stream_ascii(stream)  # release date (can be zeroed?)
        file_structure_version = binary.read_struct(stream, "H")  # techically uint8_t + 1 char pad
        assert file_structure_version == 0x0001
        out.application_bytes = stream.read(512)  # empty ASCII whitespace
        reserved = stream.read(653)  # ISO reserved bytes (typically all NULL)
        assert reserved == b"\x00" * 653, "unexpected data in RESERVED section"
        # make sure we're terminated
        terminator = stream.read(7)
        while terminator != b"\xFFCD001\x01":
            assert terminator[1:] == b"CD001\x01", "Couldn't find next VolumeDescriptor"
            assert terminator[0] in (0x02, 0x03), f"0x{terminator[0]:02X} is not a valid VolumeDescriptor type"
            # NOTE: 0x02: Supplementary, 0x03: Partition, 0x04..0xFE: Reserved
            # TODO: userwarning / add to Iso.import_log somehow
            print("skipping", {0x02: "Supplementary", 0x03: "Partition"}[terminator[0]], "Volume Descriptor")
            stream.seek(2048 - 7, 1)  # try the next Logical Block
            terminator = stream.read(7)
        return out


class Iso(base.Archive):
    ext = "*.iso"  # sometimes "*.bin"
    lba_offset: int  # add this offset to all LBA address lookups
    # GD-ROM Filesystems need a -ve lba_offset because we isolate the GD Area
    # So LBAs start in the thousands, rather than the low teens
    # Other PVDs might have the opposite problem, for those we need a +ve offset
    disc: io.BytesIO  # kept open for reads
    pvd: PrimaryVolumeDescriptor
    path_table: List[PathTableEntry]

    def __init__(self):
        self.lba_offset = 0
        # TODO: blank disc image
        # TODO: default PVD
        self.path_table = list()

    def __repr__(self) -> str:
        return f'<Iso {self.pvd.name!r} {len(self.namelist())} files @ 0x{id(self):016X}>'

    def folder_records(self, search_folder: str) -> List[Directory]:
        # NOTE: search_folder is case sensitive
        # TEST: "" & "/" should both index root
        # -- maybe also "." & "./"
        # TODO: is it easier to walk the directory tree?
        search_folder.replace("\\", "/")
        search_folder = f"/{search_folder}/"
        while "//" in search_folder:  # eliminate double slashes
            # NOTE: have to replace twice for root ("/")
            search_folder = search_folder.replace("//", "/")
        folders = [self.full_path(i) for i, path in enumerate(self.path_table)]
        assert search_folder in folders, f"couldn't find {search_folder!r}"
        path_index = folders.index(search_folder)
        return self.path_records(path_index)

    def full_path(self, path_table_index: int) -> str:
        if path_table_index == 0:
            return "/"
        path = self.path_table[path_table_index]
        names = [path.name]
        while path.parent_index != 1:
            path = self.path_table[path.parent_index - 1]
            names.append(path.name)
        return "/" + "/".join(reversed(names)) + "/"

    def path_records(self, path_index: int) -> List[Directory]:
        path = self.path_table[path_index]
        lba = path.extent_lba + self.lba_offset
        self.disc.seek(lba * self.pvd.block_size)
        # grab Directory records at top of the path extent
        # NOTE: it might be possible to get the number or files
        # -- instead of depending on hitting null bytes
        directory = Directory.from_stream(self.disc)
        records = list()
        while directory is not None:
            records.append(directory)
            directory = Directory.from_stream(self.disc)
        return records

    def listdir(self, search_folder: str) -> List[str]:
        # NOTE: search_folder is case sensitive
        records = self.folder_records(search_folder)
        assert records[0].name == "."
        assert records[1].name == ".."
        # NOTE: we could add a "/" to the end of a name if it's not a file
        return [f.name for f in records[2:]]

    def namelist(self) -> List[str]:
        filenames = set()
        for i, path in enumerate(self.path_table):
            path_name = self.full_path(i).lstrip("/")
            for record in self.path_records(i):
                if record.is_file:
                    filenames.add(path_name + record.name)
        return sorted(filenames)

    def read(self, filename: str) -> bytes:
        # NOTE: case sensitive
        folder, filename = os.path.split(filename)
        records = {r.name: r for r in self.folder_records(folder)}
        assert filename in records, "file not found"
        record = records[filename]
        assert record.is_file, "f{filename!r} is not a file"
        if record.data_interleaved_unit_size != 0 or record.data.interleaved_gap_size != 0:
            raise NotImplementedError("cannot read interleaved file")
        self.seek(record.data_lba)
        return self.disc.read(record.data_size)

    def seek(self, lba: int) -> int:
        true_lba = lba + self.lba_offset
        return self.disc.seek(true_lba * self.pvd.block_size)

    @classmethod
    def from_bytes(cls, raw_iso: bytes, pvd_address: int = None, lba_offset: int = 0) -> Iso:
        # NOTE: only from_bytes will search for PVDs
        if pvd_address is None:  # default to the first PVD (typically 0x8000)
            pvd_address = raw_iso.find(b"\x01CD001")
            assert pvd_address != -1, "Iso has no PrimaryVolumeDescriptor"
        return cls.from_stream(io.BytesIO(raw_iso), pvd_address, lba_offset)

    @classmethod
    def from_file(cls, filename: str, pvd_address: int = 0x8000, lba_offset: int = 0) -> Iso:
        return cls.from_stream(open(filename, "rb"), pvd_address, lba_offset)

    @classmethod
    def from_stream(cls, stream: io.BytesIO, pvd_address: int = 0x8000, lba_offset: int = 0) -> Iso:
        out = cls()
        out.disc = stream
        out.lba_offset = lba_offset
        # PVD
        stream.seek(pvd_address)
        out.pvd = PrimaryVolumeDescriptor.from_stream(out.disc)
        # PathTable
        path_table_lba = out.pvd.path_table_le_lba + lba_offset
        stream.seek(path_table_lba * out.pvd.block_size)
        # TODO: get the path table without creating a separate stream
        raw_path_table = out.disc.read(out.pvd.path_table_size)
        path_table_stream = io.BytesIO(raw_path_table)
        while path_table_stream.tell() < out.pvd.path_table_size:
            entry = PathTableEntry.from_stream(path_table_stream)
            out.path_table.append(entry)
        assert path_table_stream.tell() == out.pvd.path_table_size
        # NOTE: we're ignoring the optional path table & all the big-endian stuff
        return out
