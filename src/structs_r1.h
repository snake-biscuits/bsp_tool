// titanfall 1 bsp types
#include <stdbool.h>


enum {
        LUMP_ENTITIES = 0x0000, // 0
        LUMP_PLANES = 0x0001, // 1
        LUMP_TEXDATA = 0x0002, // 2
        LUMP_VERTEXES = 0x0003, // 3
        LUMP_DEPRECATED_4 = 0x0004, // 4
        LUMP_DEPRECATED_5 = 0x0005, // 5
        LUMP_UNUSED_6 = 0x0006, // 6
        LUMP_UNUSED_7 = 0x0007, // 7
        LUMP_UNUSED_8 = 0x0008, // 8
        LUMP_UNUSED_9 = 0x0009, // 9
        LUMP_DEPRECATED_10 = 0x000a, // 10
        LUMP_UNUSED_11 = 0x000b, // 11
        LUMP_UNUSED_12 = 0x000c, // 12
        LUMP_UNUSED_13 = 0x000d, // 13
        LUMP_MODELS = 0x000e, // 14
        LUMP_UNUSED_15 = 0x000f, // 15
        LUMP_DEPRECATED_16 = 0x0010, // 16
        LUMP_UNUSED_17 = 0x0011, // 17
        LUMP_UNUSED_18 = 0x0012, // 18
        LUMP_UNUSED_19 = 0x0013, // 19
        LUMP_DEPRECATED_20 = 0x0014, // 20
        LUMP_DEPRECATED_21 = 0x0015, // 21
        LUMP_DEPRECATED_22 = 0x0016, // 22
        LUMP_DEPRECATED_23 = 0x0017, // 23
        LUMP_ENTITYPARTITIONS = 0x0018, // 24
        LUMP_UNUSED_25 = 0x0019, // 25
        LUMP_UNUSED_26 = 0x001a, // 26
        LUMP_UNUSED_27 = 0x001b, // 27
        LUMP_UNUSED_28 = 0x001c, // 28
        LUMP_PHYSCOLLIDE = 0x001d, // 29
        LUMP_VERTNORMALS = 0x001e, // 30
        LUMP_UNUSED_31 = 0x001f, // 31
        LUMP_UNUSED_32 = 0x0020, // 32
        LUMP_UNUSED_33 = 0x0021, // 33
        LUMP_UNUSED_34 = 0x0022, // 34
        LUMP_GAME_LUMP = 0x0023, // 35
        LUMP_LEAFWATERDATA = 0x0024, // 36
        LUMP_UNUSED_37 = 0x0025, // 37
        LUMP_UNUSED_38 = 0x0026, // 38
        LUMP_UNUSED_39 = 0x0027, // 39
        LUMP_PAKFILE = 0x0028, // 40
        LUMP_DEPRECATED_41 = 0x0029, // 41
        LUMP_CUBEMAPS = 0x002a, // 42
        LUMP_TEXDATA_STRING_DATA = 0x002b, // 43
        LUMP_TEXDATA_STRING_TABLE = 0x002c, // 44
        LUMP_UNUSED_45 = 0x002d, // 45
        LUMP_DEPRECATED_46 = 0x002e, // 46
        LUMP_UNUSED_47 = 0x002f, // 47
        LUMP_UNUSED_48 = 0x0030, // 48
        LUMP_UNUSED_49 = 0x0031, // 49
        LUMP_UNUSED_50 = 0x0032, // 50
        LUMP_UNUSED_51 = 0x0033, // 51
        LUMP_UNUSED_52 = 0x0034, // 52
        LUMP_DEPRECATED_53 = 0x0035, // 53
        LUMP_WORLDLIGHTS_HDR = 0x0036, // 54
        LUMP_UNUSED_55 = 0x0037, // 55
        LUMP_UNUSED_56 = 0x0038, // 56
        LUMP_UNUSED_57 = 0x0039, // 57
        LUMP_UNUSED_58 = 0x003a, // 58
        LUMP_DEPRECATED_59 = 0x003b, // 59
        LUMP_UNUSED_60 = 0x003c, // 60
        LUMP_UNUSED_61 = 0x003d, // 61
        LUMP_PHYSLEVEL = 0x003e, // 62
        LUMP_UNUSED_63 = 0x003f, // 63
        LUMP_UNUSED_64 = 0x0040, // 64
        LUMP_UNUSED_65 = 0x0041, // 65
        LUMP_TRICOLL_TRIS = 0x0042, // 66
        LUMP_UNUSED_67 = 0x0043, // 67
        LUMP_TRICOLL_NODES = 0x0044, // 68
        LUMP_TRICOLL_HEADERS = 0x0045, // 69
        LUMP_PHYSTRIS = 0x0046, // 70
        LUMP_VERTS_UNLIT = 0x0047, // 71
        LUMP_VERTS_LIT_FLAT = 0x0048, // 72
        LUMP_VERTS_LIT_BUMP = 0x0049, // 73
        LUMP_VERTS_UNLIT_TS = 0x004a, // 74
        LUMP_VERTS_BLINN_PHONG = 0x004b, // 75
        LUMP_VERTS_RESERVED_5 = 0x004c, // 76
        LUMP_VERTS_RESERVED_6 = 0x004d, // 77
        LUMP_VERTS_RESERVED_7 = 0x004e, // 78
        LUMP_MESH_INDICES = 0x004f, // 79
        LUMP_MESHES = 0x0050, // 80
        LUMP_MESH_BOUNDS = 0x0051, // 81
        LUMP_MATERIAL_SORT = 0x0052, // 82
        LUMP_LIGHTMAP_HEADERS = 0x0053, // 83
        LUMP_LIGHTMAP_DATA_DXT5 = 0x0054, // 84
        LUMP_CM_GRID = 0x0055, // 85
        LUMP_CM_GRIDCELLS = 0x0056, // 86
        LUMP_CM_GEO_SETS = 0x0057, // 87
        LUMP_CM_GEO_SET_BOUNDS = 0x0058, // 88
        LUMP_CM_PRIMS = 0x0059, // 89
        LUMP_CM_PRIM_BOUNDS = 0x005a, // 90
        LUMP_CM_UNIQUE_CONTENTS = 0x005b, // 91
        LUMP_CM_BRUSHES = 0x005c, // 92
        LUMP_CM_BRUSH_SIDE_PLANE_OFFSETS = 0x005d, // 93
        LUMP_CM_BRUSH_SIDE_PROPS = 0x005e, // 94
        LUMP_CM_BRUSH_TEX_VECS = 0x005f, // 95
        LUMP_TRICOLL_BEVEL_STARTS = 0x0060, // 96
        LUMP_TRICOLL_BEVEL_INDEXES = 0x0061, // 97
        LUMP_LIGHTMAP_DATA_SKY = 0x0062, // 98
        LUMP_CSM_AABB_NODES = 0x0063, // 99
        LUMP_CSM_OBJ_REFS = 0x0064, // 100
        LUMP_LIGHTPROBES = 0x0065, // 101
        LUMP_STATIC_PROP_LIGHTPROBE_INDEX = 0x0066, // 102
        LUMP_LIGHTPROBETREE = 0x0067, // 103
        LUMP_LIGHTPROBEREFS = 0x0068, // 104
        LUMP_LIGHTMAP_DATA_REAL_TIME_LIGHTS = 0x0069, // 105
        LUMP_CELL_BSP_NODES = 0x006a, // 106
        LUMP_CELLS = 0x006b, // 107
        LUMP_PORTALS = 0x006c, // 108
        LUMP_PORTAL_VERTS = 0x006d, // 109
        LUMP_PORTAL_EDGES = 0x006e, // 110
        LUMP_PORTAL_VERT_EDGES = 0x006f, // 111
        LUMP_PORTAL_VERT_REFS = 0x0070, // 112
        LUMP_PORTAL_EDGE_REFS = 0x0071, // 113
        LUMP_PORTAL_EDGE_ISECT_EDGE = 0x0072, // 114
        LUMP_PORTAL_EDGE_ISECT_AT_VERT = 0x0073, // 115
        LUMP_PORTAL_EDGE_ISECT_HEADER = 0x0074, // 116
        LUMP_OCCLUSIONMESH_VERTS = 0x0075, // 117
        LUMP_OCCLUSIONMESH_INDICES = 0x0076, // 118
        LUMP_CELL_AABB_NODES = 0x0077, // 119
        LUMP_OBJ_REFS = 0x0078, // 120
        LUMP_OBJ_REF_BOUNDS = 0x0079, // 121
        LUMP_DEPRECATED_122 = 0x007a, // 122
        LUMP_LEVEL_INFO = 0x007b, // 123
        LUMP_SHADOW_MESH_OPAQUE_VERTS = 0x007c, // 124
        LUMP_SHADOW_MESH_ALPHA_VERTS = 0x007d, // 125
        LUMP_SHADOW_MESH_INDICES = 0x007e, // 126
        LUMP_SHADOW_MESH_MESHES = 0x007f, // 127
};

