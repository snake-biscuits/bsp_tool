#pragma once

#include <cstdint>

#include "../common.hpp"


namespace bsp_tool {
    namespace respawn_entertainment {
        struct StaticPropv12 {  // mostly identified by BobTheBob
            Vector3D<float>  origin;
            QAngle           angles;
            uint16_t         mdl_name;
            uint16_t         first_leaf;              // NOTE: rBSP has no leaves
            uint16_t         leaf_count;
            uint8_t          solid;
            uint8_t          flags;
            int32_t          skin;
            uint32_t         cubemap;                 // new! an index?
            float            fade_distance_min;
            float            fade_distance_max;
            Vector3D<float>  lighting_origin;
            float            forced_fade_scale;
            int8_t           cpu_level_min;           // -1 == any
            int8_t           cpu_level_max;
            int8_t           gpu_level_min;
            int8_t           gpu_level_max;
            Colour32         diffuse_modulation;
            bool             disable_x360;            // 4 byte bool
            float            scale;                   // should be 1.0?
            uint16_t         collision_flags_add;     // new!
            uint16_t         collision_flags_remove;  // new!
        };

        struct StaticPropv13 {  // mostly identified by BobTheBob
            Vector3D<float>  origin;
            QAngle           angles;
            int8_t           unknown_1[4];
            uint16_t         mdl_name;
            uint8_t          solid_type;
            uint8_t          flags;
            int8_t           unknown_2[4];         // generally  00 00 <num under 10> 00
            float            forced_fade_scale;
            Vector3D<float>  lighting_origin;
            int8_t           cpu_level_min;        // -1 == any
            int8_t           cpu_level_max;
            int8_t           gpu_level_min;
            int8_t           gpu_level_max;
            Colour32         diffuse_modulation;  // always 0000?
            uint16_t         collision_flags_add;
            uint16_t         collision_flags_remove;
        };
    }
}
