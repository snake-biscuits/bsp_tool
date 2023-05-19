from . import base


class Bpk(base.Archive):
    """Titanfall (Xbox360) asset archive format"""
    # need xcompress utility
    # TODO: reverse cra0 Titanfall vpk extractor v3.4

    def __init__(self, filename: str):
        raise NotImplementedError()
