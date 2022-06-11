# Exploring Titanfall CM_BRUSH_SIDE_TEXTURE_VECTORS

```python
>>> import bsp_tool
>>> from bsp_tool.extensions.decompile_rbsp import *
>>> box = bsp_tool.load_bsp("/home/bikkie/Documents/Mod/Titanfall/maps/mp_box.bsp")
>>> axis_name = {vec3(x=1): "+X", vec3(x=-1): "-X", vec3(y=1): "+Y", vec3(y=-1): "-Y", vec3(z=1): "+Z", vec3(z=-1): "-Z"}
>>> def tvn(tv):
...     s = vec3(tv.s.x, tv.s.y, tv.s.z).normalised()
...     t = vec3(tv.t.x, tv.t.y, tv.t.z).normalised()
...     return "".join([axis_name.get(v, str(v)) for v in (s, t)])
... 
>>> ptvn = lambda n: "".join([axis_name[v] for v in face_texture_vectors(n.normalised())])
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[0]), ptvn(vec3(x=1))
('-Y-Z', '+Y-Z')
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[1]), ptvn(vec3(x=-1))
('+Y-Z', '-Y-Z')
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[2]), ptvn(vec3(y=1))
('+X-Z', '+X-Z')
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[3]), ptvn(vec3(y=-1))
('-X-Z', '-X-Z')
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[4]), ptvn(vec3(z=1))
('+Y-X', '+X-Y')
>>> tvn(box.CM_BRUSH_SIDE_TEXTURE_VECTORS[5]), ptvn(vec3(z=-1))
('+Y+X', '-X-Y')
>>> # looks like different projection rules
>>> # might be some rotation at play here, idk why tho
>>> # all 6 TextureVectors should look OK on world axes
```
