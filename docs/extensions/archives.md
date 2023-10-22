## Dependencies
`extensions.archives` requires no dependencies


## The short version
Basic `zipfile.ZipFile`-like interfaces for archive files
Archive files may hold maps or assets used in maps
Interfaces follow a `developer.format` naming pattern

Some `fnmatch`-based utilities have also been mixed in
Querying archive contents is as much a focus as extraction


## Bulk Tools
### `search_folder`
Searches all archives in `path` for files matching `pattern`
### `extract_folder`
Extracts all files matching `pattern` from all archives in `path`

## `base.Archive`
A baseclass for extending the default `ZipFile`-like interface
Provides some helper methods

### `search`
Get filenames in the archive matching a `fnmatch` pattern (e.g. `*.bsp`)

### `extract_match`
Extract all files matching a search pattern
Can extract to a specific path
Defaults to the working directory


## Classes for specific archives
### `bluepoint.Bpk` for `*.bpk`
**NOT ADEQUATELY REVERSED**
Used in Titanfall (Xbox 360)
Contains game/mod filesystems
Have yet to unhash filenames
Tied to Microsoft's proprietary `xcompress`
Cra0's VPKTool version 3.4 can extract some files
Files over a certain filesize come out null-padded


### `gearbox.Nightfire007` for `*.007`
**NOT IMPLEMENTED**
Used in James Bond 007: Nightfire
Contains game/mod filesystems
Can be extracted with [Alura Zoe (ModDB)](https://www.moddb.com/games/james-bond-007-nightfire/downloads/alura-zoe)


### `id_software.Pak` for `*.pak`
**NOT IMPLEMENTED**
Used in Quake, Quake II & Daikatana
Contains game/mod filesystems
CLI extraction tools:
 * [yquake2/pakextract](https://github.com/yquake2/pakextract)
 * [Slartibarty/PAKExtract](https://github.com/Slartibarty/PAKExtract)


### `id_software.Pk3` for `*.pk3`
Used in Quake III (IdTech3) & Call of Duty 1
Contain game/mod filesystems
> NOTE: some `*.pk3` supporting games accept `*.pk3dir` folders; handy for development


### `infinity_ward.FastFile` for `*.ff`
**INCOMPLETE**
Used in Call of Duty 4: Modern Warfare
Might contain maps, but seemingly not in `*.d3dbsp` form


### `infinity_ward.Iwd` for `*.iwd`
Used in Call of Duty 2
Seems functionally identical to `*.pk3`
Contain whole game/mod filesystems (not just maps)

Big stream of zlib compression
Isolating individual files seems very difficult
Per-file headers appear between files, but do not indicate filesize
This massively complicates seeking through and collecting files
Might have to determine filesizes by parsing everything in the archive


### `nexon.Pkg` for `*.pkg`
**NOT IMPLEMENTED**
Used in Counter-Strike: Online 2 & Titanfall: Online
Contains all game files
Encrypted
Tools:
 * [L-Leite/UnCSO2](https://github.com/L-Leite/UnCSO2)
 * [p0358/libuncso2](https://github.com/p0358/libuncso2) (TF:O patch)


### `nexon.Hfs` for `*.hfs`
**NOT IMPLEMENTED**
Used in Vindictus
Contains all game files
Encrypted
Tools:
 * [yretenai/HFSExtract](https://github.com/yretenai/HFSExtract)


### `respawn.Rpak` for `*.rpak`
**NOT IMPLEMENTED**
Used in Titanfall 2 & Apex Legends
Contains various game assets
Contains maps (as of Apex Legends Season 18)
Tools:
 * [r-ex/LegionPlus](https://github.com/r-ex/LegionPlus)
 * [r-ex/RePak](https://github.com/r-ex/RePak)


### `respawn.Vpk` for `*.vpk`
**FILENAMES ONLY**
Used in Titanfall Engine Games
Contains game/mod filesystems
Can append patches
Tools:
 * [harmonytf/HarmonyVPKTool](https://github.com/harmonytf/HarmonyVPKTool)
 * [barnabwhy/TFVPKTool](https://github.com/barnabwhy/TFVPKTool) (HarmonyVPKTool backend)


### `utoplanet.Apk` for `*.apk`
Used in MeruBasu (Maerchen / Fairy-Tale Busters)
Contains all game files
Uncompressed


### `valve.Vpk` for `*.vpk`
**NOT IMPLEMENTED**
Used in post-SteamPipe Source Engine games
Contains maps for BlackMesa, DarkMessiah, Infra & SinEpisodes
Otherwise contain different categories of asset (e.g. `hl2_textures_dir.vpk`)
Can append patches
Tools:
 * [GCFScape](https://nemstools.github.io/pages/GCFScape-Download.html)
 * [ValvePython/vpk](https://github.com/ValvePython/vpk)
