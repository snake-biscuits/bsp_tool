# Changelog

# v0.3.0 (~2021)

## New
 * Added `load_bsp` function to identify bsp type  
 * Added `D3DBsp`, `IdTechBsp`, `RespawnBsp` & `ValveBsp` classes
 * Added general support for the PakFile lump
 * Added general support for the GameLump lump
 * Extension scripts
   * `archive.py` extractor for CoD `.iwd` / Quake `.pk3`
   * `diff.py` compare bsps for changelogs / study
   * `lightmaps.py` bsp lightmap -> `.png`
 * Made a basic C++ 17 implementation in `src/`

## Changed
 * `Bsp` lumps are loaded dynamically, reducing memory usage
   * New wrapper classes can be found in `bsp_tool/lumps.py`
 * `mods/` changed to `branches/`
   * Added subfolders for developers
   * Helpful lists for auto-detecting a .bsp's origin
   * Renamed `team_fortress2` to `valve/orange_box`
 * `LumpClasses` now end up in 3 dictionaries per branch script
   * `BASIC_LUMP_CLASSES` for types like `short int`
   * `LUMP_CLASSES` for standard `LumpClasses`
   * `SPECIAL_LUMP_CLASSES` for irregular types (e.g. PakFile)
   * `GAME_LUMP_CLASSES` for GameLump SpecialLumpClasses
 * `Bsp`s no longer print to console once loaded
 * `Base.Bsp` & subclasses have reserved ALL CAPS member names for lumps only
   * BSP_VERSION, FILE_MAGIC, HEADERS, REVISION -> bsp_version, file_magic, headers, revision
 * TODO: load external lumps and internal lumps at the same time

## New Supported Games
  * GoldSrc Engine (excluding Half-Life: Blue Shift)
  * Quake II
  * Quake 3 Arena
  * Source Engine

## Broken Support
  * Call of Duty
  * Dark Messiah of Might and Magic
  * Half-Life: Blue Shift
  * Quake

## Updated Game Support
 * Apex Legends
 * Orange Box
 * Titanfall
 * Titanfall 2
