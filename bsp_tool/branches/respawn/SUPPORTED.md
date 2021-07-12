# RespawnBsp (Respawn Entertainment) Supported Games (v0.3.0)
| Bsp version | Game | Branch script | Lumps supported |
| -: | ---------------------- | ------------------------- | -------: |
| 29 | Titanfall              | `respawn/titanfall.py`    | 32 / 128 |
| 37 | Titanfall 2            | `respawn/titanfall2.py`   | 34 / 128 |
| 47 | Apex Legends           | `respawn/apex_legends.py` | 35 / 128 |
| 48 | Apex Legends: Season 7 | `respawn/apex_legends.py` | 35 / 128 |
| 49 | Apex Legends: Season 8 | `respawn/apex_legends.py` | 35 / 128 |

> No differences in Apex' formats have been found, yet.
For now, assume v47 in the table will also cover v48 & v49

> The PHYSICS_LEVEL lump seems to always be empty
In Titanfall 1 & 2 this lump has a non-zero version

> All Apex Legends GameLump.sprp lump versions are the same as the BSP version

| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |
| --: | :--: | -: | -------------------------------- | -: | --------------------------------------------- | ---: |
|   0 | 0000 | 29 | `ENTITIES`                       |  0 | `shared.Entities`                             | 100% |
|   1 | 0001 | 29 | `PLANES`                         |  1 | `respawn.titanfall.Plane`                     | 100% |
|   2 | 0002 | 29 | `TEXTURE_DATA`                   |  1 | `respawn.titanfall.TextureData`               | 100% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.TextureData`            |  11% |
|   3 | 0003 | 29 | `VERTICES`                       |  0 | `respawn.titanfall.Vertex`                    | 100% |
|   4 | 0004 | 29 | `UNUSED_4`                       |  0 | :x:                                           |   0% |
|     |      | 37 | `LIGHTPROBE_PARENT_INFOS`        |  0 | :x:                                           |   0% |
|   5 | 0005 | 29 | `UNUSED_5`                       |  0 | :x:                                           |   0% |
|     |      | 37 | `SHADOW_ENVIRONMENTS`            |  0 | :x:                                           |   0% |
|   6 | 0006 | 29 | `UNUSED_6`                       |  0 | :x:                                           |   0% |
|     |      | 37 | `LIGHTPROBE_BSP_NODES`           |  0 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_6`                       |  0 | :x:                                           |   0% |
|   7 | 0007 | 29 | `UNUSED_7`                       |  0 | :x:                                           |   0% |
|     |      | 37 | `LIGHTPROBE_BSP_REF_IDS`         |  0 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_7`                       |  0 | :x:                                           |   0% |
|   8 | 0008 | 29 | `UNUSED_8`                       |  0 | :x:                                           |   0% |
|   9 | 0009 | 29 | `UNUSED_9`                       |  0 | :x:                                           |   0% |
|  10 | 000A | 29 | `UNUSED_10`                      |  0 | :x:                                           |   0% |
|  11 | 000B | 29 | `UNUSED_11`                      |  0 | :x:                                           |   0% |
|  12 | 000C | 29 | `UNUSED_12`                      |  0 | :x:                                           |   0% |
|  13 | 000D | 29 | `UNUSED_13`                      |  0 | :x:                                           |   0% |
|  14 | 000E | 29 | `MODELS`                         |  0 | `respawn.titanfall.Model`                     | 100% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.Model`                  |  10% |
|  15 | 000F | 47 | `SURFACE_NAMES`                  |  0 | `shared.TextureDataStringData`                | 100% |
|  16 | 0010 | 47 | `CONTENT_MASKS`                  |  0 | :x:                                           |   0% |
|  17 | 0011 | 47 | `SURFACE_PROPERTIES`             |  0 | :x:                                           |   0% |
|  18 | 0012 | 47 | `BVH_NODES`                      |  0 | :x:                                           |   0% |
|  19 | 0013 | 47 | `BVH_LEAF_DATA`                  |  0 | :x:                                           |   0% |
|  20 | 0014 | 29 | `UNUSED_20`                      |  0 | :x:                                           |   0% |
|  21 | 0015 | 29 | `UNUSED_21`                      |  0 | :x:                                           |   0% |
|  24 | 0018 | 29 | `ENTITY_PARTITIONS`              |  0 | `respawn.titanfall.EntityPartition`           | 100% |
|  25 | 0019 | 29 | `UNUSED_25`                      |  0 | :x:                                           |   0% |
|  26 | 001A | 29 | `UNUSED_26`                      |  0 | :x:                                           |   0% |
|  27 | 001B | 29 | `UNUSED_27`                      |  0 | :x:                                           |   0% |
|  28 | 001C | 29 | `UNUSED_28`                      |  0 | :x:                                           |   0% |
|  29 | 001D | 29 | `PHYSICS_COLLIDE`                |  0 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_29`                      |  0 | :x:                                           |   0% |
|  30 | 001E | 29 | `VERTEX_NORMALS`                 |  0 | `respawn.titanfall.Vertex`                    | 100% |
|  31 | 001F | 29 | `UNUSED_31`                      |  0 | :x:                                           |   0% |
|  32 | 0020 | 29 | `UNUSED_32`                      |  0 | :x:                                           |   0% |
|  33 | 0021 | 29 | `UNUSED_33`                      |  0 | :x:                                           |   0% |
|  34 | 0022 | 29 | `UNUSED_34`                      |  0 | :x:                                           |   0% |
|  35 | 0023 | 29 | `GAME_LUMP`                      |    | `lumps.GameLump`                              | ---- |
|     |      | 29 | `GAME_LUMP.sprp`                 | 12 | `respawn.titanfall.GameLump_SPRP`             | 100% |
|     |      | 29 | `GAME_LUMP.sprp.props`           |    | `respawn.titanfall.StaticPropv12`             |  75% |
|     |      | 37 | `GAME_LUMP.sprp`                 | 13 | `respawn.titanfall2.GameLump_SPRP`            | 100% |
|     |      | 37 | `GAME_LUMP.sprp.props`           |    | `respawn.titanfall2.StaticPropv13`            |  75% |
|     |      | 47 | `GAME_LUMP.sprp`                 | 47 | :x:                                           |   0% |
|     |      | 47 | `GAME_LUMP.sprp.props`           |    | :x:                                           |   0% |
|  36 | 0024 | 29 | `LEAF_WATER_DATA`                |  1 | :x:                                           |   0% |
|     |      | 37 | `UNUSED_36`                      |  0 | :x:                                           |   0% |
|  37 | 0025 | 29 | `UNUSED_37`                      |  0 | :x:                                           |   0% |
|     |      | 47 | `UNKNOWN_37`                     |  0 | :x:                                           |   0% |
|  38 | 0026 | 29 | `UNUSED_38`                      |  0 | :x:                                           |   0% |
|  39 | 0027 | 29 | `UNUSED_39`                      |  0 | :x:                                           |   0% |
|     |      | 47 | `UNKNOWN_39`                     |  0 | :x:                                           |   0% |
|  40 | 0028 | 29 | `PAKFILE`                        |  0 | `shared.PakFile`                              | 100% |
|  41 | 0029 | 47 | `UNUSED_41`                      |  0 | :x:                                           |   0% |
|  42 | 002A | 29 | `CUBEMAPS`                       |  0 | `respawn.titanfall.Cubemap`                   |  75% |
|  43 | 002B | 29 | `TEXTURE_DATA_STRING_DATA`       |  0 | `shared.TextureDataStringData`                | 100% |
|     |      | 47 | `UNUSED_43`                      |  0 | :x:                                           |   0% |
|  44 | 002C | 29 | `TEXTURE_DATA_STRING_TABLE`      |  0 | `shared.TextureDataStringTable`               | 100% |
|     |      | 47 | `UNUSED_44`                      |  0 | :x:                                           |   0% |
|  45 | 002D | 29 | `UNUSED_45`                      |  0 | :x:                                           |   0% |
|  46 | 002E | 29 | `UNUSED_46`                      |  0 | :x:                                           |   0% |
|  47 | 002F | 29 | `UNUSED_47`                      |  0 | :x:                                           |   0% |
|  48 | 0030 | 29 | `UNUSED_48`                      |  0 | :x:                                           |   0% |
|  49 | 0031 | 29 | `UNUSED_49`                      |  0 | :x:                                           |   0% |
|  50 | 0032 | 29 | `UNUSED_50`                      |  0 | :x:                                           |   0% |
|  51 | 0033 | 29 | `UNUSED_51`                      |  0 | :x:                                           |   0% |
|  52 | 0034 | 29 | `UNUSED_52`                      |  0 | :x:                                           |   0% |
|  53 | 0035 | 29 | `UNUSED_53`                      |  0 | :x:                                           |   0% |
|  54 | 0036 | 29 | `WORLDLIGHTS`                    |  1 | :x:                                           |   0% |
|     |      | 37 |                                  |  0 | :x:                                           |   0% |
|  55 | 0037 | 29 | `UNUSED_55`                      |  0 | :x:                                           |   0% |
|     |      | 37 | `WORLDLIGHTS_PARENT_INFO`        |  0 | :x:                                           |   0% |
|  56 | 0038 | 29 | `UNUSED_56`                      |  0 | :x:                                           |   0% |
|  57 | 0039 | 29 | `UNUSED_57`                      |  0 | :x:                                           |   0% |
|  58 | 003A | 29 | `UNUSED_58`                      |  0 | :x:                                           |   0% |
|  59 | 003B | 29 | `UNUSED_59`                      |  0 | :x:                                           |   0% |
|  60 | 003C | 29 | `UNUSED_60`                      |  0 | :x:                                           |   0% |
|  61 | 003D | 29 | `UNUSED_61`                      |  0 | :x:                                           |   0% |
|  62 | 003E | 29 | `PHYSICS_LEVEL`                  |  6 | :x:                                           |   0% |
|     |      | 37 |                                  | 16 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_62`                      |  0 | :x:                                           |   0% |
|  63 | 003F | 29 | `UNUSED_63`                      |  0 | :x:                                           |   0% |
|  64 | 0040 | 29 | `UNUSED_64`                      |  0 | :x:                                           |   0% |
|  65 | 0041 | 29 | `UNUSED_65`                      |  0 | :x:                                           |   0% |
|  66 | 0042 | 29 | `TRICOLL_TRIS`                   |  2 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_66`                      |  0 | :x:                                           |   0% |
|  67 | 0043 | 29 | `UNUSED_67`                      |  0 | :x:                                           |   0% |
|  68 | 0044 | 29 | `TRICOLL_NODES`                  |  1 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_68`                      |  0 | :x:                                           |   0% |
|  69 | 0045 | 29 | `TRICOLL_HEADERS`                |  1 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_69`                      |  0 | :x:                                           |   0% |
|  70 | 0046 | 29 | `PHYSICS_TRIANGLES`              |  0 | :x:                                           |   0% |
|     |      | 37 | `UNUSED_70`                      |  0 | :x:                                           |   0% |
|  71 | 0047 | 29 | `VERTS_UNLIT`                    |  0 | `respawn.titanfall.VertexUnlit`               |  80% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.VertexUnlit`            |  80% |
|  72 | 0048 | 29 | `VERTS_LIT_FLAT`                 |  1 | `respawn.titanfall.VertexLitFlat`             |  45% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.VertexLitFlat`          |  80% |
|  73 | 0049 | 29 | `VERTS_LIT_BUMP`                 |  1 | `respawn.titanfall.VertexLitBump`             |  73% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.VertexLitBump`          |  50% |
|  74 | 004A | 29 | `VERTS_UNLIT_TS`                 |  0 | `respawn.titanfall.VertexUnlitTS`             |  57% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.VertexUnlitTS`          | 100% |
|  75 | 004B | 29 | `VERTS_BLINN_PHONG`              |  0 | `respawn.titanfall.VertexBlinnPhong`          |  50% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.VertexBlinnPhong`       | 100% |
|  76 | 004C | 29 | `VERTS_RESERVED_5`               |  0 | :x:                                           |   0% |
|  77 | 004D | 29 | `VERTS_RESERVED_6`               |  0 | :x:                                           |   0% |
|  78 | 004E | 29 | `VERTS_RESERVED_7`               |  0 | :x:                                           |   0% |
|  79 | 004F | 29 | `MESH_INDICES`                   |  0 | `shared.UnsignedShorts`                       | 100% |
|  80 | 0050 | 29 | `MESHES`                         |  0 | `respawn.titanfall.Mesh`                      |  45% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.Mesh`                   |  80% |
|  81 | 0051 | 29 | `MESH_BOUNDS`                    |  0 | `respawn.apex_legends.MeshBounds`             |  75% |
|  82 | 0052 | 29 | `MATERIAL_SORT`                  |  0 | `respawn.titanfall.MaterialSort`              | 100% |
|     |      | 37 |                                  |  0 | `respawn.titanfall.MaterialSort`              | 100% |
|     |      | 47 |                                  |  0 | `respawn.apex_legends.MaterialSort`           |  50% |
|  83 | 0053 | 29 | `LIGHTMAP_HEADERS`               |  1 | `respawn.titanfall.LightmapHeader`            | 100% |
|  84 | 0054 | 29 | `UNUSED_84`                      |  0 | :x:                                           |   0% |
|  85 | 0055 | 29 | `CM_GRID`                        |  0 | `respawn.titanfall.Grid`                      |  15% |
|  86 | 0056 | 29 | `CM_GRID_CELLS`                  |  0 | `shared.UnsignedInts`                         |  90% |
|     |      | 47 | `UNUSED_86`                      |  0 | :x:                                           |   0% |
|  87 | 0057 | 29 | `CM_GEO_SETS`                    |  0 | :x:                                           |   0% |
|     |      | 47 | `UNUSED_87`                      |  0 | :x:                                           |   0% |
|  88 | 0058 | 29 | `CM_GEO_SET_BOUNDS`              |  0 | `respawn.titanfall.Bounds`                    |  10% |
|     |      | 47 | `UNUSED_88`                      |  0 | :x:                                           |   0% |
|  89 | 0059 | 29 | `CM_PRIMITIVES`                  |  0 | `shared.UnsignedInts`                         | 100% |
|     |      | 47 | `UNUSED_89`                      |  0 | :x:                                           |   0% |
|  90 | 005A | 29 | `CM_PRIMITIVE_BOUNDS`            |  0 | `respawn.titanfall.Bounds`                    |  10% |
|     |      | 47 | `UNUSED_90`                      |  0 | :x:                                           |   0% |
|  91 | 005B | 29 | `CM_UNIQUE_CONTENTS`             |  0 | `shared.UnsignedInts`                         | 100% |
|     |      | 47 | `UNUSED_91`                      |  0 | :x:                                           |   0% |
|  92 | 005C | 29 | `CM_BRUSHES`                     |  0 | `respawn.titanfall.Brush`                     |  88% |
|     |      | 47 | `UNUSED_92`                      |  0 | :x:                                           |  88% |
|  93 | 005D | 29 | `CM_BRUSH_SIDE_PLANE_OFFSETS`    |  0 | `respawn.titanfall.BrushSidePlaneOffsets`     | 100% |
|     |      | 47 | `UNUSED_93`                      |  0 | :x:                                           | 100% |
|  94 | 005E | 29 | `CM_BRUSH_SIDE_PROPS`            |  0 | `shared.UnsignedShorts`                       | 100% |
|     |      | 47 | `UNUSED_94`                      |  0 | :x:                                           |   0% |
|  95 | 005F | 29 | `CM_BRUSH_TEX_VECS`              |  0 | `respawn.titanfall.TextureVector`             | 100% |
|     |      | 47 | `UNUSED_95`                      |  0 | :x:                                           |   0% |
|  96 | 0060 | 29 | `TRICOLL_BEVEL_STARTS`           |  0 | `shared.UnsignedShorts`                       | 100% |
|     |      | 47 | `UNUSED_96`                      |  0 | :x:                                           |   0% |
|  97 | 0061 | 29 | `TRICOLL_BEVEL_INDICES`          |  0 | `shared.UnsignedInts`                         | 100% |
|     |      | 47 | `UNKNOWN_97`                     |  0 | :x:                                           |   0% |
|  98 | 0062 | 29 | `LIGHTMAP_DATA_SKY`              |  0 | 1x RGBA textures per header                   | 100% |
|     |      | 37 |                                  |  0 | 2x RGBA textures per header                   |  90% |
|  99 | 0063 | 29 | `CSM_AABB_NODES`                 |  0 | `respawn.titanfall.Node`                      |  75% |
| 100 | 0064 | 29 | `CSM_OBJ_REFS`                   |  0 | `shared.UnsignedShorts`                       | 100% |
| 101 | 0065 | 29 | `LIGHTPROBES`                    |  0 | :x:                                           |   0% |
| 102 | 0066 | 29 | `STATIC_PROP_LIGHTPROBE_INDEX`   |  0 | :x:                                           |   0% |
| 103 | 0067 | 29 | `LIGHTPROBE_TREE`                |  0 | :x:                                           |   0% |
| 104 | 0068 | 29 | `LIGHTPROBE_REFS`                |  0 | :x:                                           |   0% |
| 105 | 0069 | 29 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` |  0 | 2x RGBA textures per header + 1/4 size?       |  66% |
| 106 | 006A | 29 | `CELL_BSP_NODES`                 |  0 | `respawn.titanfall.Node`                      |  75% |
| 107 | 006B | 29 | `CELLS`                          |  0 | `respawn.titanfall.Cell`                      | 100% |
| 108 | 006C | 29 | `PORTALS`                        |  0 | `respawn.titanfall.Portal`                    |  33% |
| 109 | 006D | 29 | `PORTAL_VERTS`                   |  0 | `respawn.titanfall.Vertex`                    | 100% |
| 110 | 006E | 29 | `PORTAL_EDGES`                   |  0 | `respawn.titanfall.PortalEdge`                |  90% |
| 111 | 006F | 29 | `PORTAL_VERT_EDGES`              |  0 | `respawn.titanfall.PortalEdgeIntersect`       |  10% |
| 112 | 0070 | 29 | `PORTAL_VERT_REFS`               |  0 | `shared.UnsignedShorts`                       | 100% |
| 113 | 0071 | 29 | `PORTAL_EDGE_REFS`               |  0 | `shared.UnsignedShorts`                       | 100% |
| 114 | 0072 | 29 | `PORTAL_EDGE_ISECT_AT_EDGE`      |  0 | `respawn.titanfall.PortalEdgeIntersect`       |  10% |
| 115 | 0073 | 29 | `PORTAL_EDGE_ISECT_AT_VERT`      |  0 | `respawn.titanfall.PortalEdgeIntersect`       |  10% |
| 116 | 0074 | 29 | `PORTAL_EDGE_ISECT_HEADER`       |  0 | `respawn.titanfall.PortalEdgeIntersectHeader` |  90% |
| 117 | 0075 | 29 | `OCCLUSION_MESH_VERTS`           |  0 | `respawn.titanfall.Vertex`                    | 100% |
| 118 | 0076 | 29 | `OCCLUSION_MESH_INDICES`         |  0 | `shared.Shorts`                               | 100% |
| 119 | 0077 | 29 | `CELL_AABB_NODES`                |  0 | `respawn.titanfall.Node`                      |  75% |
| 120 | 0078 | 29 | `OBJ_REFS`                       |  0 | `shared.UnsignedShorts`                       | 100% |
| 121 | 0079 | 29 | `OBJ_REF_BOUNDS`                 |  0 | `respawn.titanfall.ObjRefBounds`              | 100% |
| 122 | 007A | 29 | `UNUSED_122`                     |  0 | :x:                                           |   0% |
|     |      | 37 | `LIGHTMAP_DATA_RTL_PAGE`         |  0 | `respawn.titanfall2.LightmapPage`             |  10% |
| 123 | 007B | 29 | `LEVEL_INFO`                     |  0 | :x:                                           |   0% |
| 124 | 007C | 29 | `SHADOW_MESH_OPAQUE_VERTS`       |  0 | `respawn.titanfall.Vertex`                    | 100% |
| 125 | 007D | 29 | `SHADOW_MESH_ALPHA_VERTS`        |  0 | `respawn.titanfall.ShadowMeshAlphaVertex`     |  60% |
| 126 | 007E | 29 | `SHADOW_MESH_INDICES`            |  0 | `respawn.titanfall.ShadowMeshIndex`           | 100% |
| 127 | 007F | 29 | `SHADOW_MESH_MESHES`             |  1 | `respawn.titanfall.ShadowMesh`                |  50% |
