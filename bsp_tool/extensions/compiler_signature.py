from __future__ import annotations
from datetime import datetime
import re
from typing import Union


class MRVNRadiant:
    motd: str = "Built with love using MRVN-Radiant :)"  # remap.h REMAP_MOTD
    version: str
    time: datetime
    _time_format: str = "%a %b %d %H:%M:%S %Y"

    def __init__(self, version: str, time: datetime = None, motd=motd):
        self.motd = motd
        self.version = version
        self.time = datetime.now() if time is None else time

    def __repr__(self) -> str:
        time = self.time.strftime(self._time_format)
        return f"<MRVNRadiant (version: {self.version}, time: {time})>"

    def __str__(self) -> str:
        lines = [
            self.motd,
            f"Version:        {self.version}",
            f"Time:           {self.time.strftime(self._time_format)}"]
        return "\n".join(lines)

    @classmethod
    def from_bytes(cls, raw_signature) -> MRVNRadiant:
        motd, version, time = (
            raw_signature[i * 64:(i + 1) * 64].rstrip(b"\0").decode()
            for i in range(3))
        assert re.match(r"Built with love using MRVN-[rR]adiant :\)", motd)
        assert version.startswith("Version:")
        version = re.match(r"Version:\s+(.*)", version).groups()[0]
        # TODO: if version != "Dev build": parse SemVer & git hash
        assert time.startswith("Time:")
        time = datetime.strptime(re.match(r"Time:\s+(.*)\n", time).groups()[0], cls._time_format)
        # ^ "Wed Jun 07 19:37:23 2023" -> datetime.datetime
        return cls(version, time, motd)

    def as_bytes(self) -> bytes:
        lines = str(self).split("\n")
        lines[-1] += "\n"
        return b"".join([
            L.encode() + b"\0" * (64 - len(L))
            for L in lines])


AnySignatureClass = Union[MRVNRadiant]


def identify(raw_signature: bytes) -> Union[AnySignatureClass, bytes]:
    """relying on .from_bytes() checks to determine SignatureClass"""
    for SignatureClass in (MRVNRadiant,):
        try:
            signature = SignatureClass.from_bytes(raw_signature)
        except Exception:
            # AssertionError: some check fails
            # AttributeError: re.match returns None
            pass
        else:
            return signature
    return raw_signature
