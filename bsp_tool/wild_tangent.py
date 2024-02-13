# NOTE: Genesis3D engine originally by Eclipse Entertainment
import os

from . import id_software


class Genesis3DBsp(id_software.IdTechBsp):
    """Cursed, but clearly IdTech based"""
    file_magic = b"GBSP"
    # struct ChunkHeader { uint32_t id, size, count; };
    # struct HeaderChunk { char tag[5]; uint32_t version; SYSTEMTIME BSPTime; };

    # TODO: _preload_lump: validate header.size against sizeof(LumpClass)

    def _preload(self):
        # collect files
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect lumps
        self.headers = dict()
        self.loading_errors = dict()
        lump_header = self.branch.LumpHeader()
        while self.branch.LUMP(lump_header.id) != self.branch.LUMP.END:
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            lump_name = self.branch.LUMP(lump_header.id).name
            lump_header.offset = self.file.tell()
            lump_header.length = lump_header.size * lump_header.count
            self._preload_lump(lump_name, lump_header)
            self.headers[lump_name] = lump_header
            self.file.seek(lump_header.offset + lump_header.length)
        # validate & use HEADER lump
        # NOTE: the Header "chunk" might be optional
        assert self.headers["HEADER"].count == 1
        assert self.HEADER.magic == self.file_magic
        assert self.HEADER.version == self.branch.BSP_VERSION
        self.version = self.HEADER.version
        # collect metadata
        self.file.seek(0, 2)  # move cursor to end of file
        self.filesize = self.file.tell()
        # TODO: any trailing data after END header?
