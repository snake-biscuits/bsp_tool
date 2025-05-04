import re
from typing import Any, Dict, Iterable, Tuple


ClassesDict = Dict[str, Any]
# ^ {"a": Class, "b.c": MappedArray.from_tuple}
# -- m = MappedArray(0, (1, 2),
# --     _mapping={"a": None, "b": 2},
# --     _classes={"a": Class, "b": Class})
# -- m.a = Class(0)
# -- m.b = Class(*(1, 2))
# NOTE: classes must have a __iter__ method for .to_bytes to keep working
# NOTE: classes can map more values that is passed down
# -- but must map the same attrs as the target attr
# -- or be an Enum/IntFlag
# TODO: allow _classes to target each member of a list, rather than the whole
# -- {"attr[::]": Class}
# -- would go well with List[MappedArray] mappings
# TODO: look into making _classes into MappedArray subclasses at runtime
# -- would be nice to retain _attr_formats & as_bytes
# -- edge cases: functions that return classes (e.g. enum.IntFlags)


# (ParentClass, "child", ...) -> ChildClass(...)
def school(parent: Any, child_name: str, child_value: Any) -> Any:
    """child -> class dictated by name"""
    if child_name in parent._classes:
        child_class = parent._classes[child_name]
        if not isinstance(child_value, child_class):
            if isinstance(child_value, Iterable):
                return child_class(*child_value)
            else:
                return child_class(child_value)
    return child_value  # has no class / no conversion required


# "hI3f16s" -> ("h", "I", "f", "f", "f", "16s")
def split_format(_format: str) -> Tuple[str]:
    """split a struct format string to zip with tuple"""
    # NOTE: strings returned as f"{count}s" (untouched)
    # FIXME: does not check to see if format is valid!
    # -- invalid chars are thrown out silently
    _format = re.findall(
        r"[0-9]*[xcbB\?hHiIlLqQnNefgdspP]",
        _format.replace(" ", ""))
    out = list()
    for f in _format:
        match_numbered = re.match(r"([0-9]+)([xcbB\?hHiIlLqQnNefgdpP])", f)
        # NOTE: strings ("32s" etc.) are not to be touched
        if match_numbered is not None:
            count, f = match_numbered.groups()
            out.extend(f * int(count))
        else:
            out.append(f)
    return tuple(out)


# ({'attr.sub': ...}, 'attr') -> {'sub': ...}
def subgroup(mapping: Dict[str, Any], group_name: str) -> Dict[str, Any]:
    """get subset of mapping under group_name"""
    return {
        key.partition(".")[-1]: value
        for key, value in mapping.items()
        if "." in key and key.partition(".")[0] == group_name}


# NOTE: C: #include <stdint.h>; C++: #include <cstdint.h>
type_LUT = {
    "c": "char",    "?": "bool",
    "b": "int8_t",  "B": "uint8_t",
    "h": "int16_t", "H": "uint16_t",
    "i": "int32_t", "I": "uint32_t",
    "q": "int64_t", "Q": "uint64_t",
    "f": "float",   "g": "double"}
# NOTE: can't detect strings with a dict
# -- to catch strings: type_defaults[t] if not t.endswith("s") else ...
# TODO: make a function to lookup type and check / trim string sizes
# -- a trim / warn / fail setting would be ideal

type_defaults = {
    "c": b"", "?": False,
    "b": 0, "B": 0,
    "h": 0, "H": 0,
    "i": 0, "I": 0,
    "q": 0, "Q": 0,
    "f": 0.0, "g": 0.0,
    "s": ""}
