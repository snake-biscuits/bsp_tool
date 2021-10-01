#include <map>
#include "bsp_tool.hpp"


namespace bsp_tool::id_software::quake {
    std::map<const char*, int> games = {
        {"Quake", 29}};

    namespace LUMP {
        int ENTITIES     = 0,  LEAVES     = 10,
            PLANES       = 1,  LEAF_FACES = 11,
            MIP_TEXTURES = 2,  EDGES      = 12,
            VERTICES     = 3,  SURFEDGES  = 13,
            VISIBILITY   = 4,  MODELS     = 14,
            NODES        = 5,
            TEXTURE_INFO = 6,
            FACES        = 7,
            LIGHTMAPS    = 8,
            CLIP_NODES   = 9; }

    // A rough map of the relationships between lumps:

    // Entity -> Model -> Node -> Leaf -> LeafFace -> Face
    //                        \-> ClipNode -> Plane

    //     /--> Plane
    // Face -> SurfEdge -> Edge -> Vertex
    //    \---> TextureInfo -> MipTexture
    //     \--> Lightmap

    // Visibility -> Node -> Leaf

    // LUMP structs, in alphabetical order:
    typedef struct clipnode_t {
        unsigned int plane;
        struct { short front, back; } children;
    } ClipNode;

    // NOTE: Edge = short[2];

    typedef struct face_t {
        unsigned short  plane;
        unsigned short  side;
        unsigned int    first_edge;
        unsigned short  num_edges;
        unsigned short  texture_info;
        unsigned char   lighting_type;
        unsigned char   base_light;
        unsigned char   light[2];
        int             lightmap;
    } Face;

    namespace LEAF_TYPE {
        int NORMAL = -1,  SLIME = -4,
            SOLID  = -2,  LAVA  = -5,
            WATER  = -3,  SKY   = -6; };

    typedef struct leaf_t {
        int  type;
        int  cluster;
        struct {
            struct { short x, y, z } mins;
            struct { short x, y, z } maxs;
        } bounds;
        unsigned short  first_leaf_face;
        unsigned short  num_leaf_faces;
        struct { unsigned char water, sky, slime, lava} sound;
    } Leaf;

    typedef struct model_t {
        struct {
            struct { float x, y, z } mins;
            struct { float x, y, z } maxs;
        } bounds;
        struct { float x, y, z } origin;
        int  first_node;
        int  clip_node[2];
        int  node_id3;
        int  num_leaves;
        int  first_leaf_face;
        int  num_leaf_faces;
    } Model;

    typedef struct miptexture_t {
        char  name[16];
        struct { unsigned int width, height } size;
        struct { unsigned int full, half, quarter, eighth } offsets;
        // offsets are into the .bsp file
    } MipTexture;

    typedef struct node_t {
        unsigned int  plane;
        struct { short front, back } children;
        struct {
            struct { short x, y, z } mins;
            struct { short x, y, z } maxs;
        } bounds;
        short  first_face;
        short  num_faces;
    } Node;
    
    namespace PLANE_TYPE {
        int X_ALIGNED = 0,  X_UNALIGNED = 3,
            Y_ALIGNED = 1,  Y_UNALIGNED = 4,
            Z_ALIGNED = 2,  Z_UNALIGNED = 5; }

    typedef struct plane_t {
        float  normal[3];
        float  distance;
        int    type;
    } Plane;

    typedef struct {
        struct { float x, y, z, w } u;
        struct { float x, y, z, w } v;
        unsigned int  mip_texture;
        unsigned int  animated;  // 0 or 1
    } TextureInfo;

    typedef struct vertex_t { float x, y, z; } Vertex;
}
