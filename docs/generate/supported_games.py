from collections import defaultdict, namedtuple
import inspect
from itertools import chain
import os
import sys
from types import ModuleType
from typing import Dict, List

# HACK: load ../../bsp_tool from docs/generate/
sys.path.insert(0, "../../")
# BspClasses
from bsp_tool import (  # noqa: E402
    D3DBsp, FusionBsp, GoldSrcBsp, Genesis3DBsp, IdTechBsp, InfinityWardBsp, NexonBsp,
    QuakeBsp, Quake64Bsp, RavenBsp, ReMakeQuakeBsp, RespawnBsp, RitualBsp, ValveBsp)
# branches
from bsp_tool import branches  # noqa: E402
from bsp_tool.branches import (  # noqa: E402
    ace_team, arkane, gearbox, id_software, infinity_ward, ion_storm, loiste, nexon,
    outerlight, raven, respawn, ritual, strata, troika, utoplanet, valve, wild_tangent)
# other
from bsp_tool.extensions import lightmaps  # noqa: E402
from bsp_tool.lumps import DarkMessiahSPGameLump, GameLump  # noqa: E402

# TODO: use the tools in this script to generate coverage.csv (rank branches by % of lumps mapped)
# TODO: list lumps added / deprecated / renamed by each branch
# TODO: lump relationship maps w/ completeness
# -- systems / associated subsystems (rendering, vis, light, physics)
# -- would likely require some kind of dict, mapping how lumps index could be useful in general tbh
# TODO: include lump relationships in generated docs (see GitHub Issue #)

# NOTE: forks should substitute their own repo here
# TODO: get the commit hash from `git rev-parse HEAD` for permalinks
# -- default to master if git cannot be run
# -- gitpython might be a good library for this
repo_url = "https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool"
branches_url = f"{repo_url}/branches/"

# TODO: rethink inserts
# -- order could be more dynamic
# --- merging multiple .md files together
# -- lump relationship maps from branch_script comments (requires much parsing & standardising)
# --- html <svg/> Entity Relationship Diagrams w/ LumpClasses (mermaid graphs?)
# listing new & deprecated lumps across version
# -- currently manually generated, could be automated
# timeline / engine map as a navigation pane through the documentation

