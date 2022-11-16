from ..branches.base import Struct, MappedArray, BitField, type_LUT


def int_max(c_type: str) -> str:
    return c_type.split("_")[0].upper() + "_MAX"


def LumpClasses_as_cpp(branch_script) -> str:
    out = list()
    for s in sorted({ls for d in branch_script.LUMP_CLASSES.values() for ls in d.values()}, key=lambda ls: ls.__name__):
        if not issubclass(s, (Struct, MappedArray, BitField)):
            out.append(f"/* skipping {s.__name__} */")
            continue
        try:
            out.append(s().as_cpp())
        except Exception:
            out.append(f"/* ERROR: skipping {s.__name__} */")
    return "\n\n\n".join(out) + "\n"


def BasicLumpClasses_as_cpp(branch_script) -> str:
    out = list()
    # TODO: BitField definitions & flags
    lump_formats = {L: type_LUT[list(d.values())[0]._format] for L, d in branch_script.BASIC_LUMP_CLASSES.items()}
    for lump, c_type in lump_formats.items():
        out.append(f"{c_type} {lump}[{int_max(c_type)}];")
    return "\n".join(out) + "\n"


def branch_script_as_hpp(branch_script) -> str:
    # NOTE: will need to add SpecialLumpClasses & some other LumpClasses by hand
    lcs = LumpClasses_as_cpp(branch_script)
    blcs = BasicLumpClasses_as_cpp(branch_script)
    return "\n\n".join([lcs, blcs])
