#include <chrono>
#include <cstdio>

#include <GL/glew.h>
#include <GL/gl.h>  // -lGL
#define SDL_MAIN_HANDLED  // for Windows
#include <SDL.h>  // `sdl2-config --cflags --libs`
#include <SDL_opengl.h>

#include "bsp_tool.hpp"  // <filesystem> --std=c++17 -lstdc++fs
#include "camera.hpp"
#include "respawn_entertainment/meshes.hpp"


#define WIDTH   960
#define HEIGHT  544
// NOTE: 960x544 is the screen dimensions of a PSVita


struct RenderVertex {
    Vector    position;
    Vector    normal;
    float     colour[3];
    Vector2D  uv;
};


struct RenderObject {
    /* Buffer data */
    unsigned int  vertex_count;
    RenderVertex *vertices;
    unsigned int  index_count;
    unsigned int *indices;
    /* Shader & Buffer handles */
    // GLuint        vertex_buffer;
    // GLuint        index_buffer;
    // GLuint        shader;

    /* Methods */
    RenderObject() {}
    ~RenderObject() {
        delete[] vertices;
        delete[] indices;
    }
};


// TODO: libsm64 init & physics triangles

using namespace bsp_tool::respawn_entertainment;
void bsp_geo_init(RespawnBsp *bsp, RenderObject *out) {
    using namespace titanfall;
    MaterialSort  material_sort;
    Mesh          mesh;
    TextureData   texture_data;

    unsigned int total_vertices;
    total_vertices  = bsp->header[LUMP::VERTEX_UNLIT   ].length / sizeof(VertexUnlit  );
    total_vertices += bsp->header[LUMP::VERTEX_LIT_FLAT].length / sizeof(VertexLitFlat);
    total_vertices += bsp->header[LUMP::VERTEX_LIT_BUMP].length / sizeof(VertexLitBump);
    total_vertices += bsp->header[LUMP::VERTEX_UNLIT_TS].length / sizeof(VertexUnlitTS);
    out->vertices = new RenderVertex[total_vertices];
    unsigned int vertex_count = 0;

    #define GET_LUMP(Type, name, ENUM) \
        int name##_MAX = bsp->header[ENUM].length / sizeof(Type); \
        Type *name = new Type[name##_MAX]; \
        bsp->getLump<Type>(ENUM, name);
    GET_LUMP(unsigned short,  MESH_INDICES,     LUMP::MESH_INDICES   )
    GET_LUMP(Vector,          VERTICES,         LUMP::VERTICES       )
    GET_LUMP(Vector,          VERTEX_NORMALS,   LUMP::VERTEX_NORMALS )
    GET_LUMP(VertexUnlit,     VERTEX_UNLIT,     LUMP::VERTEX_UNLIT   )
    GET_LUMP(VertexLitFlat,   VERTEX_LIT_FLAT,  LUMP::VERTEX_LIT_FLAT)
    GET_LUMP(VertexLitBump,   VERTEX_LIT_BUMP,  LUMP::VERTEX_LIT_BUMP)
    GET_LUMP(VertexUnlitTS,   VERTEX_UNLIT_TS,  LUMP::VERTEX_UNLIT_TS)
    #undef GET_LUMP

    VertexUnlit    vertex_unlit;
    VertexLitFlat  vertex_lit_flat;
    VertexLitBump  vertex_lit_bump;
    VertexUnlitTS  vertex_unlit_ts;

    Model worldspawn = bsp->getLumpEntry<Model>(LUMP::MODELS, 0);
    // worldspawn.num_meshes = 768;  // override
    unsigned int index_offset[worldspawn.num_meshes];  // MeshIndex -> Buffer Index
    unsigned int total_indices = 0;
    RenderVertex render_vertex;
    #define GET_RENDER_VERTICES(VERTEX_LUMP, mesh_vertex) \
        for (int j = 0; j < mesh.num_vertices + 1; j++) { \
            mesh_vertex = VERTEX_LUMP[mesh.first_vertex + j]; \
            render_vertex.position = VERTICES[mesh_vertex.position]; \
            render_vertex.normal = VERTEX_NORMALS[mesh_vertex.normal]; \
            memcpy(render_vertex.colour, texture_data.colour, sizeof(float) * 3); \
            render_vertex.uv = mesh_vertex.uv; \
            out->vertices[vertex_count] = render_vertex; \
            vertex_count++; \
        } \
        break;
    // convert geo
    for (unsigned int i = 0; i < worldspawn.num_meshes; i++) {
        mesh = bsp->getLumpEntry<Mesh>(LUMP::MESHES, worldspawn.first_mesh + i);
        material_sort = bsp->getLumpEntry<MaterialSort>(LUMP::MATERIAL_SORT, mesh.material_sort);
        texture_data = bsp->getLumpEntry<TextureData>(LUMP::TEXTURE_DATA, material_sort.texture_data);
        // indices
        index_offset[i] = vertex_count + material_sort.vertex_offset - mesh.first_vertex;
        total_indices += mesh.num_triangles * 3;
        switch (mesh.flags & FLAG::MASK_VERTEX) {
            case FLAG::VERTEX_UNLIT:  // VERTEX_RESERVED_0
                GET_RENDER_VERTICES(VERTEX_UNLIT, vertex_unlit)
            case FLAG::VERTEX_LIT_FLAT:  // VERTEX_RESERVED_1
                GET_RENDER_VERTICES(VERTEX_LIT_FLAT, vertex_lit_flat)
            case FLAG::VERTEX_LIT_BUMP:  // VERTEX_RESERVED_2
                GET_RENDER_VERTICES(VERTEX_LIT_BUMP, vertex_lit_bump)
            case FLAG::VERTEX_UNLIT_TS:  // VERTEX_RESERVED_3
                GET_RENDER_VERTICES(VERTEX_UNLIT_TS, vertex_unlit_ts)
        }
    }
    #undef GET_RENDER_VERTICES
    out->index_count = total_indices;
    out->indices = new unsigned int[total_indices];
    unsigned int index = 0;
    // NOTE: out->vertices blends all VERTEX_LUMPs
    // VERTEX_LUMP[min({index for index in mesh[I]})] is @ index_offset[I]
    for (unsigned int i = 0; i < worldspawn.num_meshes; i++) {
        mesh = bsp->getLumpEntry<Mesh>(LUMP::MESHES, worldspawn.first_mesh + i);
        for (int j = 0; j < mesh.num_triangles * 3; j++) {
            // TODO: libsm64 SM64Triangles for each Mesh, precalculated for physics
            // NOTE: using PhysicsCollide Triangles would be even better
            out->indices[index] = MESH_INDICES[mesh.first_mesh_index + j] + index_offset[i];
            index++;
        }
    }
    // TODO: grab all models + parent entity origins
    delete[] MESH_INDICES;
    delete[] VERTICES;
    delete[] VERTEX_NORMALS;
    delete[] VERTEX_UNLIT;
    delete[] VERTEX_LIT_FLAT;
    delete[] VERTEX_LIT_BUMP;
    delete[] VERTEX_UNLIT_TS;
    // TODO: indices
    out->vertex_count = vertex_count;
};


uint64_t time_ms() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}


