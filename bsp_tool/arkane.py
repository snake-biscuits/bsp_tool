import os
import struct
from typing import Dict

from . import lumps
from . import valve


class ArkaneBsp(valve.ValveBsp):
    def __repr__(self):
        major, minor = self.bsp_version
        version = f"({self.file_magic.decode('ascii', 'ignore')} version {major}.{minor})"
        game = self.branch.__name__[len(self.branch.__package__) + 1:]
        return f"<{self.__class__.__name__} '{self.filename}' {game} {version} at 0x{id(self):016X}>"

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file} is not a valid .bsp!"
        self.bsp_version = tuple(*struct.iter_unpack("2h", self.file.read(4)))
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_NAME = LUMP_enum.name
            self.headers[LUMP_NAME] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP_NAME == "GAME_LUMP":
                    GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                    BspLump = lumps.GameLump(self.file, lump_header, GameLumpClasses, self.branch.GAME_LUMP_HEADER)
                elif LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME][lump_header.version]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME][lump_header.version]
                    decompressed_file, decompressed_header = lumps.decompressed(self.file, lump_header)
                    decompressed_file.seek(decompressed_header.offset)
                    lump_data = decompressed_file.read(decompressed_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME][lump_header.version]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except KeyError:  # lump VERSION not supported
                self.loading_errors[LUMP_NAME] = KeyError(f"{LUMP_NAME} v{lump_header.version} is not supported")
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)
