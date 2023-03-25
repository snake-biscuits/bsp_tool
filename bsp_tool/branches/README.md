# How `bsp_tool` loads .bsps
If you're using `bsp_tool.load_bsp("reallycoolmap.bsp")` to load a `.bsp` a few things happen behind the scenes to figure out the format  
Since `bsp_tool` supports a range of `.bsp` variants, a single script to handle the rough format wasn't going to cut it  
To narrow down the exact format of a bsp file `load_bsp` looks at some key information in each file:


### Developer variants
First, `load_bsp` tries to determine the developer behind the chosen .bsp  
If the file extension is `.d3dbsp`, it's a Call of Duty 2 `InfinityWardBsp`  
Other bsps use the `.bsp` extension (Call of Duty 1 included)  
The developer is identified from the "file-magic", the first four bytes of any .bsp are:
  - `b"2015"` for `RitualBsp`
  - `b"2PSB"` for `ReMakeQuakeBsp`
  - `b"BSP2"` for `ReMakeQuakeBsp`
  - `b"EALA"` for `RitualBsp`
  - `b"EF2!"` for `RitualBsp`
  - `b"FAKK"` for `RitualBsp`
  - `b"FBSP"` for `FusionBsp`
  - `b"IBSP"` for `IdTechBsp` / `InfinityWardBsp` `D3DBsp`
  - `b"PSBV"` for `ValveBsp` (Xbox360 scripts)
  - `b"PSBr"` for `RespawnBsp` (Xbox360 scripts)
  - `b"RBSP"` for `RavenBsp`
  - `b"VBSP"` for `ValveBsp`
  - `b"rBSP"` for `RespawnBsp`

> This rule isn't perfect! most mods out there are Source Engine forks with b"VBSP"  

> Quake & GoldSrc .bsp files don't have any file magic!  

Most of the major differences between each developer's format are the number of lumps & bsp header  
They also use some lumps which are unique to each developer's Quake based engine  
More on those differences in an upcoming wiki page...  


### Game variants
Once `load_bsp` knows the developer, it has to work out which game a `.bsp` comes from  

In the `.bsp` header there will always be a 4 byte int for the `.bsp` format version

Unfortunately this isn't totally unique from game to game, [most Source Engine titles use version 20](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format#Versions)

This is where `load_bsp`'s second (optional!) argument comes in, `branch`

`branch` can be either a string or a python script
```python
>>> import bsp_tool

>>> bsp_tool.load_bsp("tests/maps/Call of Duty 4/mp/mp_lobby.bsp")
Loading mp_lobby.bsp (IBSP version 22)...
Loaded  mp_lobby.bsp
<D3DBsp mp_lobby.bsp at 0x000001FB329F7640>

>>> bsp_tool.load_bsp("tests/maps/Quake 3 Arena/mp_lobby.bsp", branch="Quake3")
Loading mp_lobby.bsp (IBSP version 46)...
Loaded  mp_lobby.bsp
<IdTechBsp mp_lobby.bsp at 0x000001FB329F78E0>

>>> bsp_tool.load_bsp("tests/maps/Team Fortress 2/test2.bsp", branch=bsp_tool.branches.valve.orange_box)
Loading pl_upward.bsp (VBSP version 20)...
Loaded  pl_upward.bsp
<ValveBsp pl_upward.bsp at 0x000001FB329F7940>
```
In the above example `bsp_tool.branches.valve.orange_box` points to [`bsp_tool/branches/valve/orange_box.py`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py)  
This branch script is used to intialise the `Bsp` subclass chosen when `load_bsp` works out the developer  

When `branch` is a string, `load_bsp` uses `branch` as a key in the `bsp_tool.branches.by_name` dictionary to choose a script  
Bsp classes take the branch script as their first argument and **do not have defaults** (except `ValveBsp`)  

When `branch` is `"unknown"` (default) the bsp format version is used as a key in the `bsp_tool.branches.by_version` dictionary



# Branch scripts
Now that we know a branch script is needed to load a specific .bsp variant, why might we need to make one?  
Well, `bsp_tool` doesn't cover a lot of formats, and those it does aren't mapped completely either!  

But with branch scripts you can develop a rough map of a particular format while copying definitions from other scripts  
[`nexon/vindictus.py`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/nexon/vindictus.py) for example, imports `valve.orange_box` and copies most of the format  
This saves a lot of code!  Especially since they only differ on the format of a handful of lumps and share a .bsp version


## Overall structure
The branch scripts that come with bsp_tool have a common format to make reading them as consistent as possible

```python
import enum
from .. import base
from .. import shared  # special lumps

BSP_VERSION = 20

class LUMP(enum.Enum):
    ENTITIES = 0
    AREAS = 20
    PAKFILE = 40

lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

# classes for each lump, in alphabetical order: [1 / 64] + shared.Entities & PakFile
class Area(base.Struct):  # LUMP 20
    num_area_portals: int   # number of AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index of first AreaPortal
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"

LUMP_CLASSES = {"AREAS": {0: Area}}

SPECIAL_LUMP_CLASSES = {"ENTITIES": {0: shared.Entities},
                        "PAKFILE":  {0: shared.PakFile}}
```

