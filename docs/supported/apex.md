# Supported Apex Legends Games
Developers: Respawn Entertainment

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 47 | Apex Legends | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 48 | Apex Legends: Season 7 - Ascension | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 49 | Apex Legends: Season 8 - Mayhem | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 49 | Apex Legends: Season 11 - Escape [19 Nov Patch] (110) | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 50 | Apex Legends: Season 10 - Emergence | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 65585 | Apex Legends: Season 11 - Escape [19 Nov Patch] (111) | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L17) | 65586 | Apex Legends: Season 11 - Escape [19 Nov Patch] | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 58 / 69 | 59 | 83.33% |


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
| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | --------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 0000 | 47 | `ENTITIES` | 0 | [shared.Entities](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 90% |
| 1 | 0001 | 47 | `PLANES` | 0 | [respawn.titanfall.Plane](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L351) | 100% |
| 2 | 0002 | 47 | `TEXTURE_DATA` | 0 | [respawn.apex_legends.TextureData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L325) | 100% |
| 3 | 0003 | 47 | `VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 4 | 0004 | 47 | `LIGHTPROBE_PARENT_INFOS` | 0 | | 0% || 5 | 0005 | 47 | `SHADOW_ENVIRONMENTS` | 0 | | 0% || 14 | 000E | 47 | `MODELS` | 0 | [respawn.apex_legends.Model](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L296) | 100% |
| 15 | 000F | 47 | `SURFACE_NAMES` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L136) | 90% |
| 16 | 0010 | 47 | `CONTENTS_MASKS` | 0 | | 0% || 17 | 0011 | 47 | `SURFACE_PROPERTIES` | 0 | | 0% || 18 | 0012 | 47 | `BVH_NODES` | 0 | | 0% || 19 | 0013 | 47 | `BVH_LEAF_DATA` | 0 | | 0% || 20 | 0014 | 47 | `PACKED_VERTICES` | 0 | [respawn.apex_legends.PackedVertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L307) | 100% |
| 24 | 0018 | 47 | `ENTITY_PARTITIONS` | 0 | [respawn.titanfall.EntityPartitions](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L511) | 90% |
| 30 | 001E | 47 | `VERTEX_NORMALS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 37 | 0025 | 47 | `UNKNOWN_37` | 0 | | 0% || 38 | 0026 | 47 | `UNKNOWN_38` | 0 | | 0% || 39 | 0027 | 47 | `UNKNOWN_39` | 0 | | 0% || 40 | 0028 | 47 | `PAKFILE` | 0 | [shared.PakFile](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L127) | 90% |
| 42 | 002A | 47 | `CUBEMAPS` | 0 | [respawn.titanfall.Cubemap](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L240) | 100% |
| 43 | 002B | 47 | `UNKNOWN_43` | 0 | | 0% || 54 | 0036 | 47 | `WORLDLIGHTS` | 0 | | 0% || 55 | 0037 | 47 | `WORLDLIGHTS_PARENT_INFO` | 0 | | 0% || 71 | 0047 | 47 | `VERTEX_UNLIT` | 0 | [respawn.apex_legends.VertexUnlit](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L364) | 100% |
| 72 | 0048 | 47 | `VERTEX_LIT_FLAT` | 0 | [respawn.apex_legends.VertexLitFlat](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L355) | 100% |
| 73 | 0049 | 47 | `VERTEX_LIT_BUMP` | 0 | [respawn.apex_legends.VertexLitBump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L343) | 100% |
| 74 | 004A | 47 | `VERTEX_UNLIT_TS` | 0 | [respawn.apex_legends.VertexUnlitTS](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L374) | 100% |
| 75 | 004B | 47 | `VERTEX_BLINN_PHONG` | 0 | [respawn.apex_legends.VertexBlinnPhong](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L337) | 100% |
| 76 | 004C | 47 | `VERTEX_RESERVED_5` | 0 | | 0% || 77 | 004D | 47 | `VERTEX_RESERVED_6` | 0 | | 0% || 78 | 004E | 47 | `VERTEX_RESERVED_7` | 0 | | 0% || 79 | 004F | 47 | `MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 80 | 0050 | 47 | `MESHES` | 0 | [respawn.apex_legends.Mesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L283) | 100% |
| 81 | 0051 | 47 | `MESH_BOUNDS` | 0 | [respawn.titanfall.MeshBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L308) | 100% |
| 82 | 0052 | 47 | `MATERIAL_SORT` | 0 | [respawn.apex_legends.MaterialSort](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L273) | 100% |
| 83 | 0053 | 47 | `LIGHTMAP_HEADERS` | 0 | [respawn.titanfall.LightmapHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L265) | 100% |
| 85 | 0055 | 47 | `CM_GRID` | 0 | | 0% || 97 | 0061 | 47 | `UNKNOWN_97` | 0 | | 0% || 98 | 0062 | 47 | `LIGHTMAP_DATA_SKY` | 0 | | 0% || 99 | 0063 | 47 | `CSM_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 100 | 0064 | 47 | `CSM_OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 101 | 0065 | 47 | `LIGHTPROBES` | 0 | | 0% || 102 | 0066 | 47 | `STATIC_PROP_LIGHTPROBE_INDEX` | 0 | | 0% || 103 | 0067 | 47 | `LIGHTPROBE_TREE` | 0 | | 0% || 104 | 0068 | 47 | `LIGHTPROBE_REFERENCES` | 0 | | 0% || 105 | 0069 | 47 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 | | 0% || 106 | 006A | 47 | `CELL_BSP_NODES` | 0 | | 0% || 107 | 006B | 47 | `CELLS` | 0 | [respawn.titanfall.Cell](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L228) | 100% |
| 108 | 006C | 47 | `PORTALS` | 0 | [respawn.titanfall.Portal](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L359) | 100% |
| 109 | 006D | 47 | `PORTAL_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 110 | 006E | 47 | `PORTAL_EDGES` | 0 | [id_software.quake.Edge](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L113) | 100% |
| 111 | 006F | 47 | `PORTAL_VERTEX_EDGES` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 112 | 0070 | 47 | `PORTAL_VERTEX_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 113 | 0071 | 47 | `PORTAL_EDGE_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 114 | 0072 | 47 | `PORTAL_EDGE_INTERSECT_EDGE` | 0 | | 0% || 115 | 0073 | 47 | `PORTAL_EDGE_INTERSECT_AT_VERTEX` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L367) | 100% |
| 116 | 0074 | 47 | `PORTAL_EDGE_INTERSECT_HEADER` | 0 | [respawn.titanfall.PortalEdgeIntersectHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L374) | 100% |
| 117 | 0075 | 47 | `OCCLUSION_MESH_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 118 | 0076 | 47 | `OCCLUSION_MESH_INDICES` | 0 | [shared.Shorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L32) | 100% |
| 119 | 0077 | 47 | `CELL_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L330) | 100% |
| 120 | 0078 | 47 | `OBJ_REFERENCES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 121 | 0079 | 47 | `OBJ_REFERENCE_BOUNDS` | 0 | [respawn.titanfall.ObjRefBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L340) | 100% |
| 122 | 007A | 47 | `LIGHTMAP_DATA_RTL_PAGE` | 0 | | 0% || 123 | 007B | 47 | `LEVEL_INFO` | 0 | | 0% || 124 | 007C | 47 | `SHADOW_MESH_OPAQUE_VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L227) | 100% |
| 125 | 007D | 47 | `SHADOW_MESH_ALPHA_VERTICES` | 0 | [respawn.titanfall.ShadowMeshAlphaVertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L391) | 100% |
| 126 | 007E | 47 | `SHADOW_MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L44) | 100% |
| 127 | 007F | 47 | `SHADOW_MESH_MESHES` | 0 | [respawn.titanfall.ShadowMesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L381) | 100% |


