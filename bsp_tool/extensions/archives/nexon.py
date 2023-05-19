from . import base


class Pkg(base.Archive):
    """CS:O 2 & TF:O encrypted asset storage"""
    # https://github.com/L-Leite/UnCSO2
    # TODO: split into CS:O 2 & TF:O classes

    def __init__(self, filename: str):
        raise NotImplementedError()


class Hfs(base.Archive):
    """Nexon's Vindictus asset archive format"""
    # https://github.com/yretenai/HFSExtract

    def __init__(self, filename: str):
        raise NotImplementedError()
