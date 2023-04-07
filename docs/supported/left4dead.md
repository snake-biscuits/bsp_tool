# Left 4 Dead Series
## Developers: Valve & Turtle Rock Studios

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 20 | Left 4 Dead | [`valve.left4dead`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/left4dead.py) | 42 / 58 | 6 | 71.90% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 21 | Left 4 Dead 2 | [`valve.left4dead2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/left4dead2.py) | 43 / 63 | 1 | 67.78% |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 27 | Contagion | [`valve.left4dead2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/left4dead2.py) | 43 / 63 | 1 | 67.78% |


### References
 * [VDC: Left 4 Dead Engine Branch](https://developer.valvesoftware.com/wiki/Left_4_Dead_(engine_branch))
 * [VDC: Left 4 Dead 2 .bsp](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Left_4_Dead_2_.2F_Contagion)


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 20 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 1 | 20 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L228) | 100% |
| 2 | 20 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L678) | 100% |
| 3 | 20 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 4 | 20 | `VISIBILITY` | 0 | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L214) | 90% |
| 5 | 20 | `NODES` | 0 | [`valve.source.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L623) | 100% |
| 6 | 20 | `TEXTURE_INFO` | 0 | [`valve.source.TextureInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L692) | 100% |
| 7 | 20 | `FACES` | 1 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L518) | 100% |
| 8 | 20 | `LIGHTING` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps.py#L107) | 100% |
| 9 | 20 | `OCCLUSION` | 0 |  | 0% |
| 10 | 20 | `LEAVES` | 0 | [`valve.source.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L551) | 100% |
| 10 | 20 | `LEAVES` | 1 | [`valve.orange_box.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L108) | 100% |
| 10 | 21 | `LEAVES` | 0 | [`valve.source.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L551) | 100% |
| 10 | 21 | `LEAVES` | 1 | [`valve.orange_box.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L108) | 100% |
| 11 | 20 | `FACE_IDS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 12 | 20 | `EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L145) | 100% |
| 13 | 20 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L13) | 100% |
| 14 | 20 | `MODELS` | 0 | [`valve.source.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L608) | 100% |
| 15 | 20 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 20 | `LEAF_FACES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 17 | 20 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 18 | 20 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L409) | 100% |
| 19 | 20 | `BRUSH_SIDES` | 0 | [`valve.source.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L419) | 100% |
| 20 | 20 | `AREAS` | 0 | [`valve.source.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L391) | 100% |
| 21 | 20 | `AREA_PORTALS` | 0 | [`valve.source.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L398) | 100% |
| 22 | 20 | `UNUSED_22` | 0 |  | 0% |
| 22 | 21 | `PROP_COLLISION` | 0 |  | 0% |
| 23 | 20 | `UNUSED_23` | 0 |  | 0% |
| 23 | 21 | `PROP_HULLS` | 0 |  | 0% |
| 24 | 20 | `UNUSED_24` | 0 |  | 0% |
| 24 | 21 | `PROP_HULL_VERTS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 25 | 20 | `UNUSED_25` | 0 |  | 0% |
| 25 | 21 | `PROP_HULL_TRIS` | 0 |  | 0% |
| 26 | 20 | `DISPLACEMENT_INFO` | 0 | [`valve.source.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L458) | 100% |
| 27 | 20 | `ORIGINAL_FACES` | 0 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L518) | 100% |
| 28 | 20 | `PHYSICS_DISPLACEMENT` | 0 | [`valve_physics.Displacement`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve_physics.py#L259) | 90% |
| 29 | 20 | `PHYSICS_COLLIDE` | 0 | [`valve_physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve_physics.py#L26) | 90% |
| 30 | 20 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 31 | 20 | `VERTEX_NORMAL_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 32 | 20 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 20 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L507) | 100% |
| 34 | 20 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 20 | `GAME_LUMP` | - | [`lumps.GameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L334) | 90% |
| 35 | 20 | `GAME_LUMP.sprp` | - | [`valve.source.GameLump_SPRP`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L775) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 4 | [`valve.source.StaticPropv4`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L830) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 5 |  | 0% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 6 |  | 0% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 8 | [`valve.left4dead.StaticPropv8`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/left4dead.py#L98) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 9 | [`valve.left4dead2.StaticPropv9`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/left4dead2.py#L114) | 100% |
| 35 | 20 | `GAME_LUMP.sprp.props` | 10 | [`valve.orange_box.StaticPropv10`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L132) | 100% |
| 36 | 20 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L600) | 100% |
| 37 | 20 | `PRIMITIVES` | 0 | [`valve.source.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L667) | 100% |
| 38 | 20 | `PRIMITIVE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 39 | 20 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 40 | 20 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L120) | 100% |
| 41 | 20 | `CLIP_PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L251) | 100% |
| 42 | 20 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L428) | 100% |
| 43 | 20 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L143) | 100% |
| 44 | 20 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L33) | 100% |
| 45 | 20 | `OVERLAYS` | 0 |  | 0% |
| 46 | 20 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 20 | `FACE_MACRO_TEXTURE_INFO` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L17) | 100% |
| 48 | 20 | `DISPLACEMENT_TRIS` | 0 |  | 0% |
| 49 | 20 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 20 | `WATER_OVERLAYS` | 0 | [`valve.source.WaterOverlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L709) | 100% |
| 51 | 20 | `LEAF_AMBIENT_INDEX_HDR` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L580) | 100% |
| 52 | 20 | `LEAF_AMBIENT_INDEX` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L580) | 100% |
| 53 | 20 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps.py#L107) | 100% |
| 54 | 20 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 20 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 20 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 20 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 20 | `FACES_HDR` | 0 |  | 0% |
| 59 | 20 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 20 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L661) | 100% |
| 61 | 20 | `OVERLAY_SYSTEM_LEVELS` | 0 |  | 0% |
| 62 | 20 | `UNUSED_62` | 0 |  | 0% |
| 62 | 21 | `PHYSICS_LEVEL` | 0 |  | 0% |
| 63 | 20 | `UNUSED_63` | 0 |  | 0% |


