#include <cstdio>
#include <filesystem>  // -std=c++17
#include <fstream>
#include <string>


namespace fs = std::filesystem;

namespace bsp_tool {

    // Base BSPFile class, gives an interface to read the .bsp file
    class BSPFile {
        public:
            std::fstream _file;
            std::string filename;
            int format_version;

            template<typename T>
            void _read(T x) { this->_file.read((char*) &x, sizeof(T)); };

            BSPFile(char filename[]) {
                this->filename = filename;
                this->_file.open(filename, std::ios::in | std::ios::binary);
                if (!this->_file) { throw "could not find .bsp file"; }
            };

            ~BSPFile() { this->_file.close(); };
    };


    namespace id_software {
        const int FILE_MAGIC = ('I' + ('B' << 8) + ('S' << 16) + ('P' << 24));
        struct LumpHeader { int offset, length; };

        // Holds a loose .bsp header and dynamically reads data from the .bsp file
        // Data is loaded fast, but with no safety checks.
        class IdSoftBSPFile : public BSPFile {
            public:
                LumpHeader headers[17];

                IdSoftBSPFile(char filename[]) : BSPFile(filename) {
                    int file_magic;
                    this->_read(file_magic);
                    if (file_magic != FILE_MAGIC) { throw "not a valid IBSP file"; }
                    this->_read(this->format_version);
                    this->_read(this->headers);
                };

                ~IdSoftBSPFile() { this->_file.close(); };

                // Vertex bsp_vertices[] = some_bsp::getLump<Vertex>(LUMP::VERTICES);
                template<typename T>
                T* getLump(int LUMP_index) {
                    T* lump_entries;
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset, std::ios::beg);
                    this->_file.read((char*) &lump_entries, header.length);
                    return lump_entries;
                };

                // Vertex v = some_bsp::getLumpEntry<Vertex>(LUMP::VERTICES, 0);
                template <typename T>
                T getLumpEntry(int LUMP_index, int entry_index) {
                    T lump_entry;
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset + (sizeof(T) * entry_index), std::ios::beg);
                    this->_read(lump_entry);
                    return lump_entry;
                };