void print_help(char* argv_0) {
    printf("%s MAPNAME [WIDTH HEIGHT]\n", argv_0);
    printf("OpenGL .bsp viewer\n");
    printf("    MAPNAME  .bsp file to load\n");
    printf("    WIDTH    viewport width\n");
    printf("    HEIGHT   viewport height\n");
}


int main(int argc, char* argv[]) {
    int width  = WIDTH;
    int height = HEIGHT;
    if (argc == 4) {  // a.out MAPNAME.bsp WIDTH HEIGHT
        width  = atoi(argv[2]);
        height = atoi(argv[3]);
    }
    else if (argc != 2) { // invalid input
        print_help(argv[0]);
        return 0;
    }

    // SETUP SDL
    SDL_Init(SDL_INIT_VIDEO);
    char  title[4096];  // can't be bothered to malloc an exact value
    sprintf(title, "OpenGL .bsp viewer [%s]", argv[1]);
    SDL_Window *window = SDL_CreateWindow(title, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height,
                                          SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS);
    if (window == NULL) {
        fprintf(stderr, "Couldn't make a window: %s\n", SDL_GetError());
        return 1; }
    SDL_GLContext gl_context = SDL_GL_CreateContext(window);
    if (gl_context == NULL) {
        fprintf(stderr, "Couldn't initialise GL context: %s\n", SDL_GetError());
        return 1; }
    SDL_GL_SetSwapInterval(0);

    SDL_SetRelativeMouseMode(SDL_TRUE);
    SDL_CaptureMouse(SDL_TRUE);

    // SETUP OpenGL
    glClearColor(0.5, 0.0, 0.5, 0.0);
    glEnable(GL_DEPTH_TEST);
    glPointSize(4);
    // TODO: load shaders
    // TODO: vertex & index buffers

    // TODO: libsm64

    // SIMULATION VARIABLES
    using namespace bsp_tool::respawn_entertainment;
    // NOTE: encounters a segfault on any map other than r1o/mp_box or r1/mp_lobby
    // note r1o/mp_npe Mesh #1194 uses VERTEX_LIT_BUMP (empty) w/ negative indices???
    RespawnBsp bsp_file = (argv[1]);
    RenderObject bsp;
    bsp_geo_init(&bsp_file, &bsp);
    printf("%d triangles; %d KB\n", bsp.index_count / 3, static_cast<int>(sizeof(RenderVertex) * bsp.vertex_count / 1024));
    // TODO: bind to buffers and use RenderObject w/ shaders

    unsigned int index;

    camera::FirstPerson fp_camera;
    memset(fp_camera.motion, false, 6);
    fp_camera.position = {0, 0, 64};
    fp_camera.rotation = {0, 0, 0};
    fp_camera.sensitivity = 0.25;
    fp_camera.speed = 1;

    camera::Lens lens;
    lens.fov = 90;
    lens.aspect_ratio = static_cast<float>(width) / static_cast<float>(height);
    lens.clip.near = 16;
    lens.clip.far = 102400;

    // INPUTS
    SDL_Keycode  key;
    bool         keys[36] = {false};  // [0-9] SDLK_0-9; [10-35] SDLK_a-z
    Vector2D     mouse;

    // TICKS
    uint64_t last_tick = time_ms();
    uint64_t tick_delta;
    uint64_t tick_length = 15; // ms per frame | ~66.67 fps
    uint64_t tick_accumulator = 0;

    // MAIN LOOP
    SDL_Event event;
    bool running = true;
    while (running) {
        // PROCESS INPUT
        // TODO: move to a function called by the main while loop
        while(SDL_PollEvent(&event) != 0) {
            switch (event.type) {
                case SDL_QUIT:
                    running = false;
                    break;  // GOTO: QUIT
                case SDL_KEYDOWN:
                    if (event.key.repeat) { break; }
                    key = event.key.keysym.sym;
                    if (key == SDLK_ESCAPE) {
                        running = false;
                        break; }  // GOTO: QUIT
                    else if (48 <= key && key <= 57) {  // SDLK_0-9
                        keys[key - 48] = true; }        // keys[0-9]
                    else if (97 <= key && key <= 122) {  // SDLK_a-z
                        keys[key - 87] = true; }        // keys[10-35]
                    break;
                case SDL_KEYUP:
                    if (event.key.repeat) { break; }
                    key = event.key.keysym.sym;
                    if (48 <= key && key <= 57) {        // SDLK_0-9
                        keys[key - 48] = false; }        // keys[0-9]
                    else if (97 <= key && key <= 122) {  // SDLK_a-z
                        keys[key - 87] = false; }        // keys[10-35]
                    break;
                case SDL_MOUSEMOTION:
                    mouse.x += event.motion.xrel;
                    mouse.y += event.motion.yrel;
                    SDL_WarpMouseInWindow(window, width / 2, height / 2);
                    break;
            }
        }

        // SIMULATE
        tick_delta = (time_ms() - last_tick) + tick_accumulator;  // may be used in draw
        while (tick_delta >= tick_length) {  // 1 tick for each tick elapsed
            // UPDATE
            // imagine a hashmap matching keys to functions
            using namespace camera::MOVE;
            memset(fp_camera.motion, false, 6);
            if (keys[SDLK_w - 87]) {
                fp_camera.motion[DOLLY_IN] = true;
            }
            if (keys[SDLK_s - 87]) {
                fp_camera.motion[DOLLY_OUT] = true;
            }
            if (keys[SDLK_a - 87]) {
                fp_camera.motion[PAN_LEFT] = true;
            }
            if (keys[SDLK_d - 87]) {
                fp_camera.motion[PAN_RIGHT] = true;
            }
            if (keys[SDLK_q - 87]) {
                fp_camera.motion[PAN_UP] = true;
            }
            if (keys[SDLK_e - 87]) {
                fp_camera.motion[PAN_DOWN] = true;
            }
            if (keys[SDLK_f - 87]) {
                // print some debug info here
            }
            fp_camera.update(mouse, tick_delta);
            mouse = {0, 0};  // zero the mouse to eliminate drift
            // END TICK
            tick_delta -= tick_length; }
        tick_accumulator = tick_delta;
        last_tick = time_ms();

        // DRAW
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        // CAMERA
        glPushMatrix();
        lens.use();
        fp_camera.rotate();
        // TODO: SKYBOX
        fp_camera.translate();
        // WORLD
        /* // bsp vertices
        glBegin(GL_POINTS);
        for (unsigned int i = 0; i < bsp.vertex_count; i++) {
            glColor3f(bsp.vertices[i].colour[0], bsp.vertices[i].colour[1], bsp.vertices[i].colour[2]);
            glVertex3d(bsp.vertices[i].position.x, bsp.vertices[i].position.y, bsp.vertices[i].position.z);
        }
        glEnd(); */
        // indexed bsp vertices
        glBegin(GL_TRIANGLES);
        for (unsigned int i = 0; i < bsp.index_count; i++) {
            index = bsp.indices[i];
            glColor3f(bsp.vertices[index].colour[0], bsp.vertices[index].colour[1], bsp.vertices[index].colour[2]);
            // glColor3f(bsp.vertices[index].normal.x, bsp.vertices[index].normal.y, bsp.vertices[index].normal.z);
            glVertex3d(bsp.vertices[index].position.x, bsp.vertices[index].position.y, bsp.vertices[index].position.z);
        }
        glEnd();
        glPopMatrix();
        // PRESENT FRAME
        SDL_GL_SwapWindow(window);
    }

    // QUIT
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
