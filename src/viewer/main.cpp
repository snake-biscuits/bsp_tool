#include <chrono>
#include <cstdio>

#include <filesystem>  // --std=c++17 -lstdc++fs
#include <GL/glew.h>  // -lGLEW
#include <GL/gl.h>  // -lGL
#include <glm/mat4x4.hpp>  // -lglm
#include <glm/gtc/type_ptr.hpp>  // -lglm
#define SDL_MAIN_HANDLED  // for Windows
#include <SDL.h>  // `sdl2-config --cflags --libs`
#include <SDL_opengl.h>

#include "../bsp_tool.hpp"  // <filesystem> --std=c++17 -lstdc++fs
#include "camera.hpp"
#include "../respawn_entertainment/meshes.hpp"


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
    RenderVertex *vertices;  // always allocate w/ `new`
    unsigned int  index_count;
    unsigned int *indices;  // always allocate w/ `new`
    /* Shader & Buffer handles */
    GLuint        vertex_buffer;
    GLuint        index_buffer;
    GLuint        shader_program;

    /* Methods */
    RenderObject() {}
    ~RenderObject() {
        delete[] vertices;
        delete[] indices;
    }
};


GLuint basic_shader_from(std::string vert_filename, std::string frag_filename) {
    GLuint shaders[2];
    char error_message[4096];  // should be enough, can't be bothered with accuracy
    for (int i=0; i<2; i++) {
        std::string filename = i == 0 ? vert_filename : frag_filename;
        std::fstream file;
        if (!std::filesystem::exists(filename)) {
            sprintf(error_message, "'%s' does not exist", filename.c_str());
            throw std::runtime_error(error_message);
        }
        int shader_length = std::filesystem::file_size(filename);
        file.open(filename, std::ios::in);
        if (!file) {
            sprintf(error_message, "Couldn't open '%s'", filename.c_str());
            throw std::runtime_error(error_message);
        }
        const GLchar *shader_text;
        shader_text = (const GLchar*) malloc(shader_length + 1);
        file.read((char*) shader_text, shader_length + 1);
        file.close();
        GLenum shader_type = i == 0 ? GL_VERTEX_SHADER : GL_FRAGMENT_SHADER;
        shaders[i] = glCreateShader(shader_type);
        glShaderSource(shaders[i], 1, &shader_text, &shader_length);
        glCompileShader(shaders[i]);
        // verify shader compiled
        GLint compile_success;
        glGetShaderiv(shaders[i], GL_COMPILE_STATUS, &compile_success);
        if (compile_success == GL_FALSE)  {
            GLint log_length;
            glGetShaderiv(shaders[i], GL_INFO_LOG_LENGTH, &log_length);
            char *error_log = (char*) malloc(log_length);
            glGetShaderInfoLog(shaders[i], log_length, &log_length, error_log);
            const char* shader_type_name = i == 0 ? "vertex" : "fragment";
            sprintf(error_message, "Failed to compile %s shader (%s):\n%s\nSource (%d bytes):\n%s",
                    shader_type_name, filename.c_str(), error_log, shader_length, (char*) shader_text);
            throw std::runtime_error(error_message);
        }
    }
    GLuint shader_program = glCreateProgram();
    glAttachShader(shader_program, shaders[0]);  // vertex
    glAttachShader(shader_program, shaders[1]);  // fragment
    glLinkProgram(shader_program);
    glDetachShader(shader_program, shaders[0]);
    glDetachShader(shader_program, shaders[1]);
    return shader_program;
}


