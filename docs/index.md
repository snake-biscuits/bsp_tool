# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  

## Supported Games
  * [Id Software](./id_software/SUPPORTED.html)
  * [Infinity Ward](./infinity_ward/SUPPORTED.html)
  <!-- * [Nexon](./nexon/SUPPORTED.html) -->
  * [Respawn Entertainment](./respawn/SUPPORTED.html)
  * [Valve Software](./valve/SUPPORTED.html)

> TODO: Generate html with documentation links for each list of supported games
> TODO: Update documentation on with GitHub actions


## Usage

```python
>>> import bsp_tool
>>> bsp_tool.load_bsp("map_folder/filename.bsp")
<ValveBsp filename.bsp (VBSP version 20) at 0x00...>
>>> bsp = _
```

> TODO: Explain the Bsp base class, expected usage, lump names & branches

> Note: Respawn .bsp files should have .bsp_lump & .ent files in the same folder

### Game Detection
`bsp_tool.load_bsp()` does it's best to detect the format branch of the give file  
However, some .bsp formats share identifiers with very different games  

> Example: both Vindictus and Team Fortress 2 are version 20  

When loading maps from the following games, you must specify the branch with:
```python
bsp_tool.load_bsp("filename", bsp_tool.branches.developer.game)
```
| Game | **incorrecty** detected branch | correct branch script |
| - | - | - |
| Vindictus | `valve.orange_box` | `nexon.vindictus` |

> Note: the loaded branch is stored in the bsp object's `.branch` attribute  

## Format Documentation & Study
`bsp_tool` seeks to provide "living documentation" of the .bsp format  

At present, my focus is on creating custom mapping tools for Titanfall & CSO2  
I hope this documentation proves useful to developers of similar tools  

Please do not use `bsp_tool` to copy another creator's work  
The primary goal of `bsp_tool` is to provide mapping tools for games that have none  
Please don't just copy a map from one game to another and call it a day  

Create something new, and see what level design can do in the hands of players  

 * [Timeline of the .bsp format](./timeline.html)

## Extending

### Branch Scripts
To parse the .bsp format, `bsp_tool` utilitises a system of "branch scripts"  
`bsp_tool/branches/` contains folders for every developer  
Each of these developer folders has a python script for each game  
Many scripts import from others, this helps to trace the "genealogy" of the format, as well as reducing redundant code  

#### Utilities
`branches/base.py` provides some base classes for mapping out rough structures  
`branches/shared.py` details some common structures (PakFiles etc.)  