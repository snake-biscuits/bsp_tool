#pragma once  // probably unnessecary

#include <cstdint>
#include <cstring>

#include "renderables.hpp"
#include "../bsp_tool.hpp"  // <filesystem>  --std=C++17 -lstdc++fs
#include "../common.hpp"
#include "../respawn/meshes.hpp"


void rbsp_titanfall_world_geo(respawn::RespawnBsp *bsp, RenderObject *out) {
    // Titanfall rBSP worldspawn (bsp.MODELS[0]) -> RenderObject
    using namespace respawn::titanfall;
    // NOTE: we only use the .bsp file, allowing for fast reads & easy TF:O support

    // read contents of lump `ENUM` into array of type `Type` named `name` & record lump length
    // NOTE: sadly we cannot concatenate `LUMP::##name` because macros require each side to be a valid token pre-concatenation
    #define GET_LUMP(Type, name, ENUM) \
        int name##_SIZE = bsp->header[ENUM].length / sizeof(Type); \
        Type *name = new Type[name##_SIZE]; \
        bsp->getLump<Type>(ENUM, name);
    GET_LUMP(uint16_t,        MESH_INDICES,    LUMP::MESH_INDICES   )
    GET_LUMP(Vector3D<float>, VERTICES,        LUMP::VERTICES       )
    GET_LUMP(Vector3D<float>, VERTEX_NORMALS,  LUMP::VERTEX_NORMALS )
    GET_LUMP(VertexUnlit,     VERTEX_UNLIT,    LUMP::VERTEX_UNLIT   )
    GET_LUMP(VertexLitFlat,   VERTEX_LIT_FLAT, LUMP::VERTEX_LIT_FLAT)
    GET_LUMP(VertexLitBump,   VERTEX_LIT_BUMP, LUMP::VERTEX_LIT_BUMP)
    GET_LUMP(VertexUnlitTS,   VERTEX_UNLIT_TS, LUMP::VERTEX_UNLIT_TS)
    #undef GET_LUMP

    unsigned int VERTEX_UNLIT_OFFSET    = 0;
    unsigned int VERTEX_LIT_FLAT_OFFSET = VERTEX_UNLIT_SIZE;
    unsigned int VERTEX_LIT_BUMP_OFFSET = VERTEX_LIT_FLAT_OFFSET + VERTEX_LIT_FLAT_SIZE;
    unsigned int VERTEX_UNLIT_TS_OFFSET = VERTEX_LIT_BUMP_OFFSET + VERTEX_LIT_BUMP_SIZE;
    out->vertex_count = VERTEX_UNLIT_TS_OFFSET + VERTEX_UNLIT_TS_SIZE;
    out->vertices = new RenderVertex[out->vertex_count];

    VertexUnlit    vertex_unlit;
    VertexLitFlat  vertex_lit_flat;
    VertexLitBump  vertex_lit_bump;
    VertexUnlitTS  vertex_unlit_ts;
    RenderVertex render_vertex;
    int vertex_count = 0;
    #define COPY_RENDER_VERTICES(VERTEX_LUMP, mesh_vertex) \
        for (int i = 0; i < VERTEX_LUMP##_SIZE; i++) { \
            mesh_vertex = VERTEX_LUMP[i]; \
            render_vertex.position = VERTICES[mesh_vertex.position]; \
            render_vertex.normal = VERTEX_NORMALS[mesh_vertex.normal]; \
            render_vertex.uv = mesh_vertex.uv0; \
            out->vertices[vertex_count] = render_vertex; \
            vertex_count++; \
        }
    COPY_RENDER_VERTICES(VERTEX_UNLIT,    vertex_unlit   )
    COPY_RENDER_VERTICES(VERTEX_LIT_FLAT, vertex_lit_flat)
    COPY_RENDER_VERTICES(VERTEX_LIT_BUMP, vertex_lit_bump)
    COPY_RENDER_VERTICES(VERTEX_UNLIT_TS, vertex_unlit_ts)
    #undef COPY_RENDER_VERTICES

    out->indices = new unsigned int[MESH_INDICES_SIZE];
    unsigned int  total_indices = 0;
    unsigned int  vertex_lump_offset;
    Model         worldspawn = bsp->getLumpEntry<Model>(LUMP::MODELS, 0);
    out->child_count = worldspawn.num_meshes;
    out->children = new Span[out->child_count];
    // TODO: create a render object for each Model (w/ shared vertex buffer)
    for (unsigned int i = 0; i < worldspawn.num_meshes; i++) {
        Mesh mesh = bsp->getLumpEntry<Mesh>(LUMP::MESHES, worldspawn.first_mesh + i);
        MaterialSort material_sort = bsp->getLumpEntry<MaterialSort>(LUMP::MATERIAL_SORT, mesh.material_sort);
        TextureData texture_data = bsp->getLumpEntry<TextureData>(LUMP::TEXTURE_DATA, material_sort.texture_data);
        switch (mesh.flags & FLAG::MASK_VERTEX) {
            case FLAG::VERTEX_UNLIT:
                vertex_lump_offset = VERTEX_UNLIT_OFFSET;    break;
            case FLAG::VERTEX_LIT_FLAT:
                vertex_lump_offset = VERTEX_LIT_FLAT_OFFSET; break;
            case FLAG::VERTEX_LIT_BUMP:
                vertex_lump_offset = VERTEX_LIT_BUMP_OFFSET; break;
            case FLAG::VERTEX_UNLIT_TS:
                vertex_lump_offset = VERTEX_UNLIT_TS_OFFSET; break;
        }
        out->children[i] = {total_indices, (unsigned int) mesh.num_triangles * 3};
        for (int j = 0; j < mesh.num_triangles * 3; j++) {
            unsigned int vertex_index = material_sort.vertex_offset + MESH_INDICES[mesh.first_mesh_index + j];
            vertex_index += vertex_lump_offset;
            render_vertex = out->vertices[vertex_index];
            memcpy(render_vertex.colour, texture_data.colour, sizeof(float) * 3);
            out->vertices[vertex_index] = render_vertex;
            out->indices[total_indices] = vertex_index;
            total_indices += 1;
        }
    }
    out->index_count = total_indices;
    printf("Using %d of %d potential indices\n", total_indices, MESH_INDICES_SIZE);
    delete[] MESH_INDICES;
    delete[] VERTICES;
    delete[] VERTEX_NORMALS;
    delete[] VERTEX_UNLIT;
    delete[] VERTEX_LIT_FLAT;
    delete[] VERTEX_LIT_BUMP;
    delete[] VERTEX_UNLIT_TS;
};

