# Changelog

# v0.3.0 (July 2021)

## New
 * Added `load_bsp` function to identify bsp type  
 * Added `D3DBsp`, `IdTechBsp`, `RespawnBsp` & `ValveBsp` classes
 * Added general support for the PakFile lump
 * Added general support for the GameLump lump
 * Extension scripts
   * `archive.py` extractor for CoD `.iwd` / Quake `.pk3`
   * `diff.py` compare bsps for changelogs / study
   * `lightmaps.py` bsp lightmap -> `.png`
   * `lump_analysis.py` determine lump sizes with stats
 * Prototype Blender 2.92 RespawnBsp editor
 * Made a basic C++ 17 implementation in `src/`

## Changed
 * Bsp lumps are loaded dynamically, reducing memory usage
 * `mods/` changed to `branches/`
   * added subfolders for developers
   * helpful lists for auto-detecting a .bsp's origin
   * renamed `team_fortress2` to `valve/orange_box`
 * `LumpClasses` now end up in 3 dictionaries per branch script
   * `BASIC_LUMP_CLASSES` for types like `short int`
   * `LUMP_CLASSES` for standard `LumpClasses`
   * `SPECIAL_LUMP_CLASSES` for irregular types (e.g. PakFile)
 * Bsps no longer print on a successful load, only on an unsuccessful load
 * `Base.Bsp` & subclasses have reserved ALL CAPS member names for lumps only
   * BSP_VERSION, FILE_MAGIC, HEADERS, REVISION -> bsp_version, file_magic, headers, revision

## New Supported Games
  * Call of Duty 1
  * Counter-Strike: Global Offensive
  * Counter-Strike: Online 2
  * Counter-Strike: Source
  * Titanfall
  * Quake 3 Arena

## Updated Game Support
 * Apex Legends
 * Titanfall
 * Titanfall 2
