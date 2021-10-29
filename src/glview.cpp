#include <chrono>
#include <cstdio>

#include <GL/glew.h>
#include <GL/gl.h>  // -lGL
#include <SDL.h>  // `sdl2-config --cflags --libs`
#include <SDL_opengl.h>

#include "bsp_tool.hpp"
#include "camera.hpp"
#include "respawn_entertainment/meshes.hpp"


#define WIDTH   960
#define HEIGHT  544


struct RenderVertex {
    Vector    position;
    Vector    normal;
    float     colour[3];
    Vector2D  uv;
};


struct RenderObject {
    // Buffer data
    int           vertex_count;
    RenderVertex *vertices;
    // GL object handles
    GLuint        vertex_buffer;
    GLuint        index_buffer;
    GLuint        shader;
};


// TODO: libsm64 init & physics triangles

using namespace bsp_tool::respawn_entertainment;
RenderObject bsp_gl_init(const char* filename) {
    // TODO: init shaders and buffers
    RespawnBsp    bsp = (filename);

    // return objects
    RenderObject out;
    memset(&out, 0, sizeof(RenderObject));

    using namespace titanfall;
    int total_vertices;
    total_vertices  = bsp.header[LUMP::VERTEX_UNLIT   ].length / sizeof(VertexUnlit  );
    total_vertices += bsp.header[LUMP::VERTEX_LIT_FLAT].length / sizeof(VertexLitFlat);
    total_vertices += bsp.header[LUMP::VERTEX_LIT_BUMP].length / sizeof(VertexLitBump);
    total_vertices += bsp.header[LUMP::VERTEX_UNLIT_TS].length / sizeof(VertexUnlitTS);
    out.vertices = (RenderVertex*) malloc(sizeof(RenderVertex) * total_vertices);

    // titanfall lump types
    MaterialSort  material_sort;
    Mesh          mesh;
    TextureData   texture_data;

    printf("MeshIndices:   %d\n", bsp.header[LUMP::MESH_INDICES   ].length);
    printf("Vertices:      %d\n", bsp.header[LUMP::VERTICES       ].length);
    printf("VertexNormals: %d\n", bsp.header[LUMP::VERTEX_NORMALS ].length);
    printf("VertexUnlit:   %d\n", bsp.header[LUMP::VERTEX_UNLIT   ].length);
    printf("VertexLitFlat: %d\n", bsp.header[LUMP::VERTEX_LIT_FLAT].length);
    printf("VertexLitBump: %d\n", bsp.header[LUMP::VERTEX_LIT_BUMP].length);
    printf("VertexUnlitTS: %d\n", bsp.header[LUMP::VERTEX_UNLIT_TS].length);
    // TODO: getLump causes "stack smashing" / buffer overflow (too big?)
    #define getLump(Type, name, ENUM)  Type *name = bsp.getLump<Type>(ENUM)
    getLump(unsigned short,  MESH_INDICES,     LUMP::MESH_INDICES   );
    getLump(Vector,          VERTICES,         LUMP::VERTICES       );
    getLump(Vector,          VERTEX_NORMALS,   LUMP::VERTEX_NORMALS );
    // VERTEX_RESERVED_0-4
    getLump(VertexUnlit,     VERTEX_UNLIT,     LUMP::VERTEX_UNLIT   );
    getLump(VertexLitFlat,   VERTEX_LIT_FLAT,  LUMP::VERTEX_LIT_FLAT);
    getLump(VertexLitBump,   VERTEX_LIT_BUMP,  LUMP::VERTEX_LIT_BUMP);
    getLump(VertexUnlitTS,   VERTEX_UNLIT_TS,  LUMP::VERTEX_UNLIT_TS);
    #undef getLump

    VertexUnlit    vertex_unlit;
    VertexLitFlat  vertex_lit_flat;
    VertexLitBump  vertex_lit_bump;
    VertexUnlitTS  vertex_unlit_ts;

    RenderVertex render_vertex;
    // convert geo  // TODO: SM64Triangles
    #define getRenderVertices(VERTEX_LUMP, mesh_vertex) \
        for (int i = 0; i < mesh.num_vertices; i++) { \
            mesh_vertex = VERTEX_LUMP[MESH_INDICES[mesh.first_vertex + i] + material_sort.vertex_offset]; \
            render_vertex.position = VERTICES[mesh_vertex.position]; \
            render_vertex.normal = VERTEX_NORMALS[mesh_vertex.normal]; \
            memcpy(render_vertex.colour, texture_data.colour, sizeof(float) * 3); \
            render_vertex.uv = mesh_vertex.uv; \
            out.vertices[out.vertex_count] = render_vertex; \
            out.vertex_count++; }
    Model worldspawn = bsp.getLumpEntry<Model>(LUMP::MODELS, 0);
    for (unsigned int i = 0; i < worldspawn.num_meshes; i++) {
        mesh = bsp.getLumpEntry<Mesh>(LUMP::MESHES, worldspawn.first_mesh + i);
        material_sort = bsp.getLumpEntry<MaterialSort>(LUMP::MATERIAL_SORT, mesh.material_sort);
        texture_data = bsp.getLumpEntry<TextureData>(LUMP::TEXTURE_DATA, material_sort.texture_data);
        switch (mesh.flags & FLAG::MASK_VERTEX) {
            case FLAG::VERTEX_UNLIT:  // VERTEX_RESERVED_0
                getRenderVertices(VERTEX_UNLIT, vertex_unlit) break;
            case FLAG::VERTEX_LIT_FLAT:  // VERTEX_RESERVED_1
                getRenderVertices(VERTEX_LIT_FLAT, vertex_lit_flat) break;
            case FLAG::VERTEX_LIT_BUMP:  // VERTEX_RESERVED_2
                getRenderVertices(VERTEX_LIT_BUMP, vertex_lit_bump) break;
            case FLAG::VERTEX_UNLIT_TS:  // VERTEX_RESERVED_3
                getRenderVertices(VERTEX_UNLIT_TS, vertex_unlit_ts) break;
        }
        // TODO: append vertex
    #undef getRenderVertices
    }
    // TODO: grab all models + parent entity origins
    return out;
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
    else if (argc != 2 || argc <= 1) { // invalid input
        print_help(argv[0]);
        // return 0;
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
    glClearColor(0.25, 0.25, 0.25, 0.0);
    glEnable(GL_DEPTH_TEST);
    // TODO: load shaders
    // TODO: vertex & index buffers

    // TODO: libsm64

    // SIMULATION VARIABLES
    // RenderObject bsp = bsp_gl_init(argv[1]);
    RenderObject bsp = bsp_gl_init("/media/bikkie/Sandisk/Respawn/r1o/maps/mp_box.bsp");
    printf("%d, %lu\n", bsp.vertex_count, sizeof(bsp.vertices[0]) / sizeof(bsp.vertices));

    camera::FirstPerson fp_camera;
    memset(fp_camera.motion, false, 6);
    fp_camera.position = {0, 0, 0.5};
    fp_camera.rotation = {0, 0, 0};
    fp_camera.sensitivity = 0.25;
    fp_camera.speed = 0.001;

    camera::Lens lens;
    lens.fov = 90;
    lens.aspect_ratio = static_cast<float>(width) / static_cast<float>(height);
    lens.clip.near = 0.1;
    lens.clip.far = 4096;

    // INPUTS
    SDL_Keycode  key;
    bool         keys[36] = {false};  // [0-9] SDLK_0-9, [10-35] SDLK_a-z
    Vector2D     mouse;

    // TICKS
    uint64_t last_tick = time_ms();
    uint64_t tick_delta;
    uint64_t tick_length = 15; // ~66.67 fps
    uint64_t tick_accumulator = 0;

    // MAIN LOOP
    SDL_Event event;
    bool running = true;
    while (running) {
        // PROCESS INPUT
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
                    break;  // without this a false keyup occurs immediately?
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
            else if (keys[SDLK_s - 87]) {
                fp_camera.motion[DOLLY_OUT] = true;
            }
            else if (keys[SDLK_a - 87]) {
                fp_camera.motion[PAN_LEFT] = true;
            }
            else if (keys[SDLK_d - 87]) {
                fp_camera.motion[PAN_RIGHT] = true;
            }
            else if (keys[SDLK_q - 87]) {
                fp_camera.motion[PAN_UP] = true;
            }
            else if (keys[SDLK_e - 87]) {
                fp_camera.motion[PAN_DOWN] = true;
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
        fp_camera.rotate();  // BUGGY
        // TODO: SKYBOX
        fp_camera.translate();
        // WORLD
        glColor3f(1, 1, 1);
        glBegin(GL_TRIANGLES);
          glVertex2d( 0.1, -0.1);
          glVertex2d( 0.0,  0.1);
          glVertex2d(-0.1, -0.1);
        glEnd();
        glColor3f(1, 0, 1);
        glBegin(GL_TRIANGLES);
          glVertex3d( 0.1, -0.1, -0.1);
          glVertex3d( 0.0,  0.1, -0.1);
          glVertex3d(-0.1, -0.1, -0.1);
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