/* Common structs */
struct Vector3 { float x, y, z; };
struct Vector2D { float x, y; };
struct Quaternion { float x, y, z, w; };

struct lump_t {
        /* 0x0000 */ int  fileofs; // size: 4
        /* 0x0004 */ int  filelen; // size: 4
        /* 0x0008 */ int  version; // size: 4
        /* 0x000c */ int  uncompLen; // size: 4
};

struct BSPHeader_t {
        /* 0x0000 */ int            ident; // size: 4
        /* 0x0004 */ int            m_nVersion; // size: 4
        /* 0x0008 */ int            mapRevision; // size: 4
        /* 0x000c */ int            lastLump; // size: 4
        /* 0x0010 */ struct lump_t  lumps[128]; // size: 16 * 128
};

struct CompressedLightCube {  // Source Engine?
        /* 0x0000 */ char m_Color[24]; // size: 24
};

struct dlightproberef_t {
        /* 0x0000 */ struct Vector3  pos; // size: 12
        /* 0x000c */ int             lightProbeIndex; // size: 4
};

struct dlightprobetree_t {
        /* 0x0000 */ int tag; // size: 4
        /* 0x0004 */ int numEntries; // size: 4
};

struct dlightprobe_t
{
        /* 0x0000 */ short  ambientSH[12]; // size: 24
        /* 0x0018 */ short  skyDirSunVis[4]; // size: 8
        /* 0x0020 */ char   staticLightWeights[4]; // size: 4
        /* 0x0024 */ short  staticLightIndexes[4]; // size: 8
        /* 0x002c */ char   pad[4]; // size: 4
};

