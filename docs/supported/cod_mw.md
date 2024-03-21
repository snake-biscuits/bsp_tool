# Call of Duty: Modern Warfare
## Developers: Infinity Ward

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`D3DBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/infinity_ward.py#L35) | 22 | Call of Duty 4: Modern Warfare | [`infinity_ward.modern_warfare`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py) | 27 / 41 | 0 | 50.56% |


## Supported Lumps
| Lump index | Bsp version | Lump name | LumpClass | Coverage |
| ---------: | ----------: | --------- | --------- | :------- |
| 0 | 22 | `TEXTURES` | [`id_software.quake3.Texture`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L321) | 100% |
| 1 | 22 | `LIGHTMAPS` | [`extensions.lightmaps.extract`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps/modern_warfare.py#L6) | 100% |
| 2 | 22 | `LIGHT_GRID_POINTS` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 3 | 22 | `LIGHT_GRID_COLOURS` |  | 0% |
| 4 | 22 | `PLANES` | [`id_software.quake3.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake3.py#L312) | 100% |
| 5 | 22 | `BRUSH_SIDES` | [`infinity_ward.call_of_duty1_demo.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L121) | 100% |
| 6 | 22 | `UNKNOWN_6` |  | 0% |
| 7 | 22 | `UNKNOWN_7` |  | 0% |
| 8 | 22 | `BRUSHES` | [`infinity_ward.call_of_duty1_demo.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty1_demo.py#L113) | 100% |
| 9 | 22 | `LAYERED_TRIANGLE_SOUPS` | [`infinity_ward.modern_warfare.TriangleSoup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L205) | 80% |
| 10 | 22 | `LAYERED_VERTICES` | [`infinity_ward.call_of_duty2.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L182) | 83% |
| 11 | 22 | `LAYERED_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 19 | 22 | `PORTAL_VERTICES` |  | 0% |
| 24 | 22 | `LAYERED_AABB_TREE` | [`infinity_ward.modern_warfare.AABBTree`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L119) | 33% |
| 25 | 22 | `CELLS` | [`infinity_ward.modern_warfare.Cell`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L127) | 66% |
| 26 | 22 | `PORTALS` |  | 0% |
| 27 | 22 | `NODES` | [`infinity_ward.modern_warfare.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L198) | 0% |
| 28 | 22 | `LEAVES` | [`infinity_ward.modern_warfare.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L165) | 0% |
| 29 | 22 | `LEAF_BRUSHES` | [`shared.UnsignedInts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L23) | 100% |
| 30 | 22 | `LEAF_FACES` |  | 0% |
| 31 | 22 | `COLLISION_VERTICES` | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L261) | 100% |
| 32 | 22 | `COLLISION_TRIANGLES` | [`infinity_ward.call_of_duty2.Triangle`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L166) | 100% |
| 33 | 22 | `COLLISION_EDGE_WALK` |  | 0% |
| 34 | 22 | `COLLISION_BORDERS` | [`infinity_ward.modern_warfare.CollisionBorder`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L149) | 0% |
| 35 | 22 | `COLLISION_PARTS` | [`infinity_ward.modern_warfare.CollisionPart`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L155) | 80% |
| 36 | 22 | `COLLISION_AABBS` | [`infinity_ward.modern_warfare.CollisionAABB`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L137) | 50% |
| 37 | 22 | `MODELS` | [`infinity_ward.modern_warfare.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L172) | 85% |
| 39 | 22 | `ENTITIES` | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L36) | 100% |
| 40 | 22 | `PATHS` |  | 0% |
| 41 | 22 | `REFLECTION_PROBES` |  | 0% |
| 42 | 22 | `LAYERED_DATA` |  | 0% |
| 43 | 22 | `PRIMARY_LIGHTS` |  | 0% |
| 44 | 22 | `LIGHT_GRID_HEADER` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 45 | 22 | `LIGHT_GRID_ROWS` |  | 0% |
| 47 | 22 | `SIMPLE_TRIANGLE_SOUPS` | [`infinity_ward.modern_warfare.TriangleSoup`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L205) | 80% |
| 48 | 22 | `SIMPLE_VERTICES` | [`infinity_ward.call_of_duty2.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/call_of_duty2.py#L182) | 83% |
| 49 | 22 | `SIMPLE_INDICES` | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L31) | 100% |
| 51 | 22 | `SIMPLE_AABB_TREE` | [`infinity_ward.modern_warfare.AABBTree`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/infinity_ward/modern_warfare.py#L119) | 33% |
| 52 | 22 | `LIGHT_REGIONS` | [`shared.UnsignedBytes`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L19) | 100% |
| 53 | 22 | `LIGHT_REGION_HULLS` |  | 0% |
| 54 | 22 | `LIGHT_REGION_AXES` |  | 0% |