                // char* buffer = some_bsp::getRawLump(LUMP::VERTICES);
                void getRawLump(int LUMP_index, char* buffer) {
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset, std::ios::beg);
                    this->_file.read(buffer, header.length);
                };
        };

        namespace quake {
            const int BSP_VERSION = 46;
            enum class LUMP {
                ENTITIES     = 0,  VERTICES      = 10,
                TEXTURES     = 1,  MESH_VERTICES = 11,
                PLANES       = 2,  EFFECTS       = 12,
                NODES        = 3,  FACES         = 13,
                LEAVES       = 4,  LIGHTMAPS     = 14,
                LEAF_FACES   = 5,  LIGHT_VOLUMES = 15,
                LEAF_BRUSHES = 6,  VIS_DATA      = 16,
                MODELS       = 7,
                BRUSHES      = 8,
                BRUSH_SIDES  = 9};
        }
    }


    namespace valve_software {
        const int FILE_MAGIC = ('V' + ('B' << 8) + ('S' << 16) + ('P' << 24));
        struct LumpHeader { int offset, length, version, uncompressed_size; };

        // VBSP .bsp files have many variants
        // https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
        // https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific
        class ValveBSPFile : public BSPFile {
            public:
                int revision;
                LumpHeader headers[17];

                ValveBSPFile(char filename[]) : BSPFile(filename) {
                    int file_magic;
                    this->_read(file_magic);
                    if (file_magic != FILE_MAGIC) { throw "not a valid VBSP file"; }
                    this->_read(this->format_version);
                    this->_read(this->headers);
                    this->_read(this->revision);
                };

                ~ValveBSPFile() { this->_file.close(); };

                // Vertex bsp_vertices[] = some_bsp::getLump<Vertex>(LUMP::VERTICES);
                template<typename T>
                T* getLump(int LUMP_index) {
                    T* lump_entries;
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset, std::ios::beg);
                    this->_file.read((char*) &lump_entries, header.length);
                    return lump_entries;
                };

                // Vertex v = some_bsp::getLumpEntry<Vertex>(LUMP::VERTICES, 0);
                template <typename T>
                T getLumpEntry(int LUMP_index, int entry_index) {
                    T lump_entry;
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset + (sizeof(T) * entry_index), std::ios::beg);
                    this->_read(lump_entry);
                    return lump_entry;
                };

                // char* buffer = some_bsp::getRawLump(LUMP::VERTICES);
                void getRawLump(int LUMP_index, char* buffer) {
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset, std::ios::beg);
                    this->_file.read(buffer, header.length);
                };
        };


        namespace orange_box {
            const int BSP_VERSION = 20;
            enum class LUMP {
                ENTITIES              =  0,  DISPLACEMENT_LIGHTMAP_ALPHAS          = 32,
                PLANES                =  1,  DISPLACEMENT_VERTICES                 = 33,
                TEXDATA               =  2,  DISPLACEMENT_LIGHTMAP_SAMPLE_POSITION = 34,
                VERTICES              =  3,  GAME_LUMP                             = 35,
                VISIBILITY            =  4,  LEAF_WATER_DATA                       = 36,
                NODES                 =  5,  PRIMITIVES                            = 37,
                TEXINFO               =  6,  PRIMITIVE_VERTICIES                   = 38,
                FACES                 =  7,  PRIMITIVE_INDICES                     = 39,
                LIGHTING              =  8,  PAKFILE                               = 40,
                OCCLUSION             =  9,  CLIP_PORTAL_VERTICES                  = 41,
                LEAVES                = 10,  CUBEMAPS                              = 42,
                FACE_IDS              = 11,  TEXDATA_STRING_DATA                   = 43,
                EDGES                 = 12,  TEXDATA_STRING_TABLE                  = 43,
                SURFEDGES             = 13,  OVERLAYS                              = 45,
                MODELS                = 14,  LEAF_MIN_DIST_TO_WATER                = 46,
                WORLD_LIGHTS          = 15,  FACE_MACRO_TEXTURE_INFO               = 47,
                LEAF_FACES            = 16,  DISPLACEMENT_TRIANGLES                = 48,
                LEAF_BRUSHES          = 17,  PHYSICS_COLLIDE_SURFACE               = 49,
                BRUSHES               = 18,  WATER_OVERLAYS                        = 50,
                BRUSH_SIDES           = 19,  LEAF_AMBIENT_INDEX_HDR                = 51,
                AREAS                 = 20,  LEAF_AMBIENT_INDEX                    = 52,
                AREA_PORTALS          = 21,  LIGHTING_HDR                          = 53,
                UNUSED_22             = 22,  WORLD_LIGHTS_HDR                      = 54,
                UNUSED_23             = 23,  LEAF_AMBIENT_LIGHTING_HDR             = 55,
                UNUSED_24             = 24,  LEAF_AMBIENT_LIGHTING                 = 56,
                UNUSED_25             = 25,  XZIP_PAKFILE                          = 57,
                DISPLACEMENT_INFO     = 26,  FACES_HDR                             = 58,
                ORIGINAL_FACES        = 27,  MAP_FLAGS                             = 59,
                PHYSICS_DISPLACEMENT  = 28,  OVERLAY_FADES                         = 60,
                PHYSICS_COLLIDE       = 29,  UNUSED_61                             = 61,
                VERTEX_NORMALS        = 30,  UNUSED_62                             = 62,
                VERTEX_NORMAL_INDICES = 31,  UNUSED_63                             = 63};
        }
    }


    namespace respawn_entertainment {
        const int FILE_MAGIC = ('r' + ('B' << 8) + ('S' << 16) + ('P' << 24));
        struct LumpHeader { int offset, length, version, uncompressed_size; };

        class RespawnBSPFile : public BSPFile {
            public:
                std::fstream _external[128];
                int revision;
                LumpHeader headers[128];

                RespawnBSPFile(char filename[]) : BSPFile(filename) {
                    int file_magic, lump_count;
                    this->_read(file_magic);
                    if (file_magic != FILE_MAGIC) { throw "not a valid rBSP file"; }
                    this->_read(this->format_version);
                    this->_read(this->revision);
                    this->_read(lump_count);
                    if (lump_count != 127) { throw "not a valid rBSP file"; }
                    this->_read(this->headers);
                    /* load external .bsp_lump files */
                    fs::path bsp_lump(".bsp_lump"), bsp_path(filename), current_file;
                    int LUMP_index; std::string LUMP_hex_index;
                    for (auto file : fs::directory_iterator(bsp_path.parent_path())) {
                        current_file = file.path();
                        if (current_file.extension() == bsp_lump) {
                            if (current_file.stem().stem() == bsp_path.filename()) {
                                LUMP_hex_index = current_file.stem().extension().string();
                                LUMP_index = std::stoi(LUMP_hex_index.substr(1, std::string::npos), 0, 16);
                                this->_external[LUMP_index] = std::fstream(current_file.string());
                            }
                        }
                    }
                };

                ~RespawnBSPFile();

                template<typename T>
                T* getLump(int LUMP_index) {
                    T* lump_entries;
                    LumpHeader header = this->headers[LUMP_index];
                    this->_file.seekg(header.offset, std::ios::beg);
                    this->_file.read((char*) &lump_entries, header.length);
                    return lump_entries;
                };

                template<typename T>
                T* getExternalLump(int LUMP_index) {
                    T* lump_entries;
                    std::fstream external_lump = this->_external[LUMP_index];
                    external_lump.seekg(0, std::ios::beg);
                    external_lump >> lump_entries;
                    return lump_entries;
                };
        };
    }

    /* Common Structs & Functions*/
    struct Vertex { float x, y, z; };  // LUMP::VERTICES, LUMP::VERTEX_NORMALS

    // returns a list of indices that match the search regexp (texted on each line)
    template<typename BSPVariant>
    int* searchEntities(BSPVariant bsp, char search[]);  // TODO: write function

    struct GameLumpHeader { char id[4]; unsigned short flags, version; int offset, length; };

    // Gets the sub-headers in the internal game lumps of a bsp file
    // NOTE: will only read the game lump in the .bsp file, not external lumps
    template<typename BSPVariant>
    struct GameLumpHeader* getGameLumpHeaders(BSPVariant bsp) {
        bsp._file.seekg(bsp.headers[35].offset);  // NOTE: LUMP::GAME_LUMP is usually 35
        int game_lump_count;
        bsp._read(game_lump_count);
        struct GameLumpHeader game_lump_headers[game_lump_count];
        bsp._read(game_lump_headers);
        return game_lump_headers;
    };

}
