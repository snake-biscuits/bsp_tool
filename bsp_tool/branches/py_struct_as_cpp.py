from __future__ import annotations
import enum
import inspect
import itertools
import re
from typing import Any, Dict, List, Union

from .base import mapping_length, MappedArray, Struct
# class base.Struct:
#   __slots__: List[str]     # top-level attr name
#   _format: str             # types
#   _arrays: Dict[str, any]  # child mapping
#   # ^ {"attr": _mapping}

# class base.MappedArray:
#     _mapping: int             # list of len _mapping
#     _mapping: List[str]       # list of named children
#     _mapping: Dict[str, Any]  # children with their own mappings
#     # ^ {"child": _mapping}
#     _mapping: None            # plain, siblings have mappings
#     # e.g. {"id": None, "position": [*"xy"]}

# type aliases
StructMapping = Union[Dict[str, Any], List[str], int, None]  # _arrays or _mapping
CType = str
TypeMap = Dict[CType, str]
# ^ {"type": "member"}


def lump_class_as_c(lump_class: Union[MappedArray, Struct]) -> str:
    name = lump_class.__name__
    formats = split_format(lump_class._format)
    if issubclass(lump_class, Struct):
        attrs = lump_class.__slots__
        mappings = getattr(lump_class, "_arrays", dict())
    elif issubclass(lump_class, MappedArray):
        special_mapping = lump_class._mapping
        if isinstance(special_mapping, list):
            attrs, mappings = special_mapping, None
        elif isinstance(special_mapping, dict):
            attrs = special_mapping.keys()
            mappings = special_mapping
    else:
        raise TypeError(f"Cannot convert {type(lump_class)} to C")
    return make_c_struct(name, attrs, formats, mappings)
    # ^ ("name", {"type": "member"})


# TODO: revise
def make_c_struct(name: str, attrs: List[str], formats: List[str], mappings: StructMapping = dict()) -> Dict[str, TypeMap]:
    members = list()
    i = 0
    for attr in attrs:
        member_name = attr
        sub_mapping = mappings.get(attr)
        if isinstance(sub_mapping, int):
            format_size = sub_mapping
        elif isinstance(sub_mapping, list):
            format_size = len(sub_mapping)
        elif isinstance(sub_mapping, dict):
            format_size = mapping_length(sub_mapping)
        else:
            raise TypeError(f"Invalid sub_mapping: {sub_mapping}")
        attr_format = formats[i:i+format_size]
        c_type, member_name = c_type_of(member_name, attr_format, sub_mapping)
        # TODO: convert c_type to one-liner
        members.append((c_type, member_name))
    return {name: {a: t for t, a in members}}
    # ^ {"name": {"type": "member"}}


def split_format(_format: str) -> List[str]:
    _format = re.findall(r"[0-9]*[xcbB\?hHiIlLqQnNefdspP]", _format.replace(" ", ""))
    out = list()
    for f in _format:
        match_numbered = re.match(r"([0-9]+)([xcbB\?hHiIlLqQnNefdpP])", f)
        # NOTE: does not decompress strings
        if match_numbered is not None:
            count, f = match_numbered.groups()
            out.extend(f * int(count))
        else:
            out.append(f)
    return out


type_LUT = {"c": "char",  "?": "bool",
            "b": "char",  "B": "unsigned char",
            "h": "short", "H": "unsigned short",
            "i": "int",   "I": "unsigned int",
            "f": "float", "g": "double"}


def c_type_of(attr: str, formats: List[str], mapping: StructMapping) -> (CType, str):
    if not isinstance(mapping, (dict, list, int, None)):
        raise TypeError(f"Invalid mapping: {type(mapping)}")
    if isinstance(mapping, None):  # one object
        c_type = type_LUT[formats[0]]
        return c_type, attr
    if isinstance(mapping, int):  # C list type
        if len(set(formats)) == 1:
            c_type = type_LUT[formats[0]]
            return c_type, f"{attr}[{mapping}]"
            # ^ ("type", "name[count]")
        else:  # mixed types
            if mapping > 26:  # ("attr", "2ih", 4) -> ("struct { int A[2]; short B; }", "attr")
                raise NotImplementedError("Cannot convert list of mixed type")
            mapping = [chr(97 + i) for i in range(mapping)]  # i=0: a, i=25: z
            return c_type_of(attr, formats, mapping)  # use list mapping instead
            # ^ {"attr": {"child_A": Type, "child_B": Type}}
    elif isinstance(mapping, (list, dict)):  # basic / nested struct
        return make_c_struct(attr, formats, mapping)
        # ^ {"attr": {"child_1": Type, "child_2": Type}}
    else:
        raise RuntimeError("How did this happen?")


def apply_typing(members: Dict[str, CType]) -> Dict[str, CType]:
    """{'name', 'char[256]'} -> {'name[256]', 'char'}"""
    # NOTE: type may be a struct
    out = dict()
    # ^ {"member_1": "type", "member_2": "type[]"}
    for member, _type in members.items():
        count_search = re.search(r"([a-z]+)\[([0-9]+)\]", _type)  # type[count]
        if count_search is not None:
            _type, count = count_search.groups()
            member = f"{member}[{count}]"
        out[member] = _type
    return out


