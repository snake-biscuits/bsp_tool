#pragma once

#include <cstring>
#include <iostream>

#include "respawn_entertainment/titanfall.hpp"  // lump structs etc.


namespace bsp_tool::respawn_entertainment {
    // NOTE: RespawnBsp LumpHeader is the same as ValveBsp LumpHeader
    struct LumpHeader {
        int  offset;
        int  length;
        int  version;
        int  decompressed_size;
    };


    struct RespawnBsp {
        char        file_magic[4];  // 'rBSP'
        int         version;  // Apex Legends Season 11+ is short[2]
        int         lump_count;  // always 127; in all shipped maps
        LumpHeader  header[128];
    };
    // NOTE: RespawnBsp often uses external files (.bsp_lump)
    // -- the contents of these files are the same format as lump contents

    // Bsp lumps typically follow the header at offets in RespawnBsp.headers
    // these offsets are relative to the start of the file
    // for Apex Legends Season 11+ .bsps (e.g. v49.1), all lumps are external,
    // but headers have offsets to data not in the .bsp file

    // TODO: useful methods / helper functions
    std::string bsp_lump_filename(int LUMP_ENUM, char* bsp_filename) {
        char filename[4096];
        snprintf(filename, 4096, "%s.%X04.bsp_lump", bsp_filename, LUMP_ENUM);
        return std::string(filename);
    };
}
