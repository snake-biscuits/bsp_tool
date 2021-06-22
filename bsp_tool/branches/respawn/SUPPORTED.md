# RespawnBsp (Respawn Entertainment) Supported Games (v0.3.0)
| Bsp version | Game | Branch script | Lumps supported |
| -: | --------------------- | ------------------------- | -------: |
| 29 | Titanfall             | `respawn/titanfall.py`    | 21 / 128 |
| 37 | Titanfall 2           | `respawn/titanfall2.py`   | 22 / 128 |
| 47 | Apex Legends          | `respawn/apex_legends.py` | 23 / 128 |

> NOTE: Apex Legends Season 7 uses bsp version 48, Season 8 uses 49
No differences have been found, yet.

> NOTE: The PHYSICS_LEVEL lump seems to always be empty
In Titanfall 1 & 2 this lump has a non-zero version

> All Apex Legends lump versions are the same as the BSP version

| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |
| --: | :--: | -: | --------------------------- | -: | ---------------------------------- | ---: |
|   0 | 0000 | 29 | `ENTITIES`                  |  0 | `shared.Entities`                  | 100% |
|     |      | 37 |                             |  0 | `shared.Entities`                  | 100% |
|     |      | 47 |                             |  0 | `shared.Entities`                  | 100% |
|   1 | 0001 | 29 | `PLANES`                    |  1 | `respawn.titanfall.Plane`          | 100% |
|     |      | 37 |                             |  1 | `respawn.titanfall.Plane`          | 100% |
|     |      | 47 |                             |  0 | `respawn.titanfall.Plane`          | 100% |
|   2 | 0002 | 29 | `TEXTURE_DATA`              |  1 | `respawn.titanfall.TextureData`    |  66% |
|     |      | 37 |                             |  1 | `respawn.titanfall.TextureData`    |  66% |
|     |      | 47 |                             |  0 | `respawn.apex_legends.TextureData` |  11% |
|   3 | 0003 | 29 | `VERTICES`                  |  0 | `respawn.titanfall.Vertex`         | 100% |
|     |      | 37 |                             |  0 | `respawn.titanfall.Vertex`         | 100% |
|     |      | 47 |                             |  0 | `respawn.titanfall.Vertex`         | 100% |
|   4 | 0004 | 29 | `UNUSED_4`                  |  0 | :x:                                |   0% |
|     |      | 37 | `LIGHTPROBE_PARENT_INFOS`   |  0 | :x:                                |   0% |
|     |      | 47 | `LIGHTPROBE_PARENT_INFOS`   |  0 | :x:                                |   0% |
|   5 | 0005 | 29 | `UNUSED_5`                  |  0 | :x:                                |   0% |
|     |      | 37 | `SHADOW_ENVIRONMENTS`       |  0 | :x:                                |   0% |
|     |      | 47 | `SHADOW_ENVIRONMENTS`       |  0 | :x:                                |   0% |
|   6 | 0006 | 29 | `UNUSED_6`                  |  0 | :x:                                |   0% |
|     |      | 37 | `LIGHTPROBE_BSP_NODES`      |  0 | :x:                                |   0% |
|     |      | 47 | `UNUSED_6`                  |  0 | :x:                                |   0% |
|   7 | 0007 | 29 | `UNUSED_7`                  |  0 | :x:                                |   0% |
|     |      | 37 | `LIGHTPROBE_BSP_REF_IDS`    |  0 | :x:                                |   0% |
|     |      | 47 | `UNUSED_7`                  |  0 | :x:                                |   0% |
|  14 | 000E | 29 | `MODELS`                    |  0 | `respawn.titanfall.Model`          | 100% |
|     |      | 37 |                             |  0 | `respawn.titanfall.Model`          | 100% |
|     |      | 47 |                             |  0 | `respawn.apex_legends.Model`       |  10% |
|  15 | 000F | 47 | `SURFACE_NAMES`             |  0 | :x:                                |   0% |
|  16 | 0010 | 47 | `CONTENT_MASKS`             |  0 | :x:                                |   0% |
|  17 | 0011 | 47 | `SURFACE_PROPERTIES`        |  0 | :x:                                |   0% |
|  18 | 0012 | 47 | `BVH_NODES`                 |  0 | :x:                                |   0% |
|  19 | 0013 | 47 | `BVH_LEAF_DATA`             |  0 | :x:                                |   0% |
|  20 | 0014 | 47 | `PACKED_VERTICES`           |  0 | :x:                                |   0% |
|  24 | 0018 | 29 | `ENTITY_PARTITIONS`         |  0 | :x:                                |   0% |
|     |      | 37 |                             |  0 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|  29 | 001D | 29 | `PHYSICS_COLLIDE`           |  0 | :x:                                |   0% |
|     |      | 37 |                             |  0 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|  30 | 001E | 29 | `VERTEX_NORMALS`            |  0 | `respawn.titanfall.Vertex`         | 100% |
|     |      | 37 |                             |  0 | `respawn.titanfall.Vertex`         | 100% |
|     |      | 47 |                             |  0 | `respawn.titanfall.Vertex`         | 100% |
|  35 | 0023 | 29 | `GAME_LUMP`                 |  0 | `lumps.GameLump`                   | ---- |
|     |      | 37 |                             | 13 | `respawn.titanfall.StaticPropv13`  |  50% |
|     |      | 47 |                             | 47 | :x:                                |   0% |
|  36 | 0024 | 29 | `LEAF_WATER_DATA`           |  1 | :x:                                |   0% |
|     |      | 37 |                             |  0 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|  37 |      | 47 | `UNKNOWN_37`                |  0 | :x:                                |   0% |
|  39 |      | 47 | `UNKNOWN_38`                |  0 | :x:                                |   0% |
|  39 |      | 47 | `UNKNOWN_39`                |  0 | :x:                                |   0% |
|  40 | 0028 | 29 | `PAKFILE`                   |  0 | `shared.PakFile`                   | 100% |
|     |      | 37 |                             |  0 | `shared.PakFile`                   | 100% |
|     |      | 47 |                             |  0 | `shared.PakFile`                   | 100% |
|  42 | 002A | 29 | `CUBEMAPS`                  |  0 | `respawn.titanfall.Cubemap`        |  75% |
|     |      | 37 |                             |  0 | `respawn.titanfall.Cubemap`        |  75% |
|     |      | 47 |                             |  0 | `respawn.titanfall.Cubemap`        |  75% |
|  43 | 002B | 29 | `TEXTURE_DATA_STRING_DATA`  |  0 | `shared.TexDataStringData`         | 100% |
|     |      | 37 |                             |  0 | `shared.TexDataStringData`         | 100% |
|     |      | 47 |                             |  0 | `shared.TexDataStringData`         | 100% |
|  44 | 002C | 29 | `TEXTURE_DATA_STRING_TABLE` |  0 | `shared.TextureDataStringTable`    | 100% |
|     |      | 37 |                             |  0 | `shared.TextureDataStringTable`    | 100% |
|     |      | 47 | `UNUSED_44`                 |  0 | :x:                                |   0% |
|  54 | 0036 | 29 | `WORLDLIGHTS`               |  1 | :x:                                |   0% |
|     |      | 37 |                             |  0 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|  55 | 0036 | 29 | `WORLDLIGHTS_PARENT_INFO`   |  0 | :x:                                |   0% |
|     |      | 37 |                             |  0 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|  62 | 003E | 29 | `PHYSICS_LEVEL`             |  6 | :x:                                |   0% |
|     |      | 37 |                             | 16 | :x:                                |   0% |
|     |      | 47 |                             |  0 | :x:                                |   0% |
|     |      |    |                             |    |                                    |      |
| 127 | 007F | 29 | `SHADOW_MESH_MESHES`        |  1 | `respawn.titanfall.ShadowMesh`     |  50% |
