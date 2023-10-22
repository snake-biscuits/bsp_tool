import zipfile

from . import base


class Pak(base.Archive):
    # https://quakewiki.org/wiki/.pak
    ext = "*.pak"

    def __init__(self):
        raise NotImplementedError()


class Pk3(zipfile.ZipFile, base.Archive):
    """IdTech .bsps are stored in .pk3 files, which are basically .zip archives"""
    ext = "*.pk3"
