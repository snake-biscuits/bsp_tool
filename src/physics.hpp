namespace bsp_tool::physics {
    struct Header { int size, id, solid_count, checksum; };

    struct TreeNode { int left_node_size, convex_offset; float unknown[5]; };
    // TODO: recursive read

    struct ConvexTriangle { int padding; short edges[3][2]; };

    struct ConvexLeaf { int vertex_offset, padding[2]; short triangle_count, unused; };

    struct Vertex { float x, y, z, w; };

    struct CollisionModel {
        float center_of_mass[3];
        float rotational_inertia[3];
        float upper_limit_radius;
        int   max_deviation: 8;
    };
}
