# Changelog

## v0.4.0 (???)

## New

## Changed
 * Moved physics SpecialLumpClasses to `branches/shared/physics.py`
 * Fixed up `GAME_LUMP.sprp` errors across `source`, `left4dead` & `source_2013`
 * Updated both `base.Struct` & `base.MappedArray`
   - `from_tuple` method added (this is used for loading from file)
   - `from_bytes` method added
   - built in asserts to verify accurate definitions (TODO: move to tests)
   - `as_bytes` method added

### Newly Supported
 * Source Engine
   - Tactical Intervention
 * Ubertools

### Updated Support
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
 * Added `D3DBsp`, `IdTechBsp`, `RespawnBsp` & `ValveBsp` classes
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
   - BSP_VERSION, FILE_MAGIC, HEADERS, REVISION -> bsp_version, file_magic, headers, revision

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
