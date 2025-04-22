import os

from ...branches.respawn import titanfall as r1
from ...branches.respawn import titanfall2 as r2
from ...utils.vector import vec3


def titanfall_to_titanfall2(r1_bsp, outdir: str = "./"):
    # NOTE: just mutating the r1 bsp, too lazy to build & populate an r2 bsp
    # NOTE: ignoring .bsp_lump, maps load fine in Northstar without them
    # switch metadata to r2
    print("Metadata")
    r1_bsp.bsp_version = r2.BSP_VERSION
    r1_bsp.branch = r2
    r1_bsp.headers = {r2.LUMP(getattr(r1.LUMP, L).value).name: h for L, h in r1_bsp.headers.items()}
    # LIGHTMAP_DATA_*
    print("Lightmaps")
    r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS = r1_rtl_to_r2(r1_bsp)
    # LightProbeRefs
    print("LightProbeRefs")
    new_lprs = [r2.LightProbeRef(**{a: getattr(r, a) for a in r.__slots__}) for r in r1_bsp.LIGHTPROBE_REFERENCES]
    r1_bsp.LIGHTPROBE_REFERENCES = new_lprs
    # ShadowEnvironment
    print("ShadowEnvironments")
    light_env = [e for e in r1_bsp.ENTITIES if e["classname"] == "light_environment"][0]
    pitch, yaw, roll = map(float, light_env.get("angles", "0 0 0").split())
    pitch = float(light_env.get("pitch", pitch))
    sun_vector = vec3(1, 0, 0).rotate(y=pitch)
    sun_vector = sun_vector.rotate(z=yaw)
    shadow_env = r2.ShadowEnvironment(
        unknown_1=(0, 0), first_shadow_mesh=0,
        unknown_2=(1, 0), num_shadow_meshes=len(r1_bsp.SHADOW_MESHES),
        sun_normal=sun_vector)
    r1_bsp.SHADOW_ENVIRONMENTS = [shadow_env]
    light_env["lightEnvironmentIndex"] = "*0"
    # Entities
    print("Entities")
    # TODO: remove Models of deleted entities
    trigger_ents = [e for e in r1_bsp.ENTITIES if e["classname"].startswith("trigger_")]
    # glass causes crashes
    breakable_ents = [e for e in r1_bsp.ENTITIES if e["classname"] in ("func_breakable", "func_breakable_surf")]
    for e in (*trigger_ents, *breakable_ents):
        # TODO: update triggers instead of deleting them
        # TODO: replace models w/ brush definition in entity ("brush_X_plane_y" "A B C D" etc.)
        r1_bsp.ENTITIES.remove(e)
    del trigger_ents, breakable_ents
    # gut .ain ents to until we can generate .ain without crashing
    ain_entclasses = ("info_hint", "info_node", "info_node_safe_hint",
                      *["info_node_cover_{x}" for x in ("crouch", "left", "right", "stand")])
    ain_ents = [e for e in r1_bsp.ENTITIES_script if e["classname"] in ain_entclasses]
    for e in ain_ents:
        r1_bsp.ENTITIES_script.remove(e)
    del ain_ents
    # GameLump
    print("GameLump (sprp)")
    r1_bsp.GAME_LUMP.headers["sprp"].version = 13
    old_sprp = r1_bsp.GAME_LUMP.sprp
    new_sprp = r2.GameLump_SPRPv13()
    new_sprp.model_names = old_sprp.model_names
    new_sprp.unknown_1 = old_sprp.unknown_1
    new_sprp.unknown_2 = old_sprp.unknown_2

    def upgrade_prop(v12_prop):
        """copy all attrs except unknown & lighting_origin"""
        d = {a: getattr(v12_prop, a) for a in r2.StaticPropv13.__slots__ if a not in ("unknown", "lighting_origin")}
        # TODO: typecasts
        return r2.StaticPropv13(**d)

    new_sprp.props = list(map(upgrade_prop, old_sprp.props))
    r1_bsp.GAME_LUMP.sprp = new_sprp
    # save changes
    print("Saving changes...")
    # NOTE: will copy any .ent files attached to r1_bsp; .bsp_lump is optional
    r1_bsp.save_as(os.path.join(outdir, r1_bsp.filename), no_bsp_lump=True)


def r1_rtl_to_r2(r1_bsp) -> bytes:
    out = list()
    rtl_start, rtl_end = 0, 0
    for header in r1_bsp.LIGHTMAP_HEADERS:
        rtl_end = rtl_start + (header.width * header.height * 4)
        r1_rtl = r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
        rtl_start = rtl_end
        r2_rtl_a, r2_rtl_b = list(), list()
        for i in range(header.width * header.height):
            texel = r1_rtl[i * 4:(i + 1) * 4]
            rgb = texel[:3]
            alpha = texel[3]
            r2_rtl_a.append(bytes([255, 255, 255, alpha]))
            r2_rtl_b.append(bytes([255 - x for x in (*rgb, alpha)]))
        out.append(b"".join(r2_rtl_a))
        out.append(b"".join(r2_rtl_b))
        r2_rtl_c = b"\x00" * header.width * header.height
        out.append(r2_rtl_c)
    return b"".join(out)
