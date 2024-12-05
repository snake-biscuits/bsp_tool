from __future__ import annotations
import io
from types import ModuleType
from typing import Dict

from . import id_software


class RitualBsp(id_software.IdTechBsp):
    _file_magics = (b"FAKK", b"2015", b"EF2!", b"EALA")
    checksum: int  # TODO: calculate / verify (CRC?)
    # struct LumpHeader { uint32_t offset, length; };
    # struct { uint32_t file_magic, version, checksum; LumpHeader headers[]; };

    @classmethod
    def from_stream(cls, branch: ModuleType, filename: str, stream: io.BytesIO) -> RitualBsp:
        bsp = cls(branch, filename)
        bsp.file = stream
        # collect metadata
        bsp.file_magic = bsp.file.read(4)
        assert bsp.file_magic in bsp._file_magics, f"{bsp.file} is not a valid .bsp!"
        assert bsp.file_magic == bsp.branch.FILE_MAGIC, f"{bsp.file} is not from {[*bsp.branch.GAME_PATHS][0]}!"
        bsp.version = int.from_bytes(bsp.file.read(4), "little")
        bsp.checksum = int.from_bytes(bsp.file.read(4), "little")
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect headers
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=12):
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        return bsp


class SinBsp(id_software.IdTechBsp):
    file_magic = b"RBSP"
    # struct LumpHeader { uint32_t offset, length; }
    # struct { uint32_t file_magic, version; LumpHeader headers[]; };
    # NOTE: basically identical to raven.RavenBsp
    # -- and SiN released before SoF2 (also RBSP v1)
