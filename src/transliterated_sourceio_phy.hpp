// See also: source-sdk-2013/sp/src/utils/common/bsplib.cpp

/* PSEUDOCODE */

namespace PHY {

    struct Header { int size, id, solid_count, checksum };


    struct TreeNode {
        int    right_node_offset;
        int    convex_offset;
        float  unknown[5];
    }
    
    
    void read_TreeNode(int offset, TreeNode *out) {  // navigates the tree
        file.read(offset, sizeof(TreeNode), &out);
        // TODO: return nested children in some form
        if (out.right_node_offset == 0) {  // node is a leaf
            // python:  `seek(out.convex_offset - struct.calcsize(TreeNode._format), 1)`
            read_ConvexLeaf(offset + out.convex_offset);
        } else {
            TreeNode left_node;
            read_TreeNode(offset + sizeof(TreeNode), *left_node);
            TreeNode right_node;
            read_TreeNode(offset + out.right_node_offset, *right_node);
            // how do I return 2 lists?
        }
    }
    
    
    struct ConvexTriangle {
        int    padding;  // should be 0
        short  edges[3][2];  // should list each index twice
    }
    
    
    struct ConvexLeaf {
        int    vertex_offset;
        int    padding[2];
        short  triangle_count;
        short  unused;
    }
    
    
    struct Vertex { float x, y, z, w };
    
    
    void read_ConvexLeaf(int offset, ConvexLeaf *out) {
        file.read(offset, sizeof(ConvexLeaf), &out);
        ConvexTriangle triangles[out.triangle_count];
        int max_vertex_index = 0;
        int max_index;
        for (int i = 0; i < out.triangle_count; i++) {
            file.read(offset + i * sizeof(ConvexTriangle), triangles[i]);
            max_index = max(trianges[i][0][0], trianges[i][1][0], trianges[i][2][0])
            max_vertex_index = max(max_vertex_index, max_index);
        }
        int vertex_count = max_vertex_index + 1;
        Vertex vertices[vertex_count];
        file.read(offset + out.vertex_offset, sizeof(Vertex) * (vertex_count), *vertices);
    }
    
    
    // source-sdk-2013/sp/src/common/studiobyteswap.cpp: legacysurfaceheader-t
    struct CollisionModel {
        float  center_of_mass[3];
        float  rotational_inertia[3];
        float  upper_limit_radius;
        // surface bitfield
        int	   max_deviation : 8;
        int	   byte_size : 24;
        int    tree_offset;
        int    padding[2];  // legacy
    }
    // immediately followed by IVPS...
    
    
    TreeNode read_CollisionModel(int offset, CollisionModel *out) {
        file.read(offset, sizeof(CollisionModel), &out);
        TreeNode tree;
        read_TreeNode(offset + out.tree_offset, &tree);
        return tree;
    }
    
    
    struct SolidHeader {
        int    solid_size;
        char   id[4];  // VPHYS / IVPS?
        short  version;
        short  type;
        int    size;  // of ???
        float  areas[3];
        int    axis_map_size;
    }
    // immediately followed by collision model
}

/*  Renderware level variable-length struct nesting
Header
 - SolidHeader[Header.solid_count]
   - CollisionModel
     - TreeNode (recursive) <- CollisionModel.tree_offset
       - TreeNode (left)  <- TreeNode<parent>._offset + sizeof(TreeNode)
       - TreeNode (right) <- TreeNode<parent>.right_node_offset
       if (TreeNode<parent>.right_node_offset == 0)
       - ConvexLeaf <- TreeNode<parent>.convex_offset
         - ConvexTriangle[ConvexLeaf.triangle_count]
         - Vertex[max(*ConvexTriangle<s>.edges[::])]
*/