#include <map>
#include "bsp_tool.hpp"


namespace bsp_tool::id_software::quake3 {
            // "Game Name", .bsp format version
            std::map<const char*, int> games = {
                {"Quake 3", 46},
                {"Quake 3 Arena", 46},
                {"Quake Live", 46}};

            namespace LUMP {
                int ENTITIES     = 0,  VERTICES      = 10,
                    TEXTURES     = 1,  MESH_VERTICES = 11,
                    PLANES       = 2,  EFFECTS       = 12,
                    NODES        = 3,  FACES         = 13,
                    LEAVES       = 4,  LIGHTMAPS     = 14,
                    LEAF_FACES   = 5,  LIGHT_VOLUMES = 15,
                    LEAF_BRUSHES = 6,  VISIBILITY    = 16,
                    MODELS       = 7,
                    BRUSHES      = 8,
                    BRUSH_SIDES  = 9; }
}
