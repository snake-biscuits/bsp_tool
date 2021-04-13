# bsp_tool
 A library for .bsp file analysis & modification

bsp_tool has no UI, it only provides a python interface to the contents of the requested .bsp  
This interface is provided via the `bsp_tool.base.Bsp` class & subclasses  
At present the tool reads .bsps from most Source Engine games, as well as Titanfall 2 & Apex Legends  

The `branches/` folder contains classes for interpreting the lumps within .bsp files  
`bsp_tool` needs to know how each lump is constructed and this varies from game to game  
`branches/base.py` provides some base classes to help quickly map out a rough structures  
NOTE: `valve/vindictus.py` extends `valve/orange_box.py`  
Since the format is mostly the same between branches, most structure definitions can be copied over  

At present, not every lump's exact format is understood  
When a lump of unknown format is loaded, `bsp_tool` just reads the raw bytes  

The user can specify what game `bsp_tool.load_bsp()` is to expect  
If no game is specified, `bsp_tool.load_bsp()` will try it's best to find a game based on the file header  

> NOTE: Vindictus .bsp files have the same `.VERSION` as Orange Box, but it's headers are different  

The defaults for each header are defined in `branches/__init__.py`  

Make sure you're using 64 bit Python!  
Respawn branch .bsp files (Apex Legends & Titanfall 2) need more than 4GB of RAM!  
