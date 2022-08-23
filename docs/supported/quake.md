# Quake Engine
## Developers: Id Software

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L51) | 0 | Alkaline | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 85.13% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L51) | 0 | Alkaline DevKit | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 85.13% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L51) | 0 | Alkaline v1.1 | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 85.13% |
| [`ReMakeQuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L51) | 0 | Dimension of the Past | [`id_software.remake_quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py) | 13 / 15 | 0 | 85.13% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L9) | 29 | DarkPlaces | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 13 / 15 | 0 | 85.13% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L9) | 29 | Quake | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 13 / 15 | 0 | 85.13% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L9) | 29 | Team Fortress Quake | [`id_software.quake`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py) | 13 / 15 | 0 | 85.13% |
| [`QuakeBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/id_software.py#L9) | 29 | Hexen II | [`raven.hexen2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/hexen2.py) | 13 / 15 | 0 | 86.00% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 0 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L43) | 100% |
| 1 | 0 | `PLANES` | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L228) | 100% |
| 2 | 0 | `MIP_TEXTURES` | [`id_software.quake.MipTextureLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L258) | 90% |
| 3 | 0 | `VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 4 | 0 | `VISIBILITY` |  | 0% |
| 5 | 0 | `NODES` | [`id_software.remake_quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L60) | 100% |
| 5 | 29 | `NODES` | [`id_software.quake.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L212) | 100% |
| 6 | 0 | `TEXTURE_INFO` | [`id_software.quake.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L237) | 100% |
| 7 | 0 | `FACES` | [`id_software.remake_quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L49) | 100% |
| 7 | 29 | `FACES` | [`id_software.quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L160) | 100% |
| 8 | 0 | `LIGHTMAPS` |  | 0% |
| 9 | 0 | `CLIP_NODES` | [`id_software.remake_quake.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L41) | 100% |
| 9 | 29 | `CLIP_NODES` | [`id_software.quake.ClipNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L138) | 100% |
| 10 | 0 | `LEAVES` | [`id_software.remake_quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L53) | 100% |
| 10 | 29 | `LEAVES` | [`id_software.quake.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L177) | 100% |
| 11 | 0 | `LEAF_FACES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L26) | 100% |
| 12 | 0 | `EDGES` | [`id_software.remake_quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake.py#L45) | 100% |
| 12 | 29 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L149) | 100% |
| 13 | 0 | `SURFEDGES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L26) | 100% |
| 14 | 0 | `MODELS` | [`id_software.quake.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L193) | 87% |
| 14 | 29 | `MODELS` | [`raven.hexen2.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/hexen2.py#L67) | 100% |


