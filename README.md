# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  
The range of .bsp formats supported covers many developers:  

| id Software | Infinity Ward | Nexon | Respawn Entertainment | Valve Software |
| ----------- | ------------- | ----- | --------------------- | -------------- |
| Quake 3 Arena | Call of Duty 1 | Counter-Strike: Online 2 | Titanfall | Counter-Strike: Source |
| | | Vindictus | Titanfall 2 | Team Fortress 2 |
| | | | Apex Legends | Counter-Strike: Global Offensive |

No format is 100% supported yet.  
For more details, see the `SUPPORTED.md` file in each developer's folder  
Unsupported elements are treated as raw bytes  

> e.g. bsp_tool/branches/valve/SUPPORTED.md

## Reading .bsps
Most .bsps can be read with the `bsp_tool.load_bsp()` function  
`bsp_tool.load_bsp()` does it's best to detect the specific branch of the format  
However some .bsp formats shared identifiers with very different games  
For example: both Vindictus and Team Fortress 2 are version 20  
In these cases, the user must manually select the game / "branch script"  

## Branch Scripts
To parse the .bsp format, `bsp_tool` utilitises a system of "branch scripts"  
`bsp_tool/branches/` contains folders for every developer  
Each of these developer folders has a python script for each game  
Many scripts import from others, this helps to trace the "genealogy" of the format, as well as reducing redundant code  

### Utilities
`branches/base.py` provides some base classes for mapping out rough structures  
`branches/shared.py` details some common structures (PakFiles etc.)  
