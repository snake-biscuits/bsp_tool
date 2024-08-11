from . import base


class Hfs(base.Archive):
    ext = "*.hfs"

    def __init__(self, filename: str):
        raise NotImplementedError()


class Pkg(base.Archive):
    ext = "*.pkg"

    def __init__(self, filename: str):
        raise NotImplementedError()
