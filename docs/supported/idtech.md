# IdTechBsp (id Software) Supported Games (v0.3.0)
| Bsp version | Game | Branch script | Lumps supported |
| -- | ---------------------------------------------------------------------------- | ----------------------- | ------: |
| 23 | [Quake](https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm) | `id_software/quake.py`  | 14 / 15 |
| 46 | [Quake III Arena](https://www.mralligator.com/q3)                            | `id_software/quake3.py` | 17 / 17 |

| Lump index | Bsp version | Lump name | LumpClass | % of struct mapped |
| -: | -: | ----------------| ---------------------------------- | ---: |
|  0 | 23 | `ENTITIES`      | `shared.Entities`                  | 100% |
|    | 46 |                 | `shared.Entities`                  | 100% |
|  1 | 23 | `PLANES`        | `id_software.quake.Plane`          | 100% |
|    | 46 | `TEXTURES`      | `id_software.quake3.Texture`       | 100% |
|  2 | 23 | `MIP_TEXTURES`  | `id_software.quake.MipTextureLump` | 100% |
|    | 46 | `PLANES`        | `id_software.quake3.Plane`         | 100% |
|  3 | 23 | `VERTICES`      | `id_software.quake.Vertex`         | 100% |
|    | 46 | `NODES`         | `id_software.quake3.Node`          | 100% |
|  4 | 23 | `VISIBILITY`    | :x:                                |   0% |
|    | 46 | `LEAVES`        | `id_software.quake3.Leaf`          | 100% |
|  5 | 23 | `NODES`         | `id_software.quake.Node`           | 100% |
|    | 46 | `LEAF_FACES`    | `id_software.quake3.LeafFace`      | 100% |
|  6 | 23 | `TEXTURE_INFO`  | `id_software.quake.TextureInfo`    | 100% |
|    | 46 | `LEAF_BRUSHES`  | `id_software.quake3.LeafBrush`     | 100% |
|  7 | 23 | `FACES`         | `id_software.quake.Face`           | 100% |
|    | 46 | `MODELS`        | `id_software.quake3.Model`         | 100% |
|  8 | 23 | `LIGHTMAPS`     | `id_software.quake.Lightmap`       | 100% |
|    | 46 | `BRUSHES`       | `id_software.quake3.Brush`         | 100% |
|  9 | 23 | `CLIP_NODES`    | `id_software.quake.ClipNode`       | 100% |
|    | 46 | `BRUSH_SIDES`   | `id_software.quake3.BrushSide`     | 100% |
| 10 | 23 | `LEAVES`        | `id_software.quake.Leaf`           | 100% |
|    | 46 | `VERTICES`      | `id_software.quake3.Vertex`        | 100% |
| 11 | 23 | `LEAF_FACES`    | `id_software.quake.LeafFace`       | 100% |
|    | 46 | `MESH_VERTICES` | `id_software.quake3.MeshVertex`    | 100% |
| 12 | 23 | `EDGES`         | `id_software.quake.Edge`           | 100% |
|    | 46 | `EFFECTS`       | `id_software.quake3.Effect`        |  90% |
| 13 | 23 | `SURFEDGES`     | `id_software.quake.SurfEdge`       | 100% |
|    | 46 | `FACES`         | `id_software.quake3.Face`          | 100% |
| 14 | 23 | `MODELS`        | `id_software.quake.Model`          | 100% |
|    | 46 | `LIGHTMAPS`     | `id_software.quake3.Lightmap`      | 100% |
| 15 | 46 | `LIGHT_VOLUMES` | `id_software.quake3.LightVolume`   | 100% |
| 16 | 46 | `VISIBILITY`    | `id_software.quake3.Visibility`    |  10% |
