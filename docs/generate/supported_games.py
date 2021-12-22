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
from bsp_tool import ArkaneBsp, GoldSrcBsp, RespawnBsp, ValveBsp  # noqa: E402
from bsp_tool import branches  # noqa: E402
from bsp_tool.extensions import lightmaps  # noqa: E402
from bsp_tool.lumps import GameLump  # noqa: E402

# NOTE: forks should substitute their own repo here
repo_url = "https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool"
branches_url = f"{repo_url}/branches/"

# detailing groups, some formats have enough overlap to be grouped
ScriptGroup = namedtuple("ScriptGroup", ["name", "filename", "developers", "insert", "branch_scripts"])
groups = [ScriptGroup("Titanfall Series", "titanfall.md", "Respawn Entertainment", "respawn.md",
                      {RespawnBsp: [branches.respawn.titanfall, branches.respawn.titanfall2]}),
          ScriptGroup("Apex Legends", "apex.md", "Respawn Entertainment", "respawn.md",
                      {RespawnBsp: [branches.respawn.apex_legends]}),
          ScriptGroup("Gold Source", "goldsrc.md", "Valve Software, Gearbox Software", "goldsrc.md",
                      {GoldSrcBsp: [branches.valve.goldsrc, branches.gearbox.blue_shift, branches.gearbox.nightfire]}),
          ScriptGroup("Source Engine", "source.md", "Valve Software, NEXON, Troika Games, Arkane Studios", "source.md",
                      {ValveBsp: [*[s for s in branches.valve.scripts if (s is not branches.valve.goldsrc)],
                                  *branches.nexon.scripts, branches.troika.vampire],
                       ArkaneBsp: [branches.arkane.dark_messiah_multiplayer,
                                   branches.arkane.dark_messiah_singleplayer]})]
out_path = "../supported"
inserts_path = "inserts"


SpecialLumpClass_confidence = defaultdict(lambda: 90)
SpecialLumpClass_confidence.update({"ENTITIES": 100,
                                    "ENTITY_PARTITIONS": 100,
                                    "TEXTURE_DATA_STRING_DATA": 100,
                                    "SURFACE_NAMES": 100})


def LumpClasses_of(branch_script: ModuleType) -> Dict[str, object]:
    return {**branch_script.BASIC_LUMP_CLASSES, **branch_script.LUMP_CLASSES, **branch_script.SPECIAL_LUMP_CLASSES}


CoverageMap = Dict[ModuleType, Dict[str, int]]
# ^ {branch_script: ["LUMP_NAME": known%]}


def url_of_BspClass(BspClass: object) -> str:
    """gets a url to the definition of BspClass in the GitHub repo"""
    script_url = BspClass.__module__.replace(".", "/")
    line_number = inspect.getsourcelines(BspClass)[1]
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
    for version in sorted(games):
        for game, branch_script in games[version]:
            BspClass = bsp_classes[branch_script]
            bsp_class_name = BspClass.__name__
            bsp_class = f"[`{bsp_class_name}`]({url_of_BspClass(BspClass)})"
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
    script_url = LumpClass.__module__[len('bsp_tool.branches.'):].replace(".", "/")
    line_number = inspect.getsourcelines(LumpClass)[1]
    lumpclass_url = f"{branches_url}{script_url}.py#L{line_number}"
    return lumpclass_url


# TODO: branch_script -> LIGHTMAP_LUMP -> extensions.lightmaps.function
vbsp_branch_scripts = chain(*[g for g in groups if g.name == "Source Engine"][0].branch_scripts.values())
lightmap_mappings = {**{bs: lightmaps.save_vbsp for bs in vbsp_branch_scripts},
                     branches.respawn.titanfall: lightmaps.save_rbsp_r1,
                     branches.respawn.titanfall2: lightmaps.save_rbsp_r2}  # also covers Apex? unsure
# TODO: IdTechBsp & InfinityWardBsp
del vbsp_branch_scripts


