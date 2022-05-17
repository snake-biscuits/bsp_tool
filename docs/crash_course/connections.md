# `.bsp` Lump Interconnections

For the purposes of efficiency, objects in `.bsp` are split into multiple different lumps

Some lumps are dependant on others, some and all sorts of lumps can refer to others.

The main way of referencing another lump is to use it's index, though some lumps index via offset.

This is mostly used to index complex lumps (`SpecialLumpClasses`) which may be RLE compressed,
or contain tightly packed objects of varying length.
 * `id_software.quake.Visibility` is RLE compressed (but only bytes of value 0)
 * `id_software.quake.MipTextureLump` holds structs of varying length


## `LumpClasses` indexing `BasicLumpClasses`

One lump can index multiple other lumps. Usually a `struct` indexes another `struct`, though any combination is possible.



```C
// source.h
struct Face {
    unsigned short  plane;                  // indexes Planes
    char            side;
    bool            on_node;
    int             first_edge;             // indexes SurfEdges
    short           num_edges;              // ^ number of SurfEdges tied to this Face
    short           texture_info;           // indexes TextureInfos
    short           displacement_info;      // indexes DisplacementInfos
    short           surface_fog_volume_id;  // possibly deprecated
    char            styles[4];              // relevant to Lighting (multiplies length)
    int             light_offset;           // offset into Lighting
    float           area;
    int             lightmap_mins[2];
    int             lightmap_size[2];       // used to calculate length of Lighting indexing
    int             original_face;          // indexes OriginalFaces
    unsigned short  num_primitives;         // number of Primitives tied to this Face
    unsigned short  first_primitive;        // ^ indexes Primitives
    unsigned int    smoothing_group;  
};
```

> TODO: index types & engine limits (`MAX_EDGES = 65535` etc.)


## Mapping connections

`bsp_tool` list lump connections after the `LUMP` definition in each branch script.

```python
# bsp_tool/branches/valve/source.py
import enum

...


class LUMP(enum.Enum):
    ...
    UNUSED_62 = 62
    UNUSED_63 = 63


class LumpHeader(base.MappedArray):
    _mapping = ["offset", "length", "version", "fourCC"]
    _format = "4I"

# changes from GoldSrc -> Source:
# MipTexture.flags -> TextureInfo.flags (Surface enum)


# a rough map of the relationships between lumps:

#     /-> SurfEdge -> Edge -> Vertex
# Face -> Plane
#    \--> TextureInfo -> TextureData -> TextureDataStringTable
#     \-> DisplacementInfo -> DisplacementVertex

...
```

> TODO: Database design principles (Normalised Form, Entity Integrity, Strong Relationships, M:N -> 2x 1:M)

> TODO: Primary Keys & Foreign Keys

> TODO: Database construction order

> TODO: Compile process & order
