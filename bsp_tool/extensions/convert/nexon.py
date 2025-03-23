import os

from ...valve import ValveBsp
from ...branches import nexon
from ...branches import valve


def vindictus_steam_to_69(bsp: ValveBsp, outdir: str = "./"):
    assert isinstance(bsp, ValveBsp)
    assert bsp.branch == nexon.vindictus

    if not hasattr(bsp, "GAME_LUMP") or "sprp" not in bsp.GAME_LUMP.headers:
        # no conversion needed, just copy the map
        bsp.save_as(os.path.join(outdir, bsp.filename))

    assert bsp.GAME_LUMP.headers["sprp"].version in (6, 7, 8)

    def downgrade(prop):
        """copy all attrs except unknown & dx_level"""
        data = dict()
        for attr in nexon.vindictus.StaticPropv7.__slots__:
            if attr != "dx_level" and not attr.startswith("unknown"):
                data[attr] = getattr(prop, attr)
        return valve.source.StaticPropv5(**data)

    old_sprp = bsp.GAME_LUMP.sprp
    # rebuild the GameLump
    bsp.GAME_LUMP.headers["sprp"].version = 6
    new_sprp = nexon.vindictus69.GameLump_SPRPv6()
    new_sprp.model_names = old_sprp.model_names
    new_sprp.leaves = old_sprp.leaves
    new_sprp.scales = old_sprp.scales
    new_sprp.props = list(map(downgrade, old_sprp.props))
    bsp.GAME_LUMP.sprp = new_sprp
    bsp.save_as(os.path.join(outdir, bsp.filename))
