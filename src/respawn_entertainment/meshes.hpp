#pragma once

#include "../common.hpp"


//              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
// Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
//              \-> .flags (VertexReservedX)     \--> VertexNormal
//                                                \-> .uv


namespace bsp_tool::respawn_entertainment::titanfall {
    namespace FLAG {
        const int SKY_2D          = 0x00002;
        const int SKY             = 0x00004;
        const int WARP            = 0x00008;  // Quake water surface?
        const int TRANSLUCENT     = 0x00010;
        // MESHES
        const int VERTEX_LIT_FLAT = 0x00000;  // VERTEX_RESERVED_1
        const int VERTEX_LIT_BUMP = 0x00200;  // VERTEX_RESERVED_2
        const int VERTEX_UNLIT    = 0x00400;  // VERTEX_RESERVED_0
        const int VERTEX_UNLIT_TS = 0x00600;  // VERTEX_RESERVED_3

        const int TRIGGER         = 0x40000;  // guessing

        // MASKS
        const int MASK_VERTEX     = 0x00600;
    };


    struct MaterialSort {
        short  texture_data;
        short  lightmap_header;
        short  cubemap;  // -1 == None
        short  unknown;
        int    vertex_offset;  // offset into VertexReservedX
    };

    struct Mesh {
        int             first_mesh_index;
        unsigned short  num_triangles;
        short           first_vertex;
        short           num_vertices;
        short           unknown[6];
        unsigned short  material_sort;
        unsigned int    flags;
    };

    // NOTE: MeshIndex is unsigned short

    struct Model {
        struct {
            Vector min;
            Vector max;
        } bounds;
        unsigned int first_mesh;
        unsigned int num_meshes;
    };

    struct TextureData {
        float  colour[3];
        int    name_index;
        struct { int width, height; } size;
        struct { int width, height; } view;
        int    flags;
    };

    // NOTE: Vertex & VertexNormal are Vector

    // VertexReservedX
    struct VertexLitBump {
        int       position;
        int       normal;
        Vector2D  uv;
        int       unknown[7];
    };

    struct VertexLitFlat {
        int       position;
        int       normal;
        Vector2D  uv;
        int       unknown[5];
    };

    struct VertexUnlit {
        int       position;
        int       normal;
        Vector2D  uv;
        int       unknown[1];
    };

    struct VertexUnlitTS {
        int       position;
        int       normal;
        Vector2D  uv;
        int       unknown[3];
    };
};
