import enum
import struct
import zlib

from . import id_software


class Iwd(id_software.Pk3):
    ext = "*.iwd"


class FastFile:
    """Work In Progress"""
    # TODO: provide a zipfile.ZipFile-like interface
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_Partial_Fastfile_Decompile  # .ff -> .dat
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_FastFile_Format  # .dat -> .*
    # https://github.com/eon8ight/cod4-prealpha/blob/master/ff-deflate.sh
    # (dd if="$1" ibs=28 skip=1 | zlib-flate -uncompress) > "$outfile"
    # file.seek(28), zlib.uncompress

    class FileType(enum.Enum):
        XMODEL_PIECES = 0x00
        PHYS_PRESET = 0x01
        XANIM = 0x02
        XMODEL = 0x03
        MATERIAL = 0x04
        PIXEL_SHADER = 0x05
        TECH_SET = 0x06
        IMAGE = 0x07
        SND_CURVE = 0x08
        LOADED_SOUND = 0x09
        COL_MAP_SP = 0x0A
        COL_MAP_MP = 0x0B
        COM_MAP = 0x0C
        GAME_MAP_SP = 0x0D  # .d3dbsp
        GAME_MAP_MP = 0x0E  # .d3dbsp
        MAP_ENTS = 0x0F  # .ent?
        GFX_MAP = 0x10
        LIGHT_DEF = 0x11
        UI_MAP = 0x12
        FONT = 0x13
        MENU_FILE = 0x14
        MENU = 0x15
        LOCALISATION = 0x16
        WEAPON = 0x17  # .gsc?
        SND_DRIVER_GLOBALS = 0x18
        IMPACT_FX = 0x19
        AI_TYPE = 0x1a
        MP_TYPE = 0x1b
        CHARACTER = 0x1c
        XMODEL_ALIAS = 0x1D
        UNKNOWN_30 = 0x1E
        RAW_FILE = 0x1F
        STRING_TABLE = 0x20  # .csv

    def __init__(self, filename: str):
        with open(filename, "rb") as ff_file:
            ff_header = struct.unpack("8sI", ff_file.read(12))
            assert ff_header == (b"IWffu100", 5), "Unexpected .ff format / version"
            decompressed_bytes = zlib.decompress(ff_file.read())  # TODO: use bytesIO
        with open(f"{filename}.dat", "wb") as dat_file:
            dat_file.write(decompressed_bytes)
        dat_header = struct.unpack("11I", decompressed_bytes[:44])
        # struct { int decompressed_size, total_size, flags, unknown_1[2], some_size, unknown_2[5] } dat_header;
        # decompressed_size = header[0]  # len(decompressed_bytes) - 44
        # total_size = header[1]
        # flags = header[2]  # unsure of use
        # 2 unknown ints (0)
        # some_size = header[5]  # size without headers & separators?
        # 5 unknown ints (0)
        print(dat_header)

        # STRING LIST INDEX
        # STRING lIST
        # DATA BLOCK INDEX
        # DATA BLOCKS

        # 0xFFFFFFFF separators between blocks

        # contents = {"filename": (start_index, data_length)}
        index_count, separator1, filetype_id, separator2 = struct.unpack("4I", decompressed_bytes[44:44 + 16])
        # assert separator1 == separator2 == 0xFFFFFFFF
        print(index_count, hex(separator1), filetype_id, hex(separator2))
        print(self.FileType(filetype_id).name)
