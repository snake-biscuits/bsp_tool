# bsp_tool
bsp_tool has no UI, the main script only provides a python interface to the contents of a given .bsp  

`bsp_tool.py` provides the `bsp` class: the interface for data loaded from a .bsp file  
bsp_tool can load .bsp files from most Source Engine games, Titanfall 2 & Apex Legends  

The `mods/` folder contains classes for interpretting the lumps within .bsp files  
Different Source Engine mods can use different lump specifications, so bsp_tool needs to know which is correct for a given .bsp  
`mods/common.py` provides some handy helper classes for defining the classes which shape most lumps  
`mods/vindictus.py` is a good example of extenting another mod (`vindictus.py` extends `team_fortress2.py`)  
Not every lump is understood, such lumps are stored as RAW lumps  
By default, bsp_tool assumes .bsps are version 20 (Team Fortress 2)  
  
The `examples/` folder contains a number of scripts which utilise bsp_tool for various tasks  
Many of these scripts are old experiments, and as a result are not well maintained  

### Converting .bsp to .obj
  Navigate to `examples/`  
  Drag the desired .bsp file(s) over `obj_model_from_bsp.py`  
  An .obj file will appear next to the .bsp, wherever you dragged it from
  
### Rendering .bsp files in 3D
  `examples/render_bsp.py` requires some external libraries  
  Install them by running `$ pip install -r requirements.txt` in `bsp_tool/examples/`  
  `render_bsp.py` is intended to be run from an editor, bsps are fed to the script manually
 
