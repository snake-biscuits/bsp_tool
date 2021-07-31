import sys

sys.path.insert(0, "../../")  # HACK to load bsp_tool from docs/generators/
from bsp_tool.branches import base  # noqa: E402
from bsp_tool.branches import respawn  # noqa: E402


# TODO: copy generated files to docs & branches

def gen_rbsp():
    bsp_format_name = "RespawnBsp (Respawn Entertainment)"
    print(f"# {bsp_format_name} Supported Games (v0.3.0)")
    # NOTE: increment with bsp_tool release

    # table of games
    print("| Bsp version | Game | Branch script | Supported lumps | Unused lumps |")
    game_scripts = {"Titanfall": respawn.titanfall,
                    "Titanfall 2": respawn.titanfall2,
                    "Apex Legends": respawn.apex_legends}
    # ^ {"game": script}
    LumpClasses = {n: {**s.BASIC_LUMP_CLASSES, **s.LUMP_CLASSES, **s.SPECIAL_LUMP_CLASSES}
                   for n, s in game_scripts.items()}
    # ^ {"game": {"LUMP_NAME": LumpClass}}
    print("| -: | - | - | -: |")
    for game in sorted(game_scripts, key=lambda g: game_scripts[g].BSP_VERSION):
        script = game_scripts[game]
        version = script.BSP_VERSION
        script_name = script.__name__[len("bsp_tool.branches."):]
        supported = len(LumpClasses[game])
        unused = sum([L.name.startswith("UNUSED_") for L in script.LUMP])
        total = len(script.LUMP) - unused
        print(f"| {version} | {game} | `{script_name}` | {supported} / {total} | {unused} |")

    # notes
    print("\n> No differences in Apex' formats have been found, yet."
          "\n> For now, we are assuming the base apex script covers all seasons\n",
          "\n> bsp_tool.load_bsp() will load Apex maps correctly, regardless of season\n",
          "\n> All Apex Legends GameLump.sprp lump versions are the same as the BSP version\n")

    # table of lumps
    print("| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |")
    print("| -: | -: | -: | - | -: | - | -:|")
    # TODO: break out this iterator into it's own set of functions
    for i in range(max([len(v.LUMP) for v in game_scripts.values()])):
        lumps = [(n, g.BSP_VERSION, g.LUMP(i)) for n, g in game_scripts.items()]
        for game, bsp_version, lump in lumps:
            lump_name = f"`{lump.name}`"
            lump_classes = LumpClasses[game].get(lump.name, dict())
            # ^ {lump_version, LumpClass}
            for lump_version, LumpClass in lump_classes.items():
                lump_class = f"`{LumpClass.__module__[len('bsp_tool.branches.'):]}.{LumpClass.__name__}`"
                percent = 100
                if lump.name in game_scripts[game].LUMP_CLASSES:
                    if issubclass(LumpClass, base.Struct):
                        attrs = len(LumpClass.__slots__)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass.__slots__])
                        # TODO: calculate as a count of unknown bytes
                    elif issubclass(LumpClass, base.MappedArray):
                        attrs = len(LumpClass._mapping)
                        unknowns = sum([a.startswith("unknown") for a in LumpClass._mapping])
                    # else:
                    #     print("*** ??? ***", lump_class, "*** ??? ***")
                    #     attrs, unknowns = 1, 0
                    percent = int((100 / attrs) * (attrs - unknowns)) if unknowns != attrs else 0
                # SPECIAL_LUMP_CLASSES are assumed to be 100%, but can be 10% (rough guess) to 90% (confident guess)
                # TODO: Lightmap data lumps are *partially* mapped by extensions.lightmaps
                print(f"| {i} | {i:04X} | {bsp_version} | {lump_name} | {lump_version} | {lump_class} | {percent}% |")
            if len(lump_classes) == 0:
                print(f"| {i} | {i:04X} | {bsp_version} | {lump_name} | 0 | :x: | 0% |")
        # TODO: skip unused lines / duplicate LumpClasses
        # TODO: blank repeated LUMP_NAMES & lump_indices for trailing lines
        # TODO: include lump relationship maps (use timeline .html nodes?)
        # TODO: include summaries of changes between sequels
        # -- (LUMP_NAME_A -> LUMP_NAME_B) [DEPRECATED / NEW if either is UNUSED]


if __name__ == "__main__":
    pass
    # build each SUPPORTED.md
    # copy to docs/{dev}/ & bsp_tool/branches/{dev}/
    gen_rbsp()
