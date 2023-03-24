"""Index of all known .bsp format variants"""
__all__ = ["arkane", "gearbox", "id_software", "infinity_ward", "ion_storm", "loiste",
           "nexon", "raven", "respawn", "ritual", "strata", "troika", "valve"
           "scripts_from_file_magic", "script_from_file_magic_and_version", "game_name_table"]

from . import arkane
from . import gearbox
from . import id_software
from . import infinity_ward
from . import ion_storm
from . import loiste
from . import nexon
from . import raven
from . import respawn
from . import ritual
from . import strata
from . import troika
from . import valve
# TODO: xatrix.kingpin
# ^ https://github.com/QuakeTools/Kingpin-SDK-v1.21
# -- (Kingpin allegedly has it's own KRadiant "on the CD")
# -- https://steamdb.info/depot/38431/ lists radiant & compilers in files


# NOTE: this dict can be generated from branch_scripts, but listing it here is more convenient
scripts_from_file_magic = {None: [id_software.quake,
                                  *gearbox.scripts,
                                  raven.hexen2,
                                  valve.goldsrc],
                           b"2015": [ritual.mohaa, ritual.mohaa_demo],
                           b"2PSB": [id_software.remake_quake_old],
                           b"BSP2": [id_software.remake_quake],
                           b"EF2!": [ritual.star_trek_elite_force2],
                           b"EALA": [ritual.mohaa_bt],
                           b"FAKK": [ritual.fakk2],
                           b"FBSP": [id_software.qfusion],
                           b"IBSP": [id_software.quake2,
                                     id_software.quake3,
                                     *infinity_ward.scripts,
                                     ion_storm.daikatana,
                                     raven.soldier_of_fortune,
                                     ritual.sin],  # v41
                           b"PSBr": [respawn.titanfall_x360],
                           b"PSBV": [valve.orange_box_x360,
                                     valve.sdk_2013_x360],
                           b"rBSP": [respawn.apex_legends,
                                     respawn.titanfall,
                                     respawn.titanfall2],
                           b"RBSP": [raven.soldier_of_fortune2,
                                     ritual.sin],
                           b"VBSP": [*arkane.scripts,
                                     strata.strata,
                                     loiste.infra,
                                     *nexon.scripts,
                                     troika.vampire,
                                     valve.alien_swarm,
                                     valve.left4dead,
                                     valve.left4dead2,
                                     valve.orange_box,
                                     valve.sdk_2013,
                                     valve.source]}


script_from_file_magic_and_version = dict()
# ^ {(file_magic, version): branch_script}
for file_magic, branch_scripts in scripts_from_file_magic.items():
    for branch_script in branch_scripts:
        script_from_file_magic_and_version[(file_magic, branch_script.BSP_VERSION)] = branch_script
        for version in branch_script.GAME_VERSIONS.values():
            script_from_file_magic_and_version[(file_magic, version)] = branch_script

# FORCED DEFAULTS:
script_from_file_magic_and_version[(None, 29)] = id_software.quake
# ^ NOT raven.hexen2
script_from_file_magic_and_version[(b"IBSP", 46)] = id_software.quake3
# ^ NOT raven.soldier_of_fortune
script_from_file_magic_and_version[(b"VBSP", 20)] = valve.orange_box
# ^ NOT nexon.vindictus OR valve.left4dead
script_from_file_magic_and_version[(b"VBSP", 21)] = valve.sdk_2013
# ^ NOT valve.alien_swarm OR valve.left4dead2
script_from_file_magic_and_version[(b"VBSP", 100)] = nexon.cso2
# ^ NOT nexon.cso2_2018
script_from_file_magic_and_version[(b"RBSP", 1)] = raven.soldier_of_fortune2
# ^ NOT ritual.sin


game_name_table = dict()
# ^ {"game": (script, version)}
for developer in (arkane, gearbox, id_software, infinity_ward, nexon, raven, respawn, ritual, valve):
    for script in developer.scripts:
        for game_name in script.GAME_VERSIONS:
            game_name_table[game_name] = (script, script.GAME_VERSIONS[game_name])
