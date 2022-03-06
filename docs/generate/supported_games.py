from collections import defaultdict, namedtuple
import inspect
from itertools import chain
import os
import re
import sys
from types import FunctionType, ModuleType
from typing import Dict, List

# HACK: load ../../bsp_tool from docs/generate/
sys.path.insert(0, "../../")
from bsp_tool import GoldSrcBsp, RespawnBsp, ValveBsp, QuakeBsp  # noqa: E402
from bsp_tool import branches  # noqa: E402
from bsp_tool.extensions import lightmaps  # noqa: E402
from bsp_tool.lumps import GameLump  # noqa: E402

# NOTE: forks should substitute their own repo here
# TODO: get the last commit hash from `git rev-parse HEAD` for permalinks
# -- default to master if git cannot be run
# -- gitpython might be a good library for this
repo_url = "https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool"
branches_url = f"{repo_url}/branches/"

# Each group gets a .md; lots of formats pretty close, so sharing a table isn't a big deal
ScriptGroup = namedtuple("ScriptGroup", ["headline", "filename", "developers", "insert", "branch_scripts"])
source_exclude = (branches.valve.goldsrc, branches.valve.alien_swarm,
                  branches.valve.left4dead, branches.valve.left4dead2,
                  *[bs for bs in branches.valve.scripts if bs.__name__.endswith("_x360")])
# NOTE: per BspClass fils could probably be generated: (would be quite messy though)
# -- bsp_tool.BspVariant_from_file_magic + branches.scripts_from_file_magic
# -- confirming all the BspClasses line up is pretty important though
# NOTE: x360 branch scripts are generated almost entirely from existing branch scripts
# -- this is incomplete however, as bitfields are also inverted somewhat
# -- no support for bitfields of any order exists yet anyway, however
# TODO: sort alphabetically
# TODO: IW Engine branches
# TODO: check all base.Bsp subclasses & are covered, and all scripts
groups = [ScriptGroup("Titanfall Series", "titanfall.md", "Respawn Entertainment & NEXON", "respawn.md",
                      {RespawnBsp: [branches.respawn.titanfall, branches.respawn.titanfall2]}),
          ScriptGroup("Apex Legends", "apex.md", "Respawn Entertainment", "respawn.md",
                      {RespawnBsp: [branches.respawn.apex_legends]}),
          ScriptGroup("Gold Source", "goldsrc.md", "Valve Software, Gearbox Software", "goldsrc.md",
                      {GoldSrcBsp: [branches.valve.goldsrc, branches.gearbox.blue_shift, branches.gearbox.nightfire]}),
          ScriptGroup("Source Engine", "source.md", "Valve Software, Troika Games", "source.md",
                      {ValveBsp: [*[bs for bs in branches.valve.scripts if (bs not in source_exclude)],
                                  branches.troika.vampire]}),
          ScriptGroup("Alien Swarm", "swarm.md", "Valve Software", "source.md",
                      {ValveBsp: [branches.valve.alien_swarm]}),
          ScriptGroup("Dark Messiah SP", "darkmessiah_sp.md", "Arkane Studios", "source.md",
                      {ValveBsp: [branches.arkane.dark_messiah_singleplayer]}),
          ScriptGroup("Dark Messiah MP", "darkmessiah_mp.md", "Arkane Studios", "source.md",
                      {ValveBsp: [branches.arkane.dark_messiah_multiplayer]}),
          ScriptGroup("NEXON Source", "nexon.md", "NEXON", "source.md",
                      {ValveBsp: branches.nexon.scripts}),
          ScriptGroup("Left 4 Dead Series", "left4dead.md", "Valve & Turtle Rock Studios", "left4dead.md",
                      {ValveBsp: [branches.valve.left4dead, branches.valve.left4dead2]}),
          ScriptGroup("Quake Engine", "quake.md", "Id Software", None,
                      {QuakeBsp: [branches.id_software.quake, branches.raven.hexen2]}),
          ScriptGroup("Quake II Engine", "quake2.md", "Id Software, Ion Storm", None,
                      {QuakeBsp: [branches.id_software.quake2, branches.ion_storm.daikatana,
                                  branches.raven.soldier_of_fortune, branches.ritual.sin]}),
          ScriptGroup("Quake III Engine", "quake3.md", "Id Software", None,
                      {QuakeBsp: [branches.id_software.quake3, branches.raven.soldier_of_fortune2,
                                  *[bs for bs in branches.ritual.scripts if (bs is not branches.ritual.sin)]]})]
del source_exclude

out_path = "../supported"
inserts_path = "inserts"
# TODO: rethink inserts
# -- order could be more dynamic
# -- lump relationship maps from branch_script comments
# deprecated lump lists
# engine map w/ links to other tables?


