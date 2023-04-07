# Quake Engine
## Developers: Id Software

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
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
| 0 | 0 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 1 | 0 | `PLANES` | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L228) | 100% |
| 2 | 0 | `MIP_TEXTURES` | [`id_software.quake.MipTextureLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 90% |
| 3 | 0 | `VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 4 | 0 | `VISIBILITY` |  | 0% |
| 4 | 29 | `VISIBILITY` | [`id_software.quake.parse_vis`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L433) | 75% |
| 4 | 29 | `VISIBILITY` |  | 0% |
| 5 | 0 | `NODES` | [`id_software.remake_quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L50) | 100% |
| 5 | 0 | `NODES` | [`id_software.remake_quake_old.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L58) | 100% |
| 5 | 29 | `NODES` | [`id_software.quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L212) | 100% |
| 6 | 0 | `TEXTURE_INFO` | [`id_software.quake.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L238) | 100% |
| 7 | 0 | `FACES` | [`id_software.remake_quake_old.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L47) | 100% |
| 7 | 29 | `FACES` | [`id_software.quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L156) | 100% |
| 8 | 0 | `LIGHTING` |  | 0% |
| 8 | 29 | `LIGHTING` | [`extensions.lightmaps.save_quakebsp_q1`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps.py#L73) | 100% |
| 8 | 29 | `LIGHTING` |  | 0% |
| 9 | 0 | `CLIP_NODES` | [`id_software.remake_quake_old.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L39) | 100% |
| 9 | 29 | `CLIP_NODES` | [`id_software.quake.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L133) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.remake_quake_old.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L51) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.remake_quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L43) | 100% |
| 10 | 29 | `LEAVES` | [`id_software.quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L174) | 100% |
| 11 | 0 | `LEAF_FACES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L17) | 100% |
| 12 | 0 | `EDGES` | [`id_software.remake_quake_old.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L43) | 100% |
| 12 | 29 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L145) | 100% |
| 13 | 0 | `SURFEDGES` | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L13) | 100% |
| 14 | 0 | `MODELS` | [`id_software.quake.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L192) | 100% |
| 14 | 29 | `MODELS` | [`raven.hexen2.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/hexen2.py#L67) | 100% |
| 14 | 29 | `MODELS` | [`id_software.quake.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L192) | 100% |


