"""General testing of LumpClasses (consistency & forgotten fields)"""
import inspect
import itertools
import struct

import pytest

from bsp_tool import branches
from bsp_tool.branches import base


# TODO: use tests/maplist.py to look at headers to ensure UNUSED_* / UNKNOWN_* lumps are correctly marked
# -- looking for unmapped lump versions would be nice too

# TODO: assert LumpClasses capture all bytes (no gaps caused by alignment)
# sizeof(_format) == sum(map(sizeof, _format))

# TODO: verify LumpClass __annotations__ match _format ("hHiI": int, "fg": float, "s": str, "?": bool)
# -- _classes will override base type, confirm the reverse conversions (enum & vec3 -> int)
# -- List[type] is appropriate for MappedArrays defined in Struct._arrays
# TODO: check for outdated annotations, allow hints for properties
# TODO: commented out type hints for _arrays?
# -- allow type hints / comments for derived members (e.g. titanfall.Brush.num_brush_sides)

# TODO: verify __slots__, _format, _arrays & _mapping line up correctly
# -- all LumpClasses must coherently translate to and from bytes
# -- no skipped bytes! (single byte alignment gets wierd)
# -- incomplete / mismatched / outdated type-hints should also be checked
# -- this may require scanning comments for "deep" type-hints `# attr.sub: type  # desc`
# TODO: check for attr.sub typos in _classes & _bitfields

# NOTE: _classes might complain about EnumClass(0) (if not defined) when initialising LumpClasses
# TODO: interrogate LumpClass instances, not just class definitions


Struct_LumpClasses = dict()
MappedArray_LumpClasses = dict()
BitField_LumpClasses = dict()
# ^^^ {"dev.game.LumpClass": LumpClass}
for branch_script in itertools.chain(*branches.scripts_from_file_magic.values()):
    script_name = ".".join(branch_script.__name__.split(".")[-2:])
    for class_name, LumpClass in inspect.getmembers(branch_script, inspect.isclass):
        if issubclass(LumpClass, base.Struct):
            Struct_LumpClasses[f"{script_name}.{class_name}"] = LumpClass
        if issubclass(LumpClass, base.MappedArray):
            MappedArray_LumpClasses[f"{script_name}.{class_name}"] = LumpClass
        if issubclass(LumpClass, base.BitField):
            BitField_LumpClasses[f"{script_name}.{class_name}"] = LumpClass


# TODO: test "other" LumpClasses (e.g. quake.Edge)
# -- need to be compatible with BspClass._preload_lump() & .lump_as_bytes()


# TODO: log which unused LumpClasses (not in branch_script.LUMP_CLASSES)
# -- need an exclusion list for broken LumpClasses
# -- some SpecialLumpClasses have child LumpClasses, these should also be excluded
# -- titanfall.Grid & LevelInfo are SpecialLumpClasses (1 instance of a LumpClass per .bsp)


@pytest.mark.parametrize("LumpClass", Struct_LumpClasses.values(), ids=Struct_LumpClasses.keys())
def test_Struct(LumpClass):
    assert hasattr(LumpClass, "_format")
    assert struct.calcsize(LumpClass._format) > 0, "invalid _format"
    assert len(LumpClass.__slots__) != 0, "forgot to create __slots__"
    assert not hasattr(LumpClass, "_mapping"), "Struct doesn't use _mapping"  # MappedArray only
    assert not hasattr(LumpClass, "_fields"), "Struct doesn't use _fields"  # BitField only
    assert hasattr(LumpClass, "_arrays"), "use MappedArray for shallow Structs"
    # TODO: how does memory effeciency differ between Struct & MappedArray
    # -- should we restrict use of MappedArray to _arrays definitions?
    LumpClass()  # must initialise once to generate struct_attr_formats entry
    _format_mapped = "".join(branches.base.struct_attr_formats[LumpClass].values())
    _format_expanded = "".join(branches.base.split_format(LumpClass._format))
    assert _format_mapped == _format_expanded, "_format does not align with size of __slots__ & _arrays"
    # assert set(LumpClass.__slots__) == set(LumpClass.__annotations__), "missing type hints"
    assert LumpClass().as_bytes() == b"\0" * struct.calcsize(LumpClass._format)


@pytest.mark.parametrize("LumpClass", MappedArray_LumpClasses.values(), ids=MappedArray_LumpClasses.keys())
def test_MappedArray(LumpClass):
    assert hasattr(LumpClass, "_format")
    assert struct.calcsize(LumpClass._format) > 0, "invalid _format"
    assert not hasattr(LumpClass, "__slots__"), "MappedArray doesn't use __slots__"  # Struct only
    assert not hasattr(LumpClass, "_arrays"), "MappedArray doesn't use _arrays"  # Struct only
    assert not hasattr(LumpClass, "_fields"), "MappedArray doesn't use _fields"  # BitField only
    assert len(LumpClass._mapping) != 0, "forgot to create _mapping"
    _format_mapped = "".join(LumpClass()._attr_formats.values())  # <- __init__ called
    _format_expanded = "".join(branches.base.split_format(LumpClass._format))
    assert _format_mapped == _format_expanded, "_format does not align with size of _mapping"
    # assert set(LumpClass._mapping) == set(LumpClass.__annotations__), "missing type hints"
    assert LumpClass().as_bytes() == b"\0" * struct.calcsize(LumpClass._format)
    # NOTE: MappedArray does some verification in __init__


@pytest.mark.parametrize("LumpClass", BitField_LumpClasses.values(), ids=BitField_LumpClasses.keys())
def test_BitField(LumpClass):
    assert hasattr(LumpClass, "_format")
    assert LumpClass._format in "BHI", "BitField can only map a single unsigned integer"
    # TODO: allow endianness char "<" / ">" (NotYetImplemented)
    assert not hasattr(LumpClass, "__slots__"), "BitField doesn't use __slots__"  # Struct only
    assert not hasattr(LumpClass, "_arrays"), "BitField doesn't use _arrays"  # Struct only
    assert not hasattr(LumpClass, "_mapping"), "BitField doesn't use _mapping"  # MappedArray only
    assert len(LumpClass._fields) != 0, "forgot to create _fields"
    _format_bits = struct.calcsize(LumpClass._format) * 8
    _mapped_bits = sum(LumpClass._fields.values())
    assert _format_bits == _mapped_bits, "_format does not align with size of _fields"
    # assert set(LumpClass._fields) == set(LumpClass.__annotations__), "missing type hints"
    assert LumpClass().as_bytes() == b"\0" * struct.calcsize(LumpClass._format)
    # NOTE: BitField does some verification in __init__
