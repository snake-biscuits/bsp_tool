import os

from . import base
from .branches import respawn


FILE_MAGIC = b"rBSP"


class RespawnBsp(base.Bsp):
    ...  # import external lumps from files

    read_lump = respawn.read_lump

    def load_lumps(self, file):
        # TODO: save contents of .bsp file as INTERNAL_<LUMPNAME>
        for ID in self._engine_branch.LUMP:
            lump_filename = f"{self.filename}.{ID.value:04x}.bsp_lump"
            if lump_filename in self.associated_files:
                header, data = open(f"{os.path.join(self.folder, lump_filename)}", "rb").read()
            else:
                self.log.append(f"external  {ID.name} lump not found")
                header, data = self.read_lump(file, self.branch.lump_header_address[ID])

            self.HEADERS[ID] = header
            if data is not None:
                setattr(self, "RAW_" + ID.name, data)
