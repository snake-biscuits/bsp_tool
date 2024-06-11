"""Index of all known .bsp format variants"""
__all__ = ["ace_team", "arkane", "gearbox", "id_software", "infinity_ward", "ion_storm", "loiste", "nexon",
           "outerlight", "raven", "respawn", "ritual", "strata", "troika", "utoplanet", "valve", "wild_tangent",
           "developers", "with_magic", "identify", "game_branch", "quake_based", "source_based", "of_engine"]

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
from . import wild_tangent
# TODO: xatrix.kingpin
# ^ https://github.com/QuakeTools/Kingpin-SDK-v1.21
# -- (Kingpin allegedly has it's own KRadiant "on the CD")
# -- https://steamdb.info/depot/38431/ lists radiant & compilers in files


developers = (
    ace_team, arkane, gearbox, id_software, infinity_ward, ion_storm, loiste, nexon,
    outerlight, raven, respawn, ritual, strata, troika, utoplanet, valve, wild_tangent)

# NOTE: we could generate this list, but it makes for nice documentation
with_magic = {
    None: [id_software.quake, *gearbox.scripts, raven.hexen2, valve.goldsrc],
    b" 46Q": [id_software.quake64],
    b"2015": [ritual.mohaa, ritual.mohaa_demo],
    b"2PSB": [id_software.remake_quake_old],
    b"BSP2": [id_software.remake_quake],
    b"EF2!": [ritual.star_trek_elite_force2],
    b"EALA": [ritual.mohaa_bt],
    b"FAKK": [ritual.fakk2, ritual.star_trek_elite_force2_demo],
    b"FBSP": [id_software.qfusion],
    b"GBSP": [wild_tangent.genesis3d],
    b"IBSP": [
        id_software.quake2, id_software.quake3,
        *infinity_ward.scripts,
        ion_storm.daikatana,
        raven.soldier_of_fortune,
        ritual.sin],
    b"PSBr": [respawn.titanfall_x360],
    b"PSBV": [valve.orange_box_x360, valve.sdk_2013_x360],
    b"QBSP": [id_software.qbism],
    b"rBSP": [
        respawn.apex_legends, respawn.apex_legends50,
        respawn.apex_legends51, respawn.apex_legends52,
        respawn.titanfall, respawn.titanfall2],
    b"RBSP": [raven.soldier_of_fortune2, ritual.sin],
    b"VBSP": [
        ace_team.zeno_clash,
        *arkane.scripts,
        strata.strata,
        loiste.infra,
        *nexon.scripts,
        outerlight.outerlight,
        troika.vampire,
        utoplanet.merubasu,
        valve.alien_swarm, valve.left4dead, valve.left4dead2,
        valve.orange_box, valve.sdk_2013, valve.source,
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

# default branches:
identify[(None, 29)] = id_software.quake
# ^ NOT raven.hexen2
identify[(b"IBSP", 41)] = ion_storm.daikatana
# ^ NOT ritual.sin (though 1 such map exists in megatest)
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

# branch groups
source_magics = (b"PSBV", b"PSBr", b"VBSP", b"rBSP")
source_based = {bs for magic, bss in with_magic.items() for bs in bss if magic in source_magics}
# NOTE: all source_based branches have "version" in LumpHeader
quake_based = {bs for magic, bss in with_magic.items() for bs in bss if magic not in source_magics}
# NOTE: all quake_based lumps are unversioned
x360_magics = (b"PSBV", b"PSBr")
big_endian = {bs for magic, bss in with_magic.items() for bs in bss if magic in x360_magics}
little_endian = {bs for magic, bss in with_magic.items() for bs in bss if magic not in x360_magics}

of_engine = {
    "Genesis3D": {wild_tangent.genesis3d},
    "GoldSrc": {valve.goldsrc, *gearbox.scripts},
    "Id Tech 2": {
        id_software.quake, id_software.quake2, id_software.quake64,
        ion_storm.daikatana, raven.hexen2, ritual.sin},
    "Id Tech 3": {
        id_software.quake3, id_software.qfusion,
        *raven.scripts, *ritual.scripts},
    "IW": {*infinity_ward.scripts},
    "IW 1.0": {infinity_ward.call_of_duty1_demo, infinity_ward.call_of_duty1},
    "IW 2.0": {infinity_ward.call_of_duty2},
    "IW 3.0": {infinity_ward.modern_warfare},
    "ReMakeQuake": {id_software.remake_quake, id_software.remake_quake_old},
    "Source": {*source_based},
    "Titanfall": {*respawn.scripts},
    "Quake": {id_software.quake, id_software.quake64, raven.hexen2},
    "Quake 2": {id_software.quake2, ion_storm.daikatana, id_software.qbism}}

of_engine["Id Tech 3"] -= {ritual.sin}  # Quake 2 / Id Tech 2
of_engine["Source"] -= {*respawn.scripts}  # Titanfall

#      /-> ReMakeQuake
# Quake -> GoldSrc
#      \-> Quake 2 -> Id Tech 3 -> IW
#                 \-> Source -> Titanfall
