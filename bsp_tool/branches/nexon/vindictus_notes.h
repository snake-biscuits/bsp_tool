Vindictus generally uses a lot more integers in place of shorts for its map data structures.

Also, vindictus uses a different dgamelump_t format:  
```c
struct dgamelump_t
{
    int    id;       // gamelump ID
    int    flags;    // flags
    int    version;  // gamelump version
    int    fileofs;  // offset to this gamelump
    int    filelen;  // length
};
```


Nodes and Leaves are also different, mainly changed to use ints instead of shorts:  
```c
struct dnode_t
{
    int    planenum;     // index into plane array
    int    children[2];  // negative numbers are -(leafs + 1), not nodes
    int    mins[3];      // for frustum culling
    int    maxs[3];
    int    firstface;    // index into face array
    int    numfaces;     // counting both sides
    int    unknown;      // seems to always be 0
};
```

The Leaf structure, among other things, does away with the area field, and flags has its own integer field.  
```c
struct dleaf_t
{
    int           contents;         // OR of all brushes (not needed?)
    int           cluster;          // cluster this leaf is in
    int           flags;            // flags
    int           mins[3];          // for frustum culling
    int           maxs[3];
    unsigned int  firstleafface;    // index into leaffaces
    unsigned int  numleaffaces;
    unsigned int  firstleafbrush;   // index into leafbrushes
    unsigned int  numleafbrushes;
    int           leafWaterDataID;  // -1 for not in water
};
```

Faces use one of two different structures, 72 bytes or 76 bytes, depending on the lump version in the file header.
Once again, the biggest difference is changing from shorts to ints:  
```c
struct dface_t
{
    unsigned int  plane;  // index of Plane
    byte          side;
    byte          on_node;  // 1 of on node, 0 if in leaf
    short         unknown_1;  // always 0?
    int           first_edge;  // index of SurfEdge
    int           num_edges;
    int           texture_info;  // index of TextureInfo
    int           displacement_ info;  // index of DisplacementInfo
    int           surfaceFogVolumeID;
    // Comment this unknown for v1
    int           unknown_2;  // v2 Faces only. Always negative?
    byte          styles[4];
    int           lightofs;  // offset into lightmap lump
    float         area;  // face area in units^2
    int           LightmapTextureMinsInLuxels[2];  // texture lighting info
    int           LightmapTextureSizeInLuxels[2];  // texture lighting info
    unsigned int  origFace;  // original face this was split from
    unsigned int  numPrims;  // primitives
    unsigned int  firstPrimID;
    unsigned int  smoothingGroups;  // lightmap smoothing group
};
```

Brush sides have an identical format, except using ints instead of shorts:  
```c
struct dbrushside_t
{
    unsigned int  plane;
    int           texture_info;
    int           displacement_info;
    int           bevel;
};
```

Edges are also identical except for using ints:
```c
struct dedge_t { unsigned int v[2]; };
```


With 232 bytes, the displacement info struct of Vindictus is notably bigger than the conventional 176 byte struct in other Source engine games.
This is mostly because of CDispNeighbor and CDispCornerNeighbors using ints instead of shorts:

struct ddispinfo_t
{
    Vector                startPosition;
    int                   DispVertStart;
    int                   DispTriStart;
    int                   power;
    float                 smoothingAngle;
    int                   unknown;
    int                   contents;
    unsigned int          MapFace;
    int                   LightmapAlphaStart;
    int                   LightmapSamplePositionStart;
    CDispNeighbor         EdgeNeighbors[4];
    CDispCornerNeighbors  CornerNeighbors[4];
    unsigned int          AllowedVerts[10];
};


Vindictus' Static Props v5 is identical to vanilla Source engine.
However, Vindictus maps may instead use a v6 Static Props lump that is different from the normal v6 Props.
The StaticPropLump_t struct remains the same (like v5 Static Props) but there is an additional struct inserted between the StaticPropLeafLump_t array and the StaticPropLump_t array,
perhaps providing additional prop scaling information.
As with the other arrays, this struct begins with an int declaring how many elements there are. There seems to always be the same amount of this struct as there are StaticPropLump_t.
```c
struct StaticPropScales_t
{
    int staticProp; // Index into the StaticPropLump_t array
    Vector  scale;      // Speculative, is this really scaling?
};
```

The overlay structure also follows the change from short to int:
```c
struct doverlay_t
{
    int           Id;
    int           TexInfo;
    unsigned int  FaceCountAndRenderOrder;
    int           Ofaces[OVERLAY_BSP_FACE_COUNT];
    float         U[2];
    float         V[2];
    Vector        UVPoints[4];
    Vector        Origin;
    Vector        BasisNormal;
};
```

So does the areaportal structure:
```c
struct dareaportal_t
{
    unsigned int  portalKey;  // binds the area portal to a func_areaportal entity with the same portalnumber key
    unsigned int  otherarea;  // The area this portal looks into.
    unsigned int  firstClipPortalVert;  // Portal geometry.
    unsigned int  clipPortalVerts;
    int           planenum;
};
```

The LeafFace and LeafBrush lumps also use unsigned ints rather than unsigned shorts.
