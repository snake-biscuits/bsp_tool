import os

from ..branches.respawn import titanfall as r1
from ..branches.respawn import titanfall2 as r2
from ..branches.vector import vec3


def r1_to_r2(r1_bsp, outdir="./"):
    # TODO: r1_bsp.external
    # NOTE: just mutating the r1 bsp; too lazy to build & populate an r2 bsp
    # NOTE: works best on r1o maps, no .bsp_lump edits yet
    r1_bsp.bsp_version = r2.BSP_VERSION
    r1_bsp.branch = r2  # need r2 script to look up LumpClasses for .lump_as_bytes
    r1_bsp.headers = {r2.LUMP(getattr(r1.LUMP, L).value).name: h for L, h in r1_bsp.headers.items()}
    # ^ lump names need to match branch script for .save_as to collect lumps
    # LIGHTMAP_DATA_*
    new_RTL = b""
    rtl_start, rtl_end = 0, 0
    for header in r1_bsp.LIGHTMAP_HEADERS:
        rtl_end = rtl_start + (header.width * header.height * 4)
        new_RTL += r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end] * 2
        new_RTL += b"\xFF" * header.width * header.height  # mystery 9th byte-per-texel
        rtl_start = rtl_end
    r1_bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS = new_RTL
    # LightProbeRefs
    new_lprs = [r2.LightProbeRef(**{a: getattr(r, a) for a in r.__slots__}) for r in r1_bsp.LIGHTPROBE_REFERENCES]
    r1_bsp.LIGHTPROBE_REFERENCES = new_lprs
    # Meshes
    for i, mesh in enumerate(r1_bsp.MESHES):
        mesh.first_vertex = 0
        mesh.num_vertices = 0
        mesh.unknown = [0] * 6
        r1_bsp.MESHES[i] = mesh
    # ShadowEnvironment
    light_env = [e for e in r1_bsp.ENTITIES if e["classname"] == "light_environment"][0]
    pitch, yaw, roll = map(float, light_env.get("angles", "0 0 0").split())
    pitch = float(light_env.get("pitch", pitch))
    sun_vector = vec3(1, 0, 0).rotate(y=pitch)
    sun_vector = sun_vector.rotate(z=yaw)
    shadow_env = r2.ShadowEnvironment(unknown_1=(0, 0), first_shadow_mesh=0,
                                      unknown_2=(1, 0), num_shadow_meshes=len(r1_bsp.SHADOW_MESHES),
                                      angle_vector=sun_vector)
    r1_bsp.SHADOW_ENVIRONMENTS = [shadow_env]
    light_env["lightEnvironmentIndex"] = "*0"
    # Entities
    trigger_ents = [e for e in r1_bsp.ENTITIES if e["classname"].startswith("trigger_")]
    # TODO: update trigger flags instead
    for e in trigger_ents:
        r1_bsp.ENTITIES.remove(e)
    del trigger_ents
    # game lump
    r1_bsp.GAME_LUMP.headers["sprp"].version = 13
    old_sprp = r1_bsp.GAME_LUMP.sprp
    raw_sprp_head = old_sprp.as_bytes()[:len(old_sprp.model_names) * 128 + 12]
    new_sprp = r2.GameLump_SPRP(raw_sprp_head + b"\0" * 8, r2.StaticPropv13)

    def upgrade_prop(v12_prop):
        d = {a: getattr(v12_prop, a) for a in r2.StaticPropv13.__slots__ if a not in ("unknown", "lighting_origin")}
        return r2.StaticPropv13(**d)

    # new_sprp.props = [upgrade_prop(p) for p in old_sprp.props]
    r1_bsp.GAME_LUMP.sprp = new_sprp
    # save changes
    # NOTE: will copy any .bsp_lump & .ent files attached to r1_bsp
    r1_bsp.save_as(os.path.join(outdir, r1_bsp.filename))
