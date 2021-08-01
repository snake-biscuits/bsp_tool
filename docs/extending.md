# Adding support for a Game

> TODO: set out standards for crediting wikis, source code, and other resources that define game specific formats  

## Branch Scripts
To parse the .bsp format, `bsp_tool` utilitises a system of "branch scripts"  
`bsp_tool/branches/` contains folders for every developer  
Each of these developer folders has a python script for each game  
Many scripts import from others, this helps to trace the "genealogy" of the format, as well as reducing redundant code  

[Guide: Lump Classes](https://github.com/snake-biscuits/bsp_tool/wiki/Lump-Classes)

### Utilities
These scripts will be useful for developing your own branch script:  
`branches/base.py` provides some base classes for mapping out rough structures  
`branches/shared.py` details some common structures (PakFiles etc.)  
