# Dark Messiah SP
## Developers: Arkane Studios

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`ValveBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/valve.py#L17) | 20.4 | Dark Messiah of Might and Magic Single Player | [`arkane.dark_messiah_sp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/arkane/dark_messiah_sp.py) | 37 / 58 | 6 | 63.45% |


[Dark Messiah SP SDK .gcf files](https://www.moddb.com/games/dark-messiah-of-might-magic/downloads/dark-messiah-might-and-magic-sdk)

Difficult to get hammer to run, is a real branch of the Source SDK made by Arkane

Appears it was available on steam for a time in some kind of beta
The SDK's Steam AppID is in `gameinfo.txt`, perhaps the SDK could be downloaded with `steamcmd`?


## SDK Guides
 * [VDC Guide](https://developer.valvesoftware.com/wiki/Dark_Messiah%3A_Single-Player_Level_Creation/SourceSDK)
 * [ModDB Guide](https://www.moddb.com/games/dark-messiah-of-might-magic/downloads/dark-messiah-might-and-magic-sdk)

Both guides are written by [soer4769](https://developer.valvesoftware.com/wiki/User:Soer4769), a VDC contributor who has created many resources helpful to mappers


## Supported Lumps
| Lump index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 20.4 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L46) | 100% |
| 1 | 20.4 | `PLANES` | 0 | [`id_software.quake.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L226) | 100% |
| 2 | 20.4 | `TEXTURE_DATA` | 0 | [`valve.source.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L582) | 100% |
| 3 | 20.4 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 4 | 20.4 | `VISIBILITY` | 0 | [`id_software.quake2.Visibility`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake2.py#L169) | 90% |
| 5 | 20.4 | `NODES` | 0 | [`valve.source.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L530) | 100% |
| 6 | 20.4 | `TEXTURE_INFO` | 0 |  | 0% |
| 7 | 20.4 | `FACES` | 1 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L427) | 100% |
| 8 | 20.4 | `LIGHTING` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 9 | 20.4 | `OCCLUSION` | 0 |  | 0% |
| 10 | 20.4 | `LEAVES` | 0 | [`valve.source.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L460) | 100% |
| 10 | 20.4 | `LEAVES` | 1 | [`valve.orange_box.Leaf`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py#L108) | 100% |
| 11 | 20.4 | `FACE_IDS` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 12 | 20.4 | `EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L144) | 100% |
| 13 | 20.4 | `SURFEDGES` | 0 | [`shared.Ints`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L21) | 100% |
| 14 | 20.4 | `MODELS` | 0 |  | 0% |
| 15 | 20.4 | `WORLD_LIGHTS` | 0 |  | 0% |
| 16 | 20.4 | `LEAF_FACES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 17 | 20.4 | `LEAF_BRUSHES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 18 | 20.4 | `BRUSHES` | 0 | [`valve.source.Brush`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L356) | 100% |
| 19 | 20.4 | `BRUSH_SIDES` | 0 | [`valve.source.BrushSide`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L366) | 100% |
| 20 | 20.4 | `AREAS` | 0 | [`valve.source.Area`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L338) | 100% |
| 21 | 20.4 | `AREA_PORTALS` | 0 | [`valve.source.AreaPortal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L345) | 100% |
| 22 | 20.4 | `UNUSED_22` | 0 |  | 0% |
| 23 | 20.4 | `UNUSED_23` | 0 |  | 0% |
| 24 | 20.4 | `UNUSED_24` | 0 |  | 0% |
| 25 | 20.4 | `UNUSED_25` | 0 |  | 0% |
| 26 | 20.4 | `DISPLACEMENT_INFO` | 0 | [`valve.source.DisplacementInfo`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L385) | 100% |
| 27 | 20.4 | `ORIGINAL_FACES` | 0 | [`valve.source.Face`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L427) | 100% |
| 28 | 20.4 | `PHYSICS_DISPLACEMENT` | 0 |  | 0% |
| 29 | 20.4 | `PHYSICS_COLLIDE` | 0 | [`physics.CollideLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/physics.py#L18) | 90% |
| 30 | 20.4 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 31 | 20.4 | `VERTEX_NORMAL_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 32 | 20.4 | `DISPLACEMENT_LIGHTMAP_ALPHAS` | 0 |  | 0% |
| 33 | 20.4 | `DISPLACEMENT_VERTICES` | 0 | [`valve.source.DisplacementVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L416) | 100% |
| 34 | 20.4 | `DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS` | 0 |  | 0% |
| 35 | 20.4 | `GAME_LUMP` | - | [`lumps.DarkMessiahSPGameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L436) | 90% |
| 35 | 20.4 | `GAME_LUMP.sprp` | - | [`valve.source.GameLump_SPRP`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L678) | 100% |
| 35 | 20.4 | `GAME_LUMP.sprp.props` | 6 |  | 0% |
| 36 | 20.4 | `LEAF_WATER_DATA` | 0 | [`valve.source.LeafWaterData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L507) | 100% |
| 37 | 20.4 | `PRIMITIVES` | 0 | [`valve.source.Primitive`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L572) | 100% |
| 38 | 20.4 | `PRIMITIVE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 39 | 20.4 | `PRIMITIVE_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 40 | 20.4 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L128) | 100% |
| 41 | 20.4 | `CLIP_PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 42 | 20.4 | `CUBEMAPS` | 0 | [`valve.source.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L375) | 100% |
| 43 | 20.4 | `TEXTURE_DATA_STRING_DATA` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L139) | 100% |
| 44 | 20.4 | `TEXTURE_DATA_STRING_TABLE` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L41) | 100% |
| 45 | 20.4 | `OVERLAYS` | 0 |  | 0% |
| 46 | 20.4 | `LEAF_MIN_DIST_TO_WATER` | 0 |  | 0% |
| 47 | 20.4 | `FACE_MACRO_TEXTURE_INFO` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L25) | 100% |
| 48 | 20.4 | `DISPLACEMENT_TRIS` | 0 |  | 0% |
| 49 | 20.4 | `PHYSICS_COLLIDE_SURFACE` | 0 |  | 0% |
| 50 | 20.4 | `WATER_OVERLAYS` | 0 | [`valve.source.WaterOverlay`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L610) | 100% |
| 51 | 20.4 | `LEAF_AMBIENT_INDEX_HDR` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L487) | 100% |
| 52 | 20.4 | `LEAF_AMBIENT_INDEX` | 0 | [`valve.source.LeafAmbientIndex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L487) | 100% |
| 53 | 20.4 | `LIGHTING_HDR` | 0 | [`extensions.lightmaps.save_vbsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/extensions/lightmaps.py#L86) | 100% |
| 54 | 20.4 | `WORLD_LIGHTS_HDR` | 0 |  | 0% |
| 55 | 20.4 | `LEAF_AMBIENT_LIGHTING_HDR` | 0 |  | 0% |
| 56 | 20.4 | `LEAF_AMBIENT_LIGHTING` | 0 |  | 0% |
| 57 | 20.4 | `XZIP_PAKFILE` | 0 |  | 0% |
| 58 | 20.4 | `FACES_HDR` | 0 |  | 0% |
| 59 | 20.4 | `MAP_FLAGS` | 0 |  | 0% |
| 60 | 20.4 | `OVERLAY_FADES` | 0 | [`valve.source.OverlayFade`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/source.py#L566) | 100% |
| 61 | 20.4 | `UNUSED_61` | 0 |  | 0% |
| 62 | 20.4 | `PHYSICS_LEVEL` | 0 |  | 0% |
| 63 | 20.4 | `UNUSED_63` | 0 |  | 0% |


