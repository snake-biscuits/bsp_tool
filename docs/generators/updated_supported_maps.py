from bsp_tool.branches import respawn


def gen_rbsp_tables():  # hardcoded to RespawnBsp
    bsp_format_name = "RespawnBsp (Respawn Entertainment)"
    print(f"# {bsp_format_name} Supported Games (as of v0.3.0)")
    # NOTE: increment with release
    
    # table of games
    print("| Bsp version | Game | Branch script | Supported lumps | Unused lumps |")
    game_scripts = {"Titanfall": respawn.titanfall,
                    "Titanfall 2": respawn.titanfall2,
                    "Apex Legends": respawn.apex_legends}
    # ^ {"game": script}
    print(f"| -: | - | - | -: |")
    for game in sorted(game_scripts, key=lambda g: game_scripts[g].BSP_VERSION):
        script = game_scripts[game]
        version = game_script.BSP_VERSION
        script_name = script.__name__[len("bsp_tool.branches"):]
        supported = len({*script.BASIC_LUMP_CLASSES,
                         *script.LUMP_CLASSES,
                         *script.SPECIAL_LUMP_CLASSES})
        unused = sum([L.name.startswith("UNUSED_") for L in script.LUMPS])
        total = len(game_script.LUMPS) - unused
        print(f"| {version} | {game} | `{script_name}` | {supported} / {total} | {unused} |")

    # notes
    print("\n> No differences in Apex' formats have been found, yet.\n"
          "For now, we are assuming the base apex script covers all season\n",
          "bsp_tool.load_bsp() will load Apex maps correctly, regardless of season\n")
    print("\n> All Apex Legends GameLump.sprp lump versions are the same as the BSP version\n")

    # table of lumps
    print("| Lump index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |")
    for i in range(max([len(v.LUMP) for v in game_scripts.values()])):
        ...
    # TODO: print each lump entry, in order of BSP_VERSION
    # TODO: if a script uses a different format, add it to the list
    # TODO: print alternate lump names
    # TODO: don't print lump name or index if it doesn't change
    """| 4 |  20 | `VISIBILITY` | 0 | :x:                     |   0% |
       | 5 |  20 | `NODES`      | 0 | `valve.orange_box.Node` | 100% |
       |   |  20 |              | 0 | `nexon.vindictus.Node`  | 100% |"""
    # NOTE: % mapped is based on number of unknowns in format