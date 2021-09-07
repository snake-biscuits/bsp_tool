# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  
Current development is focused on bringing new maps to Counter-Strike: Online 2 & the Titanfall Engine


## Installation
To use the latest version, clone from git:
```
$ git clone git@github.com:snake-biscuits/bsp_tool.git
```

Or to use the latest stable release, install via [pip](https://pypi.org/project/bsp-tool/) (Python 3.7+):
```
pip install bsp_tool
```

> NOTE: The last PyPi release (v0.2.2) is close to a year old  
> v0.3.0 has made many [changes](./CHANGELOG.md) and is the recommended version


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
**DO** use this tool to understand the .bsp format(s) and create more specific tools

> Be aware that this gets even more complicated with commercial projects


## Usage

To load a .bsp file in python:

```python
>>> import bsp_tool
>>> bsp_tool.load_bsp("map_folder/filename.bsp")
<ValveBsp filename.bsp (VBSP version 20) at 0x00...>
```

Full documentation: [snake-biscuits.github.io/bsp_tool/](https://snake-biscuits.github.io/bsp_tool/)


## Supported Games

> The :x: emoji indicates tests are failing  
> The :o: emoji indicates a lack of .bsps to test

  * [Arkane Studios](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/arkane)
    - [Dark Messiah of Might & Magic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/arkane/dark_messiah.py) :x:
  * [Gearbox Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox)
    - [Half-Life: Blue Shift](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox/bshift.py) :x:
    - [Half-Life: Opposing Force](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
  * [Id Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software)
    - [Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py) :x:
    - Quake II :x:
    - [Quake III Arena](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - Quake 4 :o:
  * [Infinity Ward](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward)
    - [Call of Duty (2003)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty1.py) :x:
    - Call of Duty 2 :x:
    - Call of Duty 4: Modern Warfare :x:
  * [Nexon](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon)
    - [Counter-Strike: Online 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/cso2.py) :x:
    - [Vindictus](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/vindictus.py) :o:
  * [Respawn Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn)
    - [Apex Legends](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/apex_legends.py)
    - [Titanfall 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall2.py)
    - [Titanfall](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Titanfall: Online](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
  * [Valve Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve)
    - [Alien Swarm](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/alien_swarm.py)
    - [Alien Swarm: Reactive Drop](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/alien_swarm.py)
    - [Counter-Strike: Condition Zero](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Counter-Strike: Condition Zero - Deleted Scenes](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Counter-Strike: Global Offensive](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/cs_go.py) :x:
    - [Counter-Strike: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py) :x:
    - [Counter-Strike](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Day of Defeat](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Day of Defeat: Source] :x:
    - [Deathmatch Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Half-Life](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - Half-Life 2 :x:
    - Half-Life 2: Deathmatch :x:
    - Half-Life 2: Episode 1 :x:
    - [Half-Life 2: Episode 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life 2: Lost Coast](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - Half-Life Deathmatch: Source :x:
    - Half-Life: Source :x:
    - [Left 4 Dead](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead.py) :x:
    - [Left 4 Dead 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead.py) :x:
    - [Portal](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - Portal 2 :x:
    - [Richochet](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - Source Filmmaker :x:
    - [Source SDK 2013](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - Synergy :x:
    - [Team Fortress 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
  * Other
    - Hexen 2 :x:
    - Black Mesa :x:
    - Blade Symphony :x:
    - Call of Duty 3 :o:
    - Daikatana :o:
    - [G-String](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Garry's Mod](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - Halfquake Trilogy :x:
    - [NEOTOKYO](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - Sven Co-op :x:
    - Synergy :x:
    - Tactical Intervention :x:

<!--
    - Call of Duty: World at War :x:
    - Call of Duty: Modern Warfare 2 :x:
    - Call of Duty: Black Ops :x:
    - Call of Duty: Modern Warfare 3 :x:
    - Call of Duty: Black Ops II :x:
    - Call of Duty: Ghosts :x:
    - Call of Duty: Black Ops III :x:
    - Call of Duty: Advanced Warfare :x:
    - Call of Duty: Infinite Warfare :x:
    - Call of Duty: Black Ops 4 :x:
    - Call of Duty: Modern Warfare (2019) :x:
    - Call of Duty: Black Ops - Cold War :x:
    - Call of Duty: Warzone :x:
    - Call of Duty: Vanguard :x:
-->
