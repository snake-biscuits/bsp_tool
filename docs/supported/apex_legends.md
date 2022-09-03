# Apex Legends
## Developers: Respawn Entertainment

| BspClass | Bsp version | Game | Branch script | Supported lumps | Unused lumps | Coverage |
| -------: | ----------: | ---- | ------------- | --------------: | -----------: | :------- |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 47 | Apex Legends | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 48 | Apex Legends: Season 7 - Ascension | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 49 | Apex Legends: Season 8 - Mayhem | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 49 | Apex Legends: Season 11 - Escape [19 Nov Patch] (110) | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 49.1 | Apex Legends: Season 11 - Escape [19 Nov Patch] (111) | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 50 | Apex Legends: Season 10 - Emergence | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 50.1 | Apex Legends: Season 11 - Escape [19 Nov Patch] | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |
| [`RespawnBsp`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/respawn.py#L148) | 51.1 | Apex Legends: Season 13 - Saviors | [`respawn.apex_legends`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py) | 65 / 66 | 62 | 77.95% |


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
 * [Titanfall VPKTool3.4 Portable](https://github.com/Wanty5883/Titanfall2/blob/master/tools/Titanfall_VPKTool3.4_Portable.zip) (GUI only)
   - by `Cra0kalo` (currently Closed Source) **recommended**
 * [TitanfallVPKTool](https://github.com/p0358/TitanfallVPKTool) (GUI & CLI)
   - by `P0358`
 * [RSPNVPK](https://github.com/squidgyberries/RSPNVPK) (CLI only)
   - Fork of `MrSteyk`'s Tool
 * [UnoVPKTool](https://github.com/Unordinal/UnoVPKTool) (CLI only)
   - by `Unordinal`

> NOTE: Apex's `GAME_LUMP` lump version should be the same as the version of the `.bsp` it is in


## Supported Lumps
| Lump index | Hex index | Bsp version | Lump name | Lump version | LumpClass | Coverage |
| ---------: | --------: | ----------: | --------- | -----------: | --------- | :------- |
| 0 | 0000 | 47 | `ENTITIES` | 0 | [`shared.Entities`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L43) | 100% |
| 1 | 0001 | 47 | `PLANES` | 0 | [`respawn.titanfall.Plane`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L544) | 100% |
| 2 | 0002 | 47 | `TEXTURE_DATA` | 0 | [`respawn.apex_legends.TextureData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L327) | 100% |
| 3 | 0003 | 47 | `VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 4 | 0004 | 47 | `LIGHTPROBE_PARENT_INFOS` | 0 |  | 0% |
| 5 | 0005 | 47 | `SHADOW_ENVIRONMENTS` | 0 | [`respawn.titanfall2.ShadowEnvironment`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L258) | 40% |
| 6 | 0006 | 47 | `UNUSED_6` | 0 |  | 0% |
| 7 | 0007 | 47 | `UNUSED_7` | 0 |  | 0% |
| 8 | 0008 | 47 | `UNUSED_8` | 0 |  | 0% |
| 9 | 0009 | 47 | `UNUSED_9` | 0 |  | 0% |
| 10 | 000A | 47 | `UNUSED_10` | 0 |  | 0% |
| 11 | 000B | 47 | `UNUSED_11` | 0 |  | 0% |
| 12 | 000C | 47 | `UNUSED_12` | 0 |  | 0% |
| 13 | 000D | 47 | `UNUSED_13` | 0 |  | 0% |
| 14 | 000E | 47 | `MODELS` | 0 | [`respawn.apex_legends.Model`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L298) | 80% |
| 15 | 000F | 47 | `SURFACE_NAMES` | 0 | [`shared.TextureDataStringData`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L132) | 100% |
| 16 | 0010 | 47 | `CONTENTS_MASKS` | 0 |  | 0% |
| 17 | 0011 | 47 | `SURFACE_PROPERTIES` | 0 |  | 0% |
| 18 | 0012 | 47 | `BVH_NODES` | 0 |  | 0% |
| 19 | 0013 | 47 | `BVH_LEAF_DATA` | 0 |  | 0% |
| 20 | 0014 | 47 | `PACKED_VERTICES` | 0 | [`respawn.apex_legends.PackedVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L309) | 100% |
| 21 | 0015 | 47 | `UNUSED_21` | 0 |  | 0% |
| 22 | 0016 | 47 | `UNUSED_22` | 0 |  | 0% |
| 23 | 0017 | 47 | `UNUSED_23` | 0 |  | 0% |
| 24 | 0018 | 47 | `ENTITY_PARTITIONS` | 0 | [`respawn.titanfall.EntityPartitions`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L706) | 100% |
| 25 | 0019 | 47 | `UNUSED_25` | 0 |  | 0% |
| 26 | 001A | 47 | `UNUSED_26` | 0 |  | 0% |
| 27 | 001B | 47 | `UNUSED_27` | 0 |  | 0% |
| 28 | 001C | 47 | `UNUSED_28` | 0 |  | 0% |
| 29 | 001D | 47 | `UNUSED_29` | 0 |  | 0% |
| 30 | 001E | 47 | `VERTEX_NORMALS` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 31 | 001F | 47 | `UNUSED_31` | 0 |  | 0% |
| 32 | 0020 | 47 | `UNUSED_32` | 0 |  | 0% |
| 33 | 0021 | 47 | `UNUSED_33` | 0 |  | 0% |
| 34 | 0022 | 47 | `UNUSED_34` | 0 |  | 0% |
| 35 | 0023 | 47 | `GAME_LUMP` | - | [`lumps.GameLump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/lumps/__init__.py#L334) | 90% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp` | - | [`respawn.titanfall2.GameLump_SPRP`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L272) | 40% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp.props` | 47 | [`respawn.titanfall2.StaticPropv13`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L311) | 92% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp.props` | 48 | [`respawn.titanfall2.StaticPropv13`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L311) | 92% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp.props` | 49 | [`respawn.titanfall2.StaticPropv13`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L311) | 92% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp.props` | 50 | [`respawn.titanfall2.StaticPropv13`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L311) | 92% |
| 35 | 0023 | 47 | `GAME_LUMP.sprp.props` | 51 | [`respawn.titanfall2.StaticPropv13`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L311) | 92% |
| 36 | 0024 | 47 | `UNUSED_36` | 0 |  | 0% |
| 37 | 0025 | 47 | `UNKNOWN_37` | 0 |  | 0% |
| 38 | 0026 | 47 | `UNKNOWN_38` | 0 |  | 0% |
| 39 | 0027 | 47 | `UNKNOWN_39` | 0 |  | 0% |
| 40 | 0028 | 47 | `PAKFILE` | 0 | [`shared.PakFile`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L121) | 100% |
| 41 | 0029 | 47 | `UNUSED_41` | 0 |  | 0% |
| 42 | 002A | 47 | `CUBEMAPS` | 0 | [`respawn.titanfall.Cubemap`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L417) | 50% |
| 43 | 002B | 47 | `UNKNOWN_43` | 0 |  | 0% |
| 44 | 002C | 47 | `UNUSED_44` | 0 |  | 0% |
| 45 | 002D | 47 | `UNUSED_45` | 0 |  | 0% |
| 46 | 002E | 47 | `UNUSED_46` | 0 |  | 0% |
| 47 | 002F | 47 | `UNUSED_47` | 0 |  | 0% |
| 48 | 0030 | 47 | `UNUSED_48` | 0 |  | 0% |
| 49 | 0031 | 47 | `UNUSED_49` | 0 |  | 0% |
| 50 | 0032 | 47 | `UNUSED_50` | 0 |  | 0% |
| 51 | 0033 | 47 | `UNUSED_51` | 0 |  | 0% |
| 52 | 0034 | 47 | `UNUSED_52` | 0 |  | 0% |
| 53 | 0035 | 47 | `UNUSED_53` | 0 |  | 0% |
| 54 | 0036 | 47 | `WORLD_LIGHTS` | 1 | [`respawn.titanfall.WorldLight`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L636) | 50% |
| 54 | 0036 | 47 | `WORLD_LIGHTS` | 2 | [`respawn.titanfall2.WorldLightv2`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L241) | 50% |
| 54 | 0036 | 47 | `WORLD_LIGHTS` | 3 | [`respawn.titanfall2.WorldLightv3`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L248) | 50% |
| 55 | 0037 | 47 | `WORLD_LIGHT_PARENT_INFOS` | 0 |  | 0% |
| 56 | 0038 | 47 | `UNUSED_56` | 0 |  | 0% |
| 57 | 0039 | 47 | `UNUSED_57` | 0 |  | 0% |
| 58 | 003A | 47 | `UNUSED_58` | 0 |  | 0% |
| 59 | 003B | 47 | `UNUSED_59` | 0 |  | 0% |
| 60 | 003C | 47 | `UNUSED_60` | 0 |  | 0% |
| 61 | 003D | 47 | `UNUSED_61` | 0 |  | 0% |
| 62 | 003E | 47 | `UNUSED_62` | 0 |  | 0% |
| 63 | 003F | 47 | `UNUSED_63` | 0 |  | 0% |
| 64 | 0040 | 47 | `UNUSED_64` | 0 |  | 0% |
| 65 | 0041 | 47 | `UNUSED_65` | 0 |  | 0% |
| 66 | 0042 | 47 | `UNUSED_66` | 0 |  | 0% |
| 67 | 0043 | 47 | `UNUSED_67` | 0 |  | 0% |
| 68 | 0044 | 47 | `UNUSED_68` | 0 |  | 0% |
| 69 | 0045 | 47 | `UNUSED_69` | 0 |  | 0% |
| 70 | 0046 | 47 | `UNUSED_70` | 0 |  | 0% |
| 71 | 0047 | 47 | `VERTEX_UNLIT` | 0 | [`respawn.apex_legends.VertexUnlit`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L366) | 75% |
| 72 | 0048 | 47 | `VERTEX_LIT_FLAT` | 0 | [`respawn.apex_legends.VertexLitFlat`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L357) | 75% |
| 73 | 0049 | 47 | `VERTEX_LIT_BUMP` | 0 | [`respawn.apex_legends.VertexLitBump`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L345) | 100% |
| 74 | 004A | 47 | `VERTEX_UNLIT_TS` | 0 | [`respawn.apex_legends.VertexUnlitTS`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L376) | 75% |
| 75 | 004B | 47 | `VERTEX_BLINN_PHONG` | 0 | [`respawn.apex_legends.VertexBlinnPhong`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L339) | 100% |
| 76 | 004C | 47 | `VERTEX_RESERVED_5` | 0 |  | 0% |
| 77 | 004D | 47 | `VERTEX_RESERVED_6` | 0 |  | 0% |
| 78 | 004E | 47 | `VERTEX_RESERVED_7` | 0 |  | 0% |
| 79 | 004F | 47 | `MESH_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 80 | 0050 | 47 | `MESHES` | 0 | [`respawn.apex_legends.Mesh`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L285) | 80% |
| 81 | 0051 | 47 | `MESH_BOUNDS` | 0 | [`respawn.titanfall.MeshBounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L490) | 75% |
| 82 | 0052 | 47 | `MATERIAL_SORT` | 0 | [`respawn.apex_legends.MaterialSort`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L275) | 75% |
| 83 | 0053 | 47 | `LIGHTMAP_HEADERS` | 0 | [`respawn.titanfall.LightmapHeader`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L448) | 100% |
| 84 | 0054 | 47 | `UNUSED_84` | 0 |  | 0% |
| 85 | 0055 | 47 | `TWEAK_LIGHTS` | 0 |  | 0% |
| 86 | 0056 | 47 | `UNUSED_86` | 0 |  | 0% |
| 87 | 0057 | 47 | `UNUSED_87` | 0 |  | 0% |
| 88 | 0058 | 47 | `UNUSED_88` | 0 |  | 0% |
| 89 | 0059 | 47 | `UNUSED_89` | 0 |  | 0% |
| 90 | 005A | 47 | `UNUSED_90` | 0 |  | 0% |
| 91 | 005B | 47 | `UNUSED_91` | 0 |  | 0% |
| 92 | 005C | 47 | `UNUSED_92` | 0 |  | 0% |
| 93 | 005D | 47 | `UNUSED_93` | 0 |  | 0% |
| 94 | 005E | 47 | `UNUSED_94` | 0 |  | 0% |
| 95 | 005F | 47 | `UNUSED_95` | 0 |  | 0% |
| 96 | 0060 | 47 | `UNUSED_96` | 0 |  | 0% |
| 97 | 0061 | 47 | `UNKNOWN_97` | 0 |  | 0% |
| 98 | 0062 | 47 | `LIGHTMAP_DATA_SKY` | 0 | [`extensions.lightmaps.save_rbsp_r5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L251) | 100% |
| 99 | 0063 | 47 | `CSM_AABB_NODES` | 0 | [`respawn.titanfall.Node`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L522) | 50% |
| 100 | 0064 | 47 | `CSM_OBJ_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 101 | 0065 | 47 | `LIGHTPROBES` | 0 |  | 0% |
| 102 | 0066 | 47 | `STATIC_PROP_LIGHTPROBE_INDICES` | 0 |  | 0% |
| 103 | 0067 | 47 | `LIGHTPROBE_TREE` | 0 |  | 0% |
| 104 | 0068 | 47 | `LIGHTPROBE_REFERENCES` | 0 | [`respawn.titanfall2.LightProbeRef`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall2.py#L232) | 66% |
| 105 | 0069 | 47 | `LIGHTMAP_DATA_REAL_TIME_LIGHTS` | 0 | [`extensions.lightmaps.save_rbsp_r5`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/bsp_tool/extensions/lightmaps.py#L251) | 100% |
| 106 | 006A | 47 | `CELL_BSP_NODES` | 0 | [`respawn.titanfall.CellBSPNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L410) | 0% |
| 107 | 006B | 47 | `CELLS` | 0 | [`respawn.titanfall.Cell`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L383) | 50% |
| 108 | 006C | 47 | `PORTALS` | 0 | [`respawn.titanfall.Portal`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L552) | 50% |
| 109 | 006D | 47 | `PORTAL_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 110 | 006E | 47 | `PORTAL_EDGES` | 0 | [`id_software.quake.Edge`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L149) | 100% |
| 111 | 006F | 47 | `PORTAL_VERTEX_EDGES` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L560) | 0% |
| 112 | 0070 | 47 | `PORTAL_VERTEX_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 113 | 0071 | 47 | `PORTAL_EDGE_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 114 | 0072 | 47 | `PORTAL_EDGE_INTERSECT_AT_EDGE` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L560) | 0% |
| 115 | 0073 | 47 | `PORTAL_EDGE_INTERSECT_AT_VERTEX` | 0 | [`respawn.titanfall.PortalEdgeIntersect`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L560) | 0% |
| 116 | 0074 | 47 | `PORTAL_EDGE_INTERSECT_HEADER` | 0 | [`respawn.titanfall.PortalEdgeIntersectHeader`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L567) | 100% |
| 117 | 0075 | 47 | `OCCLUSION_MESH_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 118 | 0076 | 47 | `OCCLUSION_MESH_INDICES` | 0 | [`shared.Shorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L26) | 100% |
| 119 | 0077 | 47 | `CELL_AABB_NODES` | 0 | [`respawn.titanfall.CellAABBNode`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L394) | 100% |
| 120 | 0078 | 47 | `OBJ_REFERENCES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 121 | 0079 | 47 | `OBJ_REFERENCE_BOUNDS` | 0 | [`respawn.titanfall.ObjRefBounds`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L533) | 100% |
| 122 | 007A | 47 | `LIGHTMAP_DATA_RTL_PAGE` | 0 |  | 0% |
| 123 | 007B | 47 | `LEVEL_INFO` | 0 |  | 0% |
| 124 | 007C | 47 | `SHADOW_MESH_OPAQUE_VERTICES` | 0 | [`id_software.quake.Vertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/id_software/quake.py#L248) | 100% |
| 125 | 007D | 47 | `SHADOW_MESH_ALPHA_VERTICES` | 0 | [`respawn.titanfall.ShadowMeshAlphaVertex`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/titanfall.py#L591) | 75% |
| 126 | 007E | 47 | `SHADOW_MESH_INDICES` | 0 | [`shared.UnsignedShorts`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/shared.py#L38) | 100% |
| 127 | 007F | 47 | `SHADOW_MESHES` | 0 | [`respawn.apex_legends.ShadowMesh`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/respawn/apex_legends.py#L318) | 66% |


