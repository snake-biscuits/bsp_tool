# Changelog

## v0.5.0 (??? 2023)

### New
 * `__init__` methods for all SpecialLumpClasses

### Changed
 * SpecialLumpClasses are now loaded with `from_bytes`, just like every other LumpClass

### Updated Support
 * ... branch name


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
