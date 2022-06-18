#pragma once

#include <cstdint>

#include "../common.hpp"


//              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
// Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
//              \-> .flags (VertexReservedX)     \--> VertexNormal
//                                                \-> .uv
//
// MeshBounds is parallel with Mesh (equal length of lump; match with same index into lump)


namespace bsp_tool {
    namespace respawn_entertainment {
        namespace titanfall {
            namespace FLAG {
                const int SKY_2D          = 0x00002;
                const int SKY             = 0x00004;
                const int WARP            = 0x00008;  // Quake water surface?
                const int TRANSLUCENT     = 0x00010;
                const int VERTEX_LIT_FLAT = 0x00000;  // VERTEX_RESERVED_1
                const int VERTEX_LIT_BUMP = 0x00200;  // VERTEX_RESERVED_2
                const int VERTEX_UNLIT    = 0x00400;  // VERTEX_RESERVED_0
                const int VERTEX_UNLIT_TS = 0x00600;  // VERTEX_RESERVED_3
                const int TRIGGER         = 0x40000;  // guessing
                // MASKS
                const int MASK_VERTEX     = 0x00600;
            };


            struct MaterialSort {
                int16_t  texture_data;
                int16_t  lightmap_header;
                int16_t  cubemap;  // -1 == None
                int16_t  unknown;
                int32_t  vertex_offset;  // offset into VertexReservedX
            };


            struct Mesh {
                int32_t   first_mesh_index;
                uint16_t  num_triangles;
                uint16_t  first_vertex;
                uint16_t  num_vertices;
                int16_t   unknown[6];
                uint16_t  material_sort;
                uint32_t  flags;
            };


            struct MeshBounds {
                Vector3D<float>  origin;
                float            radius;
                Vector3D<float>  extents;
                int32_t          unknown_2;
            };


            // NOTE: MeshIndex is unsigned short


            struct Model {
                struct {
                    Vector3D<float> min;
                    Vector3D<float> max;
                } bounds;
                uint32_t first_mesh;
                uint32_t num_meshes;
            };


            struct TextureData {
                float    colour[3];
                int32_t  name;
                struct { int32_t width, height; } size;
                struct { int32_t width, height; } view;
                int32_t  flags;
            };


            // NOTE: Vertex & VertexNormal are Vector


            // VertexReservedX
            struct VertexLitBump {
                int32_t          position;  // index into VERTICES
                int32_t          normal;    // index into VERTEX_NORMALS
                Vector2D<float>  uv0;
                int32_t          unknown[7];
            };


            struct VertexLitFlat {
                int32_t          position;
                int32_t          normal;
                Vector2D<float>  uv0;
                int32_t          unknown[5];
            };


            struct VertexUnlit {
                int32_t          position;
                int32_t          normal;
                Vector2D<float>  uv0;
                int32_t          unknown[1];
            };


            struct VertexUnlitTS {
                int32_t          position;
                int32_t          normal;
                Vector2D<float>  uv0;
                int32_t          unknown[3];
            };
        };


        namespace apex_legends {
            struct MaterialSort {
                int16_t   texture_data;
                int16_t   lightmap;
                int16_t   unknown[2];
                uint32_t  vertex_offset;
            };


            struct Mesh {
                uint32_t  first_mesh_index;
                uint16_t  num_triangles;
                int16_t   unknown[7];
                uint16_t  material_sort;
                uint32_t  flags;
            };


            struct Model {
                Vector3D<float>  mins;
                Vector3D<float>  maxs;
                uint32_t         first_mesh;
                uint32_t         num_meshes;
                int32_t          unknown[8];
            };


            struct TextureData {
               int32_t name;
               struct { int32_t width, height; } size;
               int32_t flags;
            };


            // VertexReservedX
            struct VertexBlinnPhong {  // unused
                uint32_t         position;
                uint32_t         normal;
                Vector2D<float>  uv0;
                Vector2D<float>  uv1;
            };


            struct VertexLitBump {
                uint32_t         position;
                uint32_t         normal;
                Vector2D<float>  uv0;
                int32_t          unused;
                Vector3D<float>  unknown;
            };


            struct VertexLitFlat {
                uint32_t         position;
                uint32_t         normal;
                Vector2D<float>  uv0;
                int32_t          unknown;
            };


            struct VertexUnlit {
                uint32_t         position;
                uint32_t         normal;
                Vector2D<float>  uv0;
                int32_t          unknown;
            };


            struct VertexUnlitTS {
                uint32_t         position;
                uint32_t         normal;
                Vector2D<float>  uv0;
                int32_t          unknown[2];
            };
        };
    };
};
