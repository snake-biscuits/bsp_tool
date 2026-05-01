def test_flags0(bsp):
    cell_portals = {  # portals w/ flags=0
        i: bsp.PORTALS[cell.first_portal:][:cell.num_portals]
        for i, cell in enumerate(bsp.CELLS)
        if cell.flags.value == 0}
    portal_types = {
        i: {p.type.value for p in ps}
        for i, ps in cell_portals.items()}
    # {}, {0}, {2} & {0, 2} are all valid
    return {
        i
        for i, ts in portal_types.items()
        if 1 in ts}
    # TODO: confirm cells w/ no portals aren't indexed by any portals


def test_flags1(bsp):
    cell_portals = {  # portals w/ flags=1
        i: bsp.PORTALS[cell.first_portal:][:cell.num_portals]
        for i, cell in enumerate(bsp.CELLS)
        if cell.flags.value == 1}
    portal_types = {
        i: {p.type.value for p in ps}
        for i, ps in cell_portals.items()}
    # always a mix of CELL & SKYBOX portals
    return {
        i
        for i, ts in portal_types.items()
        if ts != {0, 1}}


def test_flags3(bsp):
    # cells w/ .flags=3 never have portals
    return {
        i
        for i, cell in enumerate(bsp.CELLS)
        if cell.flags.value == 3 and cell.num_portals != 0}
    # TODO: confirm no portals index cells w/ .flags=3


def test_flags5(bsp):
    cell_portals = {  # portals w/ flags=1
        i: bsp.PORTALS[cell.first_portal:][:cell.num_portals]
        for i, cell in enumerate(bsp.CELLS)
        if cell.flags.value == 5}
    portal_types = {
        i: {p.type.value for p in ps}
        for i, ps in cell_portals.items()}
    # only SKYBOX portals
    return {
        i
        for i, ts in portal_types.items()
        if ts != {1}}


if __name__ == "__main__":
    import os
    import fnmatch

    import bsp_tool

    r1_md = "/home/bikkie/drives/ssd1/Mod/Titanfall/maps/"
    r2_md = "/home/bikkie/drives/ssd1/Mod/Titanfall2/maps/"

    for game, md in (("r1", r1_md), ("r2", r2_md)):
        for fn in sorted(fnmatch.filter(os.listdir(md), "*.bsp")):
            mapname = f"{game}/{fn[:-4]}"
            bsp = bsp_tool.load_bsp(os.path.join(md, fn))
            if not hasattr(bsp, "PORTALS"):
                print(f"{mapname:<24} SKIP")
                continue
            results = "".join([
                "." if len(test_flags0(bsp)) == 0 else "F",
                "." if len(test_flags1(bsp)) == 0 else "F",
                "." if len(test_flags3(bsp)) == 0 else "F",
                "." if len(test_flags5(bsp)) == 0 else "F"])
            print(f"{mapname:<24} {results}")