# TODO: declare confidence by SpecialLumpClass, not LUMP_NAME
SpecialLumpClass_confidence = defaultdict(lambda: 90)
SpecialLumpClass_confidence.update({"ENTITIES": 100,
                                    "ENTITY_PARTITIONS": 100,
                                    "PAKFILE": 100,  # 0 for CSO2!
                                    "SURFACE_NAMES": 100,
                                    "TEXTURE_DATA_STRING_DATA": 100})


def LumpClasses_of(branch_script: ModuleType) -> Dict[str, object]:
    return {**branch_script.BASIC_LUMP_CLASSES, **branch_script.LUMP_CLASSES, **branch_script.SPECIAL_LUMP_CLASSES}


CoverageMap = Dict[ModuleType, Dict[str, int]]
# ^ {branch_script: ["LUMP_NAME": known%]}


def url_of_BspClass(BspClass: object) -> str:
    """gets a url to the definition of BspClass in the GitHub repo"""
    script_url = BspClass.__module__.replace(".", "/")
    line_number = inspect.getsourcelines(BspClass)[1]
    # TODO: block link "#L{start}-L{start + length}"
    lumpclass_url = f"{repo_url}/{script_url}.py#L{line_number}"
    return lumpclass_url


def games_table(group: ScriptGroup, coverage: CoverageMap) -> List[str]:
    """branch_script.GAME_VERSIONS -> game_table"""
    lines = ["| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |\n",
             "| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |\n"]
    games = defaultdict(list)
    for branch_script in chain(*group.branch_scripts.values()):
        for game_name, bsp_version in branch_script.GAME_VERSIONS.items():
            bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else bsp_version
            games[str(bsp_version)].append((game_name, branch_script))
    bsp_classes = {bs: bc for bc, bss in group.branch_scripts.items() for bs in bss}
    for version in sorted(games, key=lambda v: float(v)):
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
vbsp_branch_scripts = [*[s for s in branches.valve.scripts if (s is not branches.valve.goldsrc)],
                       *branches.nexon.scripts, branches.troika.vampire, *branches.arkane.scripts]
lightmap_mappings = {**{(bs, L): lightmaps.save_vbsp for bs in vbsp_branch_scripts
                        for L in ("LIGHTING", "LIGHTING_HDR")},
                     **{(branches.respawn.titanfall, L): lightmaps.save_rbsp_r1
                        for L in ("LIGHTMAP_DATA_REAL_TIME_LIGHTS", "LIGHTMAP_DATA_SKY")},
                     **{(branches.respawn.titanfall2, L): lightmaps.save_rbsp_r2
                        for L in ("LIGHTMAP_DATA_REAL_TIME_LIGHTS", "LIGHTMAP_DATA_SKY")}}
# TODO: IdTechBsp & InfinityWardBsp (lightmap scale varies)
del vbsp_branch_scripts


TableRow = namedtuple("TableRow", ["i", "bsp_version", "lump_name", "lump_version", "LumpClass", "coverage"])