# Each group gets a .md; lots of formats pretty close, so sharing a table isn't a big deal
ScriptGroup = namedtuple("ScriptGroup", ["headline", "filename", "developers", "insert", "branch_scripts"])
# NOTE: table row sorting isn't 100% deterministic for some reason
# TODO: table sorting doesn't remove duplicates when multiple lump versions are used
# TODO: some groups list overlapping identifiers with different LumpClasses
# -- need to handle these clashes more clearly (currently some data is discarded)
# TODO: use game icons / emoji to identify overlapping branches
# -- compiling the whole Source Engine into one .md would be great
# NOTE: per BspClass files that could probably be generated: (would be quite messy though)
# -- bsp_tool.BspVariant_for_magic + branches.with_magic
# -- confirming all the BspClasses line up is pretty important though
# NOTE: x360 branch scripts are generated almost entirely from existing branch scripts
# TODO: treat x360 branches as a special case & trace their base classes
# NOTE: list of all BspClass & associated branch_script + Y/N coverage column
# -- loosely copied from games.sc
# | BspClass        | branch_script                      | Y/N |
# | :-------------- | :--------------------------------- | --- |
# | D3DBsp          | infinity_ward.modern_warfare       |  Y  |
# | FusionBsp       | id_software.qfusion                |  Y  |
# | GoldSrcBsp      | valve.goldsrc                      |  Y  |
# | GoldSrcBsp      | gearbox.blue_shift                 |  Y  |
# | GoldSrcBsp      | gearbox.nightfire                  |  Y  |
# | IdTechBsp       | id_software.quake2                 |  Y  |
# | IdTechBsp       | id_software.quake3                 |  Y  |
# | IdTechBsp       | infinity_ward.call_of_duty1        |  Y  |
# | IdTechBsp       | infinity_ward.call_of_duty1_demo   |  Y  |
# | IdTechBsp       | ion_storm.daikatana                |  Y  |
# | IdTechBsp       | raven.solder_of_fortune            |  Y  |
# | IdTechBsp       | ritual.sin                         |  Y  |
# | InfinityWardBsp | infinity_ware.call_of_duty2        |  Y  |
# | QuakeBsp        | id_software.quake                  |  Y  |
# | QuakeBsp        | raven.hexen2                       |  Y  |
# | Quake64Bsp      | id_software.quake64                |  Y  |
# | RavenBsp        | raven.soldier_of_fortune2          |  Y  |
# | RavenBsp        | ritual.sin                         |  N  |  # investigate
# | ReMakeQuakeBsp  | id_software.remake_quake           |  Y  |
# | ReMakeQuakeBsp  | id_software.remake_quake_old       |  Y  |
# | RespawnBsp      | respawn.apex_legends               |  Y  |
# | RespawnBsp      | respawn.apex_legends50             |  Y  |
# | RespawnBsp      | respawn.apex_legends51             |  Y  |
# | RespawnBsp      | respawn.apex_legends52             |  Y  |
# | RespawnBsp      | respawn.titanfall                  |  Y  |
# | RespawnBsp      | respawn.titanfall_x360             |  N  |
# | RespawnBsp      | respawn.titanfall2                 |  Y  |
# | RitualBsp       | ritual.fakk2                       |  Y  |
# | RitualBsp       | ritual.mohaa                       |  Y  |
# | RitualBsp       | ritual.mohaa_bt                    |  Y  |
# | RitualBsp       | ritual.mohaa_demo                  |  Y  |
# | RitualBsp       | ritual.star_trek_elite_force2      |  Y  |
# | RitualBsp       | ritual.star_trek_elite_force2_demo |  Y  |
# | ValveBsp        | ace_team.zeno_clash                |  Y  |
# | ValveBsp        | arkane.dark_messiah_sp             |  Y  |
# | ValveBsp        | arkane.dark_messiah_mp             |  Y  |
# | ValveBsp        | strata.strata                      |  Y  |
# | ValveBsp        | loiste.infra                       |  Y  |
# | NexonBsp        | nexon.cso2                         |  Y  |
# | NexonBsp        | nexon.cso2_2018                    |  Y  |
# | ValveBsp        | nexon.vindictus                    |  Y  |
# | ValveBsp        | nexon.vindictus69                  |  Y  |
# | ValveBsp        | outerlight.outerlight              |  Y  |
# | ValveBsp        | troika.vampire                     |  Y  |
# | ValveBsp        | utoplanet.merubasu                 |  Y  |
# | ValveBsp        | valve.alien_swarm                  |  Y  |
# | ValveBsp        | valve.left4dead                    |  Y  |
# | ValveBsp        | valve.left4dead2                   |  Y  |
# | ValveBsp        | valve.orange_box                   |  Y  |
# | ValveBsp        | valve.orange_box_x360              |  N  |
# | ValveBsp        | valve.sdk_2013                     |  Y  |
# | ValveBsp        | valve.sdk_2013_x360                |  N  |
# | ValveBsp        | valve.source                       |  Y  |
# | ValveBsp        | valve.source_filmmaker             |  Y  |
# | Genesis3DBsp    | wild_tangent.genesis3d             |  Y  |

# TODO: more prefaces (insert .md)
# NOTE: conflicts:
# -- cso2 & cso2_2018
# -- goldsrc & blue_shift
# -- orange_box & merubasu
# -- qfusion & soldier_of_fortune2
# -- quake & hexen2
# -- remake_quake & remake_quake_old
valve_exclude = (
    valve.goldsrc, valve.alien_swarm, valve.left4dead, valve.left4dead2,
    *[bs for bs in valve.scripts if bs.__name__.endswith("_x360")])
