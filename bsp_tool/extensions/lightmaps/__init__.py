__all__ = ["LightmapCollection", "LightmapPage", "extract_branch", "lightmaps_of"]
from . base import LightmapCollection, LightmapPage
# branches
from . import apex_legends
from . import cso2_2018
from . import modern_warfare
from . import quake
from . import quake2
from . import quake3
from . import source
from . import titanfall
from . import titanfall2


# USAGE:
# -- LightmapPage.from_list(lightmaps_of(bsp))
# -- LightmapCollection.from_list(bsp.filename, lightmaps_of(bsp))

# TODO: DarkPlaces / .lit / BSP2 lightdata
# TODO: Quake 64 556RGB (16-bit)
# TODO: Source Engine displacement lightmaps
# TODO: troika.vampire (multiple styles)

# TODO: use bsp_tool.branches.of_engine to group lightmap functions for multiple branches
extract_branch = {
    "id_software.quake": quake.face_lightmaps,
    "id_software.quake2": quake2.face_lightmaps,
    "id_software.quake3": quake3.extract,
    "infinity_ward.modern_warfare": modern_warfare.extract,
    "nexon.cso2_2018": cso2_2018.face_lightmaps,
    "respawn.apex_legends": apex_legends.extract,
    "respawn.titanfall": titanfall.extract,
    "respawn.titanfall2": titanfall2.extract,
    "valve.source": source.face_lightmaps}


# TODO: automatically page lightmaps for Quake, Quake2 & Source Engine maps
def lightmaps_of(bsp) -> LightmapCollection:
    branch = ".".join(bsp.branch.__name__.split(".")[-2:])
    collection = extract_branch[branch](bsp)
    if not isinstance(collection, LightmapCollection):  # List[Image]
        return LightmapCollection.from_list(collection)
    else:
        return collection
