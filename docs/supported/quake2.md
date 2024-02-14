# Quake II Engine
## Developers: Id Software, Ion Storm

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 1 | SiN | [`ritual.sin`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ritual/sin.py) | 14 / 19 | 0 | 73.16% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 1 | SiN Gold | [`ritual.sin`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ritual/sin.py) | 14 / 19 | 0 | 73.16% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 38 | Anachronox | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 17 / 19 | 0 | 88.95% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 38 | Quake II | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 17 / 19 | 0 | 88.95% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 38 | Heretic II | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 17 / 19 | 0 | 88.95% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 38 | D-Day Normandy | [`id_software.quake2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py) | 17 / 19 | 0 | 88.95% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 41 | Daikatana | [`ion_storm.daikatana`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/ion_storm/daikatana.py) | 15 / 19 | 0 | 78.42% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 46 | Soldier of Fortune | [`raven.soldier_of_fortune`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/soldier_of_fortune.py) | 14 / 22 | 0 | 63.18% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 46 | Soldier of Fortune (Dreamcast) | [`raven.soldier_of_fortune`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/raven/soldier_of_fortune.py) | 14 / 22 | 0 | 63.18% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 1 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 1 | 1 | `PLANES` | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L237) | 100% |
| 2 | 1 | `VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 3 | 1 | `VISIBILITY` | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L248) | 90% |
| 4 | 1 | `NODES` | [`id_software.quake2.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L214) | 100% |
| 5 | 1 | `TEXTURE_INFO` |  | 0% |
| 5 | 38 | `TEXTURE_INFO` | [`id_software.quake2.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L231) | 100% |
| 6 | 1 | `FACES` |  | 0% |
| 6 | 38 | `FACES` | [`id_software.quake.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L163) | 100% |
| 6 | 46 | `FACES` |  | 0% |
| 7 | 1 | `LIGHTING` |  | 0% |
| 7 | 38 | `LIGHTING` | [`extensions.lightmaps.as_page`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/quake.py#L8) | 100% |
| 7 | 41 | `LIGHTING` |  | 0% |
| 8 | 1 | `LEAVES` | [`id_software.quake2.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L186) | 100% |
| 8 | 41 | `LEAVES` |  | 0% |
| 9 | 1 | `LEAF_FACES` | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L15) | 100% |
| 10 | 1 | `LEAF_BRUSHES` |  | 0% |
| 11 | 1 | `EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L150) | 100% |
| 12 | 1 | `SURFEDGES` | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L11) | 100% |
| 13 | 1 | `MODELS` | [`id_software.quake2.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L202) | 100% |
| 14 | 1 | `BRUSHES` | [`id_software.quake2.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L170) | 100% |
| 15 | 1 | `BRUSH_SIDES` | [`id_software.quake2.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L179) | 100% |
| 16 | 1 | `POP` |  | 0% |
| 17 | 1 | `AREAS` | [`id_software.quake2.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L156) | 100% |
| 18 | 1 | `AREA_PORTALS` | [`id_software.quake2.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L163) | 100% |
| 19 | 46 | `UNKNOWN_19` |  | 0% |
| 20 | 46 | `UNKNOWN_20` |  | 0% |
| 21 | 46 | `UNKNOWN_21` |  | 0% |


