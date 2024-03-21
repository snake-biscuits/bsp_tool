# Quake Engine
## Developers: Id Software

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`Quake64Bsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L85) | 0 | Quake 64 | [`id_software.quake64`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake64.py) | 13 / 15 | 0 | 86.00% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L54) | 0 | Alkaline | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 86.00% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L54) | 0 | Alkaline DevKit | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 86.00% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L54) | 0 | Alkaline v1.1 | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 86.00% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L54) | 0 | Dimension of the Past | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 86.00% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L54) | 0 | DEPRECATED | [`id_software.remake_quake_old`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py) | 13 / 15 | 0 | 86.00% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L8) | 29 | DarkPlaces | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 15 / 15 | 0 | 97.67% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L8) | 29 | Quake | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 15 / 15 | 0 | 97.67% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L8) | 29 | Team Fortress Quake | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 15 / 15 | 0 | 97.67% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L8) | 29 | Hexen II | [`raven.hexen2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/hexen2.py) | 13 / 15 | 0 | 86.00% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 0 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 1 | 0 | `PLANES` | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L237) | 100% |
| 2 | 0 | `MIP_TEXTURES` | [`id_software.quake.MipTextureLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L295) | 90% |
| 2 | 0 | `MIP_TEXTURES` | [`id_software.quake64.MipTextureLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake64.py#L57) | 90% |
| 2 | 29 | `MIP_TEXTURES` | [`id_software.quake.MipTextureLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L295) | 90% |
| 3 | 0 | `VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 4 | 0 | `VISIBILITY` |  | 0% |
| 4 | 29 | `VISIBILITY` | [`id_software.quake.parse_vis`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L409) | 75% |
| 4 | 29 | `VISIBILITY` |  | 0% |
| 5 | 0 | `NODES` | [`id_software.remake_quake_old.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L58) | 100% |
| 5 | 0 | `NODES` | [`id_software.quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L220) | 100% |
| 5 | 0 | `NODES` | [`id_software.remake_quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L50) | 100% |
| 5 | 29 | `NODES` | [`id_software.quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L220) | 100% |
| 6 | 0 | `TEXTURE_INFO` | [`id_software.quake.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L247) | 100% |
| 7 | 0 | `FACES` | [`id_software.remake_quake_old.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L47) | 100% |
| 7 | 0 | `FACES` | [`id_software.quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L163) | 100% |
| 8 | 0 | `LIGHTING` |  | 0% |
| 8 | 29 | `LIGHTING` | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/quake.py#L6) | 100% |
| 9 | 0 | `CLIP_NODES` | [`id_software.remake_quake_old.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L39) | 100% |
| 9 | 0 | `CLIP_NODES` | [`id_software.quake.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L138) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L182) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.remake_quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L43) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.remake_quake_old.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L51) | 100% |
| 10 | 29 | `LEAVES` | [`id_software.quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L182) | 100% |
| 11 | 0 | `LEAF_FACES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L15) | 100% |
| 12 | 0 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L150) | 100% |
| 12 | 0 | `EDGES` | [`id_software.remake_quake_old.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L43) | 100% |
| 12 | 29 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L150) | 100% |
| 13 | 0 | `SURFEDGES` | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L11) | 100% |
| 14 | 0 | `MODELS` | [`id_software.quake.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L200) | 100% |
| 14 | 29 | `MODELS` | [`raven.hexen2.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/hexen2.py#L68) | 100% |
| 14 | 29 | `MODELS` | [`id_software.quake.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L200) | 100% |


