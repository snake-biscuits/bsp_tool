# RespawnBsp (Respawn Entertainment) Supported Games (v0.3.0)

| Bsp version | Game | Branch script | Supported lumps | Unused lumps |
| ----------: | ---- | ------------- | --------------: | -----------: |
| 29 | Titanfall | `respawn.titanfall` | 56 / 75 | 53 |
| 37 | Titanfall 2 | `respawn.titanfall2` | 56 / 78 | 50 |
| 47 | Apex Legends | `respawn.apex_legends` | 55 / 69 | 59 |

> No differences in Apex' formats have been found, yet.  
> For now, we are assuming the `apex_legends` script covers all seasons  

> bsp_tool.load_bsp() will load all Apex maps, regardless of season  

> All Apex Legends GameLump.sprp lump versions are the same as the BSP version  

| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |
| -: | -: | -: | - | -: | - | -:|
|  0 | 0000 | 29 | `ENTITIES` | 0 | [shared.Entities](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L58) | 100% |
|  1 | 0001 | 29 | `PLANES` | 1 | [respawn.titanfall.Plane](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L332) | 100% |
|  2 | 0002 | 29 | `TEXTURE_DATA` | 1 | [respawn.titanfall.TextureData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L412) | 100% |
|    |      | 47 | `TEXTURE_DATA` | 0 | [respawn.apex_legends.TextureData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L265) | 100% |
|  3 | 0003 | 29 | `VERTICES` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L215) | 100% |
|  4 | 0004 | 37 | `LIGHTPROBE_PARENT_INFOS` | 0 | | 0% |
|  5 | 0005 | 37 | `SHADOW_ENVIRONMENTS` | 0 | | 0% |
|  6 | 0006 | 37 | `LIGHTPROBE_BSP_NODES` | 0 | | 0% |
|  7 | 0007 | 37 | `LIGHTPROBE_BSP_REF_IDS` | 0 | | 0% |
| 14 | 000E | 29 | `MODELS` | 0 | [respawn.titanfall.Model](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L300) | 100% |
|    |      | 47 |          | 0 | [respawn.apex_legends.Model](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L245) | 80% |
| 15 | 000F | 29 | `TEXTURE_DATA_STRING_DATA` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L243) | 100% |
|    |      | 47 | `SURFACE_NAMES` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L243) | 100% |
| 16 | 0010 | 47 | `CONTENT_MASKS` | 0 | | 0% |
| 17 | 0011 | 47 | `SURFACE_PROPERTIES` | 0 | | 0% |
| 18 | 0012 | 47 | `BVH_NODES` | 0 | | 0% |
| 19 | 0013 | 47 | `BVH_LEAF_DATA` | 0 | | 0% |
| 20 | 0014 | 47 | `PACKED_VERTICES` | 0 | | 0% |
| 24 | 0018 | 29 | `ENTITY_PARTITIONS` | 0 | [respawn.titanfall.EntityPartition](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L486) | 100% |
| 29 | 001D | 29 | `PHYSICS_COLLIDE` | 0 | [shared.PhysicsCollide](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L208) | 100% |
| 30 | 001E | 29 | `VERTEX_NORMALS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L215) | 100% |
| 35 | 0023 | -- | `GAME_LUMP`            |    | [lumps.GameLump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps.py#L316)  | ---- |
|    |      | 29 | `GAME_LUMP.sprp`       | 12 | [respawn.titanfall.GameLump_SPRP](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L511)  |  75% |
|    |      |    | `GAME_LUMP.sprp.props` |    | [respawn.titanfall.StaticPropv12](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L396)  |  75% |
|    |      | 37 | `GAME_LUMP.sprp`       | 13 | [respawn.titanfall2.GameLump_SPRP](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L238) | 100% |
|    |      |    | `GAME_LUMP.sprp.props` |    | [respawn.titanfall2.StaticPropv13](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L212) |  75% |
|    |      | 47 | `GAME_LUMP.sprp`       | 47 | [respawn.titanfall2.GameLump_SPRP](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L238) | 100% |
|    |      |    | `GAME_LUMP.sprp.props` |    | [respawn.titanfall2.StaticPropv13](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L212) |  75% |
| 36 | 0024 | 29 | `LEAF_WATER_DATA` | 0 | [respawn.titanfall.LeafWaterData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L241) | 0% |
| 37 | 0025 | 47 | `UNKNOWN_37` | 0 | | 0% |
| 38 | 0026 | 47 | `UNKNOWN_38` | 0 | | 0% |
| 39 | 0027 | 47 | `UNKNOWN_39` | 0 | | 0% |
| 40 | 0028 | 29 | `PAKFILE` | 0 | [shared.PakFile](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L152) | 100% |
| 42 | 002A | 29 | `CUBEMAPS` | 0 | [respawn.titanfall.Cubemap](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L224) | 50% |
| 43 | 002B | 29 | `TEXTURE_DATA_STRING_DATA` | 0 | [shared.TextureDataStringData](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L243) | 100% |
|    |      | 47 | `UNKNOWN_43` | 0 | | 0% |
| 44 | 002C | 29 | `TEXTURE_DATA_STRING_TABLE` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 54 | 0036 | 29 | `WORLDLIGHTS` | 0 | | 0% |
| 55 | 0037 | 37 | `WORLDLIGHTS_PARENT_INFO` | 0 | | 0% |
| 62 | 003E | 29 | `PHYSICS_LEVEL` | 0 | | 0% |
| 66 | 0042 | 29 | `TRICOLL_TRIS` | 0 | | 0% |
| 68 | 0044 | 29 | `TRICOLL_NODES` | 0 | | 0% |
| 69 | 0045 | 29 | `TRICOLL_HEADERS` | 0 | | 0% |
| 70 | 0046 | 29 | `PHYSICS_TRIANGLES` | 0 | | 0% |
| 71 | 0047 | 29 | `VERTEX_UNLIT`       | 0 | [respawn.titanfall.VertexUnlit](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L462) | 75% |
|    |      | 47 |                      | 0 | [respawn.apex_legends.VertexUnlit](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L293) | 75% |
| 72 | 0048 | 29 | `VERTEX_LIT_FLAT`    | 1 | [respawn.titanfall.VertexLitFlat](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L452) | 75% |
|    |      | 47 |                      | 0 | [respawn.apex_legends.VertexLitFlat](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L287) | 75% |
| 73 | 0049 | 29 | `VERTEX_LIT_BUMP`    | 1 | [respawn.titanfall.VertexLitBump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L440) | 83% |
|    |      | 47 |                      | 0 | [respawn.apex_legends.VertexLitBump](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L281) | 80% |
| 74 | 004A | 29 | `VERTEX_UNLIT_TS`    | 0 | [respawn.titanfall.VertexUnlitTS](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L472) | 75% |
|    |      | 47 |                      | 0 | [respawn.apex_legends.VertexUnlitTS](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L299) | 100% |
| 75 | 004B | 29 | `VERTEX_BLINN_PHONG` | 0 | [respawn.titanfall.VertexBlinnPhong](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L434) | 66% |
|    |      | 47 |                      | 0 | [respawn.apex_legends.VertexBlinnPhong](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L275) | 100% |
| 79 | 004F | 29 | `MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 80 | 0050 | 29 | `MESHES` | 0 | [respawn.titanfall.Mesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L275) | 80% |
|    |      | 47 |          | 0 | [respawn.apex_legends.Mesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L237) | 80% |
| 81 | 0051 | 29 | `MESH_BOUNDS` | 0 | [respawn.titanfall.MeshBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L289) | 100% |
| 82 | 0052 | 29 | `MATERIAL_SORT` | 0 | [respawn.titanfall.MaterialSort](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L266) | 100% |
|    |      | 47 |                 | 0 | [respawn.apex_legends.MaterialSort](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L227) | 75% |
| 83 | 0053 | 29 | `LIGHTMAP_HEADERS` | 1 | [respawn.titanfall.LightmapHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L249) | 100% |
| 85 | 0055 | 29 | `CM_GRID` | 0 | [respawn.titanfall.Grid](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L233) | 50% |
|    | 0055 | 47 |           | 0 | | 0% |
| 86 | 0056 | 29 | `CM_GRID_CELLS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
| 87 | 0057 | 29 | `CM_GEO_SETS` | 0 | | 0% |
| 88 | 0058 | 29 | `CM_GEO_SET_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L198) | 0% |
| 89 | 0059 | 29 | `CM_PRIMITIVES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
| 90 | 005A | 29 | `CM_PRIMITIVE_BOUNDS` | 0 | [respawn.titanfall.Bounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L198) | 0% |
| 91 | 005B | 29 | `CM_UNIQUE_CONTENTS` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
| 92 | 005C | 29 | `CM_BRUSHES` | 0 | [respawn.titanfall.Brush](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L205) | 75% |
| 93 | 005D | 29 | `CM_BRUSH_SIDE_PLANE_OFFSETS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 94 | 005E | 29 | `CM_BRUSH_SIDE_PROPS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 95 | 005F | 29 | `CM_BRUSH_TEX_VECS` | 0 | | 0% |
| 96 | 0060 | 29 | `TRICOLL_BEVEL_STARTS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 97 | 0061 | 29 | `TRICOLL_BEVEL_INDICES` | 0 | [shared.UnsignedInts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L49) | 100% |
|    |      | 47 | `UNKNOWN_97` | 0 | | 0% |
| 98 | 0062 | 29 | `LIGHTMAP_DATA_SKY` | 0 | | 0% |
| 99 | 0063 | 29 | `CSM_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L311) | 50% |
| 100 | 0064 | 29 | `CSM_OBJ_REFS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 101 | 0065 | 29 | `LIGHTPROBES` | 0 | | 0% |
| 102 | 0066 | 29 | `STATIC_PROP_LIGHTPROBE_INDEX` | 0 | | 0% |
| 103 | 0067 | 29 | `LIGHTPROBE_TREE` | 0 | | 0% |
| 104 | 0068 | 29 | `LIGHTPROBE_REFS` | 0 | [respawn.titanfall.LightProbeRef](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L258) | 100% |
|     |      | 37 |                   | 0 | | 0% |
| 105 | 0069 | 29 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 | | 0% |
| 106 | 006A | 29 | `CELL_BSP_NODES` | 0 | | 0% |
| 107 | 006B | 29 | `CELLS` | 0 | [respawn.titanfall.Cell](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L215) | 100% |
| 108 | 006C | 29 | `PORTALS` | 0 | [respawn.titanfall.Portal](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L340) | 50% |
| 109 | 006D | 29 | `PORTAL_VERTS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L215) | 100% |
| 110 | 006E | 29 | `PORTAL_EDGES` | 0 | [respawn.titanfall.PortalEdge](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L348) | 100% |
| 111 | 006F | 29 | `PORTAL_VERT_EDGES` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L352) | 0% |
| 112 | 0070 | 29 | `PORTAL_VERT_REFS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 113 | 0071 | 29 | `PORTAL_EDGE_REFS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 114 | 0072 | 29 | `PORTAL_EDGE_ISECT_AT_EDGE` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L352) | 0% |
|     |      | 37 | `PORTAL_EDGE_ISECT_EDGE` | 0 | | 0% |
| 115 | 0073 | 29 | `PORTAL_EDGE_ISECT_AT_VERT` | 0 | [respawn.titanfall.PortalEdgeIntersect](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L352) | 0% |
| 116 | 0074 | 29 | `PORTAL_EDGE_ISECT_HEADER` | 0 | [respawn.titanfall.PortalEdgeIntersectHeader](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L359) | 100% |
| 117 | 0075 | 29 | `OCCLUSION_MESH_VERTS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L215) | 100% |
| 118 | 0076 | 29 | `OCCLUSION_MESH_INDICES` | 0 | [shared.Shorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L45) | 100% |
| 119 | 0077 | 29 | `CELL_AABB_NODES` | 0 | [respawn.titanfall.Node](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L311) | 50% |
| 120 | 0078 | 29 | `OBJ_REFS` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 121 | 0079 | 29 | `OBJ_REF_BOUNDS` | 0 | [respawn.titanfall.ObjRefBounds](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L321) | 100% |
| 122 | 007A | 37 | `LIGHTMAP_DATA_RTL_PAGE` | 0 | | 0% |
| 123 | 007B | 29 | `LEVEL_INFO` | 0 | | 0% |
| 124 | 007C | 29 | `SHADOW_MESH_OPAQUE_VERTS` | 0 | [id_software.quake.Vertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L215) | 100% |
| 125 | 007D | 29 | `SHADOW_MESH_ALPHA_VERTS` | 0 | [respawn.titanfall.ShadowMeshAlphaVertex](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L376) | 50% |
| 126 | 007E | 29 | `SHADOW_MESH_INDICES` | 0 | [shared.UnsignedShorts](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L53) | 100% |
| 127 | 007F | 29 | `SHADOW_MESH_MESHES` | 0 | [respawn.titanfall.ShadowMesh](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L366) | 66% |