struct dvertex_t {  // could just type alias tbh
        /* 0x0000 */ struct Vector3  point; // size: 12
};

struct dcell_bsp_t {
        /* 0x0000 */ int  planeNum; // size: 4
        /* 0x0004 */ int  childrenOrCell; // size: 4
};

struct dcell_t {
        /* 0x0000 */ short  numPortals; // size: 2
        /* 0x0002 */ short  firstPortal; // size: 2
        /* 0x0004 */ short  skyFlags; // size: 2
        /* 0x0006 */ short  waterDataID; // size: 2
};

struct dportal_t {
        /* 0x0000 */ char   isReversed; // size: 1
        /* 0x0001 */ char   portalType; // size: 1
        /* 0x0002 */ char   numEdges; // size: 1
        /* 0x0003 */ char   pad; // size: 1
        /* 0x0004 */ short  firstRef; // size: 2
        /* 0x0006 */ short  cellTo; // size: 2
        /* 0x0008 */ int    planeNum; // size: 4
};

struct dportal_edge_t {
        /* 0x0000 */ short  i0; // size: 2
        /* 0x0002 */ short  i1; // size: 2
};

struct dportal_edgeset_t {
        /* 0x0000 */ short  edgeIdx[8]; // size: 16
};

struct dportal_vertset_t {
        /* 0x0000 */ short  vertIdx[8]; // size: 16
};

struct dportal_isects_t {
        /* 0x0000 */ int  first; // size: 4
        /* 0x0004 */ int  count; // size: 4
};

struct dcell_aabb_t {
        /* 0x0000 */ struct Vector3  mins; // size: 12
        /* 0x000c */ char            numChildren; // size: 1
        /* 0x000d */ char            numObjRefsSelf; // size: 1
        /* 0x000e */ short           numObjRefsTotal; // size: 2
        /* 0x0010 */ struct Vector3  maxs; // size: 12
        /* 0x001c */ short           firstChild; // size: 2
        /* 0x001e */ short           firstObjRef; // size: 2
};

