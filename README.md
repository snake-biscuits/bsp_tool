# bsp_tool
Python library for analysing .bsp files  

`bsp_tool` provides a Command Line Interface for analysing .bsp files  
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
    - [Half-Life: Blue Shift](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox/bshift.py)
    - [Half-Life: Opposing Force](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
  * [Id Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software)
    - [Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py) :x:
    - [Quake II](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py)
    - [Quake III Arena](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - Quake 4 :o:
    - Quake Champions :o:
    - [Quake Live](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
  * [Infinity Ward](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward)
    - [Call of Duty](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty1.py) :x:
    - Call of Duty 2 :x:
    - Call of Duty 4: Modern Warfare :o:
    - Call of Duty: Modern Warfare 2 :o:
  * [Nexon](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon)
    - [Counter-Strike: Online 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/cso2.py) :x:
    - [Titanfall: Online](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Vindictus](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/vindictus.py) :x:
  * Raven Software
    - [Hexen 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py) :x:
    - [Soldier of Fortune](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py) :o:
    - [Soldier of Fortune II: Double Helix](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py) :o:
    - [Star Trek: Voyager - Elite Force](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py) :o:
    - [Star Wars Jedi Knight II: Jedi Outcast](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py) :o:
    - [Star Wars Jedi Knight: Jedi Academy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py) :o:
  * [Respawn Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn)
    - [Titanfall](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Titanfall 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall2.py)
    - [Apex Legends](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/apex_legends.py)
  * [Ritual Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual)
    - American McGee's Alice :o:
    - Heavy Metal F.A.K.K. 2 :o:
    - Medal of Honor: Allied Assault :o:
    - SiN :o:
    - SiN: Gold :o:
    - SiN Episodes: Emergence :o:
    - Star Trek: Elite Force II :o:
  * [Valve Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve)
    - [Alien Swarm](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/alien_swarm.py)
    - [Alien Swarm: Reactive Drop](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/alien_swarm.py)
    - [Counter-Strike: Condition Zero](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Counter-Strike: Condition Zero - Deleted Scenes](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Counter-Strike: Global Offensive](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Counter-Strike: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Counter-Strike](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Day of Defeat](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Day of Defeat: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Deathmatch Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Half-Life](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Half-Life 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Deathmatch](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Episode 1](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Episode 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life 2: Lost Coast](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life Deathmatch: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Left 4 Dead](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead.py)
    - [Left 4 Dead 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead2.py)
    - [Portal](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Portal 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Richochet](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Source Filmmaker](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Source SDK 2013](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
  * Other
    - [Black Mesa](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Blade Symphony](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - Brink :o:
    - Daikatana :o:
    - [Fortress Forever](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [G-String](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Garry's Mod](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Halfquake Trilogy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - Medal of Honor: Allied Assault :o:
    - [NEOTOKYO](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Sven Co-op](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Synergy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Tactical Intervention](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py) :x:
    - [The Beginner's Guide](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py) :o:
    - [The Stanley Parable](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py) :o:
    - Vampire: The Masquerade - Bloodlines :o:

<!--
    - Call of Duty: World at War :o:

    - Call of Duty: Black Ops :o:
    - Call of Duty: Modern Warfare 3 :o:
    - Call of Duty: Black Ops II :o:
    - Call of Duty: Ghosts :o:
    - Call of Duty: Black Ops III :o:
    - Call of Duty: Advanced Warfare :o:
    - Call of Duty: Infinite Warfare :o:
    - Call of Duty: Black Ops 4 :o:
    - Call of Duty: Modern Warfare (2019) :o:
    - Call of Duty: Black Ops - Cold War :o:
    - Call of Duty: Warzone :o:
    - Call of Duty: Vanguard :o:
-->
