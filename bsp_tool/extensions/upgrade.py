from ..branches.respawn import titanfall2 as r2


def r1_to_r2(r1_bsp):
    # NOTE: just mutating the r1 bsp
    # -- too lazy to build & populate an r2 bsp
    r1_bsp.bsp_version = r2.BSP_VERSION
    # lightmaps
    new_RTL = b""
    rtl_start, rtl_end = 0, 0
    for header in r1_bsp.LIGHTMAP_HEADERS:
        rtl_end = rtl_start + (header.width * header.height * 4)
        new_RTL += r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end] * 2
        rtl_start = rtl_end
    r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS = new_RTL
    # game lump
    r1_bsp.GAME_LUMP.headers["sprp"].version = 13
    old_sprp = r1_bsp.GAME_LUMP.sprp
    raw_sprp_head = old_sprp.as_bytes()[:len(old_sprp.model_names) * 128 + 12]
    new_sprp = r2.GameLump_SPRP(raw_sprp_head + b"\0" * 8, r2.StaticPropv13)

    def upgrade_prop(v12_prop):
        d = {a: getattr(v12_prop, a) for a in r2.StaticPropv13.__slots__ if a not in ("unknown", "lighting_origin")}
        return r2.StaticPropv13(**d)

    new_sprp.props = [upgrade_prop(p) for p in old_sprp.props]

    r1_bsp.GAME_LUMP.sprp = new_sprp
    # save changes
    # NOTE: will copy any .bsp_lump & .ent files attached to r1_bsp
    r1_bsp.save_as(f"./{r1_bsp.filename}")