def unversioned_lump_table(group: ScriptGroup, coverage: CoverageMap) -> List[str]:
    lines = ["| Lump index | Bsp version | Lump name | LumpClass | Coverage |\n",
             "| ---------: | ----------: | --------- | --------- | :------- |\n"]
    branch_scripts = list(chain(*group.branch_scripts.values()))
    lumpclasses = {bs: LumpClasses_of(bs) for bs in branch_scripts}
    max_lumps = max([len(bs.LUMP) for bs in branch_scripts])
    for i in range(max_lumps):
        for branch_script in branch_scripts:
            if i >= len(branch_script.LUMP):
                continue  # this branch_script is done
            lump_name = branch_script.LUMP(i).name
            bsp_version = branch_script.BSP_VERSION
            # NOTE: no tracking on what lumps are unique to which version
            if lump_name.startswith("UNUSED_"):
                continue  # skip unused lumps
            # TODO: Lightmap data might be covered by extensions.lightmaps
            elif lump_name not in lumpclasses[branch_script]:
                lines.append(f"| {i} | {bsp_version} | `{lump_name}` | | 0% |")
            else:
                LumpClass = lumpclasses[branch_script][lump_name]
                lump_class_module = LumpClass.__module__[len('bsp_tool.branches.'):]
                lump_class = f"[{lump_class_module}.{LumpClass.__name__}]({url_of_LumpClass(LumpClass)})"
                percent = coverage[branch_script][lump_name][None]
                # HACK: ^ coverage expects all lumpclasses to be versioned
                # -- so unversioned LumpClasses are version None; if it works, it works
                lines.append(f"| {i} | {bsp_version} | `{lump_name}` | {lump_class} | {percent}% |")
    return lines


def game_lump_table(branch_script: ModuleType, head: str) -> List[str]:
    lines, tails = list(), list()
    return lines, tails  # HACK: muting for now
    game_lump_handler_url = f"{repo_url}/lumps/__init__.py#L{inspect.getsourcelines(GameLump)[1]}"
    game_lump_handler = f"[`lumps.GameLump`]({game_lump_handler_url})"
    # NOTE: GAME_LUMP version doesn't seem to matter atm, might affect Apex & ArkaneBsp though...
    # TODO: actually calculate ~{coverage - 10} in the coverage dict
    # -- would probably require putting this GameLump iterator thing in a generator of some kind
    lines.append(" ".join([head, f"| `GAME_LUMP` | - | {game_lump_handler} | 90% |"]))
    for lump_name in branch_script.GAME_LUMP_CLASSES:
        for lump_version in branch_script.GAME_LUMP_CLASSES[lump_name]:
            GameLumpClass = branch_script.GAME_LUMP_CLASSES[lump_name][lump_version]
            GameLumpClass_url = url_of_LumpClass(GameLumpClass)
            game_lump_name = f"[`GAME_LUMP.{lump_name}`]({GameLumpClass_url})"
            if isinstance(GameLumpClass, FunctionType):
                lump_class = re.search(r"raw_lump, (.*)\)", inspect.getsource(GameLumpClass)).groups()[0]  # noqa
                # NOTE: ^ lazy solution
                # tracking down an object from a string is insane
                # maybe GameLumpClasses should use "decorators" instead?
                # this would create a class object with a traceable StaticPropClass attr?
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
            tails.append(f"| {game_lump_name} | {lump_version} | {lump_class} | {percent}% |\n")
            # NOTE: GameLumpClasses are generally SpecialLumpClasses
            # -- this means coverage cannot be measured accurately
    return lines, tails


def versioned_lump_table(group: ScriptGroup, coverage: CoverageMap, titanfall_engine=False) -> List[str]:
    if not titanfall_engine:
        lines = ["| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |\n",
                 "| ---------: | ----------: | --------- | -----------: | --------- | :------- |\n"]
        lump_index = lambda i: f"{i}"  # noqa: E731
    else:
        lines = ["| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | Coverage |\n",
                 "| ---------: | --------: | ----------: | --------- | -----------: | --------- | :------- |\n"]
        lump_index = lambda i: f"{i} | {i:04X}"  # noqa: E731
    # lines for each lump; sorted by lump_index, then bsp_version
    branch_scripts = list(chain(*group.branch_scripts.values()))
    lumpclasses = {bs: LumpClasses_of(bs) for bs in branch_scripts}
    max_lumps = max([len(bs.LUMP) for bs in branch_scripts])
    for i in range(max_lumps):
        # TODO: sort lines generated per lump by version number
        # TODO: remove redundant info between lines, leaving only deltas
        # -- this will probably require tracking the last entry per chunk
        # -- processing each lump index as a chunk makes a lot of sense actually; do that
        for branch_script in branch_scripts:
            if i > len(branch_script.LUMP):
                continue  # this branch_script is done
            lump_name = branch_script.LUMP(i).name
            bsp_version = branch_script.BSP_VERSION
            bsp_version = ".".join(map(str, bsp_version)) if isinstance(bsp_version, tuple) else bsp_version
            # NOTE: no tracking on what lumps are unique to which version
            head = f"| {lump_index(i)} | {bsp_version} |"
            tails = list()
            if lump_name.startswith("UNUSED_") or lump_name.startswith("VERTEX_RESERVED_"):
                continue  # skip unused lumps
            elif lump_name == "GAME_LUMP":
                # TODO: skip if branch_script.GAME_LUMP_CLASSES is the same as previous
                game_lump_lines, game_lump_tails = game_lump_table(branch_script, head)
                lines.extend(game_lump_lines)
                tails.extend(game_lump_tails)
            # TODO: Lightmap data might be covered by extensions.lightmaps
            elif lump_name not in lumpclasses[branch_script]:
                tails.append(f"`{lump_name}` | 0 | | 0% |")
            else:
                # TODO: some non-100% LumpClasses are being skipped why?
                for lump_version in sorted(lumpclasses[branch_script][lump_name]):
                    LumpClass = lumpclasses[branch_script][lump_name][lump_version]
                    lump_class_module = LumpClass.__module__[len('bsp_tool.branches.'):]
                    lump_class = f"[{lump_class_module}.{LumpClass.__name__}]({url_of_LumpClass(LumpClass)})"
                    percent = coverage[branch_script][lump_name][lump_version]
                    tails.append(f"`{lump_name}` | {lump_version} | {lump_class} | {percent}% |\n")
            lines.extend([" ".join([head, tail]) for tail in tails])
    # print(*lines, sep="\n")
    return lines


