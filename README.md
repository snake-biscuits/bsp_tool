# bsp_tool
Python library for analysing .bsp files  

`bsp_tool` provides a Command Line Interface for analysing .bsp files  


## Installation
To use the latest **unstable** version, clone with `git`:
```
$ git clone git@github.com:snake-biscuits/bsp_tool.git
```

You can also clone with `pip`:

```
$ pip install git+https://github.com/snake-biscuits/bsp_tool.git
```

Or, use the latest stable release (August 2024 | 0.5.0 | Python 3.8-11):
```
$ pip install bsp_tool
```


## Fair Use
**Please do not use `bsp_tool` to copy or steal another creator's work**  
The primary goal of `bsp_tool` is to extend community mapping tools  


### Always
  - **Ask** the creator's permission before touching their work  
  - **Understand** that by default creator's works are under copyright  
    - [US Law Copyright FAQ](https://www.copyright.gov/help/faq/faq-general.html#mywork)
    - [US Copyright Duration](https://www.copyright.gov/help/faq/faq-duration.html)
      - [Circular 15a](https://www.copyright.gov/circs/circ15a.pdf)  
  - **Contact** the original creator to get their permission  
    - This can get complicated  
    - Some creators don't hold the copyright on their works  
      - often because of Company / Publisher contracts  
  - **Credit** the original creator; once you have permission to share a derivative work  
  - **Support** the official release

**DO NOT** use this tool to steal another creator's work  
**DO** use this tool to understand the `.bsp` format(s) and create more specific tools

> Be aware that this gets even more complicated with commercial projects


## Usage

To load a .bsp file in python:

```python
>>> import bsp_tool
>>> bsp_tool.load_bsp("map_folder/filename.bsp")
<ValveBsp filename.bsp (VBSP version 20) at 0x00...>
```

Full documentation: [snake-biscuits.github.io/bsp_tool/](https://snake-biscuits.github.io/bsp_tool/) **[WIP]**


## Thanks
 * [BobTheBob](https://github.com/BobTheBob9)
   - Identified loads of Titanfall lumps (90% of static props & loads of other lumps)
 * [Call of Duty Promod Team](https://github.com/promod)
   - For distributing safe links to Call of Duty 4 Mod Tools
 * [Chris Strahl](https://github.com/Chrissstrahl)
   - Preserving **extensive** documentation, mods & source code for Quake 3 & Ubertools games
 * [Ficool2](https://github.com/ficool2)
   - Providing lots of current and detailed info on Source & helping track down some rarer titles
 * [F1F7Y](https://github.com/F1F7Y)
   - Lead developer on [MRVN-Radiant](https://github.com/MRVN-Radiant/MRVN-Radiant) NetRadiant-custom fork for Respawn's Source Engine fork
 * [GCFScape](https://nemstools.github.io/pages/GCFScape-Download.html)
   - Super handy `.vpk` (Valve format) browser; VTFLib / VTFEdit is also from Nem's Tools
 * [JJL772](https://github.com/JJL772)
   - Published public documentation for the otherwise closed-source VBSP v25
 * [John Romero](https://rome.ro)
   - Supplying `.map` level source files for Quake
 * [Maxime Dupuis](https://github.com/maxdup)
   - Helping me identify multiple lumps in Source Engine .bsps
 * [MobyGames](https://www.mobygames.com/)
   - Keeping records of the credits on so many games, helping to pin down engine origins
 * [pakextract](https://github.com/yquake2/pakextract)
   - Super useful tool for `.pak` files
 * [PCGamingWiki](https://community.pcgamingwiki.com/files/category/16-official-patches/)
   - Archiving old patches to help install old modding tools
 * [rexx](https://github.com/r-ex)
   - Donating a lot of time helping organise & gather maps from 2019 Apex Legends
 * [REDxEYE](https://github.com/REDxEYE)
   - Being very open and actively collaborating on SourceIO & Titanfall .bsps
 * [Taskinoz](https://github.com/taskinoz)
   - Helping me find people that can actively use my research & tools
 * [Valve Developer Wiki](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format)
   - For starting me on this path however many years ago
 * [Warmist](https://github.com/warmist)
   - Identifying physics model related structs for Titanfall 2
 * All of the Wiki Editors
   - Except for the uncited `Id Tech 3 -> Treyarch NGL` on CoDWiki **[citation needed]**
