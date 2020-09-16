# bsp_tool
 A library for .bsp file analysis & modification

bsp_tool has no UI, it only provides a python interface to the contents of the requested .bsp  
This interface is provideded via the `bsp_tool.bsp` class  
At present the tool read .bsps from most Source Engine games, as well as Titanfall 2 & Apex Legends  

The `mods/` folder contains classes for interpretting the lumps within .bsp files  
bsp_tool needs to know each lump is constructed & this varies from game to game  
`mods/common.py` provides some base classes  
`vindictus.py` extends `team_fortress2.py`  

At present, not every lump's exact format is understood  
When a lump of unknown format is loaded, it becomes `RAW_LUMPNAME` and the raw data is preserved  

The user can specify what game bsp_tool is to expect  
If no game is specified, bsp_tool will guess based on the bsp version  
Be aware that some games share a version, but have different lump formats  
To know which format bsp_tool will default to, see `mods/__init__.py`  