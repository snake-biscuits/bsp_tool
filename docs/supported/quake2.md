# Quake II Engine
## Developers: Id Software, Ion Storm

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 1 | SiN | [`ritual.sin`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ritual/sin.py) | 12 / 19 | 0 | 52.11% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 1 | SiN Gold | [`ritual.sin`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ritual/sin.py) | 12 / 19 | 0 | 52.11% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 38 | Anachronox | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 14 / 19 | 0 | 62.63% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 38 | Quake II | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 14 / 19 | 0 | 62.63% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 38 | Heretic II | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 14 / 19 | 0 | 62.63% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 38 | D-Day Normandy | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 14 / 19 | 0 | 62.63% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 41 | Daikatana | [`ion_storm.daikatana`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ion_storm/daikatana.py) | 13 / 19 | 0 | 57.37% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L84) | 46 | Soldier of Fortune | [`raven.soldier_of_fortune`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/soldier_of_fortune.py) | 12 / 19 | 0 | 52.11% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 1 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L46) | 100% |
| 1 | 1 | `PLANES` | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L226) | 100% |
| 2 | 1 | `VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 3 | 1 | `VISIBILITY` | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L212) | 90% |
| 4 | 1 | `NODES` | [`id_software.quake2.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L186) | 0% |
| 5 | 1 | `TEXTURE_INFO` |  | 0% |
| 5 | 38 | `TEXTURE_INFO` | [`id_software.quake2.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L199) | 100% |
| 6 | 1 | `FACES` |  | 0% |
| 6 | 38 | `FACES` | [`id_software.quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L155) | 100% |
| 6 | 46 | `FACES` |  | 0% |
| 7 | 1 | `LIGHTMAPS` |  | 0% |
| 8 | 1 | `LEAVES` | [`id_software.quake2.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L160) | 100% |
| 8 | 41 | `LEAVES` |  | 0% |
| 9 | 1 | `LEAF_FACES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L25) | 100% |
| 10 | 1 | `LEAF_BRUSHES` |  | 0% |
| 11 | 1 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L144) | 100% |
| 12 | 1 | `SURFEDGES` | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L21) | 100% |
| 13 | 1 | `MODELS` | [`id_software.quake2.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L175) | 100% |
| 14 | 1 | `BRUSHES` | [`id_software.quake2.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L146) | 100% |
| 15 | 1 | `BRUSH_SIDES` | [`id_software.quake2.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L154) | 0% |
| 16 | 1 | `POP` |  | 0% |
| 17 | 1 | `AREAS` |  | 0% |
| 18 | 1 | `AREA_PORTALS` |  | 0% |


