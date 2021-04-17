# Changelog

# v0.3.0 (April 2021)

## New
 * Added `load_bsp` function to identify bsp type  
 * Added `D3DBsp`, `IdTechBsp`, `RespawnBsp` & `ValveBsp` classes
 * Added general support for PakFiles
 * Extension scripts
   * `archive.py` extractor for CoD `.iwd` / Quake `.pk3`
   * `diff.py` compare bsps for changelogs / study
   * `lightmaps.py` bsp lightmap -> `.png`
   * `lump_analysis.py` determine lump sizes with stats
 * Prototype Blender 2.92 rBSP editor

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

## New Supported Games
  * Call of Duty 1
  * Counter-Strike: Global Offensive
  * Counter-Strike: Online 2
  * Counter-Strike: Source
  * Titanfall
  * Quake 3 Arena

## Updated Game Support
 * Apex Legends
 * Titanfall 2