If you compare [`bsp_tool/branches/valve/orange_box.py`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/valve/orange_box.py) you'll see I've left a lot out here, but this basic batch script is a great start for translating any .bsp variant  

At the top we have the bsp format version, mostly as a note  
Next comes the `LUMP` enum, this lists each lump in the order they appear in the bsp header  

> Lumps without LumpClasses are loaded as raw bytes
> Invalid LumpClasses will generate an error (silent, saved to bsp.loading_errors)
> Invalid lumps will still be loaded as raw bytes

Attached to this we have `lump_header_address`, this connects each LUMP entry to the offset .bsp where it's header begins  
Then comes the lump classes, these translate most lumps into python objects (more on them later)  
We also have some special lump classes, these are loaded in a different way to other lumps, and some are shared across **almost all** bsp variants

The Bsp class reads the headers for each lump and holds the contents in `Bsp.headers`  
This dictionary of headers takes the name given in the branch scripts' `LUMP` class  
Lump names are tied to a dictionary, which ties lump version (`int`) to LumpClass  
From there, a lump is either saved as `Bsp.RAW_LUMPNAME` (bytes) or `Bsp.LUMPNAME` (List[LumpClass]) if it the lump is listed in `LUMP_CLASSES`


## Lump classes
A majority of lumps are very simple, being a list of fixed length structs  
bsp_tool loads these lumps with python's built in `struct` module  
`struct.iter_unpack` takes a format specifier string and a stream of bytes  
This stream of bytes must contain a whole number of these structures or an error will be raised

The lump class in the example is a subclass of [`bsp_tool.branches.base.Struct`](https://github.com/snake-biscuits/bsp_tool/blob/master/bsp_tool/branches/base.py#L5)  
`base.Struct` exists to make defining a lump's specific format quick using very little code

The definition usually has 3 parts:
```python
class LumpClass(base.struct):
    __slots__ = ["unknown", "flags"]
    _format = "5i"
    _arrays = {"unknown": [*"abcd"]}
```

`__slots__` names the main attributes of the LumpClass  
`_format` holds the format string for `struct.iter_unpack`  
(I recommend also giving type hints for each attribute, so others don't have to work them out from `_format`)  
`_arrays` is optional, it holds a dictionary for generating a `base.MappedArray` to help group attributes  
For the most complex use of arrays (so far), see: [`branches.id_software.quake3.Face`](https://github.com/snake-biscuits/bsp_tool/blob/06f184b0cdf5133ea12ce8e0f5442398d6310d2a/bsp_tool/branches/id_software/quake3.py#L60)  

So the above example would turn the C struct:
```C
struct LumpClass {
    int unknown_a;
    int unknown_b;
    int unknown_c;
    int unknown_d;
    int flags;
}
```
into:
```python
LumpClass.unknown.a
LumpClass.unknown.b
LumpClass.unknown.c
LumpClass.unknown.d
LumpClass.flags
```
Lump classes don't have to be subclasses of `base.Struct` though, the only requirement is the `_format` attribute  
This is essential because each lump class is initialised with the tuple `struct.iter_unpack` returns for each struct  
And to read these raw bytes `Bsp.load_lumps` uses something similar to `struct.iter_unpack(LumpClass._format, RAW_LUMP)`  
If the tuple returned has a length of 0 `bsp.LUMP = list(map(LumpClass, [t[0] for t in tuples]))`  
Else: `Bsp.LUMP = list(map(LumpClass, tuples))`  
To support re-saving LumpClasses, a `.as_tuple()` method is required  
`as_tuple` must return a tuple of the same length & containing the correct type to feed `struct.pack`


## Special lump classes
Not all lumps are as simple as a list of structs, and this is where special lump classes come in  
Special lump classes are initialised from the raw bytes of a lump, turning them into python objects that are easier to work with
All that's really required is an `__init__` method and an `.as_bytes()` method for re-saving

Here's `branches.shared.TextureDataStringData` as an example of how basic a special lump class can be:
```python
class TextureDataStringData(list):
    def __init__(self, raw_texture_data_string_data):
        super().__init__([t.decode("ascii", errors="ignore") for t in raw_texture_data_string_data.split(b"\0")])

    def as_bytes(self):
        return b"\0".join([t.encode("ascii") for t in self]) + b"\0"
```
By inheriting `list` you can use all the features of python lists while still importing the data with `__init__` & saving it back with `.as_bytes()`  
You can of course make more complex classes, like adding methods (though they won't be connected to their parent `Bsp`)
Speaking of methods


## Methods
While not listed in the example branch scripts, you can add methods to a `Bsp` with a branch script!
The only requirements are that you have a list of functions in `methods` somewhere in the script

```python
def areaportals_of_area(bsp, area_index):
    area = bsp.AREAS[area_index]
    return bsp.AREA_PORTALS[area.first_areaportal:area.first_areaportal + area.num_areaportals]


methods = [areaportals_of_area]
```

These methods are attached when the `Bsp` is initialised
The only requirements for these functions is that the first argument be `bsp`, since as a method the `Bsp` will pass itself to the function
