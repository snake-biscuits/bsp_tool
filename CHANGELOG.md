# Changelog

## v0.6.0 (15 May 2024)

### New
 * `archives`
   - `cdrom.Iso`
   - `ion_storm.Dat`
   - `ion_storm.Pak`
   - `nexon.PakFile` (formerly `branches.nexon.pakfile.PakFile`)
   - `pkware.Zip` (formerly `branches.valve.source.PakFile`)
   - `ritual.Sin`
   - `sega.GDRom`
   - `troika.Vpk`
 * `ArchiveClass` filesystem utility methods
   - `.is_dir("folder")`
   - `.is_file("filename")`
   - `.list_dir("folder")`
   - `.path_exists("filename")`
   - `.tree(folder="./")`
 * `DiscClass` spec for disc images which *may* contain filesystems
   - `alcohol.Mds`
   - `golden_hawk.Cue`
   - `mame.Chd`
   - `padus.Cdi`
   - `sega.Gdi`
 * added `physics.AABB.as_model()`


### Changed
 * **Moved `branches.base` to `core`**
 * Moved `archives` out of `extensions`
 * Moved `lightmaps` out of `extensions`
 * Moved `extensions.geometry` to `scene`
   - accessed via `developer.format` (e.g. `scene.pixar.Usd`)
   - exposing all `SceneDescriptions` at top level (e.g. `scene.Obj`)
 * `ArchiveClass`es are now initialised with `@classmethod`s
   - `.from_archive("filename", archive)`
   - `.from_bytes(b"bytes")`
   - `.from_file("filename")`
   - `.from_stream(open(stream))`
 * `BspClass`es are now initialised with `@classmethod`s
   - `.from_archive(branch, "filepath", archive)`
   - `.from_bytes(branch, "filepath", b"bytes")`
   - `.from_file(branch, "filepath")`
   - `.from_stream(branch, "filepath", open(stream))`


## v0.5.0 (1 August 2024)

### New
 * `__init__` methods for all SpecialLumpClasses
 * `branches.colour`
 * `branches.ieee754`
   - `Float32` `BitField` reversing helper
 * `extensions.editor`
   - parse `.map` & `.vmf`
   - compare uncompiled maps to `.bsp`
 * `utils`
   - `binary`
   - `editor`
   - `geometry`
   - `physics`
   - `texture`
 * `NexonBsp`
   - thanks `cso2` big-endian `fourCC`
 * `BSPX` lumps can be parsed with `bspx.BspX`