groups = [
    ScriptGroup(
        "Titanfall Series", "titanfall.md", "Respawn Entertainment & NEXON", "respawn.md",
        {RespawnBsp: [respawn.titanfall, respawn.titanfall2]}),
    ScriptGroup(
        "Apex Legends", "apex_legends.md", "Respawn Entertainment", "respawn.md",
        {RespawnBsp: [respawn.apex_legends, respawn.apex_legends50, respawn.apex_legends51, respawn.apex_legends52]}),
    ScriptGroup(
        "Gold Source", "goldsrc.md", "Valve Software, Gearbox Software", "goldsrc.md",
        {GoldSrcBsp: [valve.goldsrc, gearbox.blue_shift, gearbox.nightfire]}),
    ScriptGroup(
        "Source Engine", "source.md", "Valve Software, Troika Games", "source.md",
        {ValveBsp: [
            *[bs for bs in valve.scripts if (bs not in valve_exclude)],
            ace_team.zeno_clash, loiste.infra,
            outerlight.outerlight, strata.strata,
            troika.vampire, utoplanet.merubasu]}),
    ScriptGroup(
        "Alien Swarm", "swarm.md", "Valve Software", "source.md",
        {ValveBsp: [valve.alien_swarm]}),
    ScriptGroup(
        "Dark Messiah SP", "dark_messiah_sp.md", "Arkane Studios", "darkmessiah_sp.md",
        {ValveBsp: [arkane.dark_messiah_sp]}),
    ScriptGroup(
        "Dark Messiah MP", "dark_messiah_mp.md", "Arkane Studios", "source.md",
        {ValveBsp: [arkane.dark_messiah_mp]}),
    ScriptGroup(
        "NEXON Source", "nexon.md", "NEXON", "source.md",
        {NexonBsp: [nexon.cso2, nexon.cso2_2018],
         ValveBsp: [nexon.vindictus69, nexon.vindictus]}),
    ScriptGroup(
        "Left 4 Dead Series", "left4dead.md", "Valve & Turtle Rock Studios", "left4dead.md",
        {ValveBsp: [valve.left4dead, valve.left4dead2]}),
    # TODO: present BSP2 / 2PSB / Q64 (FILE_MAGIC only; no BSP_VERSION) better
    ScriptGroup(
        "Quake Engine", "quake.md", "Id Software", None,
        {QuakeBsp: [id_software.quake, raven.hexen2],
         Quake64Bsp: [id_software.quake64],
         ReMakeQuakeBsp: [id_software.remake_quake, id_software.remake_quake_old]}),
    ScriptGroup(
        "Quake II Engine", "quake2.md", "Id Software, Ion Storm", None,
        {IdTechBsp: [
            id_software.quake2, ion_storm.daikatana,
            raven.soldier_of_fortune, ritual.sin]}),
    ScriptGroup(
        "Quake III Engine", "quake3.md", "Id Software", None,
        {FusionBsp: [id_software.qfusion],
         IdTechBsp: [id_software.quake3],
         RavenBsp: [raven.soldier_of_fortune2],
         RitualBsp: [bs for bs in ritual.scripts if (bs is not ritual.sin)]}),
    ScriptGroup(
        "Call of Duty", "cod.md", "Infinity Ward", None,
        {IdTechBsp: [infinity_ward.call_of_duty1_demo, infinity_ward.call_of_duty1],
         InfinityWardBsp: [infinity_ward.call_of_duty2]}),
    ScriptGroup(
        "Call of Duty: Modern Warfare", "cod_mw.md", "Infinity Ward", None,
        {D3DBsp: [infinity_ward.modern_warfare]}),
    ScriptGroup(
        "Genesis 3D", "genesis3d.md", "Wild Tangent", None,
        {Genesis3DBsp: [wild_tangent.genesis3d]})]
del valve_exclude

out_path = "../supported"
inserts_path = "inserts"

# NOTE: GAME_LUMP coverage is hardcoded later
SpecialLumpClass_confidence = defaultdict(lambda: 90)
SpecialLumpClass_confidence.update({
    branches.shared.Entities: 100,
    id_software.quake3.Visibility: 100,
    nexon.pakfile.PakFile: 75,  # 100% read, ~50% write
    respawn.apex_legends.LevelInfo: 75,
    respawn.titanfall.EntityPartitions: 100,
    respawn.titanfall.Grid: 100,
    respawn.titanfall.LevelInfo: 100,
    valve.source.PakFile: 100,
    valve.source.TextureDataStringData: 100})


def LumpClasses_of(branch_script: ModuleType) -> Dict[str, object]:
    out = {**branch_script.BASIC_LUMP_CLASSES, **branch_script.LUMP_CLASSES, **branch_script.SPECIAL_LUMP_CLASSES}
    out = {L: v for L, v in out.items() if hasattr(branch_script.LUMP, L)}
    return out


CoverageMap = Dict[ModuleType, Dict[str, int]]
# ^ {branch_script: ["LUMP_NAME": coverage%]}


def url_of_BspClass(BspClass: object) -> str:
    """gets a url to the definition of BspClass in the GitHub repo"""
    script_url = BspClass.__module__.split(".")
    if script_url[0] == "bsp_tool":
        script_url = script_url[1:]
    script_url = "/".join(script_url)
    line_number = inspect.getsourcelines(BspClass)[1]
    # TODO: block link "#L{start}-L{start + length}"
    lumpclass_url = f"{repo_url}/{script_url}.py#L{line_number}"
    return lumpclass_url