def supported_md(group: ScriptGroup) -> List[str]:
    lines = [f"# Supported {group.name} Games\n",
             f"Developers: {group.developers}\n\n"]
    versioned_lumps: bool = any([k in (ArkaneBsp, ValveBsp, RespawnBsp) for k in group.branch_scripts.keys()])
    # COVERAGE CALCULATIONS
    coverage = dict()
    # ^ {branch_script: {"LUMP_NAME": {lump_version: percent_covered}}}
    # TODO: some .bsp may contain lump versions that haven't been supported yet
    # -- would be worth mapping such lumps with tests/maplist.installed_games
    # -- since this still constitutes unmapped lumps (a non-present version 0 would not, however)
    # -- only known .bsp files matter, no need for hypotheticals (don't really care about leaked betas either)
    for branch_script in chain(*group.branch_scripts.values()):
        coverage[branch_script] = defaultdict(dict)
        for lump_name, LumpClass_dict in LumpClasses_of(branch_script).items():
            if not versioned_lumps:
                LumpClass_dict = {None: LumpClass_dict}
            for lump_version, LumpClass in LumpClass_dict.items():
                if lump_name in branch_script.LUMP_CLASSES:
                    # TODO: calculate unknowns as % of bytes mapped
                    if issubclass(LumpClass, branches.base.Struct):
                        attrs = len(LumpClass.__slots__)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass.__slots__])
                        # TODO: nested attrs
                    elif issubclass(LumpClass, branches.base.MappedArray):
                        attrs = len(LumpClass._mapping)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass._mapping])
                    elif issubclass(LumpClass, list):  # quake.Edge / vindictus.Edge etc.
                        attrs, unknowns = 1, 0
                    percent = int((100 / attrs) * (attrs - unknowns)) if unknowns != attrs else 0
                if lump_name in branch_script.SPECIAL_LUMP_CLASSES:
                    percent = SpecialLumpClass_confidence[lump_name]
                else:  # BASIC_LUMP_CLASSES
                    percent = 100
                coverage[branch_script][lump_name][lump_version] = percent
        # TODO: GAME_LUMP_CLASSES
    # END COVERAGE CALCULATIONS
    lines.extend(games_table(group, coverage))
    lines.append("\n\n")
    # TODO: insert notes from branch_scripts:
    # -- changes from X -> Y
    # -- rough lump relationships
    if group.insert is not None:
        with open(os.path.join(inserts_path, group.insert)) as insert:
            lines.extend(insert.readlines())
            lines.append("\n\n")
    lines.append("## Supported Lumps\n")
    if versioned_lumps:
        lines.extend(versioned_lump_table(group, coverage, group.name in ("Titanfall Engine", "Apex Legends")))
    else:
        lines.extend(unversioned_lump_table(group, coverage))
    lines.append("\n\n")
    # TODO: post-processing:
    # -- blank repeated LUMP_NAMES & lump_indices for trailing lines
    # -- ^ let a blank indicate a ditto
    return lines


if __name__ == "__main__":
    # TODO: run this script via GitHub actions to keep docs up to date w/ latest commit
    # -- would probably require moving docs to a separate branch
    # -- could also copy the changelog with this approach
    for group in groups:
        print(f"Writing {group.filename}...")
        with open(os.path.join(out_path, group.filename), "w") as outfile:
            outfile.write("".join(supported_md(group)))