struct dobjrefbounds_t {
        /* 0x0000 */ struct Vector3  mins; // size: 12
        /* 0x000c */ float           mins_zero; // size: 4
        /* 0x0010 */ struct Vector3  maxs; // size: 12
        /* 0x001c */ float           maxs_zero; // size: 4
};

struct dlevel_info_t {
        /* 0x0000 */ int  firstDecalMeshIdx; // size: 4
        /* 0x0004 */ int  firstTransMeshIdx; // size: 4
        /* 0x0008 */ int  firstSkyMeshIdx; // size: 4
        /* 0x000c */ int  numStaticProps; // size: 4
};

struct dshadowmesh_tex_vert_t {
        /* 0x0000 */ struct Vector3   position; // size: 12
        /* 0x000c */ struct Vector2D  texCoord; // size: 8
};

struct dshadowmesh_mesh_t {
        /* 0x0000 */ int  firstVtx; // size: 4
        /* 0x0004 */ int  triCount; // size: 4
        /* 0x0008 */ int  opaque[2]; // size: 2
        /* 0x000a */ int  mtlSortIdx[2]; // size: 2
};

struct dtexdata_t {
        /* 0x0000 */ struct Vector3  reflectivity; // size: 12  rgb but xyz, sure
        /* 0x000c */ int             nameStringTableID; // size: 4
        /* 0x0010 */ int             width; // size: 4
        /* 0x0014 */ int             height; // size: 4
        /* 0x0018 */ int             view_width; // size: 4
        /* 0x001c */ int             view_height; // size: 4
        /* 0x0020 */ int             flags; // size: 4
};

struct dfacebrushlist_t {
        /* 0x0000 */ short  m_nFaceBrushCount; // size: 2
        /* 0x0002 */ short  m_nFaceBrushStart; // size: 2
};

struct dvertUnlit {
        /* 0x0000 */ int    posIdx; // size: 4
        /* 0x0004 */ int    nmlIdx; // size: 4
        /* 0x0008 */ float  tex[2]; // size: 8
        /* 0x0010 */ char   color[4]; // size: 4
};

struct dvertLitFlat {
        /* 0x0000 */ int    posIdx; // size: 4
        /* 0x0004 */ int    nmlIdx; // size: 4
        /* 0x0008 */ float  tex[2]; // size: 8
        /* 0x0010 */ char   color[4]; // size: 4
        /* 0x0014 */ float  lmap[2]; // size: 8
        /* 0x001c */ float  lmapStep[2]; // size: 8
};

struct dvertLitBump {
        /* 0x0000 */ int    posIdx; // size: 4
        /* 0x0004 */ int    nmlIdx; // size: 4
        /* 0x0008 */ float  tex[2]; // size: 8
        /* 0x0010 */ char   color[4]; // size: 4
        /* 0x0014 */ float  lmap[2]; // size: 8
        /* 0x001c */ float  lmapStep[2]; // size: 8
        /* 0x0024 */ int    tangentSIdx; // size: 4
        /* 0x0028 */ int    tangentTIdx; // size: 4
};

struct dvertUnlitTS {
        /* 0x0000 */ int    posIdx; // size: 4
        /* 0x0004 */ int    nmlIdx; // size: 4
        /* 0x0008 */ float  tex[2]; // size: 8
        /* 0x0010 */ char   color[4]; // size: 4
        /* 0x0014 */ int    tangentSIdx; // size: 4
        /* 0x0018 */ int    tangentTIdx; // size: 4
};

struct dvertBlinnPhong {
        /* 0x0000 */ int    posIdx; // size: 4
        /* 0x0004 */ int    nmlIdx; // size: 4
        /* 0x0008 */ char   color[4]; // size: 4
        /* 0x000c */ float  tex[2]; // size: 8
        /* 0x0014 */ short  lmap[2]; // size: 4
        /* 0x0018 */ float  tangentQuat[4][4]; // size: 4
};

