# Supported Titanfall Series Games
Developers: Respawn Entertainment

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 29 | Titanfall | [`respawn.titanfall`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py) | 57 / 72 | 56 | 78.89% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 29 | Titanfall: Online | [`respawn.titanfall`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py) | 57 / 72 | 56 | 78.89% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 37 | Titanfall 2 | [`respawn.titanfall2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py) | 57 / 75 | 53 | 75.73% |


### References
 * [Valve Developer Wiki](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall)
 * [McSimp's Titanfall Map Exporter Tool](https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py)
   - by [Icepick](https://github.com/Titanfall-Mods/Titanfall-2-Icepick) contributor [McSimp](https://github.com/McSimp)
 * [Legion](https://github.com/dtzxporter/Legion/)


### Extracting `.bsp`s
Titanfall Engine `.bsp`, `.bsp_lump` & `.ent` are stored in `.vpk` files.
Extracting these files to work on them requires Titanfall Engine specific tools:

Once you have chosen your [extraction tool](Extraction-tools):
 * Locate the `.vpk`s for the game you want to work with (game must be installed)
   - `Titanfall/vpk/`
   - `Titanfall2/vpk/`
   - `Apex Legends/vpk/`
 * Open the `*.bsp.pak000_dir.vpk` for the map you want to load
   - Titanfall 2 map names can be found here: [NoSkill Modding Wiki](https://noskill.gitbook.io/titanfall2/documentation/file-location/vpk-file-names)
   - Lobbies are stored in `mp_common.bsp.pak000_dir.vpk`
 * Extract the `.bsp`, `.ent`s & `.bsp_lumps` from the `maps/` folder to someplace you'll remember
   - each `.vpk` holds assets for one `.bsp` (textures and models are stored elsewhere)


### Extraction Tools
 * [Titanfall VPKTool3.4 Portable](https://github.com/Wanty5883/Titanfall2/blob/master/tools/Titanfall_VPKTool3.4_Portable.zip) (GUI only)
   - by `Cra0kalo` (currently Closed Source) **recommended**
 * [TitanfallVPKTool](https://github.com/p0358/TitanfallVPKTool) (GUI & CLI)
   - by `P0358`
 * [RSPNVPK](https://github.com/squidgyberries/RSPNVPK) (CLI only)
   - Fork of `MrSteyk`'s Tool
 * [UnoVPKTool](https://github.com/Unordinal/UnoVPKTool) (CLI only)
   - by `Unordinal`

> NOTE: Apex's `GAME_LUMP` lump version should be the same as the version of the `.bsp` it is in


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 29 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
| 1 | 29 | `PLANES` | 1 | [`respawn.titanfall.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L351) | 100% |
| 2 | 29 | `TEXTURE_DATA` | 1 | [`respawn.titanfall.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L429) | 100% |
| 3 | 29 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 4 | 29 | `LIGHTPROBE_PARENT_INFOS` | 0 |  | 0% |
| 5 | 29 | `SHADOW_ENVIRONMENTS` | 0 |  | 0% |
| 6 | 29 | `LIGHTPROBE_BSP_NODES` | 0 |  | 0% |
| 7 | 29 | `LIGHTPROBE_BSP_REF_IDS` | 0 |  | 0% |
| 8 | 29 | `UNUSED_8` | 0 |  | 0% |
| 9 | 29 | `UNUSED_9` | 0 |  | 0% |
| 10 | 29 | `UNUSED_10` | 0 |  | 0% |
| 11 | 29 | `UNUSED_11` | 0 |  | 0% |
| 12 | 29 | `UNUSED_12` | 0 |  | 0% |
| 13 | 29 | `UNUSED_13` | 0 |  | 0% |
| 14 | 29 | `MODELS` | 0 | [`respawn.titanfall.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L319) | 100% |
| 15 | 29 | `UNUSED_15` | 0 |  | 0% |
| 16 | 29 | `UNUSED_16` | 0 |  | 0% |
| 17 | 29 | `UNUSED_17` | 0 |  | 0% |
| 18 | 29 | `UNUSED_18` | 0 |  | 0% |
| 19 | 29 | `UNUSED_19` | 0 |  | 0% |
| 20 | 29 | `UNUSED_20` | 0 |  | 0% |
| 21 | 29 | `UNUSED_21` | 0 |  | 0% |
| 22 | 29 | `UNUSED_22` | 0 |  | 0% |
| 23 | 29 | `UNUSED_23` | 0 |  | 0% |
| 24 | 29 | `ENTITY_PARTITIONS` | 0 | [`respawn.titanfall.EntityPartitions`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L511) | 100% |
| 25 | 29 | `UNUSED_25` | 0 |  | 0% |
| 26 | 29 | `UNUSED_26` | 0 |  | 0% |
| 27 | 29 | `UNUSED_27` | 0 |  | 0% |
| 28 | 29 | `UNUSED_28` | 0 |  | 0% |
| 29 | 29 | `PHYSICS_COLLIDE` | 0 | [`physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L17) | 90% |
| 30 | 29 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 31 | 29 | `UNUSED_31` | 0 |  | 0% |
| 32 | 29 | `UNUSED_32` | 0 |  | 0% |
| 33 | 29 | `UNUSED_33` | 0 |  | 0% |
| 34 | 29 | `UNUSED_34` | 0 |  | 0% |
| 35 | 29 | `GAME_LUMP` | 0 |  | 0% |
| 36 | 29 | `UNUSED_36` | 0 | [`respawn.titanfall.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L257) | 100% |
| 36 | 37 | `UNUSED_36` | 0 |  | 0% |
| 37 | 29 | `UNUSED_37` | 0 |  | 0% |
| 38 | 29 | `UNUSED_38` | 0 |  | 0% |
| 39 | 29 | `UNUSED_39` | 0 |  | 0% |
| 40 | 29 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L127) | 90% |
| 41 | 29 | `UNUSED_41` | 0 |  | 0% |
| 42 | 29 | `CUBEMAPS` | 0 | [`respawn.titanfall.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L240) | 100% |
| 43 | 29 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L136) | 100% |
| 44 | 29 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 45 | 29 | `UNUSED_45` | 0 |  | 0% |
| 46 | 29 | `UNUSED_46` | 0 |  | 0% |
| 47 | 29 | `UNUSED_47` | 0 |  | 0% |
| 48 | 29 | `UNUSED_48` | 0 |  | 0% |
| 49 | 29 | `UNUSED_49` | 0 |  | 0% |
| 50 | 29 | `UNUSED_50` | 0 |  | 0% |
| 51 | 29 | `UNUSED_51` | 0 |  | 0% |
| 52 | 29 | `UNUSED_52` | 0 |  | 0% |
| 53 | 29 | `UNUSED_53` | 0 |  | 0% |
| 54 | 29 | `WORLDLIGHTS` | 0 |  | 0% |
| 55 | 29 | `WORLDLIGHTS_PARENT_INFO` | 0 |  | 0% |
| 56 | 29 | `UNUSED_56` | 0 |  | 0% |
| 57 | 29 | `UNUSED_57` | 0 |  | 0% |
| 58 | 29 | `UNUSED_58` | 0 |  | 0% |
| 59 | 29 | `UNUSED_59` | 0 |  | 0% |
| 60 | 29 | `UNUSED_60` | 0 |  | 0% |
| 61 | 29 | `UNUSED_61` | 0 |  | 0% |
| 62 | 29 | `UNUSED_62` | 0 |  | 0% |
| 63 | 29 | `UNUSED_63` | 0 |  | 0% |
| 64 | 29 | `UNUSED_64` | 0 |  | 0% |
| 65 | 29 | `UNUSED_65` | 0 |  | 0% |
| 66 | 29 | `TRICOLL_TRIS` | 0 |  | 0% |
| 67 | 29 | `UNUSED_67` | 0 |  | 0% |
| 68 | 29 | `TRICOLL_NODES` | 0 |  | 0% |
| 69 | 29 | `TRICOLL_HEADERS` | 0 |  | 0% |
| 70 | 29 | `UNUSED_70` | 0 |  | 0% |
| 71 | 29 | `VERTEX_UNLIT` | 0 | [`respawn.titanfall.VertexUnlit`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L485) | 100% |
| 72 | 29 | `VERTEX_LIT_FLAT` | 1 | [`respawn.titanfall.VertexLitFlat`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L474) | 100% |
| 73 | 29 | `VERTEX_LIT_BUMP` | 1 | [`respawn.titanfall.VertexLitBump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L458) | 100% |
| 74 | 29 | `VERTEX_UNLIT_TS` | 0 | [`respawn.titanfall.VertexUnlitTS`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L496) | 100% |
| 75 | 29 | `VERTEX_BLINN_PHONG` | 0 | [`respawn.titanfall.VertexBlinnPhong`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L449) | 100% |
| 76 | 29 | `VERTEX_RESERVED_5` | 0 |  | 0% |
| 77 | 29 | `VERTEX_RESERVED_6` | 0 |  | 0% |
| 78 | 29 | `VERTEX_RESERVED_7` | 0 |  | 0% |
| 79 | 29 | `MESH_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 80 | 29 | `MESHES` | 0 | [`respawn.titanfall.Mesh`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L292) | 100% |
| 81 | 29 | `MESH_BOUNDS` | 0 | [`respawn.titanfall.MeshBounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L308) | 100% |
| 82 | 29 | `MATERIAL_SORT` | 0 | [`respawn.titanfall.MaterialSort`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L282) | 100% |
| 83 | 29 | `LIGHTMAP_HEADERS` | 1 | [`respawn.titanfall.LightmapHeader`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L265) | 100% |
| 84 | 29 | `UNUSED_84` | 0 |  | 0% |
| 85 | 29 | `CM_GRID` | 0 | [`respawn.titanfall.Grid`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L249) | 100% |
| 86 | 29 | `CM_GRID_CELLS` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 87 | 29 | `CM_GEO_SETS` | 0 |  | 0% |
| 88 | 29 | `CM_GEO_SET_BOUNDS` | 0 | [`respawn.titanfall.Bounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 89 | 29 | `CM_PRIMITIVES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 90 | 29 | `CM_PRIMITIVE_BOUNDS` | 0 | [`respawn.titanfall.Bounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 91 | 29 | `CM_UNIQUE_CONTENTS` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 92 | 29 | `CM_BRUSHES` | 0 | [`respawn.titanfall.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L218) | 100% |
| 93 | 29 | `CM_BRUSH_SIDE_PLANE_OFFSETS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 94 | 29 | `CM_BRUSH_SIDE_PROPS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 95 | 29 | `CM_BRUSH_TEX_VECS` | 0 | [`respawn.titanfall.TextureVector`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L442) | 100% |
| 96 | 29 | `TRICOLL_BEVEL_STARTS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 97 | 29 | `TRICOLL_BEVEL_INDICES` | 0 | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 98 | 29 | `LIGHTMAP_DATA_SKY` | 0 |  | 0% |
| 99 | 29 | `CSM_AABB_NODES` | 0 | [`respawn.titanfall.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 100 | 29 | `CSM_OBJ_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 101 | 29 | `LIGHTPROBES` | 0 |  | 0% |
| 102 | 29 | `STATIC_PROP_LIGHTPROBE_INDEX` | 0 |  | 0% |
| 103 | 29 | `LIGHTPROBE_TREE` | 0 |  | 0% |
| 104 | 29 | `LIGHTPROBE_REFERENCES` | 0 | [`respawn.titanfall.LightProbeRef`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L274) | 100% |
| 104 | 37 | `LIGHTPROBE_REFERENCES` | 0 |  | 0% |
| 105 | 29 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 |  | 0% |
| 106 | 29 | `CELL_BSP_NODES` | 0 |  | 0% |
| 107 | 29 | `CELLS` | 0 | [`respawn.titanfall.Cell`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L228) | 100% |
| 108 | 29 | `PORTALS` | 0 | [`respawn.titanfall.Portal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L359) | 100% |
| 109 | 29 | `PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 110 | 29 | `PORTAL_EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L113) | 100% |
| 111 | 29 | `PORTAL_VERTEX_EDGES` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 112 | 29 | `PORTAL_VERTEX_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 113 | 29 | `PORTAL_EDGE_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 114 | 29 | `PORTAL_EDGE_INTERSECT_EDGE` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 114 | 37 | `PORTAL_EDGE_INTERSECT_EDGE` | 0 |  | 0% |
| 115 | 29 | `PORTAL_EDGE_INTERSECT_AT_VERTEX` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 116 | 29 | `PORTAL_EDGE_INTERSECT_HEADER` | 0 | [`respawn.titanfall.PortalEdgeIntersectHeader`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L374) | 100% |
| 117 | 29 | `OCCLUSION_MESH_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 118 | 29 | `OCCLUSION_MESH_INDICES` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L32) | 100% |
| 119 | 29 | `CELL_AABB_NODES` | 0 | [`respawn.titanfall.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 120 | 29 | `OBJ_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 121 | 29 | `OBJ_REFERENCE_BOUNDS` | 0 | [`respawn.titanfall.ObjRefBounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L340) | 100% |
| 122 | 29 | `LIGHTMAP_DATA_RTL_PAGE` | 0 |  | 0% |
| 123 | 29 | `LEVEL_INFO` | 0 |  | 0% |
| 124 | 29 | `SHADOW_MESH_OPAQUE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 125 | 29 | `SHADOW_MESH_ALPHA_VERTICES` | 0 | [`respawn.titanfall.ShadowMeshAlphaVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L391) | 100% |
| 126 | 29 | `SHADOW_MESH_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 127 | 29 | `SHADOW_MESH_MESHES` | 0 | [`respawn.titanfall.ShadowMesh`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L381) | 100% |


