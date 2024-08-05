from . import base


class Pkg(base.Archive):
    ext = "*.pkg"

    def __init__(self, filename: str):
        raise NotImplementedError()


class Hfs(base.Archive):
    ext = "*.hfs"

    def __init__(self, filename: str):
        raise NotImplementedError()
