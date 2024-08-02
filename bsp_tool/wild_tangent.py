"""Genesis3D engine originally by Eclipse Entertainment"""
from __future__ import annotations
import io
from types import ModuleType

from . import id_software


class Genesis3DBsp(id_software.IdTechBsp):
    """Cursed, but clearly IdTech based"""
    file_magic = b"GBSP"
    # struct ChunkHeader { uint32_t id, size, count; };
    # struct HeaderChunk { char tag[5]; uint32_t version; SYSTEMTIME BSPTime; };

    # TODO: mount_lump: validate header.size against sizeof(LumpClass)

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> Genesis3DBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors = dict()
        lump_header = bsp.branch.LumpHeader()
        while bsp.branch.LUMP(lump_header.id) != bsp.branch.LUMP.END:
            lump_header = bsp.branch.LumpHeader.from_stream(bsp.file)
            lump_name = bsp.branch.LUMP(lump_header.id).name
            lump_header.offset = bsp.file.tell()
            lump_header.length = lump_header.size * lump_header.count
            bsp.mount_lump(lump_name, lump_header, bsp.file)
            bsp.headers[lump_name] = lump_header
            bsp.file.seek(lump_header.offset + lump_header.length)
        # validate & use HEADER lump
        # NOTE: the Header "chunk" might be optional
        assert bsp.headers["HEADER"].count == 1
        assert bsp.HEADER.magic == bsp.file_magic
        assert bsp.HEADER.version == bsp.branch.BSP_VERSION
        bsp.version = bsp.HEADER.version
        # collect metadata
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # TODO: any trailing data after END header?
        return bsp
