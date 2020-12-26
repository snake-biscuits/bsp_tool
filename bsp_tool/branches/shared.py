from typing import List


class Entities:
    _ents: List[str]

    def __init__(self, raw_bytestring):
        self._ents = ...
        ...

    def as_bytes(self):
        return b"\n".join(map(lambda s: s.encode("ascii"), self._ents))


class PakFile:
    def __init__(self, raw_zip_bytes):
        return ...