# TODO: quake_based branches never have unused lumps
def games_table(group: ScriptGroup, coverage: CoverageMap) -> List[str]:
    """branch_script.GAME_VERSIONS -> game_table"""
    lines = ["| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |\n",
             "| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |\n"]
    games = defaultdict(list)
    for branch_script in chain(*group.branch_scripts.values()):
        for game_name, bsp_version in branch_script.GAME_VERSIONS.items():
            if bsp_version is None:
                bsp_version = "0"
            else:
                bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else bsp_version
            games[str(bsp_version)].append((game_name, branch_script))
    bsp_classes = {bs: bc for bc, bss in group.branch_scripts.items() for bs in bss}
    for version in sorted(games, key=float):
        for game, branch_script in games[version]:
            BspClass = bsp_classes[branch_script]
            bsp_class = f"[`{BspClass.__name__}`]({url_of_BspClass(BspClass)})"
            script_name = branch_script.__name__[len("bsp_tool.branches."):]
            script = f"[`{script_name}`]({branches_url}{script_name.replace('.', '/')}.py)"
            unused = sum([L.name.startswith("UNUSED_") or L.name.startswith("VERTEX_RESERVED_")
                          for L in branch_script.LUMP])
            total = len(branch_script.LUMP) - unused
            supported = len(coverage[branch_script])
            percent = 0
            for lump_versions_dict in coverage[branch_script].values():
                percent += sum(lump_versions_dict.values()) / len(lump_versions_dict)
            percent /= total
            # {branch_script: {"LUMP_NAME": {lump_version: percent_covered}}}
            supported = f"{supported} / {total}"
            version = ".".join(map(str, version)) if isinstance(version, tuple) else version
            lines.append(f"| {bsp_class} | {version} | {game} | {script} | {supported} | {unused} | {percent:.2f}% |\n")
    return lines


def url_of_LumpClass(LumpClass: object) -> str:
    """gets a url to the definition of LumpClass in the GitHub repo"""
    script_url = LumpClass.__module__[len("bsp_tool.branches."):].replace(".", "/")
    try:
        line_number = inspect.getsourcelines(LumpClass)[1]
    except OSError as exc:  # cannot find definition (likely x360, generating via `eval` breaks inspect)
        print(f"Could not find definition for: {LumpClass.__name__}")
        raise exc
    lumpclass_url = f"{branches_url}{script_url}.py#L{line_number}"
    return lumpclass_url


# TODO: branch_script -> LIGHTMAP_LUMP -> extensions.lightmaps.function
vbsp_branch_scripts = [
    *[s for s in branches.valve.scripts if (s is not branches.valve.goldsrc)],
    *branches.arkane.scripts,
    branches.nexon.cso2,
    branches.nexon.vindictus,
    branches.nexon.vindictus69,
    branches.troika.vampire,
    branches.utoplanet.merubasu]
# TODO: outerlight, zeno_clash, infra, strata
# -- need to test; need certain lumps & members to function (Face.light_offset etc.)
# NOTE: coverage for each is currently hardcoded to 100%
# TODO: IdTechBsp & InfinityWardBsp (lightmap scale varies)
# TODO: use lightmaps.extract_branch to match functions
lightmap_mappings = {
    (branches.id_software.quake, "LIGHTING"): lightmaps.quake.face_lightmaps,
    (branches.id_software.quake2, "LIGHTING"): lightmaps.quake.face_lightmaps,  # ~90%; need scale
    (branches.id_software.quake3, "LIGHTMAPS"): lightmaps.quake3.extract,
    (branches.infinity_ward.modern_warfare, "LIGHTMAPS"): lightmaps.modern_warfare.extract,
    **{(branches.nexon.cso2_2018, L): lightmaps.cso2_2018.face_lightmaps
       for L in ("LIGHTING", "LIGHTING_HDR")},
    **{(bs, L): lightmaps.source.face_lightmaps for bs in vbsp_branch_scripts
       for L in ("LIGHTING", "LIGHTING_HDR")},
    **{(branches.respawn.titanfall, L): lightmaps.titanfall.extract
       for L in ("LIGHTMAP_DATA_REAL_TIME_LIGHTS", "LIGHTMAP_DATA_SKY")},
    **{(branches.respawn.titanfall2, L): lightmaps.titanfall2.extract
       for L in ("LIGHTMAP_DATA_REAL_TIME_LIGHTS", "LIGHTMAP_DATA_SKY")},
    **{(bs, L): lightmaps.apex_legends.extract
       for bs in (
           branches.respawn.apex_legends, branches.respawn.apex_legends50,
           branches.respawn.apex_legends51, branches.respawn.apex_legends52)
       for L in ("LIGHTMAP_DATA_REAL_TIME_LIGHTS", "LIGHTMAP_DATA_SKY")}}
