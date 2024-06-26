# NEXON Source
## Developers: NEXON

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 20 | Vindictus | [`nexon.vindictus69`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py) | 44 / 57 | 7 | 76.39% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 20 | Vindictus | [`nexon.vindictus`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py) | 44 / 57 | 7 | 76.39% |
| [`NexonBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/nexon.py#L7) | 100 | Counter-Strike: Online 2 | [`nexon.cso2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py) | 40 / 58 | 6 | 68.19% |
| [`NexonBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/nexon.py#L7) | 100 | Counter-Strike: Online 2 | [`nexon.cso2_2018`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2_2018.py) | 40 / 58 | 6 | 66.47% |


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
| 0 | 20 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 1 | 20 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L237) | 100% |
| 2 | 20 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L685) | 100% |
| 3 | 20 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 4 | 20 | `VISIBILITY` | 0 | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L248) | 90% |
| 5 | 20 | `NODES` | 0 | [`nexon.vindictus69.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L250) | 100% |
| 6 | 20 | `TEXTURE_INFO` | 0 | [`valve.source.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L698) | 100% |
| 7 | 20 | `FACES` | 1 | [`nexon.vindictus69.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L158) | 94% |
| 7 | 20 | `FACES` | 2 | [`nexon.vindictus69.Facev2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L193) | 88% |
| 7 | 100 | `FACES` | 1 | [`nexon.cso2.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py#L110) | 100% |
| 8 | 20 | `LIGHTING` | 0 | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/source.py#L8) | 100% |
| 8 | 100 | `LIGHTING` | 0 | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/cso2_2018.py#L6) | 100% |
| 9 | 20 | `OCCLUSION` | 0 |  | 0% |
| 10 | 20 | `LEAVES` | 1 | [`nexon.vindictus69.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L229) | 100% |
| 10 | 100 | `LEAVES` | 0 |  | 0% |
| 11 | 20 | `FACEIDS` | 0 |  | 0% |
| 12 | 20 | `EDGES` | 0 | [`id_software.remake_quake_old.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/remake_quake_old.py#L43) | 100% |
| 13 | 20 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L11) | 100% |
| 14 | 20 | `MODELS` | 0 | [`valve.source.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L614) | 100% |
| 15 | 20 | `WORLD_LIGHTS` | 0 | [`valve.source.WorldLight`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L737) | 100% |
| 15 | 100 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 20 | `LEAF_FACES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 17 | 20 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 18 | 20 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L413) | 100% |
| 19 | 20 | `BRUSH_SIDES` | 0 | [`nexon.vindictus69.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L117) | 100% |
| 19 | 100 | `BRUSH_SIDES` | 0 | [`nexon.cso2.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py#L101) | 100% |
| 20 | 20 | `AREAS` | 0 | [`nexon.vindictus69.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L99) | 100% |
| 21 | 20 | `AREA_PORTALS` | 0 | [`nexon.vindictus69.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L106) | 100% |
| 22 | 20 | `UNUSED_22` | 0 |  | 0% |
| 23 | 20 | `UNUSED_23` | 0 |  | 0% |
| 24 | 20 | `UNUSED_24` | 0 |  | 0% |
| 25 | 20 | `UNUSED_25` | 0 |  | 0% |
| 26 | 20 | `DISPLACEMENT_INFO` | 0 | [`nexon.vindictus69.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L126) | 92% |
| 26 | 100 | `DISPLACEMENT_INFO` | 0 | [`valve.source.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L462) | 100% |
| 26 | 100 | `DISPLACEMENT_INFO` | 0 | [`nexon.cso2_2018.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2_2018.py#L23) | 0% |
| 27 | 20 | `ORIGINAL_FACES` | 1 | [`nexon.vindictus69.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L158) | 94% |
| 27 | 20 | `ORIGINAL_FACES` | 2 | [`nexon.vindictus69.Facev2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L193) | 88% |
| 27 | 100 | `ORIGINAL_FACES` | 0 | [`nexon.cso2.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py#L110) | 100% |
| 28 | 20 | `PHYSICS_DISPLACEMENT` | 0 | [`valve.physics.Displacement`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/physics.py#L259) | 90% |
| 29 | 20 | `PHYSICS_COLLIDE` | 0 |  | 0% |
| 30 | 20 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 31 | 20 | `VERTEX_NORMAL_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 32 | 20 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 20 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L511) | 100% |
| 34 | 20 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 20 | `GAME_LUMP` | - | [`lumps.GameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L345) | 90% |
| 35 | 20 | `GAME_LUMP.sprp` | 5 | [`valve.source.GameLump_SPRPv5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L871) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.leaves` | 5 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 5 | [`valve.source.StaticPropv5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L848) | 100% |
| 35 | 20 | `GAME_LUMP.sprp` | 6 | [`nexon.vindictus.GameLump_SPRPv6`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L93) | 100% |
| 35 | 20 | `GAME_LUMP.sprp` | 6 | [`nexon.vindictus69.GameLump_SPRPv6`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L309) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.leaves` | 6 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 6 | [`valve.source.StaticPropv5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L848) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 6 | [`valve.source.StaticPropv6`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L875) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.scales` | 6 | [`nexon.vindictus69.StaticPropScale`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L300) | 100% |
| 35 | 20 | `GAME_LUMP.sprp` | 7 | [`nexon.vindictus.GameLump_SPRPv7`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L121) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.leaves` | 7 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 7 | [`nexon.vindictus.StaticPropv7`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py#L97) | 100% |
| 35 | 100 | `GAME_LUMP.sprp` | ? |  | 0% |
| 36 | 20 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L606) | 100% |
| 37 | 20 | `PRIMITIVES` | 0 | [`valve.source.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L674) | 100% |
| 37 | 100 | `PRIMITIVES` | 0 | [`nexon.cso2.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py#L145) | 100% |
| 38 | 20 | `PRIMITIVE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 39 | 20 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 39 | 100 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 40 | 20 | `PAKFILE` | 0 | [`valve.source.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L933) | 100% |
| 40 | 100 | `PAKFILE` | 0 | [`nexon.pakfile.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/pakfile.py#L129) | 75% |
| 41 | 20 | `CLIP_PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 42 | 20 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L432) | 100% |
| 42 | 100 | `CUBEMAPS` | 0 |  | 0% |
| 43 | 20 | `TEXTURE_DATA_STRING_DATA` | 0 | [`valve.source.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L969) | 100% |
| 44 | 20 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 44 | 100 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 45 | 20 | `OVERLAYS` | 0 | [`nexon.vindictus69.Overlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus69.py#L265) | 100% |
| 45 | 100 | `OVERLAYS` | 0 |  | 0% |
| 46 | 20 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 20 | `FACE_MACRO_TEXTURE_INFO` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L15) | 100% |
| 48 | 20 | `DISPLACEMENT_TRIANGLES` | 0 | [`valve.source.DisplacementTriangle`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L503) | 100% |
| 49 | 20 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 20 | `WATER_OVERLAYS` | 0 | [`valve.source.WaterOverlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L719) | 100% |
| 51 | 20 | `LEAF_AMBIENT_INDEX_HDR` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L586) | 100% |
| 52 | 20 | `LEAF_AMBIENT_INDEX` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L586) | 100% |
| 53 | 20 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/source.py#L8) | 100% |
| 53 | 100 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/cso2_2018.py#L6) | 100% |
| 53 | 100 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.face_lightmaps`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/source.py#L8) | 100% |
| 54 | 20 | `WORLD_LIGHTS_HDR` | 0 | [`valve.source.WorldLight`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L737) | 100% |
| 54 | 100 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 20 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 20 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 20 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 20 | `FACES_HDR` | 0 |  | 0% |
| 58 | 100 | `FACES_HDR` | 1 | [`nexon.cso2.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/cso2.py#L110) | 100% |
| 59 | 20 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 20 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L668) | 100% |
| 61 | 20 | `UNUSED_61` | 0 |  | 0% |
| 61 | 100 | `UNKNOWN_61` | 0 |  | 0% |
| 62 | 20 | `UNUSED_62` | 0 |  | 0% |
| 63 | 20 | `UNUSED_63` | 0 |  | 0% |


