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

calling this function at the end of the file, in the `if __name__ == "__main__":` section and saving the contents to a file is advised, as this can take a while and really fill up a terminal  
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
While it hasn't been implemented, this data could easily be exported to a `.json` or similar database for used in external programs, helping to map out the relationship between lightmap and `.bsp` geometry  

`lightmaps.py` provides functions for loading lightmaps from `IdTechBsp` (Quake III), `ValveBsp` and `RespawnBsp` **(Titanfall 2 ONLY)**  
```python
def save_ibsp(ibsp: bsp_tool.IdTechBsp, folder="./"):
    """Saves to {folder}/{ibsp.filename}.lightmaps.png"""
    # stitches 3x 512x512 RGB_888 images

def save_vbsp(vbsp: bsp_tool.ValveBsp, folder="./"):
    """Saves to {folder}/{vbsp.filename}.lightmaps.png"""
    # each face has a uniquely shaped lightmap

def save_rbsp(rbsp: bsp_tool.RespawnBsp, folder="./"):  # TITANFALL 2 ONLY!
    """Saves to {folder}/{rbsp.filename}.sky.lightmaps.png"""
    # rBSP have a LIGHTMAP_HEADERS lump, Titanfall 1, 2 & Apex all vary
    # Titanfall 2 appears to have two consecutive entries per LightmapHeader
    # both of equal size and 2 in both the LIGHTMAP_DATA_SKY & LIGHTMAP_DATA_REAL_TIME_LIGHTS lumps
    # Titanfall 1 appears to only have one for each?
    # Apex is different again
    # They appear to map: base lightmap albedo, areas covered by dynamic light, surface normals & dot(sunVector, N)
    # TLDR: Since RespawnBsp varies a lot when it comes to lightmaps, only Titanfall2 is supported currently
```

> TODO: Load and present lightmaps with blender bsp viewer / editor scripts


## lump_analysis.py
This script requires no dependencies  
Similar to `diff.py`, provides functions for comparing `.bsp` headers  

Noteworthy:  
`headers_markdown`: used to generate markdown listing `.bsp` headers  
`sizes_csv`: generates `.csv` files comparing multiple `.bsps` and guessing lump entry sizes based on variations in lump size  

Everything else is either helper functions to help with abstraction or quick tools for analysing raw data  
