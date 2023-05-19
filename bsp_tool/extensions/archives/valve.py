from . import base


class Vpk(base.Archive):
    """BlackMesa, Infra, SinEpisodes, DarkMessiah all store maps in .vpk"""
    # https://github.com/ValvePython/vpk
    # ^ wrap into a zipfile.ZipFile-like interface?

    def __init__(self, filename: str):
        raise NotImplementedError()
