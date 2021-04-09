"""Tools for opening and searching .iwd & .pk3 archives"""
import fnmatch
import os
import struct
import zipfile
import zlib


# TODO: Nexon .pkg loader
# TODO: Respawn .vpk loader

class Pk3(zipfile.ZipFile):
    """Quake & Call of Duty 1 .bsps are stored in .pk3 files, which are basically .zip archives"""
    def extract_match(self, pattern="*.bsp", path=None):
        for filename in self.search(pattern):
            self.extract(filename, path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)


Iwd = Pk3
Iwd.__doc__ = """Call of Duty 2 .bsps are stored in .iwd files, which are basically .zip archives"""


class FastFile:  # TODO: provide a zipfile.ZipFile-like interface
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_Partial_Fastfile_Decompile  # .ff -> .dat
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_FastFile_Format  # .dat -> .*

    def __init__(self, filename: str):
        file = open(filename, "rb")
        ff_header = struct.unpack("8sI", file.read(12))
        assert ff_header == (b"IWffu100", 5)  # 5 is format version?
        decompressed_bytes = zlib.decompress(file.read())  # TODO: use bytesIO
        file.close()
        header = struct.unpack("11I", decompressed_bytes[:44])
        # decompressed_size = header[0]  # len(decompressed_bytes) - 44
        # total_size = header[1]
        # flags = header[2]  # unsure of use
        # 2 unknown ints (0)
        # some_size = header[5]  # size without headers & separators?
        # 5 unknown ints (0)
        print(header)

        # STRING LIST INDEX
        # STRING lIST
        # DATA BLOCK INDEX
        # DATA BLOCKS

        # 0xFFFFFFFF separators

        filetypes = {0x04: "material", 0x05: "shader", 0x06: "image", 0x13: "font",
                     0x16: "string", 0x1F: "raw_file", 0x20: "string_table"}
        # contents = {"filename": (start_index, data_length)}
        index_count, separator1, filetype_key, separator2 = struct.unpack("4I", decompressed_bytes[44:44 + 16])
        # assert separator1 == separator2 == 0xFFFFFFFF
        print(index_count, hex(separator1), filetype_key, hex(separator2))
        print(filetypes[filetype_key])


def search_folder(folder, pattern="*.bsp", archive="*.pk3"):
    for pk3_filename in fnmatch.filter(os.listdir(folder), archive):
        print(pk3_filename)
        pk3 = Pk3(os.path.join(folder, pk3_filename))
        print(*["\t" + bsp for bsp in pk3.search(pattern)], sep="\n", end="\n\n")


def extract_folder(folder, pattern="*.bsp", path=None, archive="*.pk3"):
    for archive_filename in fnmatch.filter(os.listdir(folder), archive):
        archive_file = Pk3(os.path.join(folder, archive_filename))  # works on any zip-like format
        archive_file.extract_match(pattern=pattern, path=path)
