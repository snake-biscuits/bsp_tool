#pragma once

#include <cstdint>
#include <cstring>
#include <iostream>

#include "respawn/titanfall.hpp"  // lump enum & structs


namespace respawn {
    // NOTE: same for valve
    struct LumpHeader {
        uint32_t  offset;
        uint32_t  length;
        uint32_t  version;
        uint32_t  decompressed_size;  // fourCC
    };


    struct RespawnBsp {
        uint32_t    file_magic;
        uint16_t    version;
        uint16_t    external_only;  // Apex S11 onwards
        uint32_t    lump_count;     // always 127
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
        char filename[4096];  // len(bsp_filename + 14)
        snprintf(filename, 4096, "%s.%04X.bsp_lump", bsp_filename, LUMP_ENUM);
        return std::string(filename);
    };
}
