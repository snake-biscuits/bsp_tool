__all__ = ["apex_legends", "base", "for_branch", "quake", "quake2",
           "quake3", "source", "titanfall", "titanfall2"]

from . import apex_legends
from . import base
from . import quake
from . import quake2
from . import quake3
from . import source
from . import titanfall
from . import titanfall2


# TODO: DarkPlaces / .lit / BSP2 lightdata
# TODO: Quake 64 556RGB (16-bit)

# TODO: quake3.tiled
# TODO: apex_legends.split
# TODO: vampire.as_page

for_branch = {"id_software.quake": quake.as_page,
              "id_software.quake2": quake2.as_page,
              "id_software.quake3": quake3.tiled,
              "respawn.apex_legends": apex_legends.tiled,
              "respawn.titanfall": titanfall.tiled_or_split,
              "respawn.titanfall2": titanfall2.tiled_or_split,
              "valve.source": source.as_page}

# TODO: match "valve.as_page" to "branches.of_engine['Source']"
# TODO: attach ".lightmap_as_image(filename: str)" methods to branches
