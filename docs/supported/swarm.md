# Alien Swarm
## Developers: Valve Software

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L69) | 21 | Alien Swarm | [`valve.alien_swarm`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/alien_swarm.py) | 29 / 58 | 6 | 48.10% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L69) | 21 | Alien Swarm: Reactive Drop | [`valve.alien_swarm`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/alien_swarm.py) | 29 / 58 | 6 | 48.10% |


### References
 * [Valve Developer Wiki](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format)
 * [Source SDK 2013](https://github.com/ValveSoftware/source-sdk-2013)
   - [bspfile.h](https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h)
   - [bspflags.h](https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspflags.h)


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 21 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
| 1 | 21 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L208) | 100% |
| 2 | 21 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L479) | 100% |
| 3 | 21 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 4 | 21 | `VISIBILITY` | 0 |  | 0% |
| 5 | 21 | `NODES` | 0 | [`valve.source.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L456) | 100% |
| 6 | 21 | `TEXTURE_INFO` | 0 | [`valve.source.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L490) | 100% |
| 7 | 21 | `FACES` | 1 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L407) | 100% |
| 8 | 21 | `LIGHTING` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L83) | 100% |
| 9 | 21 | `OCCLUSION` | 0 |  | 0% |
| 10 | 21 | `LEAVES` | 1 | [`valve.orange_box.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L114) | 100% |
| 11 | 21 | `FACE_IDS` | 0 |  | 0% |
| 12 | 21 | `EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L113) | 100% |
| 13 | 21 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L28) | 100% |
| 14 | 21 | `MODELS` | 0 | [`valve.source.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L443) | 100% |
| 15 | 21 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 21 | `LEAF_FACES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 17 | 21 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 18 | 21 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L342) | 100% |
| 19 | 21 | `BRUSH_SIDES` | 0 | [`valve.source.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L351) | 100% |
| 20 | 21 | `AREAS` | 0 | [`valve.source.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L324) | 100% |
| 21 | 21 | `AREA_PORTALS` | 0 | [`valve.source.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L331) | 100% |
| 22 | 21 | `UNUSED_22` | 0 |  | 0% |
| 23 | 21 | `UNUSED_23` | 0 |  | 0% |
| 24 | 21 | `UNUSED_24` | 0 |  | 0% |
| 25 | 21 | `UNUSED_25` | 0 |  | 0% |
| 26 | 21 | `DISPLACEMENT_INFO` | 0 | [`valve.source.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L369) | 100% |
| 27 | 21 | `ORIGINAL_FACES` | 0 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L407) | 100% |
| 28 | 21 | `PHYSICS_DISPLACEMENT` | 0 |  | 0% |
| 29 | 21 | `PHYSICS_COLLIDE` | 0 | [`physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L17) | 90% |
| 30 | 21 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 31 | 21 | `VERTEX_NORMAL_INDICES` | 0 |  | 0% |
| 32 | 21 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 21 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L397) | 100% |
| 34 | 21 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 21 | `GAME_LUMP` | 0 |  | 0% |
| 36 | 21 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L435) | 0% |
| 37 | 21 | `PRIMITIVES` | 0 |  | 0% |
| 38 | 21 | `PRIMITIVE_VERTICES` | 0 |  | 0% |
| 39 | 21 | `PRIMITIVE_INDICES` | 0 |  | 0% |
| 40 | 21 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L127) | 100% |
| 41 | 21 | `CLIP_PORTAL_VERTICES` | 0 |  | 0% |
| 42 | 21 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L360) | 100% |
| 43 | 21 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L136) | 100% |
| 44 | 21 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 45 | 21 | `OVERLAYS` | 0 |  | 0% |
| 46 | 21 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 21 | `FACE_MACRO_TEXTURE_INFO` | 0 |  | 0% |
| 48 | 21 | `DISPLACEMENT_TRIS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 49 | 21 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 21 | `WATER_OVERLAYS` | 0 |  | 0% |
| 51 | 21 | `LEAF_AMBIENT_INDEX_HDR` | 0 |  | 0% |
| 52 | 21 | `LEAF_AMBIENT_INDEX` | 0 |  | 0% |
| 53 | 21 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L83) | 100% |
| 54 | 21 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 21 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 21 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 21 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 21 | `FACES_HDR` | 0 |  | 0% |
| 59 | 21 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 21 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L473) | 100% |
| 61 | 21 | `UNUSED_61` | 0 |  | 0% |
| 62 | 21 | `UNUSED_62` | 0 |  | 0% |
| 63 | 21 | `DISPLACEMENT_MULTIBLEND` | 0 |  | 0% |