# ^ {(branch_script, "LUMP"): function}
del vbsp_branch_scripts

method_mappings = {(branches.id_software.quake, "VISIBILITY"): (branches.id_software.quake.parse_vis, 75)}
# ^ {(branch_script, "LUMP"): (method, coverage)}

# TODO: list Quake derived LIGHTING & VISIBILITY


# lump coverage table
TableRow = namedtuple("TableRow", ["i", "bsp_version", "lump_name", "lump_version", "LumpClass", "coverage"])


# NOTE: base wrapper class is `GameLump if lump != dark_messiah_sp else DarkMessiahSPGameLump`
# NOTE: GameLumpHeader per branch_script is `branch_script.GAME_LUMP_HEADER`
gamelump_mappings = dict()
# ^ {"sub_lump": SpecialLumpClass, "sub_lump.child": {version: LumpClass}}
# NOTE: `None` mappings are used for structs that exist, but are not yet mapped
# TODO: cso2 & cso2_2018
unmapped_sprp = {
    branches.ace_team.zeno_clash: {7},
    branches.nexon.vindictus: {7},
    branches.outerlight.outerlight: {5, 6},
    branches.valve.source_filmmaker: {10}}

for branch_script in branches.source_based:
    d = {"sprp": {v: None for v in unmapped_sprp.get(branch_script, set())}}
    if branch_script.GAME_LUMP_CLASSES == dict():
        if len(d["sprp"]) < 0:
            gamelump_mappings[branch_script] = d
        else:
            gamelump_mappings[branch_script] = {"sprp": {"?": None}}
        continue
    d["sprp"].update(branch_script.GAME_LUMP_CLASSES["sprp"])
    d.update({"sprp.props": {
        v: glc.StaticPropClass
        for v, glc in branch_script.GAME_LUMP_CLASSES["sprp"].items()}})
    leaves = {
        v: branches.shared.UnsignedShorts
        for v, glc in d["sprp"].items()
        if glc is not None and hasattr(glc(), "leaves")}
    if len(leaves) != 0:
        d["sprp.leaves"] = leaves
    if branch_script in (branches.nexon.vindictus69, branches.nexon.vindictus):
        d["sprp.scales"] = {6: branches.nexon.vindictus69.StaticPropScale}
    if branch_script in {*branches.of_engine["Titanfall"]} - {branches.respawn.titanfall, branches.respawn.titanfall_x360}:
        d["sprp.unknown_3"] = {
            v: glc.Unknown3Class
            for v, glc in branch_script.GAME_LUMP_CLASSES["sprp"].items()}
    # TODO: "dprp": None etc.
    gamelump_mappings[branch_script] = d
del branch_script, d, leaves
del unmapped_sprp

# TODO: automatically skip changes in version number only
# keep apex_legends.md to v47, structs stay the same
gamelump_mappings[branches.respawn.apex_legends] = {
        k: {v: c for v, c in d.items() if v == 47}
        for k, d in gamelump_mappings[branches.respawn.apex_legends].items()}
gamelump_mappings[branches.respawn.apex_legends50] = gamelump_mappings[branches.respawn.apex_legends]
gamelump_mappings[branches.respawn.apex_legends51] = gamelump_mappings[branches.respawn.apex_legends]
gamelump_mappings[branches.respawn.apex_legends52] = gamelump_mappings[branches.respawn.apex_legends]


gamelump_coverage = dict()
# ^ {LumpClass: percent, SpecialLumpClass: percent}
# TODO: gather all the classes defined above and calculate their % unknown automatically
# -- split supported_md's coverage calculator into a function we can use
# TODO: include GameLump coverage in overall branch coverage
for branch_script in branches.source_based:
    if branch_script.GAME_LUMP_CLASSES == dict():
        continue
    for GameLumpClass in branch_script.GAME_LUMP_CLASSES["sprp"].values():
        # TODO: use coverage calculator for StaticPropClass
        gamelump_coverage.update({GameLumpClass: 100, GameLumpClass.StaticPropClass: 100})
del branch_script, GameLumpClass

