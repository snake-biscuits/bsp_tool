"""Index of all known .bsp format variants"""
__all__ = ["ace_team", "arkane", "gearbox", "id_software", "infinity_ward", "ion_storm", "loiste",
           "nexon", "outerlight", "raven", "respawn", "ritual", "strata", "troika", "utoplanet", "valve",
           "developers", "with_magic", "identify", "game_branch", "quake_based", "source_based"]

from . import ace_team
from . import arkane
from . import gearbox
from . import id_software
from . import infinity_ward
from . import ion_storm
from . import loiste
from . import nexon
from . import outerlight
from . import raven
from . import respawn
from . import ritual
from . import strata
from . import troika
from . import utoplanet
from . import valve
# TODO: xatrix.kingpin
# ^ https://github.com/QuakeTools/Kingpin-SDK-v1.21
# -- (Kingpin allegedly has it's own KRadiant "on the CD")
# -- https://steamdb.info/depot/38431/ lists radiant & compilers in files


developers = (ace_team, arkane, gearbox, id_software, infinity_ward, ion_storm, loiste,
              nexon, outerlight, raven, respawn, ritual, strata, troika, utoplanet, valve)

# NOTE: we could generate this list, but it makes for nice documentation
with_magic = {None: [id_software.quake, *gearbox.scripts, raven.hexen2, valve.goldsrc],
              b" 46Q": [id_software.quake64],
              b"2015": [ritual.mohaa, ritual.mohaa_demo],
              b"2PSB": [id_software.remake_quake_old],
              b"BSP2": [id_software.remake_quake],
              b"EF2!": [ritual.star_trek_elite_force2],
              b"EALA": [ritual.mohaa_bt],
              b"FAKK": [ritual.fakk2, ritual.star_trek_elite_force2_demo],
              b"FBSP": [id_software.qfusion],
              b"IBSP": [id_software.quake2, id_software.quake3,
                        *infinity_ward.scripts, ion_storm.daikatana,
                        raven.soldier_of_fortune, ritual.sin],
              b"PSBr": [respawn.titanfall_x360],
              b"PSBV": [valve.orange_box_x360,
                        valve.sdk_2013_x360],
              b"rBSP": [respawn.apex_legends,
                        respawn.apex_legends13,
                        respawn.titanfall,
                        respawn.titanfall2],
              b"RBSP": [raven.soldier_of_fortune2,
                        ritual.sin],
              b"VBSP": [ace_team.zeno_clash,
                        *arkane.scripts,
                        strata.strata,
                        loiste.infra,
                        *nexon.scripts,
                        outerlight.outerlight,
                        troika.vampire,
                        utoplanet.merubasu,
                        valve.alien_swarm,
                        valve.left4dead,
                        valve.left4dead2,
                        valve.orange_box,
                        valve.sdk_2013,
                        valve.source,
                        valve.source_filmmaker]}

# TODO: with_magic_version defaultdict(set)
# ^ {(file_magic, version): {branch_script}}

identify = dict()
# ^ {(file_magic, version): branch_script}
for file_magic, branch_scripts in with_magic.items():
    for branch_script in branch_scripts:
        identify[(file_magic, branch_script.BSP_VERSION)] = branch_script
        for version in branch_script.GAME_VERSIONS.values():
            identify[(file_magic, version)] = branch_script

# edge case: (only found in 1 map, unsure how to list in branch script)
identify[(b"IBSP", 41)] = ritual.sin
# default branches:
identify[(None, 29)] = id_software.quake
# ^ NOT raven.hexen2
identify[(b"IBSP", 46)] = id_software.quake3
# ^ NOT raven.soldier_of_fortune
identify[(b"VBSP", 20)] = valve.orange_box
# ^ NOT nexon.vindictus OR nexon.vindictus69 OR outerlight.outerlight
# -- OR utoplanet.merubasu OR valve.left4dead
identify[(b"VBSP", 21)] = valve.sdk_2013
# ^ NOT valve.alien_swarm OR valve.left4dead2 OR valve.source_filmmaker
identify[(b"VBSP", 100)] = nexon.cso2
# ^ NOT nexon.cso2_2018
identify[(b"RBSP", 1)] = raven.soldier_of_fortune2
# ^ NOT ritual.sin

game_branch = dict()
# ^ {"game": (script, version)}
for developer in developers:
    for script in developer.scripts:
        for game_name in script.GAME_VERSIONS:
            game_branch[game_name] = (script, script.GAME_VERSIONS[game_name])

source_magics = (b"PSBV", b"PSBr", b"VBSP", b"rBSP")
source_based = [bs for magic, bss in with_magic.items() for bs in bss if magic in source_magics]
# NOTE: all source_based branches have "version" in LumpHeader
quake_based = [bs for magic, bss in with_magic.items() for bs in bss if magic not in source_magics]
# NOTE: all quake_based lumps are unversioned
