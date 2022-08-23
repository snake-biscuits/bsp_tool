# Alien Swarm
## Developers: Valve Software

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L17) | 21 | Alien Swarm | [`valve.alien_swarm`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/alien_swarm.py) | 41 / 58 | 6 | 70.34% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L17) | 21 | Alien Swarm: Reactive Drop | [`valve.alien_swarm`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/alien_swarm.py) | 41 / 58 | 6 | 70.34% |


### References

 * [Valve Developer Wiki](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format)
 * [Source SDK 2013](https://github.com/ValveSoftware/source-sdk-2013)
   - [bspfile.h](https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h)
   - [bspflags.h](https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspflags.h)
   - [bsplib.cpp](https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bsplib.cpp)


### Vampire SDK

 * [Unofficial SDK](https://www.moddb.com/mods/vtmb-unofficial-patch/downloads/bloodlines-sdk)
 * [Planet Vampire Modding Community](https://forums.planetvampire.com/bloodlines-modding/bloodlines-sdk/)


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 21 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L43) | 100% |
| 1 | 21 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L228) | 100% |
| 2 | 21 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L573) | 100% |
| 3 | 21 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 4 | 21 | `VISIBILITY` | 0 | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L168) | 90% |
| 5 | 21 | `NODES` | 0 | [`valve.source.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L524) | 100% |
| 6 | 21 | `TEXTURE_INFO` | 0 | [`valve.source.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L584) | 100% |
| 7 | 21 | `FACES` | 1 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L417) | 100% |
| 8 | 21 | `LIGHTING` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 9 | 21 | `OCCLUSION` | 0 |  | 0% |
| 10 | 21 | `LEAVES` | 0 | [`valve.source.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L446) | 100% |
| 10 | 21 | `LEAVES` | 1 | [`valve.orange_box.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L108) | 100% |
| 11 | 21 | `FACE_IDS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 12 | 21 | `EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L149) | 100% |
| 13 | 21 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L22) | 100% |
| 14 | 21 | `MODELS` | 0 | [`valve.source.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L511) | 100% |
| 15 | 21 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 21 | `LEAF_FACES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 17 | 21 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 18 | 21 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L352) | 100% |
| 19 | 21 | `BRUSH_SIDES` | 0 | [`valve.source.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L361) | 100% |
| 20 | 21 | `AREAS` | 0 | [`valve.source.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L334) | 100% |
| 21 | 21 | `AREA_PORTALS` | 0 | [`valve.source.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L341) | 100% |
| 22 | 21 | `UNUSED_22` | 0 |  | 0% |
| 23 | 21 | `UNUSED_23` | 0 |  | 0% |
| 24 | 21 | `UNUSED_24` | 0 |  | 0% |
| 25 | 21 | `UNUSED_25` | 0 |  | 0% |
| 26 | 21 | `DISPLACEMENT_INFO` | 0 | [`valve.source.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L379) | 100% |
| 27 | 21 | `ORIGINAL_FACES` | 0 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L417) | 100% |
| 28 | 21 | `PHYSICS_DISPLACEMENT` | 0 |  | 0% |
| 29 | 21 | `PHYSICS_COLLIDE` | 0 | [`physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L18) | 90% |
| 30 | 21 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 31 | 21 | `VERTEX_NORMAL_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 32 | 21 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 21 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L407) | 100% |
| 34 | 21 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 21 | `GAME_LUMP` | - | [`lumps.GameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L334) | 90% |
| 35 | 21 | `GAME_LUMP.sprp` | - | [`valve.source.GameLump_SPRP`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L661) | 100% |
| 35 | 21 | `GAME_LUMP.sprp.props` | 4 | [`valve.source.StaticPropv4`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L712) | 100% |
| 35 | 21 | `GAME_LUMP.sprp.props` | 5 | [`valve.source.StaticPropv5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L731) | 100% |
| 35 | 21 | `GAME_LUMP.sprp.props` | 6 | [`valve.source.StaticPropv6`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L752) | 100% |
| 35 | 21 | `GAME_LUMP.sprp.props` | 7 | [`valve.orange_box.StaticPropv10`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L146) | 100% |
| 35 | 21 | `GAME_LUMP.sprp.props` | 10 | [`valve.orange_box.StaticPropv10`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L146) | 100% |
| 36 | 21 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L503) | 100% |
| 37 | 21 | `PRIMITIVES` | 0 | [`valve.source.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L563) | 100% |
| 38 | 21 | `PRIMITIVE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 39 | 21 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 40 | 21 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L121) | 100% |
| 41 | 21 | `CLIP_PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 42 | 21 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L370) | 100% |
| 43 | 21 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L132) | 100% |
| 44 | 21 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 45 | 21 | `OVERLAYS` | 0 |  | 0% |
| 46 | 21 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 21 | `FACE_MACRO_TEXTURE_INFO` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L26) | 100% |
| 48 | 21 | `DISPLACEMENT_TRIS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 49 | 21 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 21 | `WATER_OVERLAYS` | 0 | [`valve.source.WaterOverlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L597) | 100% |
| 51 | 21 | `LEAF_AMBIENT_INDEX_HDR` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L485) | 100% |
| 52 | 21 | `LEAF_AMBIENT_INDEX` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L485) | 100% |
| 53 | 21 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 54 | 21 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 21 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 21 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 21 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 21 | `FACES_HDR` | 0 |  | 0% |
| 59 | 21 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 21 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L557) | 100% |
| 61 | 21 | `UNUSED_61` | 0 |  | 0% |
| 62 | 21 | `UNUSED_62` | 0 |  | 0% |
| 63 | 21 | `DISPLACEMENT_MULTIBLEND` | 0 |  | 0% |