# TODO: get functioning to level of hand crafted block
# -- likely need a dict to map all subclasses
# -- checking versions in dict against branch scripts should help ensure all is up to date
# -- coverage data would also be ideal (mixing SpecialLumpClasses & regular LumpClasses)
def game_lump_table(branch_script: ModuleType, row_as_string: FunctionType) -> List[str]:
    game_lump_handler_url = f"{repo_url}/lumps/__init__.py#L{inspect.getsourcelines(GameLump)[1]}"
    game_lump_handler = f"[`lumps.GameLump`]({game_lump_handler_url})"
    # NOTE: GAME_LUMP version  in the .bsp header doesn't seem to matter atm, might affect Apex though...
    # TODO: actually calculate ~{coverage - 10} in the coverage dict
    # -- would probably require putting this GameLump iterator thing in a generator of some kind
    bsp_version = branch_script.BSP_VERSION
    bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else str(bsp_version)
    row_header = (branch_script.LUMP.GAME_LUMP.value, bsp_version)
    table_block = {row_as_string(TableRow(*row_header, "`GAME_LUMP`", "-", game_lump_handler, 90))}
    for lump_name in branch_script.GAME_LUMP_CLASSES:
        for lump_version in branch_script.GAME_LUMP_CLASSES[lump_name]:
            GameLumpClass = branch_script.GAME_LUMP_CLASSES[lump_name][lump_version]
            GameLumpClass_url = url_of_LumpClass(GameLumpClass)
            game_lump_name = f"[`GAME_LUMP.{lump_name}`]({GameLumpClass_url})"
            if isinstance(GameLumpClass, FunctionType):
                lump_class = re.search(r"raw_lump, (.*)\)", inspect.getsource(GameLumpClass)).groups()[0]  # noqa
                # NOTE: ^ lazy solution
                print(lump_class)
                if lump_class == "None":
                    table_block.add(TableRow(*row_header, game_lump_name, lump_version, "", 0))
                    continue
                # NOTE: tracking down an object from a string is insane
                # -- maybe don't bother?
                child_class = inspect.getmodule(GameLumpClass)
                for attr in lump_class.split("."):
                    child_class = getattr(child_class, attr)  # TODO: breaking here-ish
                assert child_class.__module__.startswith("bsp_tool.branches.")
                child_class_name = child_class.__name__[len("bsp_tool.branches."):]
                lump_class = f"[`{child_class_name}`]({url_of_LumpClass(child_class)})"
            else:
                lump_class = f"[`{GameLumpClass.__name__}`]({GameLumpClass_url})"
            # TODO: cover GameLumpClass child classes
            # percent = coverage[branch_script][lump_name][lump_version]
            percent = 90
            table_block.add(TableRow(*row_header, game_lump_name, lump_version, lump_class, percent))
            # NOTE: GameLumpClasses are generally SpecialLumpClasses
            # -- this means coverage cannot be measured accurately
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
    max_lumps = max([len(bs.LUMP) for bs in branch_scripts])
    # TODO: find a way to make the blue shift lump swap clearer
    # -- same bsp_version!
    # NOTE: CoD4Bsp uses IDs for each lump, so we have to iterate over the present values, not just a range
    # -- for i in sorted({L.value for bs in branch_scripts for L in bs.LUMP}):
    # if i not in {L.value for L in branch_script.LUMP}
    for i in range(max_lumps):
        table_block = set()
        for branch_script in branch_scripts:
            if i >= len(branch_script.LUMP):
                continue  # this branch_script does not have this lump
            lump_name = branch_script.LUMP(i).name
            bsp_version = branch_script.BSP_VERSION
            bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else str(bsp_version)
            # TODO: move special cases (Lightmaps, GameLump etc.) to coverage to be counted in branch_script total
            # if lump_name == "GAME_LUMP":
            #     # NOTE: likely won't play nice with sorting
            #     # might be easier to write the whole block?
            #     game_lump_block = game_lump_table(branch_script, row_as_string)
            #     table_block.update(game_lump_block)
            if (branch_script, lump_name) in lightmap_mappings:
                LumpClass = lightmap_mappings[(branch_script, lump_name)]
                lump_class = f"[`extensions.lightmaps.{LumpClass.__name__}`]({url_of_BspClass(LumpClass)})"
                table_block.add(TableRow(i, bsp_version, lump_name, 0, lump_class, 100))
            elif lump_name not in lump_classes[branch_script]:
                table_block.add(TableRow(i, bsp_version, lump_name, 0, "", 0))
            else:
                for lump_version in lump_classes[branch_script][lump_name]:
                    percent = coverage[branch_script][lump_name][lump_version]
                    LumpClass = lump_classes[branch_script][lump_name][lump_version]
                    lump_class_module = LumpClass.__module__[len("bsp_tool.branches."):]
                    lump_class = f"[`{lump_class_module}.{LumpClass.__name__}`]({url_of_LumpClass(LumpClass)})"
                    table_block.add(TableRow(i, bsp_version, lump_name, lump_version, lump_class, percent))
        # TODO: sort differently if GAME_LUMP
        sorted_block = list(sorted(table_block, key=lambda r: float(r.bsp_version) * 2 + r.lump_version))
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
                continue  # no repeats
            final_block.append(row)
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
    # -- since this still constitutes unmapped lumps (a non-present version 0 would not, however)
    # -- only known .bsp files matter, no need for hypotheticals (don't really care about leaked betas either)
    # TODO: include lightmap coverage via lightmap_mappings
    # TODO: have some override list for edge cases (e.g. LEVEL_INFO & PHYSICS_LEVEL)
    for branch_script in chain(*group.branch_scripts.values()):
        coverage[branch_script] = defaultdict(dict)
        for lump_name, LumpClass_dict in LumpClasses_of(branch_script).items():
            if not versioned_lumps:
                LumpClass_dict = {0: LumpClass_dict}
            for lump_version, LumpClass in LumpClass_dict.items():
                if lump_name in branch_script.LUMP_CLASSES:
                    # TODO: calculate unknowns as % of bytes mapped
                    if issubclass(LumpClass, branches.base.Struct):
                        attrs = len(LumpClass.__slots__)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass.__slots__])
                        # TODO: nested attrs (get format of unknown & divide by struct.calcsize()
                    elif issubclass(LumpClass, branches.base.MappedArray):
                        attrs = len(LumpClass._mapping)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass._mapping])
                    elif issubclass(LumpClass, list):  # quake.Edge / vindictus.Edge etc.
                        attrs, unknowns = 1, 0
                    percent = int((100 / attrs) * (attrs - unknowns)) if unknowns != attrs else 0
                elif lump_name in branch_script.SPECIAL_LUMP_CLASSES or lump_name == "GAME_LUMP":
                    percent = SpecialLumpClass_confidence[lump_name]
                else:  # BASIC_LUMP_CLASSES
                    percent = 100
                coverage[branch_script][lump_name][lump_version] = percent
        # TODO: GAME_LUMP_CLASSES (StaticPropvX etc.)
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
