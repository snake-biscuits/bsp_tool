#include <cstdio>
#include <filesystem>  // -std=c++17
#include <fstream>
#include <string>


namespace fs = std::filesystem;

namespace bsp_tool {

    // Bsp base class; gives an interface to read the .bsp file
    template<typename LumpHeaderStruct, int lump_count>
    class Bsp {
        public:
            std::fstream      _file;
            std::string       filename;
            int               format_version;
            LumpHeaderStruct  headers[lump_count];

            // NOTE: _read requires x to be initialised; as a result, x cannot be initialised with _read.
            template<typename T>
            void _read(T* x) { this->_file.read((char*) x, sizeof(*x)); };

            Bsp(const char filename[]) {
                this->filename = filename;
                this->_file.open(filename, std::ios::in | std::ios::binary);
                if (!this->_file) {
                    throw std::runtime_error("could not find .bsp file"); }
            };

            ~Bsp() {};

            // Vertex vertices[] = some_bsp::getLump<Vertex>(LUMP::VERTICES);
            // char raw_lump[] = some_bsp::getLump<char>(LUMP::VERTICES);
            template<typename T>
            T* getLump(int LUMP_index) {
                T* lump_entries;
                LumpHeaderStruct header = this->headers[LUMP_index];
                this->_file.seekg(header.offset, std::ios::beg);
                this->_file.read((char*) &lump_entries, header.length);
                return lump_entries;
            };

            // Vertex v; v = some_bsp::getLumpEntry<Vertex>(LUMP::VERTICES, 0);
            // char raw_snippet[1024]; raw_snippet = some_bsp::getLumpEntry<char>(LUMP::VERTICES, 0);
            template <typename T>
            T getLumpEntry(int LUMP_index, int entry_index) {
                T lump_entry;
                LumpHeaderStruct header = this->headers[LUMP_index];
                this->_file.seekg(header.offset + (sizeof(T) * entry_index), std::ios::beg);
                this->_read(&lump_entry);
                return lump_entry;
            };
    };


    namespace id_software {
        const int FILE_MAGIC = ('I' + ('B' << 8) + ('S' << 16) + ('P' << 24));
        struct LumpHeader { int offset, length; };

        class IdTechBsp : public Bsp<LumpHeader, 17> {
            public:
                using BspBaseClass = Bsp<LumpHeader, 17>;

                IdTechBsp(const char filename[]) : BspBaseClass(filename) {
                    this->_file.seekg(0, std::ios::beg);
                    int file_magic; this->_read(&file_magic);
                    if (file_magic != FILE_MAGIC) {
                        throw std::runtime_error("unexpected file magic for IBSP"); }
                    this->_read(&this->format_version);
                    this->_read(&this->headers);
                };

                ~IdTechBsp() {};
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
        class ValveBsp : public Bsp<LumpHeader, 64> {
            public:
                int revision;

                using BspBaseClass = Bsp<LumpHeader, 64>;

                ValveBsp(const char filename[]) : BspBaseClass(filename) {
                    this->_file.seekg(0, std::ios::beg);
                    int file_magic = 0; this->_read(&file_magic);
                    if (file_magic != FILE_MAGIC) {
                        throw std::runtime_error("unexpected file magic for VBSP"); }
                    this->_read(&this->format_version);
                    this->_read(&this->headers);
                    this->_read(&this->revision);
                };

                ~ValveBsp() {};
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

        class RespawnBsp : public Bsp<LumpHeader, 128> {
            public:
                std::fstream _external[128];
                int revision;

                using BspBaseClass = Bsp<LumpHeader, 128>;

                RespawnBsp(const char filename[]) : BspBaseClass(filename) {
                    this->_file.seekg(0, std::ios::beg);
                    int file_magic, lump_count; this->_read(&file_magic);
                    if (file_magic != FILE_MAGIC) {
                        throw std::runtime_error("unexpected file magic for rBSP"); }
                    this->_read(&this->format_version);
                    this->_read(&this->revision);
                    this->_read(&lump_count);
                    if (lump_count != 127) {
                        throw std::runtime_error("rBSP header does not contain '127'"); }
                    this->_read(&this->headers);
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

                ~RespawnBsp() {};

                // Vertex v[] = some_bsp::getExternalLump<Vertex>(LUMP::VERTICES);
                // char raw_lump[] = some_bsp::getExternalLump<char>(LUMP::VERTICES);
                template<typename T>
                T* getExternalLump(int LUMP_index) {
                    T* lump_entries;
                    std::fstream external_lump = this->_external[LUMP_index];
                    external_lump.seekg(0, std::ios::beg);
                    external_lump >> lump_entries;
                    return lump_entries;
                };

                // Vertex v = some_bsp::getExternalLumpEntry<Vertex>(LUMP::VERTICES, 0);
                // char raw_snippet[1024] = some_bsp::getExternalLumpEntry<char>(LUMP::VERTICES, 0);
                template <typename T>
                T getExternalLumpEntry(int LUMP_index, int entry_index) {
                    T lump_entry;
                    std::fstream external_lump = this->_external[LUMP_index];
                    external_lump.seekg(sizeof(T) * entry_index, std::ios::beg);
                    external_lump.read((char*) &lump_entry, sizeof(T));
                    return lump_entry;
                };
        };
    }

    /* Common Methods */

    /* Game Lump */
    struct GameLumpHeader { char id[4]; unsigned short flags, version; int offset, length; };

    // Gets the sub-headers in the internal game lumps of a bsp file
    // NOTE: will only read the game lump in the .bsp file, not external lumps
    template<typename BSPVariant>
    struct GameLumpHeader* getGameLumpHeaders(BSPVariant bsp) {
        bsp._file.seekg(bsp.headers[35].offset);  // NOTE: LUMP::GAME_LUMP is usually 35
        int game_lump_count;
        bsp._read(&game_lump_count);
        struct GameLumpHeader game_lump_headers[game_lump_count];
        bsp._read(&game_lump_headers);
        return game_lump_headers;
    };
}
