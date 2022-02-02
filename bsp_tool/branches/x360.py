from typing import Any, Dict


def make_big_endian(cls):
    class cls_x360(cls):
        __name__ = f"{cls.__name__}_x360"
        _format = f">{cls._format}"
    return cls_x360


LumpClassDict = Dict[str, Dict[int, Any]]


def convert_versioned(LumpClass_dict: LumpClassDict) -> (LumpClassDict, Dict[str, Any]):
    out = dict()
    _globals = dict()
    for LUMP_NAME, version_dict in LumpClass_dict.items():
        out[LUMP_NAME] = dict()
        for version, LumpClass in version_dict.items():
            LumpClass_x360 = make_big_endian(LumpClass)
            _globals[LumpClass_x360.__name__] = LumpClass_x360
            out[LUMP_NAME][version] = LumpClass_x360
    return out, _globals