### Changed
 * `SpecialLumpClasses` & `GameLumpClasses`
   - new basic `__init__` for making your own from scratch
   - loaded from files with `from_bytes`
 * `RawBspLump`
   - added `append`, `extend` & `insert` methods
   - slices are now `bytearray`s
 * `BspLump`
   - new barebones `__init__`
   - maps bsp lumps with `from_header`
   - pulled out of streams with `from_count`
   - `BspLump.find(attr=val)` method is now `.search()`
   - removed `.find()` method from `BasicBspLump`
   - allowed implicit changes (e.g. `bsp.VERTICES[0].z += 1`)
   - `__iter__` doesn't update `_changes`, reducing unnessecary caching
   - TODO: `bsp.LUMP[::]` creates a copy & doesn't affect / share `_changes`
 * `archives`
   - `base.Archive` class to provide common methods
   - One script per developer
   - Placeholders for not-yet-supported archives
 * `extensions.compiler_signature`
   - `RespawnBsp` [MRVN-Radiant](https://github.com/MRVN-Radiant/MRVN-Radiant) signature
     + saved by `.save_as`
     + parser in `extensions.compiler_signature`
 * RespawnBsp `.save_as()` can now skip `.bsp_lump`
 * `respawn.ExternalLumpManager` now handles `.bsp_lump` saving
 * Moved `methods` from a `list` to a `dict`
   - Overriding methods from parents is easier
 * Moved `valve_physics` to `valve.physics`
 * Moved `branches.vector` to `utils.vector`

### Fixed
 * `shared.Entities` no longer breaks on:
   - curly braces inside key values
   - multi-line keys
 * `pkware.Zip` can be edited
   - `.as_bytes()` correctly includes "end record", without calling `.close()`

### Newly Supported Branches
 * Genesis3D
 * Id Tech 2
   - Qbism
   - Quake 64
 * IW Engine
   - Call of Duty 1 SP Demo: Burnville
   - Call of Duty 1 SP Demo: Dawnville
 * Source Engine
   - Fairy Tale Busters (メルヘソバスターズ)
   - Zeno Clash
 * Titanfall Engine
   - Apex Legends Season 13-18
   - Apex Legends Season 18+
 * Ubertools
   - Star Trek Elite Force II SP Demo

### Updated Support
 * Quake
 * Source Engine
   - Static prop parsing is deferred w/ `BspLump.from_count`
   - Breaking out into more branches to handle static prop variants
 * Titanfall Engine
   - Split Apex Legends into multiple branch scripts


## v0.4.0 (28 March 2023)

### New
 * Added support for Ritual Entertainment's Ubertools (Quake III Engine Branch)
 * If `autoload` cannot find the specified `.bsp` file a UserWarning is issued
 * Support for `ValveBsp` & `RespawnBsp` Xbox360 formats (`.360.bsp`)

### Changed
 * Moved physics SpecialLumpClasses to `branches/shared/physics.py`
 * Fixed up `GAME_LUMP.sprp` errors across `source`, `left4dead` & `source_2013`
 * Updated both `base.Struct` & `base.MappedArray`
   - built in asserts to verify accurate definitions
   - rebuilt `__init__` method, can now generate blank
   - added `_bitfields` attr, defines child `base.BitFields`
   - added `_classes` attr, overrides class of named attr
   - added `as_bytes` method
   - added `as_cpp` method
   - added `from_bytes` method
   - added `from_stream` method
   - added `from_tuple` method (replaces old `__init__` behaviour)
 * Added `base.BitField` for more reliable bitfield mapping
   - behaves similarly to `base.MappedArray`
 * Completely refactored `branch_script` detection
   - only `file_magic` & `bsp_version` matter (unless `.d3dbsp`)
   - `load_bsp` now only accepts a `branch_script` as it's optional argument
 * RespawnBsp `.ent` file headers moved to `RespawnBsp.entity_headers`
 * RespawnBsp `.bsp_lump` moved to `bsp.external`
   - Uses the `respawn.ExternalLumpManager`
   - `.bsp_lump` are only opened when accesed via `bsp.external.LUMP_NAME`
 * "MegaTest" RAM usage significantly reduced
 * `ArkaneBsp` has been rolled into `ValveBsp`
 * `LumpHeader` now use `bsp.branch.LumpHeader` instead of `collections.namedtuple`
 * Support for `ValveBsp` & `RespawnBsp` x360 (big-endian) formats
 * Caught some unexpected behaviour with `GAME_LUMP_CLASS` dict deepcopies

### Newly Supported Branches
 * Infinity Ward Engine
   - Call of Duty 2
   - Call of Duty 4: Modern Warfare
 * Ion Storm IdTech
   - Daikatana
 * Respawn Engine
   - Titanfall (Xbox360)
 * Source Engine
   - Half-Life 2 (Xbox)
   - Infra
   - Momentum Mod
   - Orange Box (Xbox360)
   - Portal 2 (Xbox360)
   - Tactical Intervention
   - Vampire the Masquerade: Bloodlines
 * Ubertools

### Updated Support
 * Id Tech 3
   - Quake III Arena
   - Raven Software Titles
 * Infinity Ward Engine
   - Call of Duty
 * Quake Engine
   - Hexen II
 * Source Engine
 * Titanfall Engine


## v0.3.1 (4th October 2021)

### New
 * Identified & thwarted Half-Life: Blue Shift obfuscation

### Changed
 * Fixed `.as_bytes()` method for `shared.PhysicsCollide`
   - byte perfect recreation of input
 * Re-implemented `PhysicsCollide` for Source & Titanfall Engines

### Newly Supported
  * Half-Life: Blue Shift

### Updated Support
 * Source Engine
 * Titanfall Engine


## v0.3.0 (29th September 2021)

### New
 * Added `load_bsp` function to identify bsp type
 * Added `InfinityWardBsp`, `IdTechBsp`, `RespawnBsp` & `ValveBsp` classes
 * Added general support for the PakFile lump
 * Added general support for the GameLump lump
 * Extension scripts
   - `archive.py` extractor for CoD `.iwd` / Quake `.pk3`
   - `diff.py` compare bsps for changelogs / study
   - `lightmaps.py` bsp lightmap -> `.png`
 * Made a basic C++ 17 implementation in `src/`

### Changed
 * `Bsp` lumps are loaded dynamically, reducing memory usage
   - New wrapper classes can be found in `bsp_tool/lumps.py`
 * `mods/` changed to `branches/`
   - Added subfolders for developers
   - Helpful lists for auto-detecting a .bsp's origin
   - Renamed `team_fortress2` to `valve/orange_box`
 * `LumpClasses` now end up in 3 dictionaries per branch script
   - `BASIC_LUMP_CLASSES` for types like `short int`
   - `LUMP_CLASSES` for standard `LumpClasses`
   - `SPECIAL_LUMP_CLASSES` for irregular types (e.g. PakFile)
   - `GAME_LUMP_CLASSES` for GameLump SpecialLumpClasses
 * `Bsp`s no longer print to console once loaded
 * `Base.Bsp` & subclasses have reserved ALL CAPS member names for lumps only
   - `BSP_VERSION, FILE_MAGIC, HEADERS, REVISION` -> `bsp_version, file_magic, headers, revision`

### Newly Supported
  * IdTech Engine
    - Quake II
    - Quake 3 Arena
  * GoldSrc Engine
  * Source Engine
    - 2013 SDK
    - Alien Swarm branch
    - Counter-Strike: Global Offensive
    - Half-Life 2
    - Left 4 Dead branch

### Broken Support
  * GoldSrc Engine
    - Half-Life: Blue Shift
  * IdTech Engine
    - Quake
  * IW Engine
    - Call of Duty
  * Source Engine
    - Dark Messiah of Might and Magic
    - Vindictus

### Updated Support
 * Source Engine
   - Orange Box
 * Titanfall Engine
   - Titanfall
   - Titanfall 2
   - Apex Legends
