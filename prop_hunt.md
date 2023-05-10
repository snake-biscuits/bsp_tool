# Failing SPRP lumps


## Blade Symphony (berimbau)

> 8 / 21 .bsps failed
> `possible_sizeof = 80.0`

| BspClass | branch script                      | version | lump             | lump version |
| -------: | :--------------------------------- | ------: | :--------------- | -----------: |
| ValveBsp | `bsp_tool.branches.valve.sdk_2013` |      21 | `GAME_LUMP.sprp` |           11 |

```python
>>> failing = {"cp_docks", "duel_castle", " duel_monastery", "duel_practice_box",
...            "ffa_community", "free_district", "free_docks", "free_monastery"}
>>> import bsp_tool, os, fnmatch
>>> md = "D:/SteamLibrary/steamapps/common/Blade Symphony/berimbau/maps"
>>> maps = {m[:-4]: bsp_tool.load_bsp(os.path.join(md, m)) for m in fnmatch.filter(os.listdir(md), "*.bsp")}
>>> {b.GAME_LUMP.headers["sprp"].version for b in maps.values()}
{9, 10, 11}
>>> sprp_vers = {v: {m for m, b in maps.items() if b.GAME_LUMP.headers["sprp"].version == v} for v in {9, 10, 11}}
>>> {print(f"{str(k):>2}: {sorted(v)}") for k, v in sprp_vers.items()}
 9: ['cp_parkour', 'cp_sequence', 'cp_terrace', 'cp_test', 'tut_training']
10: ['duel_box', 'duel_district', 'duel_temple', 'duel_winter',
     'free_temple', 'free_winter', 'lightstyle_test', 'practice_box']
11: ['cp_docks', 'duel_castle', 'duel_monastery', 'duel_practice_box',
     'ffa_community', 'free_district', 'free_docks', 'free_monastery']  # all failing maps
```


## Counter-Strike: Global Offensive (csgo)

> 29 / 41 .bsps failed
> `possible_sizeof = 80.0`

| BspClass | branch script                      | version | lump             | lump version |
| -------: | :--------------------------------- | ------: | :--------------- | -----------: |
| ValveBsp | `bsp_tool.branches.valve.sdk_2013` |      21 | `GAME_LUMP.sprp` |           11 |

```python
>>> import bsp_tool, os, fnmatch
>>> md = "D:/SteamLibrary/steamapps/common/.../csgo/maps"
>>> maps = {m[:-4]: bsp_tool.load_bsp(os.path.join(md, m)) for m in fnmatch.filter(os.listdir(md), "*.bsp")}
>>> failing = {"ar_lunacy", "ar_shoots", "cs_italy", "cs_militia", "cs_office",
...            "de_ancient", "de_anubis", "de_bank", "de_boyard", "de_cache",
...            "de_canals", "de_cbble", "de_chalice", "de_dust2", "de_inferno", "de_mirage",
...            "de_nuke", "de_overpass", "de_shortnuke", "de_train", "de_tuscan", "de_vertigo",
...            "dz_blacksite", "dz_ember", "dz_sirocco", "dz_vineyard",
...            "gd_cbble", "lobby_mapveto", "training1"}
```


## Jabroni Brawl: Episode 3

> 54 / 133 .bsps failed
> `possible_sizeof = 80`

| BspClass | branch script                      | version | lump             | lump version |
| -------: | :--------------------------------- | ------: | :--------------- | -----------: |
| ValveBsp | `bsp_tool.branches.valve.sdk_2013` |      21 | `GAME_LUMP.sprp` |           11 |

```python
>>> failing = {"firing_range", "jb_airship", "jb_akina", "jb_arcane", "jb_bloodstained", "jb_cloisters",
...            "jb_coast03", "jb_coast10", "jb_coldscience", "jb_complex", "jb_core", "jb_deathcarts", "jb_deepsea",
...            "jb_depot_fof", "jb_dimensional", "jb_divetest", "jb_estate", "jb_eye_arcturus", "jb_eye_enceladus",
...            "jb_eye_marsarena", "jb_fortbuildv2", "jb_frostbite", "jb_gunman_frontier", "jb_gunman_mayan",
...            "jb_hairball", "jb_hairballer", "jb_hideout", "jb_industries", "jb_infighting", "jb_island17",
...            "jb_killbox", "jb_killhouse", "jb_lich", "jb_lich2", "jb_mars", "jb_mesa_c99", "jb_minigames",
...            "jb_miniroyale", "jb_office", "jb_pipedream", "jb_poolparty", "jb_postalzone_halloween",
...            "jb_railbridge", "jb_sabbath", "jb_sauna", "jb_sky_temple", "jb_ss2_ops", "jb_subway",
...            "jb_survivor", "jb_tallorder", "jb_truss_bridge", "jb_truth", "jb_verticull", "jb_volcanicpanic"}
```

## Source Filmmaker

> 7 / 71 .bsps failed
> `possible_sizeof = 72`

| BspClass | branch script                      | version | lump             | lump version |
| -------: | :--------------------------------- | ------: | :--------------- | -----------: |
| ValveBsp | `bsp_tool.branches.valve.sdk_2013` |      21 | `GAME_LUMP.sprp` |           10 |

```python
>>> failing = {"ctf_foundry", "ctf_gorge", "koth_lakeside_event",
...            "pl_cactuscanyon", "pl_upward", "rd_asteroid", "sd_doomsday_event"}
>>> import bsp_tool, os, fnmatch
>>> md = "D:/SteamLibrary/steamapps/common/SourceFilmmaker/game/tf/maps"
>>> maps = {m[:-4]: bsp_tool.load_bsp(os.path.join(md, m)) for m in fnmatch.filter(os.listdir(md), "*.bsp")}
>>> {b.GAME_LUMP.headers["sprp"].version for b in maps.values()}
{9, 10, 5, 6}
>>> {m for m, b in maps.items() if b.GAME_LUMP.headers["sprp"].version == 10} == failing
True
```
