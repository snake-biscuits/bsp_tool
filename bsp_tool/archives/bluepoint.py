from . import base


class Bpk(base.Archive):
    """Titanfall (Xbox360) asset archive format"""
    ext = "*.bpk"

    def __init__(self, filename: str):
        raise NotImplementedError()