gamelump_coverage.update({
    utoplanet.merubasu.StaticPropv11: 75,
    nexon.vindictus69.StaticPropScale: 100,
    respawn.titanfall.GameLump_SPRPv12: 60, respawn.titanfall.StaticPropv12: 94,
    respawn.titanfall2.GameLump_SPRPv13: 40, respawn.titanfall2.StaticPropv13: 92, respawn.titanfall2.Unknown3: 10,
    respawn.apex_legends.GameLump_SPRP: 40, respawn.apex_legends.Unknown3: 20,
    branches.shared.UnsignedShorts: 100})


# TODO: get functioning to level of hand crafted block
# -- [x] likely need a dict to map all subclasses
# -- [ ] checking versions in dict against branch scripts should help ensure all is up to date
# -- [ ] coverage data would also be ideal (mixing SpecialLumpClasses & regular LumpClasses)
def game_lump_table(branch_script: ModuleType) -> List[str]:
    base_GameLump = GameLump
    if branch_script is branches.arkane.dark_messiah_sp:
        base_GameLump = DarkMessiahSPGameLump
    game_lump_handler_url = f"{repo_url}/lumps/__init__.py#L{inspect.getsourcelines(base_GameLump)[1]}"
    game_lump_handler = f"[`lumps.{base_GameLump.__name__}`]({game_lump_handler_url})"
    # NOTE: GAME_LUMP version  in the .bsp header doesn't seem to matter atm, might affect Apex though...
    # TODO: precalculate coverage for the game table's total coverage calculation
    bsp_version = branch_script.BSP_VERSION
    bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else str(bsp_version)
    row_header = (branch_script.LUMP.GAME_LUMP.value, bsp_version)
    # TODO: use a coverage total here rather than defaulting to 90
    table_block = {TableRow(*row_header, "GAME_LUMP", "-", game_lump_handler, 90)}
    for sub_lump, mapping in gamelump_mappings[branch_script].items():
        game_lump_name = f"GAME_LUMP.{sub_lump}"
        for lump_version, LumpClass in mapping.items():
            if LumpClass is not None:
                lump_class_module = LumpClass.__module__[len("bsp_tool.branches."):]
                lump_class = f"[`{lump_class_module}.{LumpClass.__name__}`]({url_of_LumpClass(LumpClass)})"
                # TODO: get LumpClass / SpecialLumpClass coverage
                percent = gamelump_coverage.get(LumpClass, 90)
            else:
                lump_class = ""
                percent = 0
            table_block.add(TableRow(*row_header, game_lump_name, lump_version, lump_class, percent))
    return table_block


