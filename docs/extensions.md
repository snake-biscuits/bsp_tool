# `bsp_tool` Extensions
`bsp_tool/extensions` holds various extension scripts that use bsp_tool to do various operations


## archive.py
This script requires no dependencies  
`archive.py` has tools for opening and searching `.iwd`, `.ff` & `.pk3` archives

`.pk3` files are used to store maps for Quake III & Call of Duty 1  
`.iwd` files are used to store maps for Call of Duty 2

The `Pk3` and `Iwd` classes are identical, they open `.pk3` / `.iwd` files
Since both formats are similar to `.zip`, they both extend `zipfile.ZipFile`

Both classes also provide the following two methods:
```python
def extract_match(self, pattern="*.bsp", path=None):
    for filename in self.search(pattern):
        self.extract(filename, path)

def search(self, pattern="*.bsp"):
    return fnmatch.filter(self.namelist(), pattern)
```
`extract_match` uses the builtin `fnmatch` libary to search for file extensions, and extracts matches to `path`
`search` also uses `fnmatch`, but only returns a list of matching filenames, without extracting

There is also a `FastFile` class for extracting data from `.ff` files, containing Call of Duty 4 maps, however this class is currently incomplete.
The format seems to hold many files crushed together with `zlib` compression, then places headers between files denoting type, but not length?
Understanding the formats of compressed files may be essential to unpacking this format.

Finally there are two functions:
```python
search_folder(folder, pattern="*.bsp", archive="*.pk3")

extract_folder(folder, pattern="*.bsp", path=None, archive="*.pk3")
```
Each search `folder` for archives, and run the `extract_match` & `search` methods or each archive found


## diff.py
This script requires no dependencies
`diff.py` has tools for comparing `.bsp`s, handy for comparing ported maps

Being somewhat purpose built, the script is focused on comparing Titanfall 1 & 2 maps
The following functions are provided:
```python
def diff_bsps(bsp1, bsp2, full=False):
    """Compares .bsps lump by lumps, printing comparisons"""

def diff_rbsps(rbsp1, rbsp2, full=False):
    """Same as diff_bsps but also compares .ent files"""

def diff_entities(bsp1: RespawnBsp, bsp2: RespawnBsp):
    """semi-context aware diff of entities"""

def diff_pakfiles(bsp1: RespawnBsp, bsp2: RespawnBsp):
    """semi-context aware diff of pakfile lumps"""

def dump_headers(maplist):  # just for r1 / r1o / r2  (Titanfall Games)
    """Takes a specific list and compares Titanfall 1 to Titanfall 2 maps"""

def split(iterable: Iterable, chunk_size: int) -> Iterable:
    """Used by xxd to split up data into rows"""

def xxd(data: bytes, width: int = 32) -> str:
    """quick and dirty hex-editor view of bytes; yields one line at a time"""
```

`diff_bsps` goes through headers numerically and prints `Y` or `N` for each int in the header  
It then compares the raw binary of each `.bsp`'s lump, and prints `YES!` or `NOPE` to indicate a match  
If some error occurs, or the lumps is empty, `????` is printed instead  
Setting `full` to `True` will use `difflib` to show the differences in bytes

> TODO: changing this to compare the __repr__ of the mapped lump would be better

calling this function at the end of the file, in the `if __name__ == "__main__":` section and saving the output to a file is advised, as this can take a while and really fill up a terminal
```sh
$ python bsp_tool/extensions/diff.py > diff_results/css_cso2_dust2.txt
```

`diff_entities` and `diff_pakfiles` give more targetted diffs for special lumps  
`dump_headers` is a purpose built function, with hardcoded filepaths; It probably won't work  
`xxd` is a quick handy little function for printing out bytes in a pretty way  
It is not meant to replace a hex editor (like xxd for example), but is just a lazy tool


## lightmaps.py
This script depends on `PIL` or `Pillow`
```python
$ pip install Pillow
```

Using the Python Image Library, lightmaps are stitched into .png files  
The `LightmapPage` class creates an infinitely scrolling image to paste smaller images into, as well as handling image packing somewhat.  
Adding an image to a `LightmapPage` is done with the `__add__` operator override  
The exported image is not created until the `.image` property is accessed  
`LightmapPage`s also contain a `.children` attribute: a dictionary holding the coordinate of every child `Image`  

`lightmaps.py` provides functions for loading lightmaps from `IdTechBsp` (Quake III), `ValveBsp` and `RespawnBsp` **(Titanfall 2 ONLY)**
```python
def save_ibsp(ibsp: bsp_tool.IdTechBsp, image_dir="./"):  # Quake III?
    """Saves to {folder}/{ibsp.filename}.lightmaps.png"""
    # stitches 3x 512x512 RGB_888 images

def save_vbsp(vbsp: bsp_tool.ValveBsp, image_dir="./"):
    """Saves to {folder}/{vbsp.filename}.lightmaps.png"""
    # each face has a uniquely shaped lightmap

def save_rbsp_r1(rbsp: bsp_tool.RespawnBsp, image_dir="./"):  # Titanfall 1
    """Saves to {folder}/{rbsp.filename}.sky/rtl.png"""
    # LIGHTMAP_HEADERS + LIGHTMAP_DATA_SKY + LIGHTMAP_DATA_RTL

def save_rbsp_r2(rbsp: bsp_tool.RespawnBsp, image_dir="./"):  # Titanfall 2
    """Saves to {folder}/{rbsp.filename}.sky/rtl.png"""
    # LIGHTMAP_HEADERS + LIGHTMAP_DATA_SKY + LIGHTMAP_DATA_RTL
    # outputs a .json with each lightmap page

def write_rbsp_r2(rbsp: bsp_tool.RespawnBsp, image_dir="./"):  # Titanfall 2
    """Finds extracted .png & .json(s) and writes new lightmaps to rbsp"""
    # LIGHTMAP_HEADERS + LIGHTMAP_DATA_SKY + LIGHTMAP_DATA_RTL
```

> TODO: Use .jsons with every output, & use these to generate lightmap uvs in Blender

### Editing Titanfall 2 lightmaps
```python
>>> import bsp_tool
>>> from bsp_tool.extensions import lightmaps
>>> bsp_tool.load_bsp(".../maps/mp_lf_deck.bsp")
<RespawnBsp 'mp_lf_deck.bsp' titanfall2 (rBSP version 37) at 0x000001D4DF197160>
>>> deck = _
>>> lightmaps.save_rbsp_r2(deck)
# creates mp_lf_deck.bsp.rtl.png, .rtl.json, .sky.png & .sky.json
```
Then edit the .png images
In the same folder...
```python
>>> import bsp_tool
>>> from bsp_tool.extensions import lightmaps
>>> deck = bsp_tool.load_bsp(".../maps/mp_lf_deck.bsp")
>>> lightmaps.write_rbsp_r2(deck)
```

> NOTE: both `save_rbsp_r2()` & `write_rbsp_r2()` has an optional `image_dir` argument



## lump_analysis.py
This script requires no dependencies
Similar to `diff.py`, provides functions for comparing `.bsp` headers

Noteworthy:
`headers_markdown`: used to generate markdown listing `.bsp` headers
`sizes_csv`: generates `.csv` files comparing multiple `.bsps` and guessing lump entry sizes based on variations in lump size

Everything else is either helper functions to help with abstraction or quick tools for analysing raw data