struct dmesh_t {
        /* 0x0000 */ int    firstIdx; // size: 4
        /* 0x0004 */ short  triCount; // size: 2
        /* 0x0006 */ short  firstVtxRel; // size: 2
        /* 0x0008 */ short  lastVtxOfs; // size: 2
        /* 0x000a */ char   vtxType; // size: 1
        /* 0x000b */ char   unused_0; // size: 1
        /* 0x000c */ char   lightStyles[4]; // size: 4
        /* 0x0010 */ short  luxelOrg[2]; // size: 4
        /* 0x0014 */ char   luxelOfsMax[2]; // size: 2
        /* 0x0016 */ short  mtlSortIdx; // size: 2
        /* 0x0018 */ int    flags; // size: 4
};

struct dmeshbounds_t {
        /* 0x0000 */ float  origin[3]; // size: 12
        /* 0x000c */ float  radius; // size: 4
        /* 0x0010 */ float  extents[3]; // size: 12
        /* 0x001c */ float  tanYaw; // size: 4
};

struct dmaterialsort_t {
        /* 0x0000 */ short  texdata; // size: 2
        /* 0x0002 */ short  lmapIdx; // size: 2
        /* 0x0004 */ short  cubemapIdx; // size: 2
        /* 0x0006 */ short  lastVtxOfs; // size: 2
        /* 0x0008 */ int    firstVertex; // size: 4
};

struct dlightmapheader_t {
        /* 0x0000 */ char   type; // size: 1
        /* 0x0004 */ short  width; // size: 2
        /* 0x0006 */ short  height; // size: 2
};

struct dcollgrid_t {
        /* 0x0000 */ float  cellSize; // size: 4
        /* 0x0004 */ int    cellOrg[2]; // size: 8
        /* 0x000c */ int    cellCount[2]; // size: 8
        /* 0x0014 */ int    straddleGroupCount; // size: 4
        /* 0x0018 */ int    basePlaneOffset; // size: 4
};

struct dcollgridcell_t {
        /* 0x0000 */ short  geoSetStart; // size: 2
        /* 0x0002 */ short  geoSetCount; // size: 2
};

struct dcollgeoset_t {
        /* 0x0000 */ short  straddleGroup; // size: 2
        /* 0x0002 */ short  primCount; // size: 2
        /* 0x0004 */ int    primStart; // size: 4
};

struct dcollyawbox_t {
        /* 0x0000 */ short  origin[3]; // size: 6
        /* 0x0006 */ short  negCos; // size: 2
        /* 0x0008 */ short  extent[3]; // size: 6
        /* 0x000e */ short  posSin; // size: 2
};

struct dcollbrushsideprops_t {
        // bitfield :D
        /* 0x0000 */ short  bf[1]; // size: 1
};

struct dcollbrushtexvecs_t {
        /* 0x0000 */ float  texelsPerWorldUnits[8]; // size: 32
};

struct dfastplane_t {
        /* 0x0000 */ struct Vector3  normal; // size: 12
        /* 0x000c */ float           dist; // size: 4
};

struct dcollbrush_t {
        /* 0x0000 */ struct          Vector3 origin; // size: 12
        /* 0x000c */ char            nonAxialCount[2]; // size: 2
        /* 0x000e */ short           priorBrushCount; // size: 2
        /* 0x0010 */ struct Vector3  extent; // size: 12
        /* 0x001c */ int             priorNonAxialCount; // size: 4
};

struct dmodel_t {
        /* 0x0000 */ struct Vector3  mins; // size: 12
        /* 0x000c */ struct Vector3  maxs; // size: 12
        /* 0x0018 */ int             firstMesh; // size: 4
        /* 0x001c */ int             meshCount; // size: 4
};

struct dphysmodel_t {
        /* 0x0000 */ int  modelIndex; // size: 4
        /* 0x0004 */ int  dataSize; // size: 4
        /* 0x0008 */ int  keydataSize; // size: 4
        /* 0x000c */ int  solidCount; // size: 4
};

struct dphystris_t {
        /* 0x0000 */ short triCollCount; // size: 2
};

