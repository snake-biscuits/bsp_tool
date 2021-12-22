# Supported Titanfall Series Games
Developers: Respawn Entertainment

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 29 | Titanfall | [`respawn.titanfall`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py) | 57 / 75 | 53 | 75.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 29 | Titanfall: Online | [`respawn.titanfall`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py) | 57 / 75 | 53 | 75.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 37 | Titanfall 2 | [`respawn.titanfall2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py) | 57 / 78 | 50 | 72.44% |


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
 * [Titanfall_VPKTool3.4_Portable](https://github.com/Wanty5883/Titanfall2/blob/master/tools/Titanfall_VPKTool3.4_Portable.zip) (GUI only)
   - by `Cra0kalo` (currently Closed Source) **recommended**
 * [TitanfallVPKTool](https://github.com/p0358/TitanfallVPKTool) (GUI & CLI)
   - by `P0358`
 * [RSPNVPK](https://github.com/squidgyberries/RSPNVPK) (CLI only)
   - Fork of `MrSteyk`'s Tool
 * [UnoVPKTool](https://github.com/Unordinal/UnoVPKTool) (CLI only)
   - by `Unordinal`


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 29 | `ENTITIES` | 0 | [shared.Entities](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 90% |
| 0 | 37 | `ENTITIES` | 0 | [shared.Entities](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 90% |
| 1 | 29 | `PLANES` | 1 | [respawn.titanfall.Plane](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L351) | 100% |
| 1 | 37 | `PLANES` | 1 | [respawn.titanfall.Plane](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L351) | 100% |
| 2 | 29 | `TEXTURE_DATA` | 1 | [respawn.titanfall.TextureData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L429) | 100% |
| 2 | 37 | `TEXTURE_DATA` | 1 | [respawn.titanfall.TextureData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L429) | 100% |
| 3 | 29 | `VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 3 | 37 | `VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 4 | 37 | `LIGHTPROBE_PARENT_INFOS` | 0 | | 0% || 5 | 37 | `SHADOW_ENVIRONMENTS` | 0 | | 0% || 6 | 37 | `LIGHTPROBE_BSP_NODES` | 0 | | 0% || 7 | 37 | `LIGHTPROBE_BSP_REF_IDS` | 0 | | 0% || 14 | 29 | `MODELS` | 0 | [respawn.titanfall.Model](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L319) | 100% |
| 14 | 37 | `MODELS` | 0 | [respawn.titanfall.Model](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L319) | 100% |
| 24 | 29 | `ENTITY_PARTITIONS` | 0 | [respawn.titanfall.EntityPartitions](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L511) | 90% |
| 24 | 37 | `ENTITY_PARTITIONS` | 0 | [respawn.titanfall.EntityPartitions](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L511) | 90% |
| 29 | 29 | `PHYSICS_COLLIDE` | 0 | [physics.CollideLump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L17) | 90% |
| 29 | 37 | `PHYSICS_COLLIDE` | 0 | [physics.CollideLump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L17) | 90% |
| 30 | 29 | `VERTEX_NORMALS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 30 | 37 | `VERTEX_NORMALS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 36 | 29 | `LEAF_WATER_DATA` | 0 | [respawn.titanfall.LeafWaterData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L257) | 100% |
| 40 | 29 | `PAKFILE` | 0 | [shared.PakFile](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L127) | 90% |
| 40 | 37 | `PAKFILE` | 0 | [shared.PakFile](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L127) | 90% |
| 42 | 29 | `CUBEMAPS` | 0 | [respawn.titanfall.Cubemap](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L240) | 100% |
| 42 | 37 | `CUBEMAPS` | 0 | [respawn.titanfall.Cubemap](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L240) | 100% |
| 43 | 29 | `TEXTURE_DATA_STRING_DATA` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L136) | 90% |
| 43 | 37 | `TEXTURE_DATA_STRING_DATA` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L136) | 90% |
| 44 | 29 | `TEXTURE_DATA_STRING_TABLE` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 44 | 37 | `TEXTURE_DATA_STRING_TABLE` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 54 | 29 | `WORLDLIGHTS` | 0 | | 0% || 54 | 37 | `WORLDLIGHTS` | 0 | | 0% || 55 | 37 | `WORLDLIGHTS_PARENT_INFO` | 0 | | 0% || 62 | 29 | `PHYSICS_LEVEL` | 0 | | 0% || 66 | 29 | `TRICOLL_TRIS` | 0 | | 0% || 66 | 37 | `TRICOLL_TRIS` | 0 | | 0% || 68 | 29 | `TRICOLL_NODES` | 0 | | 0% || 68 | 37 | `TRICOLL_NODES` | 0 | | 0% || 69 | 29 | `TRICOLL_HEADERS` | 0 | | 0% || 69 | 37 | `TRICOLL_HEADERS` | 0 | | 0% || 70 | 29 | `PHYSICS_TRIANGLES` | 0 | | 0% || 71 | 29 | `VERTEX_UNLIT` | 0 | [respawn.titanfall.VertexUnlit](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L485) | 100% |
| 71 | 37 | `VERTEX_UNLIT` | 0 | [respawn.titanfall.VertexUnlit](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L485) | 100% |
| 72 | 29 | `VERTEX_LIT_FLAT` | 1 | [respawn.titanfall.VertexLitFlat](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L474) | 100% |
| 72 | 37 | `VERTEX_LIT_FLAT` | 1 | [respawn.titanfall.VertexLitFlat](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L474) | 100% |
| 73 | 29 | `VERTEX_LIT_BUMP` | 1 | [respawn.titanfall.VertexLitBump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L458) | 100% |
| 73 | 37 | `VERTEX_LIT_BUMP` | 1 | [respawn.titanfall.VertexLitBump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L458) | 100% |
| 74 | 29 | `VERTEX_UNLIT_TS` | 0 | [respawn.titanfall.VertexUnlitTS](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L496) | 100% |
| 74 | 37 | `VERTEX_UNLIT_TS` | 0 | [respawn.titanfall.VertexUnlitTS](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L496) | 100% |
| 75 | 29 | `VERTEX_BLINN_PHONG` | 0 | [respawn.titanfall.VertexBlinnPhong](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L449) | 100% |
| 75 | 37 | `VERTEX_BLINN_PHONG` | 0 | [respawn.titanfall.VertexBlinnPhong](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L449) | 100% |
| 76 | 29 | `VERTEX_RESERVED_5` | 0 | | 0% || 76 | 37 | `VERTEX_RESERVED_5` | 0 | | 0% || 77 | 29 | `VERTEX_RESERVED_6` | 0 | | 0% || 77 | 37 | `VERTEX_RESERVED_6` | 0 | | 0% || 78 | 29 | `VERTEX_RESERVED_7` | 0 | | 0% || 78 | 37 | `VERTEX_RESERVED_7` | 0 | | 0% || 79 | 29 | `MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 79 | 37 | `MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 80 | 29 | `MESHES` | 0 | [respawn.titanfall.Mesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L292) | 100% |
| 80 | 37 | `MESHES` | 0 | [respawn.titanfall.Mesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L292) | 100% |
| 81 | 29 | `MESH_BOUNDS` | 0 | [respawn.titanfall.MeshBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L308) | 100% |
| 81 | 37 | `MESH_BOUNDS` | 0 | [respawn.titanfall.MeshBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L308) | 100% |
| 82 | 29 | `MATERIAL_SORT` | 0 | [respawn.titanfall.MaterialSort](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L282) | 100% |
| 82 | 37 | `MATERIAL_SORT` | 0 | [respawn.titanfall.MaterialSort](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L282) | 100% |
| 83 | 29 | `LIGHTMAP_HEADERS` | 1 | [respawn.titanfall.LightmapHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L265) | 100% |
| 83 | 37 | `LIGHTMAP_HEADERS` | 1 | [respawn.titanfall.LightmapHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L265) | 100% |
| 85 | 29 | `CM_GRID` | 0 | [respawn.titanfall.Grid](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L249) | 100% |
| 85 | 37 | `CM_GRID` | 0 | [respawn.titanfall.Grid](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L249) | 100% |
| 86 | 29 | `CM_GRID_CELLS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 86 | 37 | `CM_GRID_CELLS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 87 | 29 | `CM_GEO_SETS` | 0 | | 0% || 87 | 37 | `CM_GEO_SETS` | 0 | | 0% || 88 | 29 | `CM_GEO_SET_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 88 | 37 | `CM_GEO_SET_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 89 | 29 | `CM_PRIMITIVES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 89 | 37 | `CM_PRIMITIVES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 90 | 29 | `CM_PRIMITIVE_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 90 | 37 | `CM_PRIMITIVE_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L211) | 100% |
| 91 | 29 | `CM_UNIQUE_CONTENTS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 91 | 37 | `CM_UNIQUE_CONTENTS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 92 | 29 | `CM_BRUSHES` | 0 | [respawn.titanfall.Brush](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L218) | 100% |
| 92 | 37 | `CM_BRUSHES` | 0 | [respawn.titanfall.Brush](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L218) | 100% |
| 93 | 29 | `CM_BRUSH_SIDE_PLANE_OFFSETS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 93 | 37 | `CM_BRUSH_SIDE_PLANE_OFFSETS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 94 | 29 | `CM_BRUSH_SIDE_PROPS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 94 | 37 | `CM_BRUSH_SIDE_PROPS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 95 | 29 | `CM_BRUSH_TEX_VECS` | 0 | [respawn.titanfall.TextureVector](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L442) | 100% |
| 95 | 37 | `CM_BRUSH_TEX_VECS` | 0 | [respawn.titanfall.TextureVector](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L442) | 100% |
| 96 | 29 | `TRICOLL_BEVEL_STARTS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 96 | 37 | `TRICOLL_BEVEL_STARTS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 97 | 29 | `TRICOLL_BEVEL_INDICES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 97 | 37 | `TRICOLL_BEVEL_INDICES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L40) | 100% |
| 98 | 29 | `LIGHTMAP_DATA_SKY` | 0 | | 0% || 98 | 37 | `LIGHTMAP_DATA_SKY` | 0 | | 0% || 99 | 29 | `CSM_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 99 | 37 | `CSM_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 100 | 29 | `CSM_OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 100 | 37 | `CSM_OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 101 | 29 | `LIGHTPROBES` | 0 | | 0% || 101 | 37 | `LIGHTPROBES` | 0 | | 0% || 102 | 29 | `STATIC_PROP_LIGHTPROBE_INDEX` | 0 | | 0% || 102 | 37 | `STATIC_PROP_LIGHTPROBE_INDEX` | 0 | | 0% || 103 | 29 | `LIGHTPROBE_TREE` | 0 | | 0% || 103 | 37 | `LIGHTPROBE_TREE` | 0 | | 0% || 104 | 29 | `LIGHTPROBE_REFERENCES` | 0 | [respawn.titanfall.LightProbeRef](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L274) | 100% |
| 104 | 37 | `LIGHTPROBE_REFERENCES` | 0 | | 0% || 105 | 29 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 | | 0% || 105 | 37 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 | | 0% || 106 | 29 | `CELL_BSP_NODES` | 0 | | 0% || 106 | 37 | `CELL_BSP_NODES` | 0 | | 0% || 107 | 29 | `CELLS` | 0 | [respawn.titanfall.Cell](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L228) | 100% |
| 107 | 37 | `CELLS` | 0 | [respawn.titanfall.Cell](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L228) | 100% |
| 108 | 29 | `PORTALS` | 0 | [respawn.titanfall.Portal](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L359) | 100% |
| 108 | 37 | `PORTALS` | 0 | [respawn.titanfall.Portal](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L359) | 100% |
| 109 | 29 | `PORTAL_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 109 | 37 | `PORTAL_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 110 | 29 | `PORTAL_EDGES` | 0 | [id_software.quake.Edge](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L113) | 100% |
| 110 | 37 | `PORTAL_EDGES` | 0 | [id_software.quake.Edge](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L113) | 100% |
| 111 | 29 | `PORTAL_VERTEX_EDGES` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 111 | 37 | `PORTAL_VERTEX_EDGES` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 112 | 29 | `PORTAL_VERTEX_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 112 | 37 | `PORTAL_VERTEX_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 113 | 29 | `PORTAL_EDGE_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 113 | 37 | `PORTAL_EDGE_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 114 | 29 | `PORTAL_EDGE_INTERSECT_AT_EDGE` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 114 | 37 | `PORTAL_EDGE_INTERSECT_EDGE` | 0 | | 0% || 115 | 29 | `PORTAL_EDGE_INTERSECT_AT_VERTEX` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 115 | 37 | `PORTAL_EDGE_INTERSECT_AT_VERTEX` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 116 | 29 | `PORTAL_EDGE_INTERSECT_HEADER` | 0 | [respawn.titanfall.PortalEdgeIntersectHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L374) | 100% |
| 116 | 37 | `PORTAL_EDGE_INTERSECT_HEADER` | 0 | [respawn.titanfall.PortalEdgeIntersectHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L374) | 100% |
| 117 | 29 | `OCCLUSION_MESH_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 117 | 37 | `OCCLUSION_MESH_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 118 | 29 | `OCCLUSION_MESH_INDICES` | 0 | [shared.Shorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L32) | 100% |
| 118 | 37 | `OCCLUSION_MESH_INDICES` | 0 | [shared.Shorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L32) | 100% |
| 119 | 29 | `CELL_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 119 | 37 | `CELL_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 120 | 29 | `OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 120 | 37 | `OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 121 | 29 | `OBJ_REFERENCE_BOUNDS` | 0 | [respawn.titanfall.ObjRefBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L340) | 100% |
| 121 | 37 | `OBJ_REFERENCE_BOUNDS` | 0 | [respawn.titanfall.ObjRefBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L340) | 100% |
| 122 | 37 | `LIGHTMAP_DATA_RTL_PAGE` | 0 | | 0% || 123 | 29 | `LEVEL_INFO` | 0 | | 0% || 123 | 37 | `LEVEL_INFO` | 0 | | 0% || 124 | 29 | `SHADOW_MESH_OPAQUE_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 124 | 37 | `SHADOW_MESH_OPAQUE_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 125 | 29 | `SHADOW_MESH_ALPHA_VERTICES` | 0 | [respawn.titanfall.ShadowMeshAlphaVertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L391) | 100% |
| 125 | 37 | `SHADOW_MESH_ALPHA_VERTICES` | 0 | [respawn.titanfall.ShadowMeshAlphaVertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L391) | 100% |
| 126 | 29 | `SHADOW_MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 126 | 37 | `SHADOW_MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 127 | 29 | `SHADOW_MESH_MESHES` | 0 | [respawn.titanfall.ShadowMesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L381) | 100% |
| 127 | 37 | `SHADOW_MESH_MESHES` | 0 | [respawn.titanfall.ShadowMesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L381) | 100% |


