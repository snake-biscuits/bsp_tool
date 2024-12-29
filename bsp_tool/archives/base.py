from __future__ import annotations
import enum
import fnmatch
import io
import os
from typing import Dict, List, Tuple

from .. import external


def path_tuple(path: str) -> Tuple[str]:
    out = tuple(path.replace("\\", "/").strip("/").split("/"))
    if len(out) > 1 and out[0] == ".":
        return out[1:]
    else:
        return out


class Archive:
    ext = None
    extras: Dict[str, external.File]

    def __init__(self):
        self.extras = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.namelist())} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def extra_patterns(self) -> List[str]:
        """filename patterns for files to mount (e.g. '*.bin')"""
        return list()

    def extract(self, filename, to_path=None):
        if filename not in self.namelist():
            raise FileNotFoundError(f"Couldn't find {filename!r} to extract")
        to_path = "./" if to_path is None else to_path
        out_filename = os.path.join(to_path, filename)
        os.makedirs(os.path.dirname(out_filename), exist_ok=True)
        with open(out_filename, "rb") as out_file:
            out_file.write(self.read(filename))

    def extract_all(self, to_path=None):
        for filename in self.namelist():
            self.extract(filename, to_path)

    def extract_all_matching(self, pattern="*.bsp", to_path=None, case_sensitive=False):
        for filename in self.search(pattern, case_sensitive):
            self.extract(filename, to_path)

    def is_dir(self, filename: str) -> bool:
        all_dirs = {path_tuple(fn)[:-1] for fn in self.namelist()}
        all_dirs.update({tuple_[:i] for tuple_ in all_dirs for i in range(1, len(tuple_))})
        all_dirs.update({path_tuple(root) for root in (".", "./", "/")})
        return path_tuple(filename) in all_dirs

    def is_file(self, filename: str) -> bool:
        return filename in self.namelist()

    def listdir(self, folder: str) -> List[str]:
        if not self.is_dir(folder):
            raise FileNotFoundError(f"no such directory: {folder}")
        folder_tuple = path_tuple(folder)
        if folder_tuple in {path_tuple(root) for root in (".", "./", "/")}:
            folder_tuple = tuple()  # empty
        namelist_tuples = map(path_tuple, self.namelist())
        folder_contents = list()
        for tuple_ in namelist_tuples:
            if tuple_[:-1] == folder_tuple:
                folder_contents.append(tuple_[-1])  # file
            elif tuple_[:len(folder_tuple)] == folder_tuple:
                subfolder = tuple_[len(folder_tuple)] + "/"
                if subfolder not in folder_contents:
                    folder_contents.append(subfolder)
        return folder_contents

    def mount_file(self, filename: str, external_file: external.File):
        self.extras[filename] = external_file

    def namelist(self) -> List[str]:
        # NOTE: we assume namelist only contains filenames, no folders
        raise NotImplementedError("ArchiveClass has not defined .namelist()")

    def path_exists(self, filename: str) -> bool:
        return self.is_file(filename) or self.is_dir(filename)

    def read(self, filename: str) -> bytes:
        raise NotImplementedError("ArchiveClass has not defined .read()")

    def search(self, pattern="*.bsp", case_sensitive=False):
        pattern = pattern if case_sensitive else pattern.lower()
        namelist = self.namelist() if case_sensitive else [fn.lower() for fn in self.namelist()]
        return fnmatch.filter(namelist, pattern)

    def sizeof(self, filename: str) -> int:
        return len(self.read(filename))

    def tree(self, folder: str = ".", depth: int = 0):
        """namelist pretty printer"""
        for filename in self.listdir(folder):
            print(f"{'  ' * depth}{filename}")
            full_filename = os.path.join(folder, filename)
            if self.is_dir(full_filename):
                self.tree(full_filename, depth + 1)

    def unmount_file(self, filename: str):
        self.extras.pop(filename)

    @classmethod
    def from_archive(cls, parent_archive: Archive, filename: str) -> Archive:
        """for ArchiveClasses composed of multiple files"""
        archive = cls.from_bytes(parent_archive.read(filename))
        folder = os.path.dirname(filename)
        extras = [
            filename
            for filename in parent_archive.listdir(folder)
            for pattern in archive.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_archive(full_filename, parent_archive)
            archive.mount_file(filename, external_file)
        return archive

    @classmethod
    def from_bytes(cls, raw_archive: bytes) -> Archive:
        return cls.from_stream(io.BytesIO(raw_archive))

    @classmethod
    def from_file(cls, filename: str) -> Archive:
        archive = cls.from_stream(open(filename, "rb"))
        folder = os.path.dirname(filename)
        extras = [
            filename
            for filename in os.listdir(folder)
            for pattern in archive.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_file(full_filename)
            archive.mount_file(filename, external_file)
        return archive

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Archive:
        raise NotImplementedError("ArchiveClass has not defined .from_stream()")


class TrackMode(enum.Enum):
    AUDIO = 0
    BINARY_1 = 1
    BINARY_2 = 2


class Track:
    mode: TrackMode
    sector_size: int  # 2048, 2336 or 2352
    start_lba: int
    length: int  # in sectors, not bytes
    name: str

    def __init__(self, mode, sector_size, start_lba, length, name):
        self.mode = mode
        assert sector_size in (2048, 2336, 2352)
        self.sector_size = sector_size
        self.start_lba = start_lba
        self.length = length
        self.name = name

    def __repr__(self) -> str:
        args = ", ".join([
            str(getattr(self, a))
            for a in ("mode", "sector_size", "start_lba", "length")])
        return f'Track({args}, "{self.name}")'

    def data_slice(self) -> slice:
        """index raw sector with this slice to get just the data"""
        # TODO: add sector sizes I forgot
        if self.mode == TrackMode.AUDIO or self.sector_size == 2048:
            return slice(0, self.sector_size)
        elif self.mode == TrackMode.BINARY_1:
            header_size = {2352: 16}[self.sector_size]
        elif self.mode == TrackMode.BINARY_2:
            header_size = {2336: 8, 2352: 24}[self.sector_size]
        return slice(header_size, 2048 + header_size)


class DiscImage:
    ext = None
    extras: Dict[str, external.File]
    tracks: List[Track]  # indexes extras with filename
    _cursor: Tuple[int, int]
    # ^ (track_index, sub_lba)
    # NOTE: true_lba = track.start_lba + sub_lba

    def __init__(self):
        self.extras = dict()
        self.tracks = list()
        self._cursor = (0, 0)

    def __repr__(self):
        descriptor = f"{len(self)} sectors ({len(self.tracks)} tracks)"
        # TODO: length in MB / seconds
        # Red Book CD-DA: 44.1 KHz 16-bit PCM Stereo -> 176400 bytes / second
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def __contains__(self, lba: int) -> bool:
        return any([
            track.start_lba <= lba <= track.start_lba + track.length
            for track in self.tracks])

    def __len__(self):
        if len(self.tracks) > 0:
            return max(t.start_lba + t.length for t in self.tracks)
        else:
            return 0

    def export_wav(self, track_index: int, filename: str = None):
        # https://docs.fileformat.com/audio/wav/
        track = self.tracks[track_index]
        assert track.mode == TrackMode.AUDIO, "track is not audio"
        if filename is None:
            if track.name.endswith(".raw"):
                filename = track.name.replace(".raw", ".wav")
            else:
                filename = f"track_{track_index:02d}.wav"
        # generate header
        data_size = track.length * track.sector_size
        wav_header = [
            b"RIFF", (data_size + 36).to_bytes(4, "little"), b"WAVEfmt ",
            b"\x10\x00\x00\x00", b"\x01\x00", b"\x02\x00",
            (44100).to_bytes(4, "little"), (176400).to_bytes(4, "little"),
            b"\x04\x00", b"\x10\x00", b"data", data_size.to_bytes(4, "little")]
        data_stream = self.extras[track.name]
        data_stream.seek(0)  # just in case
        with open(filename, "wb") as wav_file:
            wav_file.write(b"".join(wav_header))
            wav_file.write(data_stream.read())

    def extra_patterns(self) -> List[str]:
        return [track.name for track in self.tracks]

    def mount_file(self, filename: str, external_file: external.File):
        self.extras[filename] = external_file

    def read(self, length: int = -1) -> bytes:
        """moves cursor to end of sector, use with caution"""
        if length == -1:
            return self.sector_read()
        sector_length = length // 2048
        if length % 2048 != 0:
            sector_length += 1
        return self.sector_read(sector_length)[:length]

    def sector_read(self, length: int = -1) -> bytes:
        """expects length in sectors"""
        track_index, sub_lba = self._cursor
        track = self.tracks[track_index]
        if length == -1:
            if track.start_lba + track.length == len(self):  # last track
                length = track.length - sub_lba
            else:
                raise NotImplementedError("cannot read past end of current track")
        if sub_lba + length > track.length:
            raise NotImplementedError("cannot read past end of current track")
        data_slice = track.data_slice()
        track_stream = self.extras[track.name]
        track_stream.seek(sub_lba * track.sector_size)
        sector_data = [
            track_stream.read(track.sector_size)[data_slice]
            for i in range(length)]
        # NOTE: we're assuming that all tracks have gaps between them
        # -- so we don't need to worry about changing tracks here
        self._cursor = (track_index, sub_lba + length)
        return b"".join(sector_data)

    def sector_seek(self, lba: int, whence: int = 0) -> int:
        assert whence in (0, 1, 2)
        current_lba = self.sector_tell()
        if whence == 1:
            lba = current_lba + lba
        elif whence == 2:
            lba = len(self) + lba
        for track_index, track in enumerate(self.tracks):
            if track.start_lba <= lba <= track.start_lba + track.length:
                self._cursor = (track_index, lba - track.start_lba)
                return lba
        raise RuntimeError(f"couldn't find a track containing sector: {lba}")

    def sector_tell(self) -> int:
        track_index, sub_lba = self._cursor
        track = self.tracks[track_index]
        return track.start_lba + sub_lba

    def unmount_file(self, filename: str):
        self.extras.pop(filename)

    @classmethod
    def from_archive(cls, parent_archive: Archive, filename: str) -> DiscImage:
        disc = cls.from_bytes(parent_archive.read(filename))
        folder = os.path.dirname(filename)
        extras = [
            filename
            for filename in parent_archive.listdir(folder)
            for pattern in disc.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_archive(full_filename, parent_archive)
            disc.mount_file(filename, external_file)
        # get track lengths from filesizes (if nessecary)
        for track_index, track in enumerate(disc.tracks):
            if track.length == -1:
                assert disc.extras[track.name].size % track.sector_size == 0
                track.length = disc.extras[track.name].size // track.sector_size
                disc.tracks[track_index] = track
        return disc

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> DiscImage:
        return cls.from_stream(io.BytesIO(raw_data))

    @classmethod
    def from_file(cls, filename: str) -> DiscImage:
        # NOTE: I don't expect "/dev/sr0" or "/dev/cdrom" to work
        disc = cls.from_stream(open(filename, "rb"))
        folder = os.path.dirname(filename)
        extras = [
            filename
            for filename in os.listdir(folder)
            for pattern in disc.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_file(full_filename)
            disc.mount_file(filename, external_file)
        # get track lengths from filesizes (if nessecary)
        for track_index, track in enumerate(disc.tracks):
            if track.length == -1:
                assert disc.extras[track.name].size % track.sector_size == 0
                track.length = disc.extras[track.name].size // track.sector_size
                disc.tracks[track_index] = track
        return disc

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> DiscImage:
        raise NotImplementedError("DiscClass has not defined .from_stream()")
