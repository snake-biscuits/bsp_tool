"""Valve Software developed the GoldSrc Engine, building on idTech 2.
This variant powered Half-Life & CS:1.6. Valve went on to develop the Source Engine for Half-Life 2."""
from . import alien_swarm
from . import sdk_2013
from . import source
from . import goldsrc  # Most GoldSrc Games
from . import left4dead
from . import left4dead2
from . import orange_box  # Most Source Engine Games
# TODO: portal2
# TODO: vampire


scripts = [alien_swarm, goldsrc, left4dead, left4dead2, orange_box, sdk_2013, source]

# TRIVIA: when FILE_MAGIC is incorrect Source engine games give the error message: "Not an IBSP file"
# - this refers to the IdTech 2 FILE_MAGIC, pre-dating Half-Life 1!
