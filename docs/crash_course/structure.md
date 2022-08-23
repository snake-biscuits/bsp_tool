# `.bsp` File Structure

All `.bsp` contain multiple "lumps", a variety of structures used by the game engine as a sort of database, representing a level.

The number of lumps & use varies from branch to branch.


## Lumps

In `bsp_tool`, each "branch script" enumerates lump names in `LUMP`

```python
# bsp_tool/branches/developer/branch.py
import enum


class LUMP(enum.Enum):
    ENTITIES = 0
    INDICES = 1  # not a real lump, used for later examples
    VERTICES = 2
    ...
```

The value of each `LUMP` enum is an index into the lump headers section of the `.bsp` file header.
```C
/* quake_bsp.h */
#include <stdint.h>

#define NUM_LUMPS  17


struct LumpHeader {
    uint32_t  offset;
    uint32_t  length;
};

struct BspHeader {
    uint32_t    version;
    LumpHeader  headers[NUM_LUMPS];
};
```

> NOTE: In `bsp_tool`: `LumpHeader` is defined per branch script, and `BspHeader` is defined per `BspClass`  
> -- `BspClasses` are defined in scripts which import `bsp_tool.base.Bsp`  
> -- the header is processed by the `_preload` method

We use the names of the `LUMP` enums to identify the structure of each lump.

> NOTE: Valve & Respawn variants of the `.bsp` format have per-lump format versions


### LumpClasses

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


## Game Lumps

A 4th type of LumpClass is used in Valve/Respawn branches: `GameLumpClass`

Lump `35`: `GAME_LUMP` has a master structure
```C
/* game_lump.h */
#include <stdint.h>


struct GameLumpHeader {
    int32_t  id;
    int16_t  flags;
    int16_t  version;
    int32_t  offset;
    int32_t  length;
};


/* NOTE: ids are 4 char as int; identifies LUMP type */
/* taken from Source SDK 2013 (src/public/gamebspfile.h:25) */
#define MAKE_ID(a, b, c, d) ((a) << 24 | (b) << 16 | (c) << 8 | (d) << 0)
enum {
    GAME_LUMP_DETAIL_PROPS             = MAKE_ID('d', 'p', 'r', 'p'),
    GAME_LUMP_DETAIL_PROP_LIGHTING     = MAKE_ID('d', 'p', 'l', 't'),
    GAME_LUMP_STATIC_PROPS             = MAKE_ID('s', 'p', 'r', 'p'),
    GAME_LUMP_DETAIL_PROP_LIGHTING_HDR = MAKE_ID('d', 'p', 'l', 'h'),
};
#undef MAKE_ID


struct GameLump {
    uint32_t        count;
    GameLumpHeader  headers[count];
};
```

> NOTE: Each Valve / Respawn branch script defines / selects a `GameLumpHeader` class

This master structure indexes child lumps within the full length of the `GAME_LUMP` lump.  
```C
uint32_t        num_game_lumps;
GameLumpHeader  headers[num_game_lumps];
/* NOTE: most lumps are in series like this
 * however: each lump should be byte-algined to 4 bytes for 32-bit CPUs
 * most structures will fit this nicely, but sometimes lumps are compressed
 * it's generally best to respect the headers vs. making assumptions.
*/
/* @ headers[0].offset */
char  game_lump_0_bytes[headers[0].length];
/* @ headers[1].offset */
char  game_lump_1_bytes[headers[1].length];
/* to use, determine type from each game lump id
 * GameLump0_t  game_lump_0 = (GameLump0_t) game_lump_0_bytes;
 * GameLump1_t  game_lump_1 = (GameLump1_t) game_lump_1_bytes;
*/
```


> NOTE: GameLumpHeader offsets are relative to the file, not the lump!  
> -- for this reason, a GameLump in a `.bsp` will not match that in an external `.lmp` or `.bsp_lump`!



### GameLumpClasses

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
/* game_lump_sprp.h */
#include <stdint.h>

#define MAX_NAME_LEN 128


struct GameLump_SPRP {
    int32_t     num_model_names;
    char        model_names[num_model_names][MAX_NAME_LEN];
    int32_t     num_leaves;
    int16_t     leaves[num_leaves];
    int32_t     num_props;
    StaticProp  props[num_props];
    /* NOTE: StaticProp is an abstraction here.
     * most SPRP lumps keep this master structure
     * StaticProp format will vary per lump version
    */
};
```

Since only the format of `StaticProp` varies with each version, we pass a `StaticPropClass` to `GameLump_SPRP`.  
Recycling code like this generally simplifies maintenance as well as letting new feature bleed across branches.


### Backwards Compatability

In the engine codebases, sometimes a game needs to support multiple lump or bsp formats.  
This is achieved with a `MIN_VERSION` constant which the engine checks at loadtime.  
Runtime formats are locked to the latest format for the sake of simplicity;
To get older formats to behave, they are updated to the latest version by using default values for new fields.

Older maps don't get to take advantage of newer features with this approach, but it can make development easier.  
Having to recompile all maps to test a new feature set could seriously hurt iteration time.


## External lumps

Valve & Respawn engines support storing lump data in external files.
In the case of Valve branches, this can be used for quick pathes while keeping download sizes small.

Valve branches use `.lmp` files, these begin with a small header
```C
/* external_lmp.h */
#include <stdint.h>


struct LmpHeader{
    uint32_t  offset;    /* should always be sizeof(LmpHeader) */
    uint32_t  id;        /* lump index */
    uint32_t  version;   /* should match LumpHeader */
    uint32_t  length;    /* should match LumpHeader */
    uint32_t  revision;  /* should match BspHeader, or used to resolve file conflicts? */
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
There seems to be a flag set within `version` to indicate this (went from 1x `uint32_t` to 2x `uint16_t`)



## References

[^VDC_lmp]: Valve Developer Community: [`.lmp` file format](https://developer.valvesoftware.com/wiki/Lump_file_format)
