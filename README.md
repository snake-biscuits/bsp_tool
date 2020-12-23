# bsp_tool
 A library for .bsp file analysis & modification

bsp_tool has no UI, it only provides a python interface to the contents of the requested .bsp  
This interface is provided via the `bsp_tool.base.Bsp` class & subclasses  
At present the tool reads .bsps from most Source Engine games, as well as Titanfall 2 & Apex Legends  

The `branches/` folder contains classes for interpreting the lumps within .bsp files  
bsp_tool needs to know each lump is constructed & this varies from game to game  
`branches/base.py` provides some base classes to help quickly map out a rough structures  
NOTE: `valve/vindictus.py` extends `valve/orange_box.py`  
since the format is mostly the same between branches, most structure definitions can be copied over  

At present, not every lump's exact format is understood  
When a lump of unknown format is loaded, the raw byte data is stored in `RAW_<LUMPNAME>` attributes  

The user can specify what game bsp_tool is to expect  
If no game is specified, bsp_tool will try it's best to find a definition based on the file header  
NOTE: Vindictus .bsp headers are identical to Orange Box  
The defaults for each header are defined in `branches/__init__.py`  
