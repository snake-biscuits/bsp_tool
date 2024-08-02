import io
import struct
from typing import Any

from . import valve


class NexonBsp(valve.ValveBsp):
    file_magic = b"VBSP"
    revision: int = 0
    # struct SourceBspHeader { char file_magic[4]; int version; LumpHeader headers[64]; int revision; };

    def mount_lump(self, lump_name: str, lump_header: Any, stream: io.BytesIO):
        assert self.endianness == "little"  # please
        lump_header.fourCC = struct.unpack("<I", struct.pack(">I", lump_header.fourCC))[0]
        super(NexonBsp, self).mount_lump(lump_name, lump_header, stream)