def lump_table(group: ScriptGroup, coverage: CoverageMap, versioned_lumps=False, titanfall_engine=False) -> List[str]:
    row_head = lambda r: f"| {r.i} | {r.bsp_version} | `{r.lump_name}` |"  # noqa E731
    row_as_string = lambda r: " ".join((row_head(r), f"{r.lump_version} | {r.LumpClass} | {r.coverage}% |\n"))  # noqa E731
    if not versioned_lumps:  # IdTech / GoldSrc / IW Engine
        lines = ["| Lump index | Bsp version | Lump name | LumpClass | Coverage |\n",
                 "| ---------: | ----------: | --------- | --------- | :------- |\n"]
        row_as_string = lambda r: " ".join((row_head(r), f"{r.LumpClass} | {r.coverage}% |\n"))  # noqa E731
    elif not titanfall_engine:  # Source
        lines = ["| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |\n",
                 "| ---------: | ----------: | --------- | -----------: | --------- | :------- |\n"]
    else:  # Titanfall Engine
        lines = ["| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | Coverage |\n",
                 "| ---------: | --------: | ----------: | --------- | -----------: | --------- | :------- |\n"]
        row_head = lambda r: f"| {r.i} | {i:04X} | {r.bsp_version} | `{r.lump_name}` |"  # noqa E731
    # lines for each lump; sorted by lump_index, then bsp_version
    branch_scripts = list(chain(*group.branch_scripts.values()))
    lump_classes = {bs: LumpClasses_of(bs) for bs in branch_scripts}
    if not versioned_lumps:
        lump_classes = {bs: {ln: {0: lc} for ln, lc in ld.items()} for bs, ld in lump_classes.items()}
    max_lumps = max([max([e.value for e in bs.LUMP]) for bs in branch_scripts]) + 1
    # TODO: find a way to make the blue shift lump swap clearer
    # -- same bsp_version!
    # -- would also be nice to present more branch_script families in a single script
    # --- maybe game icons instead of bsp versions?
    # NOTE: CoD4Bsp uses IDs for each lump, so we have to iterate over the present values, not just a range
    # TODO: replace CoD4 "lump index" label with "lump id"
    for i in range(max_lumps):
        table_block = set()
        for branch_script in branch_scripts:
            if i not in {L.value for L in branch_script.LUMP}:
                continue  # this branch_script does not have this lump
            lump_name = branch_script.LUMP(i).name
            bsp_version = branch_script.BSP_VERSION
            if bsp_version is None:
                bsp_version = "0"
            else:
                bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else str(bsp_version)
                # (20, 4) -> "20.4"; 29 -> "29"
            # TODO: move special cases (Lightmaps, GameLump etc.) to coverage to be counted in branch_script total
            if lump_name == "GAME_LUMP":
                game_lump_block = game_lump_table(branch_script)
                table_block.update(game_lump_block)
            elif (branch_script, lump_name) in lightmap_mappings:
                LumpClass = lightmap_mappings[(branch_script, lump_name)]
                lump_class = f"[`extensions.lightmaps.{LumpClass.__name__}`]({url_of_BspClass(LumpClass)})"
                table_block.add(TableRow(i, bsp_version, lump_name, 0, lump_class, 100))
            elif (branch_script, lump_name) in method_mappings:
                method, percent = method_mappings[(branch_script, lump_name)]
                method_module = method.__module__[len("bsp_tool.branches."):]
                method_link = f"[`{method_module}.{method.__name__}`]({url_of_BspClass(method)})"
                table_block.add(TableRow(i, bsp_version, lump_name, 0, method_link, percent))
            elif lump_name not in lump_classes[branch_script]:
                table_block.add(TableRow(i, bsp_version, lump_name, 0, "", 0))
            else:  # standard lump
                for lump_version in lump_classes[branch_script][lump_name]:
                    percent = coverage[branch_script][lump_name][lump_version]
                    LumpClass = lump_classes[branch_script][lump_name][lump_version]
                    lump_class_module = LumpClass.__module__[len("bsp_tool.branches."):]
                    lump_class = f"[`{lump_class_module}.{LumpClass.__name__}`]({url_of_LumpClass(LumpClass)})"
                    table_block.add(TableRow(i, bsp_version, lump_name, lump_version, lump_class, percent))
        fix = lambda x: x if isinstance(x, (int, float)) else -1  # noqa E731
        sorted_block = list(sorted(table_block, key=lambda row: (float(row.bsp_version), fix(row.lump_version))))
        if len(sorted_block) == 0:
            continue
        # start removing doubles
        # -- same LUMP_NAME & LumpClass is an implied ditto
        # -- record only the point of change
        # -- e.g. v7: LumpClassv7; v8: None; v10: LumpClassv10
        final_block = [sorted_block[0]]
        lump_names = {r.lump_name for r in sorted_block}
        unused_lumps = {ln.startswith("UNUSED_") for ln in lump_names}
        partially_unused = any(unused_lumps) and not all(unused_lumps)
        for row in sorted_block[1:]:
            # TODO: remove redundant text between lines
            # -- cannot simply remove lump_index if titanfall_engine /;
            if partially_unused and not row.lump_name.startswith("UNUSED_"):
                # NOTE: assumes sorted_block[0] starts with "UNUSED_"
                # NOTE: might still have duplicate lump classes in this scenario!
                # -- mostly trying to catch lump_name changes when there is no LumpClass
                final_block.append(row)
                continue
            elif row.LumpClass == final_block[-1].LumpClass:
                continue  # remove repeats
            final_block.append(row)
        if "GAME_LUMP" in lump_names:  # alternate sorting & reduction
            # sort by (bsp_version, lump_version, lump_name)
            sorted_block = sorted(table_block, key=lambda row: (float(row.bsp_version), fix(row.lump_version), row.lump_name))
            # remove duplicate (lump_name, lump_version, LumpClass)
            defined = list()
            final_block = list()
            for row in sorted_block:
                key = (row.lump_name, row.lump_version, row.LumpClass)
                if key not in defined:
                    final_block.append(row)
                    defined.append(key)
        lines.extend(map(row_as_string, final_block))
    return lines