struct dworldlight_t {
        /* 0x0000 */ struct Vector3  origin; // size: 12
        /* 0x000c */ struct Vector3  intensity; // size: 12
        /* 0x0018 */ struct Vector3  normal; // size: 12
        /* 0x0024 */ struct Vector3  shadow_cast_offset; // size: 12
        /* 0x0030 */ int             unused; // size: 4
        /* 0x0034 */ int             type; // size: 4
        /* 0x0038 */ int             style; // size: 4
        /* 0x003c */ float           stopdot; // size: 4
        /* 0x0040 */ float           stopdot2; // size: 4
        /* 0x0044 */ float           exponent; // size: 4
        /* 0x0048 */ float           radius; // size: 4
        /* 0x004c */ float           constant_attn; // size: 4
        /* 0x0050 */ float           linear_attn; // size: 4
        /* 0x0054 */ float           quadratic_attn; // size: 4
        /* 0x0058 */ int             flags; // size: 4
        /* 0x005c */ int             texdata; // size: 4
        /* 0x0060 */ int             owner; // size: 4
};

struct dleafwaterdata_t {
        /* 0x0000 */ float  surfaceZ; // size: 4
        /* 0x0004 */ float  minZ; // size: 4
        /* 0x0008 */ int    surfaceTexData; // size: 4
};

struct doccluderdata_t {
        /* 0x0000 */ int             flags; // size: 4
        /* 0x0004 */ int             firstpoly; // size: 4
        /* 0x0008 */ int             polycount; // size: 4
        /* 0x000c */ struct Vector3  mins; // size: 12
        /* 0x0018 */ struct Vector3  maxs; // size: 12
        /* 0x0024 */ int             area; // size: 4
};

struct doccluderpolydata_t {
        /* 0x0000 */ int  firstvertexindex; // size: 4
        /* 0x0004 */ int  vertexcount; // size: 4
        /* 0x0008 */ int  planeIdx; // size: 4
};

struct dcubemapsample_t {
        /* 0x0000 */ int origin[3]; // size: 12
        /* 0x000c */ int unused; // size: 4
};

struct dgamelumpheader_t {
        /* 0x0000 */ int lumpCount; // size: 4
};

struct dgamelump_t {
        /* 0x0000 */ int    id; // size: 4
        /* 0x0004 */ short  flags; // size: 2
        /* 0x0006 */ short  version; // size: 2
        /* 0x0008 */ int    fileofs; // size: 4
        /* 0x000c */ int    filelen; // size: 4
};

struct StaticPropDictLump_t {
        /* 0x0000 */ char m_Name[128]; // size: 128
};

struct StaticPropLump_t {
        /* 0x0000 */ struct Vector3  m_Origin; // size: 12
        /* 0x000c */ struct Vector3  m_Angles; // size: 12
        /* 0x0018 */ short           m_PropType; // size: 2
        /* 0x001a */ short           m_FirstLeaf; // size: 2
        /* 0x001c */ short           m_LeafCount; // size: 2
        /* 0x001e */ char            m_Solid; // size: 1
        /* 0x001f */ char            m_Flags; // size: 1
        /* 0x0020 */ short           m_Skin; // size: 2
        /* 0x0022 */ short           m_EnvCubemap; // size: 2
        /* 0x0024 */ float           m_FadeMinDist; // size: 4
        /* 0x0028 */ float           m_FadeMaxDist; // size: 4
        /* 0x002c */ struct Vector3  m_LightingOrigin; // size: 12
        /* 0x0038 */ float           m_flForcedFadeScale; // size: 4
        /* 0x003c */ char            m_nMinCPULevel; // size: 1
        /* 0x003c */ char            m_nMaxCPULevel; // size: 1
        /* 0x003e */ char            m_nMinGPULevel; // size: 1
        /* 0x003e */ char            m_nMaxGPULevel; // size: 1
        /* 0x0040 */ int             m_DiffuseModulation; // size: 4
        /* 0x0044 */ bool            m_bDisableX360; // size: 1
        /* 0x0048 */ float           m_Scale; // size: 4
        /* 0x004c */ int             m_collisionFlagsAdd; // size: 4
        /* 0x0050 */ int             m_collisionFlagsRemove; // size: 4
};

struct StaticPropLeafLump_t {
        /* 0x0000 */ short m_Leaf; // size: 2
};

