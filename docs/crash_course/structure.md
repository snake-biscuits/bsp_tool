# `.bsp` File Structure

All `.bsp` contain multiple "lumps", a variety of structures used by the game engine as a sort of database, representing a level.

The number of lumps & use varies from branch to branch.


## Lumps

In `bsp_tool`, each "branch script" enumerates lump names in `LUMP`

```python
# bsp_tool/branches/developer/branch_script.py
import enum


class LUMP(enum.Enum):
    ENTITIES = 0
    INDICES = 2
    VERTICES = 3
    ...
```

The value of each `LUMP` enum is an index into the lump headers section of the `.bsp` file header.
```C
// quake_bsp.h
struct LumpHeader {
    int  offset;
    int  length;
};

struct BspHeader {
    int         version;
    LumpHeader  headers[17]
};
```

> NOTE: In `bsp_tool`: `LumpHeader` is defined per branch script, and `BspHeader` is defined per `BspClass`  
> -- `BspClasses` are defined in scripts which import `bsp_tool.base.Bsp`  
> -- the header is processed by the `_preload` method

We use the names of the `LUMP` enums to identify the structure of each lump.

> NOTE: Valve & Respawn variants of the `.bsp` format have per-lump format versions

`bsp_tool` matches lump names to structures in 3 different ways:
 1) `BASIC_LUMP_CLASSES`
    Arrays of basic numeric types; e.g. `unsigned int  LUMP[LUMP_length / sizeof(unsigned int)];`
 2) `LUMP_CLASSES`
    Arrays of structs; e.g. `struct Vector { float x, y, z; };  Vector  LUMP[LUMP_length / sizeof(Vector)]`
 3) `SPECIAL_LUMP_CLASSES`
    These lumps are more complex. `bsp_tool` uses a specialised class to handle the raw bytes of the whole lump.

```python
# bsp_tool/branches/developer/branch_script.py
import enum

from .. import base  # LumpClass base classes
from .. import shared  # common Basic & SpecialLumpClasses


...  # LUMP definition etc.


class Vertex(base.MappedArray):
    _mapping = [*"xyz"]  # creates attribute names to map data to
    _format = "3f"  # python `struct` module format string
    # NOTE: ^ same as `struct Vertex { float x, y, z; };` in C

# {"LUMP_NAME": LumpClass}
# NOTE: Valve/Respawn branches use `{"LUMP_NAME": {LumpVersion: LumpClass}}` dicts
BASIC_LUMP_CLASSES = {"INDICES": shared.UnsignedShorts}

LUMP_CLASSES = {"VERTICES": Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}
```


### Game Lumps

A 4th type of LumpClass is used in Valve/Respawn branches: `GameLumpClass`

Lump `35`: `GAME_LUMP` has a master structure
```C
// game_lump.h
struct GameLumpHeader {
    int    id;     // four characters merged into an int; used like LUMP_NAME
    short  flags;
    short  version;
    int    offset;
    int    length;
};


// ids from Source SDK 2013 (src/public/gamebspfile.h:25)
#define MAKE_ID(a, b, c, d) ((a) << 24 | (b) << 16 | (c) << 8 | (d) << 0)
enum {
    GAME_LUMP_DETAIL_PROPS             = MAKE_ID('d', 'p', 'r', 'p'),
    GAME_LUMP_DETAIL_PROP_LIGHTING     = MAKE_ID('d', 'p', 'l', 't'),
    GAME_LUMP_STATIC_PROPS             = MAKE_ID('s', 'p', 'r', 'p'),
    GAME_LUMP_DETAIL_PROP_LIGHTING_HDR = MAKE_ID('d', 'p', 'l', 'h'),
};
#undef MAKE_ID


struct GameLump {
    unsigned int    count;
    GameLumpHeader  headers[count];
};
```

> NOTE: Each Valve / Respawn branch script defines / selects a `GameLumpHeader` class

This master structure indexes child lumps within the full length of the `GAME_LUMP` lump.  
```C
int             num_game_lumps;
GameLumpHeader  headers[num_game_lumps];
// @ headers[0].offset
char  game_lump_0_bytes[headers[0].length];
// @ headers[1].offset
char  game_lump_1_bytes[headers[1].length];
// to use, determine type from each game lump id
// GameLump0_t game_lump_0 = (GameLump0_t) game_lump_0_bytes;
// GameLump1_t game_lump_1 = (GameLump1_t) game_lump_1_bytes;
```


> NOTE: GameLumpHeader offsets are relative to the file, not the lump!  
> -- for this reason, a GameLump in a `.bsp` will not match that in an external `.lmp` or `.bsp_lump`!


To map game lump classes, `bsp_tool` does the following:
```python
# bsp_tool/branches/developer/branch_script.py
...

GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": {4: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv4)}}
```

Note the `GameLump_SPRP` class, this acts like a `SpecialLumpClass`, but also takes a child class as an argument.  
The `SpecialLumpClass` is defined as a `lambda` here to set the child class per game lump version

`sprp` or Static Prop GameLumps have the following structure:
```C
// game_lump_sprp.h
#define MAX_NAME_LEN 128

struct GameLump_SPRP {
    int         num_model_names;
    char        model_names[num_model_names][MAX_NAME_LEN];
    int         num_leaves;
    short       leaves[num_leaves];
    int         num_props;
    StaticProp  props[num_props];  // type varies with each lump version
};
```

Since only the type of the last component varies with each version, we pass it to `GameLump_SPRP` as an argument.  
This massively simplifies the codebase.

> NOTE: Support for multiple lump versions is acheived with a `MIN_VERSION` for legacy support  
> -- any lump from `MIN_VERSION` to `VERSION` is updated to the current type at load time  
> -- this system can't take advantage of new features, as it can only set missing fields to some default



## External lumps

Valve & Respawn engines support storing lump data in external files.
In the case of Valve branches, this can be used for quick pathes while keeping download sizes small.

Valve branches use `.lmp` files, these begin with a small header
```C
# external_lmp.h
struct LmpHeader{
    int  offset;    // should always be 20
    int  id;        // lump index / enum
    int  version;   // should match LumpHeader
    int  length;    // should match LumpHeader
    int  revision;  // should match BspHeader, or used to resolve file conflicts?
};
```
Followed by the lump data.

`.lmp` files are named `<bsp_name>_l_<id>.lmp`. Apparently some Left4Dead maps use `_h_` & `_s_` for certain gamemodes.[^VDC_lmp]

> NOTE: `GAME_LUMP` offsets may be relative to the `.lmp`, unsure if that includes the header


### Respawn `.bsp_lump`

Respawn branches use `.bsp_lump` files. These have no header and seem to match the lump in the `.bsp` one-to-one.

Naming convention: `<bsp_name>.bsp.<hex_id>.bsp_lump`

> NOTE: `<hex_id>` is always 4 characters, even though only `0000` to `007F` are used.

One exception is Titanfall 2 lightmaps, some of which expect a different lump size.

Apex Legends maps after Season 11 only keep the `BspHeader` in the `.bsp`, with all lump data in `.bsp_lump`s  
There seems to be a flag set next to `version` to indicate this



## Footnote

[^VDC_lmp]: Valve Developer Community: [`.lmp` file format](https://developer.valvesoftware.com/wiki/Lump_file_format)
