"""Tools for opening and searching .iwd & .pk3 archives"""
import enum
import fnmatch
import os
import struct
import zipfile
import zlib


# TODO: Nexon .pkg loader
# TODO: Valve .vpk loader
# -- BlackMesa, Infra, SinEpisodes, DarkMessiah all store maps in .vpk
# TODO: Respawn .vpk loader  (make a pull request to ValvePython/vpk)
# -- copy functionality from mrsteyk/RSPNVPK (with permission ofc)
# TODO: Bluepoint .bpk loader (Titanfall for the Xbox360)
# TODO: IdTech .pak loader  (https://quakewiki.org/wiki/.pak)
# -- yquake2/pakextract or Slartibarty/PAKExtract are good tools

# NOTE: you could access raw .bsp files with Zipfile.read("filename.bsp"), but bsp_tool doesn't accept open files
# -- e1m1 = IdTechBsp(quake, "maps/e1m1.bsp")
# -- e1m1.file = pak000.read("maps/e1m1.bsp")
# -- e1m1._preload()

class Pk3(zipfile.ZipFile):
    """Quake & Call of Duty 1 .bsps are stored in .pk3 files, which are basically .zip archives"""
    def extract_match(self, pattern="*.bsp", path=None):
        for filename in self.search(pattern):
            self.extract(filename, path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)


class Iwd(Pk3):
    """Call of Duty 2 .bsps are stored in .iwd files, which are basically .zip archives"""
    pass


class FastFile:  # TODO: provide a zipfile.ZipFile-like interface
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


def search_folder(folder, pattern="*.bsp", archive="*.pk3"):
    for pk3_filename in fnmatch.filter(os.listdir(folder), archive):
        print(pk3_filename)
        pk3 = Pk3(os.path.join(folder, pk3_filename))
        print(*["\t" + bsp for bsp in pk3.search(pattern)], sep="\n", end="\n\n")


def extract_folder(folder, pattern="*.bsp", path=None, archive="*.pk3"):
    for archive_filename in fnmatch.filter(os.listdir(folder), archive):
        archive_file = Pk3(os.path.join(folder, archive_filename))  # works on any zip-like format
        archive_file.extract_match(pattern=pattern, path=path)
