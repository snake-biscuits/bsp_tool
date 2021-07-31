# [ValveBsp](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format) (Valve Software) Supported Games (v0.3.0)
| Bsp version | Game | Branch script | Lumps supported |
| -: | -------------------------------- | --------------------- | ------: |
| 19 | Counter-Strike: Source           | `valve/orange_box.py` | 25 / 64 |
| 20 | Team Fortress 2                  | `valve/orange_box.py` | 25 / 64 |
| 21 | Counter-Strike: Global Offensive | `valve/orange_box.py` | 25 / 64 |

| Lump index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |
| -: | -: | ---------------------------------------- | -: | ------------------------------------- | ---: |
|  0 | 19 | `ENTITIES`                               |  0 | `shared.Entities`                     | 100% |
|  1 | 19 | `PLANES`                                 |  0 | `valve.orange_box.Plane`              | 100% |
|  2 | 19 | `TEXTURE_DATA`                           |  0 | `valve.orange_box.TextureData`        | 100% |
|  3 | 19 | `VERTICES`                               |  0 | `valve.orange_box.Vertex`             | 100% |
|  4 | 19 | `VISIBILITY`                             |  0 | :x:                                   |   0% |
|  5 | 19 | `NODES`                                  |  0 | `valve.orange_box.Node`               | 100% |
|  6 | 19 | `TEXTURE_INFO`                           |  0 | `valve.orange_box.TextureInfo`        | 100% |
|  7 | 19 | `FACES`                                  |  1 | `valve.orange_box.Face`               | 100% |
|  8 | 19 | `LIGHTING`                               |  1 | raw RGBE pixels                       | 100% |
|  9 | 19 | `OCCLUSION`                              |  2 | :x:                                   |   0% |
| 10 | 19 | `LEAVES`                                 |  1 | `valve.orange_box.Leaf`               | 100% |
| 11 | 19 | `FACEIDS`                                |  0 | :x:                                   |   0% |
| 12 | 19 | `EDGES`                                  |  0 | `valve.orange_box.Edge`               | 100% |
| 13 | 19 | `SURFEDGES`                              |  0 | `valve.orange_box.SurfEdge`           | 100% |
| 14 | 19 | `MODELS`                                 |  0 | `valve.orange_box.Model`              | 100% |
| 15 | 19 | `WORLD_LIGHTS`                           |  0 | `valve.orange_box.WorldLight`         | 100% |
| 16 | 19 | `LEAF_FACES`                             |  0 | `valve.orange_box.LeafFace`           | 100% |
| 17 | 19 | `LEAF_BRUSHES`                           |  0 | `valve.orange_box.LeafBrush`          | 100% |
| 18 | 19 | `BRUSHES`                                |  0 | `valve.orange_box.Brush`              | 100% |
| 19 | 19 | `BRUSH_SIDES`                            |  0 | `valve.orange_box.BrushSide`          | 100% |
| 20 | 19 | `AREAS`                                  |  0 | `valve.orange_box.Area`               | 100% |
| 21 | 19 | `AREA_PORTALS`                           |  0 | `valve.orange_box.AreaPortal`         | 100% |
| 22 | 19 | `UNUSED_22`                              |  0 | :x:                                   |   0% |
| 23 | 19 | `UNUSED_23`                              |  0 | :x:                                   |   0% |
| 24 | 19 | `UNUSED_24`                              |  0 | :x:                                   |   0% |
| 25 | 19 | `UNUSED_25`                              |  0 | :x:                                   |   0% |
| 26 | 19 | `DISPLACEMENT_INFO`                      |  0 | `valve.orange_box.DisplacementInfo`   | 100% |
| 27 | 19 | `ORIGINAL_FACES`                         |  0 | `valve.orange_box.Face`               | 100% |
| 28 | 19 | `PHYSICS_DISPLACEMENT`                   |  0 | `orange_box.PhysicsDisplacement`      |  90% |
| 29 | 19 | `PHYSICS_COLLIDE`                        |  0 | `shared.PhysicsCollide`               |  66% |
| 30 | 19 | `VERTEX_NORMALS`                         |  0 | :x:                                   |   0% |
| 31 | 19 | `VERTEX_NORMAL_INDICES`                  |  0 | :x:                                   |   0% |
| 32 | 19 | `DISPLACEMENT_LIGHTMAP_ALPHAS`           |  0 | :x:                                   |   0% |
| 33 | 19 | `DISPLACEMENT_VERTICES`                  |  0 | `valve.orange_box.DisplacementVertex` | 100% |
| 34 | 19 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` |  0 | :x:                                   |   0% |
| 35 | 19 | `GAME_LUMP`                              |  0 | `lumps.GameLump`                      |      |
|    |    | `GAME_LUMP.sprp`                         | 10 | `valve.orange_box.StaticPropv10`      | 100% |
|    |    | `GAME_LUMP.dprp`                         |  0 | :x:                                   |   0% |
| 36 | 19 | `LEAF_WATER_DATA`                        |  0 | :x:                                   |   0% |
| 37 | 19 | `PRIMITIVES`                             |  0 | :x:                                   |   0% |
| 38 | 19 | `PRIMITIVE_VERTICES`                     |  0 | :x:                                   |   0% |
| 39 | 19 | `PRIMITIVE_INDICES`                      |  0 | :x:                                   |   0% |
| 40 | 19 | `PAKFILE`                                |  0 | `shared.PakFile`                      | 100% |
| 41 | 19 | `CLIP_PORTAL_VERTICES`                   |  0 | :x:                                   |   0% |
| 42 | 19 | `CUBEMAPS`                               |  0 | `valve.orange_box.Cubemap`            | 100% |
| 43 | 19 | `TEXTURE_DATA_STRING_DATA`               |  0 | `shared.TextureDataStringData`        | 100% |
| 44 | 19 | `TEXTURE_DATA_STRING_TABLE`              |  0 | `shared.TextureDataStringTable`       | 100% |
| 45 | 19 | `OVERLAYS`                               |  0 | :x:                                   |   0% |
| 46 | 19 | `LEAF_MIN_DIST_TO_WATER`                 |  0 | :x:                                   |   0% |
| 47 | 19 | `FACE_MACRO_TEXTURE_INFO`                |  0 | :x:                                   |   0% |
| 48 | 19 | `DISPLACEMENT_TRIS`                      |  0 | :x:                                   |   0% |
| 49 | 19 | `PHYSICS_COLLIDE_SURFACE`                |  0 | :x:                                   |   0% |
| 50 | 19 | `WATER_OVERLAYS`                         |  0 | :x:                                   |   0% |
| 51 | 19 | `LEAF_AMBIENT_INDEX_HDR`                 |  0 | :x:                                   |   0% |
| 52 | 19 | `LEAF_AMBIENT_INDEX`                     |  0 | :x:                                   |   0% |
| 53 | 19 | `LIGHTING_HDR`                           |  1 | raw RGBE pixels                       | 100% |
| 54 | 19 | `WORLD_LIGHTS_HDR`                       |  0 | `valve.orange_box.WorldLight`         | 100% |
| 55 | 19 | `LEAF_AMBIENT_LIGHTING_HDR`              |  1 | :x:                                   |   0% |
| 56 | 19 | `LEAF_AMBIENT_LIGHTING`                  |  1 | :x:                                   |   0% |
| 57 | 19 | `XZIP_PAKFILE`                           |  0 | :x:                                   |   0% |
| 58 | 19 | `FACES_HDR`                              |  1 | :x:                                   |   0% |
| 59 | 19 | `MAP_FLAGS`                              |  0 | :x:                                   |   0% |
| 60 | 19 | `OVERLAY_FADES`                          |  0 | :x:                                   |   0% |
| 61 | 19 | `UNUSED_61`                              |  0 | :x:                                   |   0% |
| 62 | 19 | `UNUSED_62`                              |  0 | :x:                                   |   0% |
| 63 | 19 | `UNUSED_63`                              |  0 | :x:                                   |   0% |
