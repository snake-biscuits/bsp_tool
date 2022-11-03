# bsp_tool
Python library for analysing .bsp files  

`bsp_tool` provides a Command Line Interface for analysing .bsp files  
Current development is focused on bringing new maps to Counter-Strike: Online 2 & the Titanfall Engine


## Installation
To use the latest version, clone from git:
```
$ git clone git@github.com:snake-biscuits/bsp_tool.git
```

Or to use the latest stable release (0.3.1), install via [pip](https://pypi.org/project/bsp-tool/) (Python 3.7+):
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
    - [Dark Messiah of Might & Magic Singleplayer](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/arkane/dark_messiah_sp.py)
    - [Dark Messiah of Might & Magic Multi-Player](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/arkane/dark_messiah_mp.py)
  * [Gearbox Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox)
    - [Half-Life: Blue Shift](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox/blue_shift.py)
    - [Half-Life: Opposing Force](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [James Bond 007: Nightfire](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/gearbox/nightfire.py)
  * [Id Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software)
    - [Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py)
    - [Quake II](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py)
    - [Quake III Arena](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [Quake III Arena (Dreamcast)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [Quake III: Team Arena](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - Quake Champions :o:
    - [Quake Live](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
  * [Infinity Ward](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward)
    - [Call of Duty](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty1.py)
    - [Call of Duty 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty2.py)
    - [Call of Duty 4: Modern Warfare](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/modern_warfare.py)
    - Call of Duty: Modern Warfare 2 :o:
  * [Ion Storm](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ion_storm)
    - [Anachronox](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py)
    - [Daikatana](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ion_storm/daikatana.py)
  * [Nexon](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon)
    - [Counter-Strike: Online 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/cso2.py) :x:
    - [Titanfall: Online](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Vindictus](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/vindictus.py) :x:
  * [Raven Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven)
    - [Heretic II](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py)
    - [Hexen II](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven/hexen2.py)
    - [Soldier of Fortune](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven/soldier_of_fortune.py)
    - [Soldier of Fortune II: Double Helix](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven/soldier_of_fortune2.py)
    - [Star Trek: Voyager - Elite Force](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [Star Wars: Jedi Knight - Jedi Academy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven/soldier_of_fortune2.py)
    - [Star Wars: Jedi Knight II - Jedi Outcast](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/raven/soldier_of_fortune2.py)
  * [Respawn Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn)
    - [Titanfall](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Titanfall (Xbox360)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall_x360.py) :o:
    - [Titanfall 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall2.py)
    - [Apex Legends](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/apex_legends.py)
  * [Ritual Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual)
    - [American McGee's Alice](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/fakk2.py)
    - [Heavy Metal F.A.K.K. 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/fakk2.py)
    - [SiN](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/sin.py)
    - [SiN: Gold](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/sin.py)
    - [SiN Episodes: Emergence](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Star Trek: Elite Force II](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/star_trek_elite_force2.py)
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
    - [Half-Life 2 (Xbox)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Deathmatch](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Episode 1](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life 2: Episode 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life 2: Lost Coast](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life Deathmatch: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Half-Life: Paranoia (Dreamcast)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Half-Life: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Left 4 Dead](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead.py)
    - [Left 4 Dead (Xbox360)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box_x360.py) :x:
    - [Left 4 Dead 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/left4dead2.py)
    - [Left 4 Dead 2 (Xbox360)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box_x360.py)
    - [Portal](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Portal 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Portal 2 (Xbox360)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013_x360.py) :x:
    - [Richochet](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Source Filmmaker](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Source SDK 2013](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Team Fortress 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [The Orange Box (Xbox360)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box_x360.py)
  * Other
    - [Alkaline](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/remake_quake.py)
    - [Black Mesa](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Blade Symphony](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - Bloody Good Time :o:
    - Call of Duty: Black Ops III :o:
    - [Call of Duty: United Offensive](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty1.py) :o:
    - Call of Duty: World at War :o:
    - [Cocaine Diesel](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/qfusion.py) :o:
    - Contagion :o:
    - [Cry of Fear](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [DarkPlaces](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py)
    - [D-Day Normandy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py)
    - [Dino D-Day](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py)
    - [Double Action: Boogaloo](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Entropy: Zero 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [E.Y.E: Divine Cybermancy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Fistful of Frags](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Fortress Forever](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [G-String](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Garry's Mod](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Half-Life 2 VR Mod](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/brances/valve/source.py)
    - [Halfquake Trilogy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [INFRA](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/loiste/infra.py)
    - [Kingpin: Life of Crime](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake2.py) :o:
    - [Medal of Honor: Allied Assault Demo](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/mohaa_demo.py)
    - [Medal of Honor: Allied Assault](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/mohaa.py)
    - [Medal of Honor: Allied Assault - Spearhead](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/mohaa.py)
    - [Medal of Honor: Allied Assault - Breakthrough](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/ritual/mohaa_bt.py)
    - [Natural Selection](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [NEOTOKYO](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Nexuiz Classic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [No More Room in Hell](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Nosferatu](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/qfusion.py) :o:
    - [Quake: Dimension of the Past](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/remake_quake.py)
    - [Return to Castle Wolfenstein](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - The Ship :o:
    - [Sven Co-op](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/goldsrc.py)
    - [Synergy](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/source.py)
    - [Tactical Intervention](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
    - [Team Fortress Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py)
    - [The Beginner's Guide](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py) :o:
    - [The Stanley Parable](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/sdk_2013.py) :o:
    - [Vampire: The Masquerade - Bloodlines](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/troika/vampire.py)
    - [Warsow](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/qfusion.py)
    - [Wolfenstein: Enemy Territory](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [WRATH: Aeon of Ruin](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
    - [Xonotic](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)


## Thanks
 * [BobTheBob](https://github.com/BobTheBob9)
   - Identified loads of Titanfall lumps (90% of static props + more)
 * [Call of Duty Promod Team](https://github.com/promod)
   - For distributing safe links to Call of Duty 4 Mod Tools
 * [Chris Strahl](https://github.com/Chrissstrahl)
   - Preserving **extensive** documentation, mods & source code for Quake 3 & Ubertools games
 * [Ficool2](https://github.com/ficool2)
   - Providing lots of current and detailed info on Source & helping track down some rarer titles
 * [F1F7Y](https://github.com/F1F7Y)
   - Lead developer on [Spyglass Radiant](https://github.com/F1F7Y/spyglass-radiant) NetRadiant-Custom fork for Titanfall Series
 * [GCFScape](https://nemstools.github.io/pages/GCFScape-Download.html)
   - Super handy `.vpk` (Valve format) browser; VTFLib / VTFEdit is also from Nem's Tools
 * [Maxime Dupuis](https://github.com/maxdup)
   - Helping me identify multiple lumps in Source Engine .bsps
 * [MobyGames](https://www.mobygames.com/)
   - Keeping records of the credits on so many games, helping to pin down engine origins
 * [pakextract](https://github.com/yquake2/pakextract)
   - Super useful tool for `.pak` files
 * [PCGamingWiki](https://community.pcgamingwiki.com/files/category/16-official-patches/)
   - Archiving old patches to help install old modding tools
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
