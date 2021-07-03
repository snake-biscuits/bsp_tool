from __future__ import annotations
import enum
import itertools
from typing import Any, Dict, List, Union

from bsp_tool.branches.base import mapping_length, Struct
# bsp_tool.branches.base Types Quick Reference
# class base.Struct:
#   __slots__: List[str]     # top-level attr name
#   _format: str             # types
#   _arrays: Dict[str, any]  # child mapping
#   # ^ {"attr": _mapping}
#
# class base.MappedArray:
#     _mapping: int             # list of len _mapping
#     _mapping: List[str]       # list of named children
#     _mapping: Dict[str, Any]  # children with their own mappings
#     # ^ {"child": _mapping}
#     _mapping: None            # plain, siblings have mappings
#     # e.g. {"id": None, "position": [*"xy"]}

# TODO: Tests! None of this code is tested!

# type aliases
ChildMapping = Union[Dict[str, Any], List[str], int, None]
CType = str


def LumpClass_as_C(LumpClass: Struct) -> str:
    name = LumpClass.__name__
    attrs = LumpClass.__slots__
    formats = split_format(LumpClass._format)
    mappings = getattr(LumpClass, "_arrays", dict())
    return make_c_struct(name, attrs, formats, mappings)
    # ^ {"name": {"type": "child_name"}}


def make_c_struct(name: str, attrs: List[str], formats: List[str], mappings: ChildMapping = dict()) -> Dict[str, any]:
    members = list()
    i = 0
    for attr in attrs:
        member_name = attr
        sub_mapping = mappings.get(attr)
        format_size = mapping_length(sub_mapping)
        attr_format = formats[i:i+format_size]
        c_type, member_name = c_type_of(member_name, attr_format, sub_mapping)
        # TODO: convert c_type to one-liner
        members.append((c_type, member_name))
    return {name: {a: t for t, a in members}}
    # ^ {"name": {"type": "child_name"}}


def split_format(_format: str) -> List[str]:
    # TODO: reduce complexity w/ regex
    # https://stackoverflow.com/questions/5318143/find-and-replace-a-string-pattern-n-times-where-n-is-defined-in-the-pattern
    out = list()
    _format = _format.replace(" ", "")
    if _format[-1].isnumeric():
        raise RuntimeError("_format is invalid (ends in a number)")
    i = 0
    while i < len(_format):
        char = _format[i]
        if char.isalpha() or char == "?":
            out.append(_format[i])
        elif char.isnumeric():
            # find the whole number
            j = 1
            while _format[i:i + j].isnumeric():
                j += 1
            j -= 1
            count, i = int(_format[i:i + j]), i + j
            f = _format[i]
            assert f.isalpha() or f == "?", f"Invalid character '{f}' in _format"
            if f == "s":
                out.append(f"{count}s")
            else:
                out.extend([f] * count)
        else:
            raise RuntimeError(f"Invalid character '{char}' in _format")
        i += 1
    return out


type_LUT = {"c": "char",  "?": "bool",
            "b": "char",  "B": "unsigned char",
            "h": "short", "H": "unsigned short",
            "i": "int",   "I": "unsigned int",
            "f": "float", "g": "double"}


def c_type_of(attr: str, formats: List[str], mapping: ChildMapping) -> (CType, str):
    if not isinstance(mapping, (dict, list, int, None)):
        raise TypeError(f"Invalid mapping: {type(mapping)}")
    if isinstance(mapping, None):  # one object
        c_type = type_LUT[formats[0]]
        return c_type, attr
    if isinstance(mapping, int):  # C list type
        if len(set(format)) > 1:  # mixed types
            raise NotImplementedError("List mapping mixes types: '{format}'")
            # ("attr", "2ih", 4) -> ("struct { int A[2]; short B; }", "attr")
            if mapping > 26:
                raise NotImplementedError("Cannot convert list of mixed type")
            mapping = [chr(97 + i) for i in range(mapping)]
            return c_type_of(attr, format, mapping)  # use list mapping instead
        c_type = type_LUT[formats[0]]
        return c_type, f"{attr}[{mapping}]"  # type  name[count]
    elif isinstance(mapping, (list, dict)):  # basic / nested struct
        return make_c_struct(attr, formats, mapping)
        # ^ {"attr": {"child_1": Type, "child_2": Type}}
    else:
        raise RuntimeError("How did this happen?")


class StyleFlags(enum.Enum):
    TYPE_MASK = 0b11
    OUTER_FULL = 0b00
    # struct OuterFull {
    #     type  member;
    # };
    OUTER_ONER = 0b01  # struct OuterOner { type a, b; type c; };
    INNER_FULL = 0b10
    # struct {  // inner_full
    #     type  member;
    # } inner_full;
    INNER_ONER = 0b11  # struct { type d, e, f; } inner_oner;
    ONER = 0b01
    INNER = 0b10
    # other flags
    ALIGN_MEMBERS = 0x04
    ALIGN_COMMENTS = 0x08
    # COMPACT = 0x10  # use compact members (smaller multi-line definitions)


