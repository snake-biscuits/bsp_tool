import pytest

from bsp_tool.archives import base
from bsp_tool.archives import alcohol
from bsp_tool.archives import golden_hawk
from bsp_tool.archives import padus
from bsp_tool.archives import sega


disc_classes = [
    alcohol.Mds,
    golden_hawk.Cue,
    padus.Cdi,
    sega.Gdi]


def class_name(cls: object) -> str:
    short_module = cls.__module__.split(".")[-1]
    return ".".join([short_module, cls.__name__])


@pytest.mark.parametrize("disc_class", disc_classes, ids=map(class_name, disc_classes))
def test_in_spec(disc_class: object):
    assert issubclass(disc_class, base.DiscImage), "not a base.DiscImage subclass"
    assert hasattr(disc_class, "ext"), "ext not specified"
    assert isinstance(disc_class.ext, str), "ext must be of type str"
    assert disc_class.ext.startswith("*."), "ext must start with wildcard"
    assert hasattr(disc_class, "read"), "no read method"
    # TODO: test other fundamentals
    # -- extra_patterns, mount_file & unmount_file
    # -- __init__ prepares tracks, extras & _cursor