struct dprophull_t {
        /* 0x0000 */ int m_nVertCount; // size: 4
        /* 0x0004 */ int m_nVertStart; // size: 4
        /* 0x0008 */ int m_nSurfaceProp; // size: 4
        /* 0x000c */ int m_nContents; // size: 4
};

struct dprophulltris_t {
        /* 0x0000 */ int m_nIndexStart; // size: 4
        /* 0x0004 */ int m_nIndexCount; // size: 4
};

struct dpropcollision_t {
        /* 0x0000 */ int m_nHullCount; // size: 4
        /* 0x0004 */ int m_nHullStart; // size: 4
};

struct dtricolltri_t {
        /* 0x0000 */ int packed; // size: 4
};

struct dtricollleaf_t {
        /* 0x0000 */ short first; // size: 2
        /* 0x0002 */ short count; // size: 2
};

struct dtricollnode_t {
        /* 0x0000 */ float org_x[4]; // size: 16
        /* 0x0010 */ float org_y[4]; // size: 16
        /* 0x0020 */ float org_z[4]; // size: 16
        /* 0x0030 */ float ext_x[4]; // size: 16
        /* 0x0040 */ float ext_y[4]; // size: 16
        /* 0x0050 */ float ext_z[4]; // size: 16
        /* 0x0060 */ short children[4]; // size: 8
};

struct dtricollheader_t {
        /* 0x0000 */ short           flags; // size: 2
        /* 0x0002 */ short           texinfoFlags; // size: 2
        /* 0x0004 */ short           texdata; // size: 2
        /* 0x0006 */ short           numVerts; // size: 2
        /* 0x0008 */ short           numTris; // size: 2
        /* 0x000a */ short           numBevelIndexes; // size: 2
        /* 0x000c */ int             firstVert; // size: 4
        /* 0x0010 */ int             firstTri; // size: 4
        /* 0x0014 */ int             firstNode; // size: 4
        /* 0x0018 */ int             firstBevelIndex; // size: 4
        /* 0x001c */ struct Vector3  org; // size: 12
        /* 0x0028 */ float           scale; // size: 4
};

struct MeshHeader_t {
        /* 0x0000 */ int m_nLod; // size: 4
        /* 0x0004 */ int m_nVertexes; // size: 4
        /* 0x0008 */ int m_nOffset; // size: 4
        /* 0x000c */ int m_nUnused[4]; // size: 16
};

struct FileHeader_t {
        /* 0x0000 */ int m_nVersion; // size: 4
        /* 0x0004 */ int m_nChecksum; // size: 4
        /* 0x0008 */ int m_nVertexFlags; // size: 4
        /* 0x000c */ int m_nVertexSize; // size: 4
        /* 0x0010 */ int m_nVertexes; // size: 4
        /* 0x0014 */ int m_nMeshes; // size: 4
        /* 0x0018 */ int m_nUnused[4]; // size: 16
};

// cry
// struct dphyslevelV0_t
// {
//      /* 0x0000 */ int toolVersion; // size: 4
//      /* 0x0004 */ int dataVersion; // size: 4
//      /* 0x0008 */ int sizeofDiskPhysics2LevelMesh; // size: 4
//      /* 0x000c */ int buildTime; // size: 4
//      /* 0x0010 */ int levelMeshes.offset; // size: 4
//      /* 0x0014 */ int levelMeshes.size; // size: 4
//      /* 0x0018 */ int polysoup.offset; // size: 4
//      /* 0x001c */ int mopp.offset; // size: 4
//      /* 0x0020 */ int staticProps.offset; // size: 4
//      /* 0x0024 */ int levelWaterMeshes.offset; // size: 4
//      /* 0x0028 */ int levelWaterMeshes.size; // size: 4
//      /* 0x003c */ int nReserved2[0]; // size: 4
//      /* 0x0040 */ int nReserved2[1]; // size: 4
// };
//
// struct DiskPhysics2Polytope_t
// {
//      /* 0x0000 */ int offsetPolytope; // size: 4
//      /* 0x0004 */ int offsetInertia; // size: 4
// };
//
// struct DiskPhysics2LevelMesh_t
// {
//      /* 0x0000 */ int polymesh.offset; // size: 4
//      /* 0x0004 */ int flags; // size: 4
// };
