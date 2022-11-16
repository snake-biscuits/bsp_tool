#include <cstdint>


struct Bounds {
    struct { int16_t x, y, z; } origin;
    int16_t unknown_1;
    struct { int16_t x, y, z; } extents;
    int16_t unknown_2;
};

struct Brush {
    struct { float x, y, z; } origin;
    uint8_t unknown;
    uint8_t num_plane_offsets;
    int16_t index;
    struct { float x, y, z; } extents;
    int32_t brush_side_offset;
};

struct Cell {
    uint32_t num_portals;
    uint16_t unknown[2];
};

struct CellAABBNode {
    struct { float x, y, z; } mins;
    uint32_t child_data;
    struct { float x, y, z; } maxs;
    uint32_t unknown;
};

struct CellBSPNode { int32_t unknown_1, unknown_2; };

struct Cubemap {
    struct { int32_t x, y, z; } origin;
    uint32_t unknown;
};

using Edge = uint16_t[2];

struct GeoSet {
    uint16_t unknown[2];
    struct { uint32_t unknown: 8, index: 16, type: 8; } child;
};

struct GridCell { uint16_t first_geo_set, num_geo_sets; };

struct LeafWaterData { float surface_z, min_z; uint32_t texture_data; };

struct LevelInfo {
    uint32_t unknown[4];
    uint32_t num_static_props;
    struct { float x, y, z; } sun_angle;
    uint32_t num_entity_models;
};

struct LightProbe {
    int32_t unknown_1;
    int16_t unknown_2[2];
    int32_t unknown_3[10];
};

struct LightProbeRef {
    struct { float x, y, z; } origin;
    uint32_t lightprobe;
    int32_t unknown;
};

struct LightmapHeader { uint32_t flags; uint16_t width, height; };

using LightmapPage = uint8_t[128];

struct MaterialSort {
    int16_t texture_data;
    int16_t lightmap_index;
    int16_t unknown[2];
    uint32_t vertex_offset;
};

/* ERROR: skipping Mesh */
struct Mesh {
    uint32_t first_mesh_index;
    uint16_t num_triangles;
    int16_t unknown[8];
    uint16_t material_sort;
    uint32_t flags;
};

struct MeshBounds {
    struct { float x, y, z; } origin;
    float radius;
    struct { float x, y, z; } extents;
    uint32_t unknown_2;
};

struct Model {
    struct { float x, y, z; } mins;
    struct { float x, y, z; } maxs;
    uint32_t first_mesh;
    uint32_t num_meshes;
    int32_t unknown[8];
};

struct Node {
    struct { float x, y, z; } mins;
    int32_t unknown_1;
    struct { float x, y, z; } maxs;
    int32_t unknown_2;
};

struct ObjRefBounds {
    struct { float x, y, z; } mins;
    int32_t unused_1;
    struct { float x, y, z; } maxs;
    int32_t unused_2;
};

struct PackedVertex { int16_t x, y, z; };

struct Plane {
    struct { float x, y, z; } normal;
    float distance;
};

struct Portal {
    uint32_t unknown[2];
    uint32_t index;
};

struct PortalEdgeIntersect {
    int32_t unknown[4];
};

struct PortalEdgeIntersectHeader { uint32_t start, count; };

struct Primitive { int16_t start, count; };

struct ShadowEnvironment {
    int32_t unknown_1[2];
    int32_t first_shadow_mesh;
    int32_t unknown_2[2];
    int32_t num_shadow_meshes;
    float angle_vector[3];
};

struct ShadowMesh {
    uint32_t start_index;
    uint32_t num_triangles;
    int16_t unknown[2];
};

struct ShadowMeshAlphaVertex {
    struct { float x, y, z; } position;
    float unknown[2];
};

struct TextureData {
    int32_t name_index;
    struct { int32_t width, height; } size;
    int32_t flags;
};

struct TextureVector {
    struct { float x, y, z, offset; } s;
    struct { float x, y, z, offset; } t;
};

struct TricollHeader {
    int32_t flags;
    int16_t material;
    int16_t num_vertices;
    int32_t num_bevels;
    int32_t first_vertex;
    int32_t first_bevel_start;
    int32_t first_tricoll_node;
    int32_t num_bevel_indices;
    float unknown[4];
};

struct TricollNode {
    int32_t unknown[4];
};

struct Vertex { float x, y, z; };

struct VertexBlinnPhong {
    uint32_t position_index;
    uint32_t normal_index;
    struct { float u, v; } uv0;
    struct { float u, v; } uv1;
};

struct VertexLitBump {
    uint32_t position_index;
    uint32_t normal_index;
    struct { float u, v; } uv0;
    int32_t negative_one;
    struct { float u, v; } uv1;
    struct { uint8_t r, g, b, a; } colour;
};

struct VertexLitFlat {
    uint32_t position_index;
    uint32_t normal_index;
    struct { float u, v; } uv0;
    int32_t unknown;
};

struct VertexUnlit {
    int32_t position_index;
    int32_t normal_index;
    struct { float u, v; } uv0;
    int32_t unknown;
};

struct VertexUnlitTS {
    uint32_t position_index;
    uint32_t normal_index;
    struct { float u, v; } uv0;
    int32_t unknown[2];
};

struct WorldLight {
    struct { float x, y, z; } origin;
    uint32_t unknown[22];
};

struct WorldLightv2 {
    struct { float x, y, z; } origin;
    uint32_t unknown[24];
};

struct WorldLightv3 {
    struct { float x, y, z; } origin;
    uint32_t unknown[25];
};


/* TODO: find maxs for each lump and use them here */
uint16_t CM_BRUSH_SIDE_PLANE_OFFSETS[UINT16_MAX];
uint16_t CM_BRUSH_SIDE_PROPERTIES[UINT16_MAX];  /* TODO: bitfield / mask for flags vs texture index */
uint32_t CM_UNIQUE_CONTENTS[UINT32_MAX];
uint16_t CSM_OBJ_REFENENCES[UINT16_MAX];
uint16_t MESH_INDICES[UINT16_MAX];
uint16_t OBJ_REFERENCES[UINT16_MAX];
int16_t  OCCLUSION_MESH_INDICES[INT16_MAX];
uint16_t PORTAL_EDGE_REFERENCES[UINT16_MAX];
uint16_t PORTAL_VERTEX_REFERENCES[UINT16_MAX];
uint16_t SHADOW_MESH_INDICES[UINT16_MAX];
uint32_t TEXTURE_DATA_STRING_TABLE[UINT32_MAX];
uint16_t TRICOLL_BEVEL_STARTS[UINT16_MAX];
uint32_t TRICOLL_BEVEL_INDICES[UINT32_MAX];
uint32_t TRICOLL_TRIANGLES[UINT32_MAX];
