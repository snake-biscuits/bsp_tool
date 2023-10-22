from . import base


class Vpk(base.Archive):
    ext = "*.vpk"

    def __init__(self, filename: str):
        raise NotImplementedError()