def supported_md(group: ScriptGroup) -> List[str]:
    lines = [f"# {group.headline}\n",
             f"## Developers: {group.developers}\n\n"]
    versioned_lumps: bool = any([k in (ValveBsp, RespawnBsp) for k in group.branch_scripts.keys()])
    # COVERAGE CALCULATIONS
    coverage = dict()
    # ^ {branch_script: {"LUMP_NAME": {lump_version: percent_covered}}}
    # TODO: some .bsp may contain lump versions that haven't been supported yet
    # -- would be worth mapping such lumps with tests.maplist.installed_games
    # -- since this still constitutes unmapped lumps (a non-public version 0 would not, however)
    # -- only known .bsp files matter, no need for hypotheticals (don't really care about leaked betas either)
    # TODO: have some override list for edge cases (e.g. LEVEL_INFO & PHYSICS_LEVEL)
    # -- respawn.titanfall2.PHYSICS_LEVEL is just the lump.version metadata
    for branch_script in chain(*group.branch_scripts.values()):
        coverage[branch_script] = defaultdict(dict)
        for lump_name, LumpClass_dict in LumpClasses_of(branch_script).items():
            if not versioned_lumps:
                LumpClass_dict = {0: LumpClass_dict}
            for lump_version, LumpClass in LumpClass_dict.items():
                if lump_name in branch_script.LUMP_CLASSES:
                    # TODO: calculate unknowns as % of bytes mapped
                    # -- should be able to use split_format for this
                    # -- also, break out this coverage calculator into another function
                    if issubclass(LumpClass, branches.base.Struct):
                        attrs = len(LumpClass.__slots__)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass.__slots__])
                        # TODO: nested attrs (get format of unknown & divide by struct.calcsize()
                        # -- child BitField unknowns
                    elif issubclass(LumpClass, branches.base.MappedArray):
                        attrs = len(LumpClass._mapping)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass._mapping])
                    elif issubclass(LumpClass, branches.base.BitField):
                        attrs = len(LumpClass._fields.keys())
                        unknowns = sum([a.startswith("unknown") for a in LumpClass._fields.keys()])
                    elif issubclass(LumpClass, list):  # quake.Edge / vindictus.Edge etc.
                        attrs, unknowns = 1, 0
                    percent = int((100 / attrs) * (attrs - unknowns)) if unknowns != attrs else 0
                elif lump_name in branch_script.SPECIAL_LUMP_CLASSES or lump_name == "GAME_LUMP":
                    if lump_name == "GAME_LUMP":
                        mapped_classes = gamelump_mappings.get(branch_script, dict())
                        coverages = list()
                        for child in mapped_classes.values():
                            if isinstance(child, dict):
                                coverages.extend([gamelump_coverage.get(lc, 0) for lc in child.values()])
                            else:
                                coverages.append(gamelump_coverage.get(child, 0))
                        percent = sum(coverages) / len(coverages)
                    else:
                        SpecialLumpClass = LumpClass_dict[lump_version]
                        percent = SpecialLumpClass_confidence[SpecialLumpClass]
                else:  # BASIC_LUMP_CLASSES
                    percent = 100
                coverage[branch_script][lump_name][lump_version] = percent
        for lump_name in [L.name for L in branch_script.LUMP]:
            key = (branch_script, lump_name)
            if key in lightmap_mappings:
                percent = 100
            elif key in method_mappings:
                percent = method_mappings[(branch_script, lump_name)][1]
            else:
                continue
            # TODO: verify lump_version is always 0
            coverage[branch_script][lump_name][0] = percent
    # END COVERAGE CALCULATIONS
    lines.extend(games_table(group, coverage))
    lines.append("\n\n")
    # TODO: insert notes from branch_scripts:
    # -- changes from X -> Y
    # -- rough lump relationships
    # -- inspect.getmodule() + inspect.getcomments() + regex?
    if group.insert is not None:
        with open(os.path.join(inserts_path, group.insert)) as insert:
            lines.extend(insert.readlines())
            lines.append("\n\n")
    lines.append("## Supported Lumps\n")
    has_titanfall_engine = any([bs.FILE_MAGIC == b"rBSP" for bs in chain(*group.branch_scripts.values())])
    lines.extend(lump_table(group, coverage, versioned_lumps, has_titanfall_engine))
    lines.append("\n\n")
    return lines


if __name__ == "__main__":
    # TODO: run this script via GitHub actions to keep docs up to date w/ latest commit
    # -- would probably require moving docs to a separate branch
    # -- could also copy the changelog with this approach
    for group in groups:
        print(f"Writing {group.filename}...")
        with open(os.path.join(out_path, group.filename), "w") as outfile:
            outfile.write("".join(supported_md(group)))
