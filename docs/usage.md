# Usage
```python
>>> import bsp_tool
>>> bsp_tool.load_bsp("map_folder/filename.bsp")
<ValveBsp filename.bsp (VBSP version 20) at 0x00...>
```

> Note: Respawn .bsp files should have .bsp_lump & .ent files in the same folder


## Game Detection
`bsp_tool.load_bsp()` does it's best to detect the format branch of the give file  
However, some .bsp formats share identifiers with very different games  

> Example: both Vindictus and Team Fortress 2 are version 20  

When loading maps from the following games, you must specify the branch with:

```python
bsp_tool.load_bsp("filename", bsp_tool.branches.developer.game)
```


### Blind Spots
| Game                  | Detected                    | Correct                    |
| --------------------- | --------------------------- | -------------------------- |
| Alien Swarm           | `valve.sdk_2013`            | `valve.alien_swarm`        |
| Bloody Good Time      | `valve.orange_box`          | `outerlight.outerlight`    |
| CS:O 2 (2018+)        | `nexon.cso2`                | `nexon.cso2_2018`          |
| Dark Messiah: MP      | `arkane.dark_messiah_sp`    | `arkane.dark_messiah_mp`   |
| Half-Life: Blue Shift | `valve.goldsrc`             | `gearbox.blue_shift`       |
| Hexen 2               | `id_software.quake`         | `raven.hexen2`             |
| Left 4 Dead           | `valve.orange_box`          | `valve.left4dead`          |
| Left 4 Dead 2         | `valve.sdk_2013`            | `valve.left4dead2`         |
| Maerchen Busters      | `valve.orange_box`          | `utoplanet.merubasu`       |
| SiN                   | `raven.soldier_of_fortune2` | `ritual.sin`               |
| Soldier of Fortune    | `id_software.quake3`        | `raven.soldier_of_fortune` |
| Source Filmmaker      | `valve.orange_box`          | `valve.source_filmmaker`   |
| The Ship              | `valve.orange_box`          | `outerlight.outerlight`    |
| Vindictus 1.69        | `valve.orange_box`          | `nexon.vindictus69`        |
| Vindictus             | `valve.orange_box`          | `nexon.vindictus`          |
| Zeno Clash            | `valve.orange_box`          | `ace_team.zeno_clash`      |

Any suggestions on how to better detect these titles are welcome in [Issue #17](https://github.com/snake-biscuits/bsp_tool/issues/17)


## Browsing .bsp contents
`bsp_tool.load_bsp(filename)` returns a `Bsp` object

```python
class Bsp:
    """Bsp base class"""
    bsp_version: int = 0  # .bsp format version
    associated_files: List[str]  # files in the folder of loaded file with similar names
    branch: ModuleType  # soft copy of "branch script"
    bsp_file_size: int = 0  # size of .bsp in bytes
    file_magic: bytes = b"XBSP"
    filename: str
    folder: str
    headers: Dict[str, LumpHeader]
    # ^ {"LUMP_NAME": LumpHeader}
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Exception encountered}
```

This `Bsp` object will also set attributes for each lump

```python
>>> import bsp_tool
>>> bsp = bsp_tool.load_bsp("map_folder/filename.bsp")
>>> bsp.PLANES
<bsp_tool.lumps.BspLump object at 0x00...>
>>> bsp.OCCLUSION
<bsp_tool.lumps.RawBspLump object at 0x00...>
```

Mapped lumps will be available as `bsp_tool.lumps.BspLump`  
You can generally treat these like lists  
```python
for p in bsp.PLANES:
    ...

len(bsp.PLANES)
bsp.PLANES[0], bsp.PLANES[0:-1], bsp.PLANES[-1]

bsp.PLANES.index(Plane(x, y, z, d))

as_list = bsp.PLANES[::]
```

Unmapped Lumps will be available as `bsp_tool.lumps.RawBspLump`
These generally behaving like bytes, however inserting bytes is not yet possible

If a lump is not present in the `Bsp`, there will be no attribute available  

`Bsp.branch.LUMP` provides a list of possible lumps  
`Bsp.headers` is a dict which can tell you which lumps are available  
```python
>>> bsp.headers["PLANES"]
LumpHeader(offset=1036, length=3200, version=0, fourCC=0)
>>> [L.name for L in bsp.branch.LUMP if bsp.headers[L.name].offset != 0]
['ENTITIES', 'PLANES', ..., 'OCCLUSION', ...]
```
