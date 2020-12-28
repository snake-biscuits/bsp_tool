import io
import re
import struct
from typing import Dict, List
import zipfile


class Entities:
    _ents: List[Dict[str, str]]
    # ^ [{"key": "value"}]

    def __init__(self, raw_bytestring):
        # TODO: use fgd-tools to fully unstringify entities
        self._ents = list()
        for line_no, line in enumerate(raw_bytestring.decode(errors="ignore").split("\n")):
            if re.match(R"^[ \t]*$", line):  # line is blank / whitespace
                continue
            if "{" in line:  # new entity
                ent = dict()
            elif '"' in line:
                key, value = re.findall(R'(?<=")[^"]*(?=")', line)[::2]
                if key not in ent:
                    ent[key] = value
                else:  # don't override duplicate keys, share a list instead
                    if isinstance(ent[key], list):  # more than 2 of this key
                        ent[key].append(value)
                    else:  # second occurance of key
                        ent[key] = [ent[key], value]
            elif "}" in line:  # close entity
                self._ents.append(ent)
            elif line == b"\x00".decode():
                continue  # ignore raw bytes, might be related to lump alignment
            else:
                raise RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")

    def as_bytes(self):
        return b"\n".join(map(lambda s: s.encode("ascii"), self._ents))


class PakFile(zipfile.ZipFile):
    def __init__(self, raw_zip_bytes):
        self._buffer = io.BytesIO(raw_zip_bytes)
        super(zipfile.ZipFile, self).__init__(self._buffer)

    def as_bytes(self):
        return self._buffer.getvalue()


class GameLump:
    def __init__(self, raw_game_lump):  # do we need the header too?
        raise NotImplementedError("Game lumps hard")
        # If it's compressed, good luck. Each sub-lump is compressed individually.

    def as_bytes(self):
        raise NotImplementedError("Game lumps hard")


class TexDataStringData(list):
    def __init__(self, raw_texdata_string_data):
        super().__init__([t.decode("ascii", errors="ignore") for t in raw_texdata_string_data.split(b"\0")])

    def as_bytes(self):
        return b"\0".join([t.encode("ascii") for t in self])


class Visiblity:
    def __init__(self, raw_visibility):
        vis_data = [v[0] for v in struct.iter_unpack("i", raw_visibility)]
        num_clusters = vis_data
        for i in range(num_clusters):
            i = (2 * i) + 1
            pvs_offset = vis_data[i]  # noqa: F841
            pas_offset = vis_data[i + 1]  # noqa: F841
            # ^ pointers into RLE encoded bits mapping the PVS tree
            # from bytes inside the .bsp file?
        raise NotImplementedError("Understanding of Visibility lump is incomplete")

    def as_bytes(self):
        raise NotImplementedError("Visibility lump hard")