void r1_rbsp_geo_init(bsp_tool::respawn_entertainment::RespawnBsp *bsp, RenderObject *out) {
    // Titanfall rBSP worldspawn (bsp.MODELS[0]) -> RenderObject
    using namespace bsp_tool::respawn_entertainment::titanfall;

    // read contents of lump `ENUM` into array of type `Type` named `name` & record lump length
    // NOTE: sadly we cannot concatenate `LUMP::##name` because marcos require each side to be a valid token pre-concatenation
    #define GET_LUMP(Type, name, ENUM) \
        int name##_SIZE = bsp->header[ENUM].length / sizeof(Type); \
        Type *name = new Type[name##_SIZE]; \
        bsp->getLump<Type>(ENUM, name);
    GET_LUMP(unsigned short, MESH_INDICES,    LUMP::MESH_INDICES   )
    GET_LUMP(Vector,         VERTICES,        LUMP::VERTICES       )
    GET_LUMP(Vector,         VERTEX_NORMALS,  LUMP::VERTEX_NORMALS )
    GET_LUMP(VertexUnlit,    VERTEX_UNLIT,    LUMP::VERTEX_UNLIT   )
    GET_LUMP(VertexLitFlat,  VERTEX_LIT_FLAT, LUMP::VERTEX_LIT_FLAT)
    GET_LUMP(VertexLitBump,  VERTEX_LIT_BUMP, LUMP::VERTEX_LIT_BUMP)
    GET_LUMP(VertexUnlitTS,  VERTEX_UNLIT_TS, LUMP::VERTEX_UNLIT_TS)
    #undef GET_LUMP

    unsigned int VERTEX_UNLIT_OFFSET    = 0;
    unsigned int VERTEX_LIT_FLAT_OFFSET = VERTEX_UNLIT_SIZE;
    unsigned int VERTEX_LIT_BUMP_OFFSET = VERTEX_LIT_FLAT_OFFSET + VERTEX_LIT_FLAT_SIZE;
    unsigned int VERTEX_UNLIT_TS_OFFSET = VERTEX_LIT_BUMP_OFFSET + VERTEX_LIT_BUMP_SIZE;
    out->vertex_count = VERTEX_UNLIT_TS_OFFSET + VERTEX_UNLIT_TS_SIZE;
    out->vertices = new RenderVertex[out->vertex_count];

    VertexUnlit    vertex_unlit;
    VertexLitFlat  vertex_lit_flat;
    VertexLitBump  vertex_lit_bump;
    VertexUnlitTS  vertex_unlit_ts;
    RenderVertex render_vertex;
    int vertex_count = 0;
    #define COPY_RENDER_VERTICES(VERTEX_LUMP, mesh_vertex) \
        for (int i = 0; i < VERTEX_LUMP##_SIZE; i++) { \
            mesh_vertex = VERTEX_LUMP[i]; \
            render_vertex.position = VERTICES[mesh_vertex.position]; \
            render_vertex.normal = VERTEX_NORMALS[mesh_vertex.normal]; \
            render_vertex.uv = mesh_vertex.uv; \
            out->vertices[vertex_count] = render_vertex; \
            vertex_count++; \
        }
    COPY_RENDER_VERTICES(VERTEX_UNLIT,    vertex_unlit   )
    COPY_RENDER_VERTICES(VERTEX_LIT_FLAT, vertex_lit_flat)
    COPY_RENDER_VERTICES(VERTEX_LIT_BUMP, vertex_lit_bump)
    COPY_RENDER_VERTICES(VERTEX_UNLIT_TS, vertex_unlit_ts)
    #undef COPY_RENDER_VERTICES

    out->indices = new unsigned int[MESH_INDICES_SIZE];
    unsigned int  total_indices = 0;
    unsigned int  vertex_lump_offset;
    Model         worldspawn = bsp->getLumpEntry<Model>(LUMP::MODELS, 0);
    // TODO: create a render object for each Model (w/ shared vertex buffer)
    for (unsigned int i = 0; i < worldspawn.num_meshes; i++) {
        Mesh mesh = bsp->getLumpEntry<Mesh>(LUMP::MESHES, worldspawn.first_mesh + i);
        MaterialSort material_sort = bsp->getLumpEntry<MaterialSort>(LUMP::MATERIAL_SORT, mesh.material_sort);
        TextureData texture_data = bsp->getLumpEntry<TextureData>(LUMP::TEXTURE_DATA, material_sort.texture_data);
        switch (mesh.flags & FLAG::MASK_VERTEX) {
            case FLAG::VERTEX_UNLIT:
                vertex_lump_offset = VERTEX_UNLIT_OFFSET;    break;
            case FLAG::VERTEX_LIT_FLAT:
                vertex_lump_offset = VERTEX_LIT_FLAT_OFFSET; break;
            case FLAG::VERTEX_LIT_BUMP:
                vertex_lump_offset = VERTEX_LIT_BUMP_OFFSET; break;
            case FLAG::VERTEX_UNLIT_TS:
                vertex_lump_offset = VERTEX_UNLIT_TS_OFFSET; break;
        }
        for (int j = 0; j < mesh.num_triangles * 3; j++) {
            unsigned int vertex_index = material_sort.vertex_offset + MESH_INDICES[mesh.first_mesh_index + j];
            vertex_index += vertex_lump_offset;
            render_vertex = out->vertices[vertex_index];
            memcpy(render_vertex.colour, texture_data.colour, sizeof(float) * 3);
            out->vertices[vertex_index] = render_vertex;
            out->indices[total_indices] = vertex_index;
            total_indices += 1;
        }
    }
    out->index_count = total_indices;
    printf("Using %d of %d potential indices\n", total_indices, MESH_INDICES_SIZE);
    delete[] MESH_INDICES;
    delete[] VERTICES;
    delete[] VERTEX_NORMALS;
    delete[] VERTEX_UNLIT;
    delete[] VERTEX_LIT_FLAT;
    delete[] VERTEX_LIT_BUMP;
    delete[] VERTEX_UNLIT_TS;
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
    printf("    currently only supports Titanfall & Titanfall: Online .bsp files\n");
}


// TODO: optionally set shader folder in args


int main(int argc, char* argv[]) {
    int width  = WIDTH;
    int height = HEIGHT;
    if (argc == 4) {  // a.out MAPNAME.bsp WIDTH HEIGHT
        width  = atoi(argv[2]);
        height = atoi(argv[3]);
    }
    else if (argc != 2) {  // invalid input
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
    glewInit();
    glClearColor(0.5, 0.0, 0.5, 0.0);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_POLYGON_OFFSET_LINE);
    glEnable(GL_POLYGON_OFFSET_FILL);
    glPointSize(4);

    // TODO: move all the initialisation to other functions
    // -- keeping stale temp variables around is wasteful
    // SIMULATION VARIABLES
    using namespace bsp_tool::respawn_entertainment;
    RespawnBsp bsp_file = (argv[1]);
    RenderObject bsp;
    r1_rbsp_geo_init(&bsp_file, &bsp);
    printf("%d triangles; %d KB\n", bsp.index_count / 3, static_cast<int>(sizeof(RenderVertex) * bsp.vertex_count / 1024));
    // TODO: move this buffer initialisation to other functions / RenderObject methods
    // vertex buffer
    glGenBuffers(1, &bsp.vertex_buffer);
    glBindBuffer(GL_ARRAY_BUFFER, bsp.vertex_buffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(RenderVertex) * bsp.vertex_count, bsp.vertices, GL_STATIC_DRAW);
    // explaining the RenderVertex struct to shaders
    glEnableVertexAttribArray(0);  // vertex_position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, position));
    glEnableVertexAttribArray(1);  // vertex_normal
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, normal));
    glEnableVertexAttribArray(2);  // vertex_colour
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, colour));
    glEnableVertexAttribArray(3);  // vertex_uv0
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, uv));
    // index buffer
    glGenBuffers(1, &bsp.index_buffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bsp.index_buffer);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(unsigned int) * bsp.index_count, bsp.indices, GL_STATIC_DRAW);
    // shaders
    // NOTE: shaders can be editted without recompiling C++
    // -- however, shader uniform use is hardcoded
    std::filesystem::path exe_dir(argv[0]);
    exe_dir = exe_dir.parent_path();
    std::filesystem::path vertex_shader_file = "../src/viewer/shaders/basic.vert";
    vertex_shader_file = exe_dir / vertex_shader_file;
    std::filesystem::path fragment_shader_file = "../src/viewer/shaders/basic.frag";
    fragment_shader_file = exe_dir / fragment_shader_file;
    try {
        bsp.shader_program = basic_shader_from(vertex_shader_file.string(), fragment_shader_file.string());
    } catch (const std::runtime_error& e) {
        fprintf(stderr, "%s\n", e.what());
        SDL_DestroyWindow(window);  // could goto a label to kill, but that feels cursed imo
        SDL_Quit();
        return 1;
    };
    glUseProgram(bsp.shader_program);
    // TODO: create & mutate camera matrices in camera.hpp w/ <glm>
    GLint view_matrix_loc = glGetUniformLocation(bsp.shader_program, "view_matrix");
    glm::mat4 view_matrix;

    // TODO: libsm64 init
    // NOTE: 1024 triangle limit on static geo
    // sm64_static_surfaces_load(bsp.worldspawn)  // need to dynamically update?
    // sm64_surface_object_create(bsp.model[i])
    // sm64_surface_object_move(bsp.model[i])
    // sm64_mario_create(*bsp.spawnpoint[0].xyz)

    // TODO: squirrel VM for vscript

    camera::FirstPerson fp_camera;
    memset(fp_camera.motion, false, 6);
    fp_camera.position = {0.0, 0.0, 64.0};
    fp_camera.rotation = {0.0, 0.0, 0.0};
    fp_camera.sensitivity = 0.25;
    fp_camera.speed = 1.0;

    camera::Lens lens;
    lens.fov = 90;
    lens.aspect_ratio = static_cast<float>(width) / static_cast<float>(height);
    lens.clip.near = 16;
    lens.clip.far = 102400;
    lens.update_matrix();
    glUniformMatrix4fv(view_matrix_loc, 1, GL_FALSE, glm::value_ptr(lens.matrix));

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
                        keys[key - 87] = true; }         // keys[10-35]
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
                fp_camera.motion[PAN_DOWN] = true;
            }
            if (keys[SDLK_e - 87]) {
                fp_camera.motion[PAN_UP] = true;
            }
            if (keys[SDLK_f - 87]) {  // print some debug info here
                printf("fp_camera @ (%.3f, %.3f, %.3f)\n",
                       fp_camera.position.x, fp_camera.position.y, fp_camera.position.z);
            }
            fp_camera.update(mouse, tick_delta);
            mouse = {0, 0};  // zero the mouse to eliminate drift
            // END TICK
            tick_delta -= tick_length;
        }
        tick_accumulator = tick_delta;
        last_tick = time_ms();

        // DRAW
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        // CAMERA
        glPushMatrix();
        // lens.update_matrix();
        view_matrix = fp_camera.rotate(lens.matrix);
        // TODO: SKYBOX
        view_matrix = fp_camera.translate(view_matrix);
        // WORLD
        glUseProgram(bsp.shader_program);
        // TODO: update view_matrix with camera transforms
        glUniformMatrix4fv(view_matrix_loc, 1, GL_FALSE, glm::value_ptr(view_matrix));
        glDrawElements(GL_TRIANGLES, bsp.index_count, GL_UNSIGNED_INT, NULL);
        glPopMatrix();
        // PRESENT FRAME
        SDL_GL_SwapWindow(window);
    }

    // QUIT
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