def apply_typing(members: Dict[str, CType]) -> Dict[str, CType]:
    """{'name', 'char[256]'} -> {'name[256]', 'char'}"""
    # NOTE: type may be a struct
    out = dict()
    # ^ {"member_1": "type", "member_2": "type[]"}
    for member, _type in members.items():
        if _type.endswith("]"):
            _type, count = member[:-1].split("[")
            member = f"{member}[{count}]"
        out[member] = _type
    return out


def compact_members(members: Dict[str, str]) -> List[str]:
    """run after apply_typing"""
    # NOTE: type may be a struct, cannot chain inner structs!
    # - in this case, the inner must be declared externally
    members = list(members.items())
    # ^ [("member_1", "type"), ("member_2", "type")]
    type_groups = [[members[0], members[0]]]
    # ^ [["type", "member_1", "member_2"], "type", "member_1"]
    for member, _type in list(members.items())[1:]:
        if _type == type_groups[-1][0]:
            type_groups[-1].append(member)
        else:
            type_groups.append([_type, member])
    out = list()
    for _type, *members in type_groups:
        members = ", ".join(members)
        out.append(f"{_type} {members};")
    return out


def definition_as_str(name: str, members: Dict[str, Any], mode: int = 0x04, comments: Dict[str, str] = dict()) -> str:
    # members = {"member_1": "type", "member_2": "type[]"}
    # comments = {"member_1": "comment"}
    if ~(mode & StyleFlags.INNER):  # snake_case -> CamelCase
        name = "".join([word.title() for word in name.split("_")])
    # NOTE: this should be redundant, but strict styles make reading Cpp easier
    # generate output
    output_type = mode & StyleFlags.TYPE_MASK
    if output_type & StyleFlags.INNER:
        opener, closer = "struct {", "}" + f" {name};\n"
    else:  # OUTER
        opener, closer = f"struct {name} " + "{", "};\n"
    if output_type & StyleFlags.ONER:
        definitions = compact_members(apply_typing(members))
        return " ".join([opener, *definitions, closer])
    else:  # FULL (multi-line)
        alignment = 1
        if mode & StyleFlags.ALIGN_MEMBERS:
            alignment = max([len(t) for t, n in members]) + 2
        definitions = [f"    {t.ljust(alignment)} {n};" for n, t in apply_typing(members)]
        if output_type & StyleFlags.INNER:
            opener += f"  // {name}"
        return "\n".join([opener, *definitions, closer])
    # TODO: ensure recursion works ok for assembling inner structs
    # TODO: member comments


def branch_script_as_cpp(branch_script):
    raise NotImplementedError()
    bs = branch_script
    out = [f"const int BSP_VERSION = {bs.BSP_VERSION};\n"]
    lumps = {L.value: L.name for L in bs.LUMP}  # will error if bs.LUMP is incomplete
    half = (len(lumps) + 1) // 2 + 1

    def justify(x: Any) -> str:
        return str(x).rjust(len(str(len(lumps))))

    decls = []
    for i, j in itertools.zip_longest(lumps[1:half], lumps[half + 1:]):
        declarations = [f"              {lumps[i]} = {justify(i)}"]
        if j is not None:
            declarations.append(f"{lumps[j]} = {justify(j)},")
        decls.append(",  ".join(declarations))
    decls[-1] = decls[-1][:-1] + ";"  # replace final comma with a semi-colon
    # TODO: align all the `=` signs
    lump_decls = "\n".join(["namespace LUMP {",
                            f"    const int {lumps[0]} = {justify(0)},  {lumps[half]} = {justify(half)},",
                            decls, "}\n\n"])
    out.extend(lump_decls)
    # TODO: BasicLumpClasses -> comments?
    # TODO: LumpClasses -> LumpClass_as_C
    # TODO: SpecialLumpClasses -> inspect.getsource(SpecialLumpClass) in Cpp TODO
    # TODO: methods -> [inspect.getsource(m) for m in methods] in Cpp TODO

# TODO: Tests! None of this code is tested!

# Nice to haves:
# Give common inner structs their own types  (this would require the user to name each type)
# struct Vector { float x, y, z; };
# struct LumpClass {
#     int             id;
#     Vector          origin;
#     char            name[128];
#     unsigned short  unknown[4];
# };

# Parse the Python script and grab comments from annotations
# - Cannot be aligned until after the struct definition is assembled
# import inspect, re
# comments
# for line in inspect.getsource(LumpClass):
#

# LumpClass.__doc__ in a comment above it's Cpp definition
# // for one liner, /* */ with padded spaces for multi-line
