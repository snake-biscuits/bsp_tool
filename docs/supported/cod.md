# Call of Duty
## Developers: Infinity Ward

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`InfinityWardBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/infinity_ward.py#L9) | 4 | Call of Duty 2 | [`infinity_ward.call_of_duty2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py) | 21 / 40 | 0 | 50.60% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 58 | Call of Duty (Demo) Burnville | [`infinity_ward.call_of_duty1_demo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py) | 26 / 31 | 0 | 79.71% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 58 | Call of Duty (Demo) Dawnville | [`infinity_ward.call_of_duty1_demo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py) | 26 / 31 | 0 | 79.71% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 59 | Call of Duty | [`infinity_ward.call_of_duty1`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1.py) | 26 / 31 | 0 | 79.71% |
| [`IdTechBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/id_software.py#L92) | 59 | Call of Duty: United Offensive | [`infinity_ward.call_of_duty1`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1.py) | 26 / 31 | 0 | 79.71% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 4 | `TEXTURES` | [`id_software.quake3.Texture`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L321) | 100% |
| 1 | 4 | `LIGHTMAPS` |  | 0% |
| 1 | 58 | `LIGHTMAPS` | [`infinity_ward.call_of_duty1_demo.Lightmap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L183) | 100% |
| 2 | 4 | `LIGHT_GRID_HASHES` |  | 0% |
| 2 | 58 | `PLANES` | [`id_software.quake3.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L312) | 100% |
| 3 | 4 | `LIGHT_GRID_VALUES` |  | 0% |
| 3 | 58 | `BRUSH_SIDES` | [`infinity_ward.call_of_duty1_demo.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L121) | 100% |
| 4 | 4 | `PLANES` | [`id_software.quake3.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L312) | 100% |
| 4 | 58 | `BRUSHES` | [`infinity_ward.call_of_duty1_demo.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L113) | 100% |
| 5 | 4 | `BRUSH_SIDES` | [`infinity_ward.call_of_duty1_demo.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L121) | 100% |
| 6 | 4 | `BRUSHES` | [`infinity_ward.call_of_duty1_demo.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L113) | 100% |
| 6 | 58 | `TRIANGLE_SOUPS` | [`infinity_ward.call_of_duty1_demo.TriangleSoup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L253) | 100% |
| 7 | 4 | `TRIANGLE_SOUPS` | [`infinity_ward.call_of_duty2.TriangleSoup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L171) | 100% |
| 7 | 58 | `VERTICES` | [`infinity_ward.call_of_duty1_demo.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L264) | 100% |
| 8 | 4 | `VERTICES` | [`infinity_ward.call_of_duty2.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L182) | 83% |
| 8 | 58 | `INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 9 | 4 | `TRIANGLES` | [`infinity_ward.call_of_duty2.Triangle`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L166) | 100% |
| 9 | 58 | `CULL_GROUPS` | [`infinity_ward.call_of_duty1_demo.CullGroup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L145) | 100% |
| 10 | 4 | `CULL_GROUPS` | [`infinity_ward.call_of_duty1_demo.CullGroup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L145) | 100% |
| 10 | 58 | `CULL_GROUP_INDICES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 11 | 4 | `CULL_GROUP_INDICES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 11 | 58 | `PORTAL_VERTICES` |  | 0% |
| 12 | 4 | `SHADOW_VERTICES` |  | 0% |
| 13 | 4 | `SHADOW_INDICES` |  | 0% |
| 13 | 58 | `OCCLUDER_PLANES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 14 | 4 | `SHADOW_CLUSTERS` |  | 0% |
| 14 | 58 | `OCCLUDER_EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L150) | 100% |
| 15 | 4 | `SHADOW_AABB_TREES` |  | 0% |
| 15 | 58 | `OCCLUDER_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 16 | 4 | `SHADOW_SOURCES` |  | 0% |
| 17 | 4 | `PORTAL_VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 17 | 58 | `CELLS` | [`infinity_ward.call_of_duty1_demo.Cell`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L128) | 75% |
| 18 | 4 | `OCCLUDERS` |  | 0% |
| 18 | 58 | `PORTALS` | [`infinity_ward.call_of_duty1_demo.Portal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L244) | 100% |
| 19 | 4 | `OCCLUDER_PLANES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 19 | 58 | `LIGHT_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 20 | 4 | `OCCLUDER_EDGES` | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L150) | 100% |
| 20 | 58 | `NODES` | [`id_software.quake3.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L297) | 100% |
| 21 | 4 | `OCCLUDER_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 21 | 58 | `LEAVES` | [`infinity_ward.call_of_duty1_demo.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L156) | 66% |
| 22 | 4 | `AABB_TREE` |  | 0% |
| 22 | 58 | `LEAF_BRUSHES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 23 | 4 | `CELLS` | [`infinity_ward.call_of_duty1_demo.Cell`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L128) | 75% |
| 23 | 58 | `LEAF_FACES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 24 | 4 | `PORTALS` | [`infinity_ward.call_of_duty1_demo.Portal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L244) | 100% |
| 24 | 58 | `PATCH_COLLISION` | [`infinity_ward.call_of_duty1_demo.PatchCollision`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L231) | 80% |
| 25 | 4 | `NODES` | [`id_software.quake3.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L297) | 100% |
| 25 | 58 | `COLLISION_VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 26 | 4 | `LEAVES` | [`infinity_ward.call_of_duty1_demo.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L156) | 66% |
| 26 | 58 | `COLLISION_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 27 | 4 | `LEAF_BRUSHES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 27 | 58 | `MODELS` | [`infinity_ward.call_of_duty1_demo.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L205) | 100% |
| 28 | 4 | `LEAF_FACES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 28 | 58 | `VISIBILITY` |  | 0% |
| 29 | 4 | `COLLISION_VERTICES` |  | 0% |
| 29 | 58 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 30 | 4 | `COLLISION_EDGES` |  | 0% |
| 30 | 58 | `LIGHTS` | [`infinity_ward.call_of_duty1_demo.Light`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L170) | 50% |
| 31 | 4 | `COLLISION_TRIANGLES` |  | 0% |
| 32 | 4 | `COLLISION_BORDERS` |  | 0% |
| 33 | 4 | `COLLISION_PARTS` |  | 0% |
| 34 | 4 | `COLLISION_AABBS` |  | 0% |
| 35 | 4 | `MODELS` | [`infinity_ward.call_of_duty1_demo.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L205) | 100% |
| 36 | 4 | `VISIBILITY` |  | 0% |
| 37 | 4 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 38 | 4 | `PATHS` |  | 0% |
| 39 | 4 | `LIGHTS` |  | 0% |


