# NEXON Source
## Developers: NEXON

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L17) | 20 | Vindictus | [`nexon.vindictus`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py) | 44 / 57 | 7 | 76.39% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L17) | 100 | Counter-Strike: Online 2 | [`nexon.cso2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py) | 33 / 58 | 6 | 56.55% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/valve.py#L17) | 100 | Counter-Strike: Online 2 | [`nexon.cso2_2018`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2_2018.py) | 34 / 58 | 6 | 56.55% |


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
| 0 | 20 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L43) | 100% |
| 1 | 20 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L228) | 100% |
| 2 | 20 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L572) | 100% |
| 3 | 20 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 4 | 20 | `VISIBILITY` | 0 | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L168) | 90% |
| 5 | 20 | `NODES` | 0 | [`nexon.vindictus.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L218) | 100% |
| 6 | 20 | `TEXTURE_INFO` | 0 | [`valve.source.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L583) | 100% |
| 6 | 100 | `TEXTURE_INFO` | 0 |  | 0% |
| 7 | 20 | `FACES` | 1 | [`nexon.vindictus.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L151) | 94% |
| 7 | 20 | `FACES` | 2 | [`nexon.vindictus.Facev2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L180) | 88% |
| 7 | 100 | `FACES` | 0 |  | 0% |
| 8 | 20 | `LIGHTING` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 9 | 20 | `OCCLUSION` | 0 |  | 0% |
| 10 | 20 | `LEAVES` | 1 | [`nexon.vindictus.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L210) | 100% |
| 10 | 100 | `LEAVES` | 0 |  | 0% |
| 11 | 20 | `FACEIDS` | 0 |  | 0% |
| 12 | 20 | `EDGES` | 0 | [`nexon.vindictus.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L140) | 100% |
| 13 | 20 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L22) | 100% |
| 14 | 20 | `MODELS` | 0 | [`valve.source.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L510) | 100% |
| 15 | 20 | `WORLD_LIGHTS` | 0 | [`valve.source.WorldLight`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L612) | 100% |
| 15 | 100 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 20 | `LEAF_FACES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L34) | 100% |
| 17 | 20 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L34) | 100% |
| 18 | 20 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L351) | 100% |
| 19 | 20 | `BRUSH_SIDES` | 0 | [`nexon.vindictus.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L113) | 100% |
| 19 | 100 | `BRUSH_SIDES` | 0 |  | 0% |
| 20 | 20 | `AREAS` | 0 | [`nexon.vindictus.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L96) | 100% |
| 21 | 20 | `AREA_PORTALS` | 0 | [`nexon.vindictus.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L103) | 100% |
| 22 | 20 | `UNUSED_22` | 0 |  | 0% |
| 23 | 20 | `UNUSED_23` | 0 |  | 0% |
| 24 | 20 | `UNUSED_24` | 0 |  | 0% |
| 25 | 20 | `UNUSED_25` | 0 |  | 0% |
| 26 | 20 | `DISPLACEMENT_INFO` | 0 | [`nexon.vindictus.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L122) | 92% |
| 26 | 100 | `DISPLACEMENT_INFO` | 0 |  | 0% |
| 26 | 100 | `DISPLACEMENT_INFO` | 0 | [`nexon.cso2_2018.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2_2018.py#L23) | 0% |
| 27 | 20 | `ORIGINAL_FACES` | 1 | [`nexon.vindictus.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L151) | 94% |
| 27 | 20 | `ORIGINAL_FACES` | 2 | [`nexon.vindictus.Facev2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L180) | 88% |
| 27 | 100 | `ORIGINAL_FACES` | 0 |  | 0% |
| 28 | 20 | `PHYSICS_DISPLACEMENT` | 0 |  | 0% |
| 29 | 20 | `PHYSICS_COLLIDE` | 0 | [`physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L18) | 90% |
| 30 | 20 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 31 | 20 | `VERTEX_NORMAL_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 32 | 20 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 20 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L406) | 100% |
| 34 | 20 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 20 | `GAME_LUMP` | - | [`lumps.GameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L333) | 90% |
| 35 | 20 | `GAME_LUMP.sprp` | - | [`nexon.vindictus.GameLump_SPRP`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L255) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 6 | [`valve.source.StaticPropv6`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L748) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.scales` | 6 | [`nexon.vindictus.StaticPropScale`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L304) | 100% |
| 36 | 20 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L502) | 100% |
| 37 | 20 | `PRIMITIVES` | 0 | [`valve.source.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L562) | 100% |
| 38 | 20 | `PRIMITIVE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 39 | 20 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 40 | 20 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L121) | 100% |
| 40 | 100 | `PAKFILE` | 0 |  | 0% |
| 41 | 20 | `CLIP_PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 42 | 20 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L369) | 100% |
| 42 | 100 | `CUBEMAPS` | 0 |  | 0% |
| 43 | 20 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L132) | 100% |
| 44 | 20 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 45 | 20 | `OVERLAYS` | 0 | [`nexon.vindictus.Overlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L225) | 100% |
| 45 | 100 | `OVERLAYS` | 0 |  | 0% |
| 46 | 20 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 20 | `FACE_MARCO_TEXTURE_INFO` | 0 |  | 0% |
| 48 | 20 | `DISPLACEMENT_TRIS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 49 | 20 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 20 | `WATER_OVERLAYS` | 0 | [`valve.source.WaterOverlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L596) | 100% |
| 51 | 20 | `LEAF_AMBIENT_INDEX_HDR` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L484) | 100% |
| 52 | 20 | `LEAF_AMBIENT_INDEX` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L484) | 100% |
| 53 | 20 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 54 | 20 | `WORLD_LIGHTS_HDR` | 0 | [`valve.source.WorldLight`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L612) | 100% |
| 54 | 100 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 20 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 20 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 20 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 20 | `FACES_HDR` | 0 |  | 0% |
| 59 | 20 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 20 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L556) | 100% |
| 61 | 20 | `UNUSED_61` | 0 |  | 0% |
| 61 | 100 | `UNKNOWN_61` | 0 |  | 0% |
| 62 | 20 | `UNUSED_62` | 0 |  | 0% |
| 63 | 20 | `UNUSED_63` | 0 |  | 0% |


