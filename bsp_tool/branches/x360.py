import enum
import inspect

from typing import Any, Dict


def make_big_endian(cls) -> object:
    """forces cls._format to big endian"""
    # NOTE: using exec is silly, but it renames the class, other approaches do not
    # alternatives tried:
    # -- subclass w/ __name__: only applied on creation
    # -- copying class in locals() to a new name: original name persisted
    if issubclass(cls, enum.Enum):  # class BasicBspClass(FormatBase, enum.IntFlag): pass
        BaseClass = make_big_endian(inspect.getmro(cls)[1])  # hopefully index is consistent
        exec("\n".join([f"class {cls.__name__}_x360(BaseClass, enum.IntFlag):",
                        *[f"    {FLAG} = {value}" for FLAG, value in cls.__members__.items()]]))
        return locals()[f"{cls.__name__}_x360"]
    exec("\n".join([f"class {cls.__name__}_x360(cls):",
                    f'    _format = ">{cls._format}"']))
    # NOTE: trying to use the `inspect` module on a LumpClass_x360 will raise an OSError
    return locals()[f"{cls.__name__}_x360"]


LumpClassDict = Dict[str, Dict[int, Any]]
# ^ {"LUMP_NAME": {lump_version: LumpClass}}


def convert_versioned(LumpClass_dict: LumpClassDict) -> (LumpClassDict, Dict[str, Any]):
    """flip the endians on a dict of versioned LumpClasses & returns a list of global names"""
    out = dict()
    _globals = dict()
    for LUMP_NAME, version_dict in LumpClass_dict.items():
        out[LUMP_NAME] = dict()
        for version, LumpClass in version_dict.items():
            LumpClass_x360 = make_big_endian(LumpClass)
            _globals[LumpClass_x360.__name__] = LumpClass_x360
            out[LUMP_NAME][version] = LumpClass_x360
    return out, _globals
