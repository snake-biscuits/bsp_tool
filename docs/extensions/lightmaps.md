# `extensions.lightmaps`
Depends on `Pillow`
```
$ pip install Pillow
```
```python
import PIL
```

Most of the converters group all the lightmaps as tiles

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
