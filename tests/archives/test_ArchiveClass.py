import pytest

from bsp_tool.archives import base


subclasses = {
    ".".join([sc.__module__.split(".")[-1], sc.__name__]): sc
    for sc in sorted(
        base.Archive.__subclasses__(),
        key=lambda sc: (sc.__module__, sc.__name__))}


@pytest.mark.xfail
@pytest.mark.parametrize("subclass", subclasses.values(), ids=subclasses.keys())
def test_in_spec(subclass: base.Archive):
    assert hasattr(subclass, "ext")
    assert isinstance(subclass.ext, str)
    assert subclass.ext.startswith("*.")
    assert hasattr(subclass, "namelist")
    # TODO: doesn't raise NotImplementedError
    assert hasattr(subclass, "read")
    # TODO: doesn't raise NotImplementedError
    assert hasattr(subclass, "listdir")  # bonus / Issue 190
    # TODO: doesn't raise NotImplementedError
    # TODO: .from_stream / .from_bytes / .from_file classmethods
