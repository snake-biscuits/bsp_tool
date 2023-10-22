### Citations
Source code & wiki links go at the top of the script
```python
# https://github.com/.../bspfile.h
```
Specific citations can be used in `LumpClass` definitions
Though only if the whole source isn't cited at the top of the script


### Imports
```python
# builtins
import enum

# local utilities
from .. import base  # LumpClass baseclasses
from . import parent  # same developer
from developer import branch
```
Imported branches should always be from a predecessor
This is why `mohaa` imports `mohaa_demo`, even though `mohaa` is more common


### Metadata
Sample from `quake.py`
```python
FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = {"DarkPlaces": "DarkPlaces", "Quake": "Quake",
              "Team Fortress Quake": "QUAKE/FORTRESS"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}
```


### `LUMP` enum
```python
class LUMP(enum.Enum):
    ENTITIES = 0
    ...
```


### `LumpHeader` `LumpClass`
Sample from `quake.py`
```python
class LumpHeader(base.MappedArray):
    _mapping = ["offset", "length"]
    _format = "2I"
```
Most will shrimply copy a root definition
```python
LumpHeader = quake.LumpHeader
```

### Summary of lump relationships
### Lump changes relative to parent
### `Enum`s & `IntFlag`s
### `LumpClass` definitions
### `SpecialLumpClass` definitions
### `LUMP_CLASS` dictionaries
### methods
