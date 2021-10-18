"""Index of all known .bsp format variants"""
__all__ = ["arkane", "gearbox", "id_software", "infinity_ward", "nexon",
           "raven", "respawn", "ritual", "scripts_from_file_magic", "game_path_table"]

from . import arkane
from . import gearbox
from . import id_software
from . import infinity_ward
from . import nexon
from . import raven
from . import respawn
from . import ritual
from . import troika
from . import valve


# NOTE: this dict can be generated from branch_scripts, but listing it here is more convenient
scripts_from_file_magic = {None: [id_software.quake,
                                  raven.hexen2,
                                  valve.goldsrc],
                           b"2015": [ritual.moh_allied_assault],
                           b"EF2!": [ritual.star_trek_elite_force2],
                           b"FAKK": [ritual.fakk2],
                           b"IBSP": [id_software.quake2,
                                     id_software.quake3,
                                     *infinity_ward.scripts,
                                     ritual.sin],
                           b"rBSP": [*respawn.scripts],
                           b"RBSP": [raven.soldier_of_fortune2,
                                     ritual.sin],
                           b"VBSP": [*arkane.scripts,
                                     *nexon.scripts,
                                     *troika.scripts,
                                     *[s for s in valve.scripts if (s is not valve.goldsrc)]]}


script_from_file_magic_and_version = dict()
# ^ {(file_magic, version): branch_script}
for file_magic, branch_scripts in scripts_from_file_magic.items():
    for branch_script in branch_scripts:
        for version in branch_script.GAME_VERSIONS.values():
            script_from_file_magic_and_version[(file_magic, version)] = branch_script
# NOTE: multiple branch_scripts exist for (b"VBSP", 20) & (b"VBSP", 21)


game_path_table = dict()
# ^ {"game": (script, version)}
for developer in (arkane, gearbox, id_software, infinity_ward, nexon, raven, respawn, ritual, valve):
    for script in developer.scripts:
        for game_path in script.GAME_PATHS:
            game_path_table[game_path] = (script, script.GAME_VERSIONS[game_path])
