# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  
Current development is focused on bringing new maps to Titanfall 1 & 2 and Counter-Strike: Online 2  

## Supported Games
  * [Id Software](./id_software/SUPPORTED.html)
  * [Infinity Ward](./infinity_ward/SUPPORTED.html)
  * [Nexon](./nexon/SUPPORTED.html)
  * [Respawn Entertainment](./respawn/SUPPORTED.html)
  * [Valve Software](./valve/SUPPORTED.html)

## Installation
To use / contribute to the latest version, clone this package
```
git clone git@github.com:snake-biscuits/bsp_tool.git
```

Or to use the latest stable release, install via [pip](https://pypi.org/project/bsp-tool/) (Python 3.7+)
```
pip install bsp_tool
```

> NOTE: The last PyPi release (v0.2.2) is close to a year old!  

## Use & Respecting Level Designers
**Please do not use `bsp_tool` to copy or steal another creator's work**  
The primary goal of `bsp_tool` is to extend community mapping tools  

Always ask the mappers permission before using their work!
And credit the original mapper!
Don't stop at copying existing maps!
Show us all what level design tools can do in the hands of players!  

## Guides
[Basic Usage](./usage.html) <!-- Split up / include links to the wiki -->
<!-- [BSP format crash course](...) # include branch specific pages -->
<!-- Links & credits to other community tools -->

## [Changelog](./CHANGELOG.html)
You can see a list of all changes in the [changelog](./CHANGELOG.html)


## .bsp Format Reference
[Timeline of the .bsp format (WIP)](./timeline.html)


## Contributing
At present the easiest way to contibute to the project is to add /extend a "branch script" for a game `bsp_tool` doesn't yet fully support

[Learn More](https://github.com/snake-biscuits/bsp_tool/wiki)

## Branch Scripts
To parse the .bsp format, `bsp_tool` utilitises a system of "branch scripts"  
`bsp_tool/branches/` contains folders for every developer  
Each of these developer folders has a python script for each game  
Many scripts import from others, this helps to trace the "genealogy" of the format, as well as reducing redundant code  

[Guide: Lump Classes](https://github.com/snake-biscuits/bsp_tool/wiki/Lump-Classes)

### Utilities
`branches/base.py` provides some base classes for mapping out rough structures  
`branches/shared.py` details some common structures (PakFiles etc.)  
