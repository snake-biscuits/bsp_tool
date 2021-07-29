# [ValveBsp](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format) (Nexon) Supported Games (v0.3.0)
| Bsp version | Game | Branch script | Lumps supported |
| --: | ------------------------ | -------------------- | ------: |
|  20 | Vindictus                | `nexon/vindictus.py` | 25 / 64 |
| 100 | Counter-Strike: Online 2 | `nexon/cso2.py`      |  2 / 64 |


| Lump index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |
| -: | --: | ---------------------------------------- | -: | ------------------------------------- | ---: |
|  0 |  20 | `ENTITIES`                               |  0 | `shared.Entities`                     | 100% |
|  1 |  20 | `PLANES`                                 |  0 | `valve.orange_box.Plane`              | 100% |
|  2 |  20 | `TEXTURE_DATA`                           |  0 | `valve.orange_box.TextureData`        | 100% |
|  3 |  20 | `VERTICES`                               |  0 | `valve.orange_box.Vertex`             | 100% |
|  4 |  20 | `VISIBILITY`                             |  0 | :x:                                   |   0% |
|  5 |  20 | `NODES`                                  |  0 | `nexon.vindictus.Node`                | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.Node`               | 100% |
|  6 |  20 | `TEXTURE_INFO`                           |  0 | `valve.orange_box.TextureInfo`        | 100% |
|  7 |  20 | `FACES`                                  |  1 | `nexon.vindictus.Face`                |  90% |
|    | 100 |                                          |  1 | `valve.orange_box.Face`               | 100% |
|  8 |  20 | `LIGHTING`                               |  1 | raw RGBE pixels                       | 100% |
|  9 |  20 | `OCCLUSION`                              |  2 | :x:                                   |   0% |
| 10 |  20 | `LEAVES`                                 |  1 | `nexon.vindictus.Leaf`                | 100% |
|    | 100 |                                          |  1 | `valve.orange_box.Leaf`               | 100% |
| 11 |  20 | `FACEIDS`                                |  0 | :x:                                   |   0% |
| 12 |  20 | `EDGES`                                  |  0 | `nexon.vindictus.Edge`                | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.Edge`               | 100% |
| 13 |  20 | `SURFEDGES`                              |  0 | `valve.orange_box.SurfEdge`           | 100% |
| 14 |  20 | `MODELS`                                 |  0 | `valve.orange_box.Model`              | 100% |
| 15 |  20 | `WORLD_LIGHTS`                           |  0 | `valve.orange_box.WorldLight`         | 100% |
| 16 |  20 | `LEAF_FACES`                             |  0 | `nexon.vindictus.LeafFace`            | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.LeafFace`           | 100% |
| 17 |  20 | `LEAF_BRUSHES`                           |  0 | `valve.orange_box.LeafBrush`          | 100% |
| 18 |  20 | `BRUSHES`                                |  0 | `valve.orange_box.Brush`              | 100% |
| 19 |  20 | `BRUSH_SIDES`                            |  0 | `nexon.vindictus.BrushSide`           | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.BrushSide`          | 100% |
| 20 |  20 | `AREAS`                                  |  0 | `nexon.vindictus.Area`                | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.Area`               | 100% |
| 21 |  20 | `AREA_PORTALS`                           |  0 | `nexon.vindictus.AreaPortal`          | 100% |
|    | 100 |                                          |  0 | `valve.orange_box.AreaPortal`         | 100% |
| 22 |  20 | `UNUSED_22`                              |  0 | :x:                                   |   0% |
| 23 |  20 | `UNUSED_23`                              |  0 | :x:                                   |   0% |
| 24 |  20 | `UNUSED_24`                              |  0 | :x:                                   |   0% |
| 25 |  20 | `UNUSED_25`                              |  0 | :x:                                   |   0% |
| 26 |  20 | `DISPLACEMENT_INFO`                      |  0 | `nexon.vindictus.DisplacementInfo`    |  90% |
|    | 100 |                                          |  0 | `nexon.cso2.DisplacementInfo`         |  10% |
| 27 |  20 | `ORIGINAL_FACES`                         |  0 | `valve.orange_box.Face`               | 100% |
|    |     |                                          |  0 | `nexon.vindictus.Face`                |  90% |
| 28 |  20 | `PHYSICS_DISPLACEMENT`                   |  0 | `orange_box.PhysicsDisplacement`      |  90% |
| 29 |  20 | `PHYSICS_COLLIDE`                        |  0 | `shared.PhysicsCollide`               |  66% |
| 30 |  20 | `VERTEX_NORMALS`                         |  0 | :x:                                   |   0% |
| 31 |  20 | `VERTEX_NORMAL_INDICES`                  |  0 | :x:                                   |   0% |
| 32 |  20 | `DISPLACEMENT_LIGHTMAP_ALPHAS`           |  0 | :x:                                   |   0% |
| 33 |  20 | `DISPLACEMENT_VERTICES`                  |  0 | `valve.orange_box.DisplacementVertex` | 100% |
| 34 |  20 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` |  0 | :x:                                   |   0% |
| 35 |  20 | `GAME_LUMP`                              |  0 | `lumps.GameLump`                      |      |
|    |     | `GAME_LUMP.sprp`                         | 10 | `valve.orange_box.StaticPropv10`      | 100% |
|    |     | `GAME_LUMP.dprp`                         |  0 | :x:                                   |   0% |
| 36 |  20 | `LEAF_WATER_DATA`                        |  0 | :x:                                   |   0% |
| 37 |  20 | `PRIMITIVES`                             |  0 | :x:                                   |   0% |
| 38 |  20 | `PRIMITIVE_VERTICES`                     |  0 | :x:                                   |   0% |
| 39 |  20 | `PRIMITIVE_INDICES`                      |  0 | :x:                                   |   0% |
| 40 |  20 | `PAKFILE`                                |  0 | `shared.PakFile`                      | 100% |
| 41 |  20 | `CLIP_PORTAL_VERTICES`                   |  0 | :x:                                   |   0% |
| 42 |  20 | `CUBEMAPS`                               |  0 | `valve.orange_box.Cubemap`            | 100% |
| 43 |  20 | `TEXTURE_DATA_STRING_DATA`               |  0 | `shared.TextureDataStringData`        | 100% |
| 44 |  20 | `TEXTURE_DATA_STRING_TABLE`              |  0 | `shared.TextureDataStringTable`       | 100% |
| 45 |  20 | `OVERLAYS`                               |  0 | :x:                                   |   0% |
| 46 |  20 | `LEAF_MIN_DIST_TO_WATER`                 |  0 | :x:                                   |   0% |
| 47 |  20 | `FACE_MACRO_TEXTURE_INFO`                |  0 | :x:                                   |   0% |
| 48 |  20 | `DISPLACEMENT_TRIS`                      |  0 | :x:                                   |   0% |
| 49 |  20 | `PHYSICS_COLLIDE_SURFACE`                |  0 | :x:                                   |   0% |
| 50 |  20 | `WATER_OVERLAYS`                         |  0 | :x:                                   |   0% |
| 51 |  20 | `LEAF_AMBIENT_INDEX_HDR`                 |  0 | :x:                                   |   0% |
| 52 |  20 | `LEAF_AMBIENT_INDEX`                     |  0 | :x:                                   |   0% |
| 53 |  20 | `LIGHTING_HDR`                           |  1 | raw RGBE pixels                       | 100% |
| 54 |  20 | `WORLD_LIGHTS_HDR`                       |  0 | `valve.orange_box.WorldLight`         | 100% |
| 55 |  20 | `LEAF_AMBIENT_LIGHTING_HDR`              |  1 | :x:                                   |   0% |
| 56 |  20 | `LEAF_AMBIENT_LIGHTING`                  |  1 | :x:                                   |   0% |
| 57 |  20 | `XZIP_PAKFILE`                           |  0 | :x:                                   |   0% |
| 58 |  20 | `FACES_HDR`                              |  1 | :x:                                   |   0% |
| 59 |  20 | `MAP_FLAGS`                              |  0 | :x:                                   |   0% |
| 60 |  20 | `OVERLAY_FADES`                          |  0 | :x:                                   |   0% |
| 61 |  20 | `UNUSED_61`                              |  0 | :x:                                   |   0% |
| 62 |  20 | `UNUSED_62`                              |  0 | :x:                                   |   0% |
| 63 |  20 | `UNUSED_63`                              |  0 | :x:                                   |   0% |