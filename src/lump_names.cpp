#include "bsp_tool.hpp"
#include "lump_names.hpp"


// TODO: develop into more of a general bspinfo.exe
// -- requires lump limits for target

// TODO: auto-detect in bsp_tool to replace asking user for developer name

void print_help(char* argv_0) {
    printf("%s DEVELOPER FILE1 [FILE2 ...]\n", argv_0);
    printf("Print the headers of each .bsp for the given developer\n");
    printf("    DEVELOPER  one of the following: idsoft valve respawn\n");
}


int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_help(argv[0]);
        return 0;
    }

    std::string developer (argv[1]);
    // TODO: auto-detect branch

    int i, j;
    if (developer == std::string("idsoft") || developer == std::string("idtech")) {
        using namespace bsp_tool::id_software;
        for (i = 2; i < argc; i++) {
            // NOTE: Quake 3 Only
            IdTechBsp<17> bsp(argv[i]);
            printf("Loaded: %s\n", bsp.filename.c_str());
            for (j = 0; j < 17; j++) {
                LumpHeader header = bsp.header[j];
                printf("%s:\n\toffset = %i\n\tlength = %i\n", quake3::lump_names[j], header.offset, header.length);
            }
        }
    } else if (developer == std::string("valve")) {
        using namespace bsp_tool::valve_software;
        for (i = 2; i < argc; i++) {
            ValveBsp bsp (argv[i]);
            printf("Loaded: %s\n", bsp.filename.c_str());
            for (j = 0; j < 64; j++) {
                LumpHeader header = bsp.header[j];
                printf("%s:\n\toffset  = %i\n\tlength  = %i\n\tversion = %i\n\tfourCC  = %i\n", source::lump_names[j],
                       header.offset, header.length, header.version, header.uncompressed_size);
            }
        }
    } else if (developer == std::string("respawn")) {
        using namespace bsp_tool::respawn_entertainment;
        for (i = 2; i<argc; i++) {
            RespawnBsp bsp (argv[i]);
            printf("Loaded: %s\n", bsp.filename.c_str());
            for (j = 0; j < 128; j++) {
                LumpHeader header = bsp.header[j];
                printf("%s:\n\toffset  = %i\n\tlength  = %i\n\tversion = %i\n\tfourCC  = %i\n", titanfall::lump_names[j],
                       header.offset, header.length, header.version, header.uncompressed_size);
            }
        }
    } else {
        print_help(argv[0]);
    }
    return 0;
}
