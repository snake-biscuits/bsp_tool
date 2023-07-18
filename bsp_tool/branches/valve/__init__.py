"""Valve Software developed the GoldSrc Engine, building on idTech 2.
This variant powered Half-Life & CS:1.6. Valve went on to develop the Source Engine for Half-Life 2."""
__all__ = ["alien_swarm", "goldsrc", "left4dead", "left4dead2", "orange_box", "orange_box_x360",
           "physics", "sdk_2013", "sdk_2013_x360", "source", "source_filmmaker"]

# branches
from . import alien_swarm
from . import goldsrc
from . import left4dead
from . import left4dead2
from . import orange_box
from . import orange_box_x360
from . import sdk_2013
from . import sdk_2013_x360
from . import source
from . import source_filmmaker
# other
from . import physics


scripts = [alien_swarm, goldsrc, left4dead, left4dead2, orange_box, orange_box_x360,
           sdk_2013, sdk_2013_x360, source, source_filmmaker]

# TRIVIA: when FILE_MAGIC is incorrect Source engine games give the error message: "Not an IBSP file"
# - this refers to the IdTech 2 FILE_MAGIC, pre-dating Half-Life 1!
