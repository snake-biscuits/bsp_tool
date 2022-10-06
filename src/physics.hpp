// for source / respawn PhysicsCollide lumps
#include <cstdint>
#include "common.hpp"


namespace physics_collide {

    struct Header { int32_t size, id, solid_count, checksum; };  // 0, 0, -1, -1 for EOF

    struct TreeNode { int32_t left_node_size, convex_offset; float unknown[5]; };
    // TODO: read nodes recursively

    struct ConvexTriangle { int32_t padding; int16_t edges[3][2]; };

    struct ConvexLeaf { int32_t vertex_offset, padding[2]; int16_t triangle_count, unused; };

    struct Vertex { float x, y, z, w; };

    struct CollisionModel {
        Vector3D<float>  center_of_mass;
        Vector3D<float>  rotational_inertia;
        float            upper_limit_radius;
        int32_t          max_deviation: 8;
    };
}
