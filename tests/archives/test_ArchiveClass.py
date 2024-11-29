import pytest

from bsp_tool.archives import base
from bsp_tool.archives import bluepoint
from bsp_tool.archives import cdrom
from bsp_tool.archives import gearbox
from bsp_tool.archives import id_software
from bsp_tool.archives import infinity_ward
from bsp_tool.archives import ion_storm
from bsp_tool.archives import nexon
from bsp_tool.archives import pi_studios
from bsp_tool.archives import pkware
from bsp_tool.archives import respawn
from bsp_tool.archives import sega
from bsp_tool.archives import utoplanet
from bsp_tool.archives import valve


archive_classes = [
    bluepoint.Bpk,
    cdrom.Iso,
    gearbox.Nightfire007,
    id_software.Pak,
    id_software.Pk3,
    infinity_ward.FastFile,
    infinity_ward.Iwd,
    ion_storm.Dat,
    ion_storm.Pak,
    nexon.Hfs,
    nexon.PakFile,
    nexon.Pkg,
    pi_studios.Bpk,
    pkware.Zip,
    respawn.RPak,
    respawn.Vpk,
    sega.GDRom,
    utoplanet.Apk,
    valve.Vpk]


def class_name(cls: object) -> str:
    short_module = cls.__module__.split(".")[-1]
    return ".".join([short_module, cls.__name__])


@pytest.mark.parametrize("archive_class", archive_classes, ids=map(class_name, archive_classes))
def test_in_spec(archive_class: object):
    assert issubclass(archive_class, base.Archive), "not a base.Archive subclass"
    assert hasattr(archive_class, "ext"), "ext not specified"
    assert isinstance(archive_class.ext, str), "ext must be of type str"
    assert archive_class.ext.startswith("*"), "ext must start with wildcard"
    # NOTE: mostly "*.ext", but "*_dir.vpk" breaks the pattern
    assert hasattr(archive_class, "namelist"), "no namelist method"
    assert hasattr(archive_class, "read"), "no read method"
    # NOTE: base.Archive provides defaults for all essential methods
    # -- but most raise NotImplementedError
    # -- .from_stream(), .namelist() & .read() must all be implemented by the subclass
    # -- each subclass will need it's own tests for those methods
    # -- as well as confirming __init__ creates an empty ArchiveClass
