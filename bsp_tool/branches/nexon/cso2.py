"""Counter-Strike: Online 2.  Appears to be similar to Vindictus"""
import collections
import enum
import io
import struct
import zipfile

from . import vindictus
from .. import shared


BSP_VERSION = 100

LUMP = vindictus.LUMP
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])


def read_lump_header(file, LUMP: enum.Enum):
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4i", file.read(16))
    header = LumpHeader(offset, length, version, fourCC)
    return header


# classes for each lump, in alphabetical order: [XX / 64]
...

# NOTE: dcubemap_t varies (160 bytes 2013era, 164 bytes 2017era)
# NOTE: if lighting settings are not Medium, maps from 2013 era crash


# special lump classes, in alphabetical order
class PakFile(zipfile.ZipFile):  # WIP
    """CSO2 PakFiles have a custom .zip format"""
    # b"CS" file magic & different header format?
    def __init__(self, raw_zip: bytes):
        # TODO: translate header to b"PK\x03\x04..."
        raw_zip = b"".join([b"PK", raw_zip[2:]])
        self._buffer = io.BytesIO(raw_zip)
        super(PakFile, self).__init__(self._buffer)

    def as_bytes(self) -> bytes:
        # TODO: translate header to b"CS\x03\x04..."
        raw_zip = self._buffer.getvalue()
        raw_zip = b"".join([b"CS", raw_zip[2:]])
        return raw_zip


LUMP_CLASSES = vindictus.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,
                        "TEXDATA_STRING_DATA": shared.TexDataStringData,
                        "PAKFILE": PakFile}

methods = vindictus.methods