def compact_members(members: Dict[str, str]) -> List[str]:
    """run after apply_typing"""
    # NOTE: type may be a struct, cannot chain inner structs!
    # - in this case, the inner must be declared externally
    members = list(members.items())
    # ^ [("member_1", "type"), ("member_2", "type")]
    type_groups = [list(members[0])]
    # ^ [["type", "member_1", "member_2"], ["type", "member_1"]]
    for member, _type in members[1:]:
        if _type == type_groups[-1][0]:
            type_groups[-1].append(member)
        else:
            type_groups.append([_type, member])
    out = list()
    # NOTE: this automatically creates "lines" & does not allow for aligning variables
    for _type, *members in type_groups:
        out.append(f"{_type} {', '.join(map(str, members))};")
    return out


pattern_thc = re.compile(r"([\w\.]+):\s[\w\[\]]+  # ([\w ]+)")
# NOTE: also catches commented type hints to allow labelling of inner members


def get_type_hint_comments(cls: object) -> Dict[str, str]:
    out = dict()  # {"member": "comment"}
    for line in inspect.getsource(cls):
        match = pattern_thc.seach(line)
        if match is None:
            continue
        member, comment = match.groups()
        out[member] = comment
    return out


class Style(enum.IntFlag):
    # masks
    TYPE_MASK = 0b11
    ONER = 0b01
    INNER = 0b10
    # major styles
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
    # _FULL bonus flags
    ALIGN_MEMBERS = 0x04
    ALIGN_COMMENTS = 0x08
    # TODO: align with inner structs?
    # TODO: COMPACT = 0x10  # use compact members


def definition_as_str(name: str, members: Dict[str, Any], mode: int = 0x04, comments: Dict[str, str] = dict()) -> str:
    # members = {"member_1": "type", "member_2": "type[]"}
    # comments = {"member_1": "comment"}
    if not mode & Style.INNER:  # snake_case -> CamelCase
        name = "".join([word.title() for word in name.split("_")])
    # NOTE: this should be redundant, but strict styles make reading Cpp easier
    # generate output
    output_type = mode & Style.TYPE_MASK
    if output_type & Style.INNER:
        opener, closer = "struct {", "}" + f" {name};\n"
    else:  # OUTER
        opener, closer = f"struct {name} " + "{", "};\n"
    if output_type & Style.ONER:
        joiner = " "
        definitions = compact_members(apply_typing(members))
    else:  # FULL (multi-line)
        joiner = "\n"
        alignment = 1
        if mode & Style.ALIGN_MEMBERS:
            alignment = max([len(t) for t in members.keys() if not t.startswith("struct")]) + 2
        half_definitions = [f"    {t.ljust(alignment)} {n};" for n, t in apply_typing(members).items()]
        alignment = max([len(d) for d in half_definitions]) if mode & Style.ALIGN_COMMENTS else 1
        definitions = []
        for member, definition in zip(members, half_definitions):
            if member in comments:
                definitions.append(f"{definition.ljust(alignment)}  \\\\ {comments[member]}")
            else:
                definitions.append(definition)
        if output_type & Style.INNER:
            opener += f"  // {name}"
    return joiner.join([opener, *definitions, closer])


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
    # TODO: LumpClasses -> lump_class_as_c
    # TODO: SpecialLumpClasses -> inspect.getsource(SpecialLumpClass) in Cpp TODO
    # TODO: methods -> [inspect.getsource(m) for m in methods] in Cpp TODO

# Nice to haves:
# Give common inner structs their own types  (this would require the user to name each type)
# struct Vector { float x, y, z; };
# struct LumpClass {
#     int             id;
#     Vector          origin;
#     char            name[128];
#     unsigned short  unknown[4];
# };

# LumpClass.__doc__ in a comment above it's Cpp definition
# // for one liner, /* */ with padded spaces for multi-line


if __name__ == "__main__":
    pass

    # print(split_format("128s4I2bhHhh"))  # OK
    members = {"id": "int", "name": "char[256]", "inner": "struct { float a, b; }",
               "skin": "short", "flags": "short"}
    comments = {"id": "GUID", "inner": "inner struct"}
    # print(apply_typing(members))  # OK
    # print(compact_members(members))  # OK
    print("=== Outer Full ===")
    print(definition_as_str("Test", members, comments=comments, mode=Style.OUTER_FULL))  # OK
    print("=== Outer Full + Aligned Members ===")
    print(definition_as_str("Test", members, comments=comments, mode=0 | 4))  # OK
    print("=== Outer Full + Aligned Members & Comments ===")
    print(definition_as_str("Test", members, comments=comments, mode=0 | 4 | 8))  # OK
    print("=== Outer Oner ===")
    print(definition_as_str("Test", members, comments=comments, mode=Style.OUTER_ONER))  # OK
    print("=== Inner Full ===")
    print(definition_as_str("test", members, comments=comments, mode=Style.INNER_FULL))  # OK
    print("=== Inner Full + Aligned Members ===")
    print(definition_as_str("test", members, comments=comments, mode=2 | 4))  # OK
    print("=== Outer Full + Aligned Members & Comments ===")
    print(definition_as_str("Test", members, comments=comments, mode=2 | 4 | 8))  # OK
    print("=== Inner Oner ===")
    print(definition_as_str("test", members, comments=comments, mode=Style.INNER_ONER))  # OK

    # TODO: test branch_script_as_cpp
    # from bsp_tool.branches.id_software.quake3 import Face  # noqa F401
    # TODO: test lump_class_as_c(Face)
    # from bsp_tool.branches.valve.orange_box import Plane
    # print(lump_class_as_c(Plane))
