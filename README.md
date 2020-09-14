# bsp_tool
 A library for .bsp file analysis & modification

bsp_tool has no UI, it only provides a python interface to the contents of the requested .bsp  
This interface is provideded via the `bsp_tool.bsp` class  
At present the tool read .bsps from most Source Engine games, as well as Titanfall 2 & Apex Legends  

The `mods/` folder contains classes for interpretting the lumps within .bsp files  
bsp_tool needs to know each lump is constructed & this varies from game to game. 
`mods/common.py` provides some handy helper classes for defining the classes which shape most lumps  
`mods/vindictus.py` is a good example of extenting another mod (`vindictus.py` extends `team_fortress2.py`)  

At present, not every lump's exact format is understood  
When a lump of unknown format is loaded, it becomes `RAW_LUMPNAME` & the raw data is preserved
By default, bsp_tool assumes .bsps are version 20 (Team Fortress 2)  
If this assumption is found to be false, bsp_tool will try other mods  
The user can also specify what mod bsp_tool is to expect  
 
