import zipfile

from . import base


class Pak(base.Archive):
    # https://quakewiki.org/wiki/.pak
    # yquake2/pakextract & Slartibarty/PAKExtract are good existing tools
    def __init__(self):
        raise NotImplementedError()


class Pk3(zipfile.ZipFile, base.Archive):
    """IdTech .bsps are stored in .pk3 files, which are basically .zip archives"""
    # NOTE: "*.pk3" is also used for some DOOM engine source ports
    # -- folders fitting the pattern "*.pk3dir" can be used to mount files in some cases
