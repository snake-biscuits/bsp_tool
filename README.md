# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  

## Supported Games
The range of .bsp formats supported covers many developers:  

| id Software | Infinity Ward | Nexon | Respawn Entertainment | Valve Software |
| ----------- | ------------- | ----- | --------------------- | -------------- |
| Quake | Call of Duty 1 | Counter-Strike: Online 2 | Titanfall | Counter-Strike: Source |
| Quake 3 Arena | | Vindictus | Titanfall 2 | Team Fortress 2 |
| | | | Apex Legends | Counter-Strike: Global Offensive |

No format is 100% supported, yet.  
Unsupported elements are treated as raw bytes  
For more details, see the `SUPPORTED.md` file in each developer's branch folder  


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

## Project Goals
`bsp_tool` seeks to provide "living documentation" of the .bsp format  

At present, my focus is on creating custom mapping tools for Titanfall & CSO2  
I hope this documentation proves useful to developers of similar tools  

Please do not use `bsp_tool` to copy another creator's work  
The primary goal of `bsp_tool` is to provide mapping tools for games that have none  
Please don't just copy a map from one game to another and call it a day  

Create something new, and see what level design can do in the hands of players  
