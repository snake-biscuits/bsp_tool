#include <chrono>
#include <cstdio>
#include <cstring>

#include <filesystem>  // --std=c++17 -lstdc++fs
#include <GL/glew.h>  // -lGLEW
#include <GL/gl.h>  // -lGL
#include <glm/mat4x4.hpp>  // -lglm
#include <glm/gtc/type_ptr.hpp>  // -lglm
#define SDL_MAIN_HANDLED  // for Windows
#include <SDL2/SDL.h>  // `sdl2-config --cflags --libs`
#include <SDL2/SDL_opengl.h>

#include "../bsp_tool.hpp"  // BspClasses
// viewer utils
#include "camera.hpp"
#include "renderables.hpp"
// per-branch_script renderable adapters
#include "titanfall.hpp"
#include "apex_legends.hpp"


#define WIDTH   960
#define HEIGHT  544
// NOTE: 960x544 is the screen dimensions of a PSVita


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
        memset((void*) shader_text, 0, shader_length + 1);
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
    // TODO: stop capturing mouse when window is not in focus
    // -- also stop teleporting mouse & simulating ticks while not in focus?

    // SETUP OpenGL
    glewInit();
    glClearColor(0.5, 0.0, 0.5, 0.0);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glFrontFace(GL_CW);
    glCullFace(GL_BACK);
    // TODO: decal rendering
    glEnable(GL_POLYGON_OFFSET_LINE);
    glEnable(GL_POLYGON_OFFSET_FILL);
    glPolygonOffset(1.0, 1.0);

    // TODO: move all the initialisation to other functions
    // -- keeping stale temp variables around is wasteful
    // SIMULATION VARIABLES
    respawn::RespawnBsp bsp_file = argv[1];
    RenderObject bsp;
    if (bsp_file.format_version <= 37) {
        // Titanfall / Titanfall: Online
        // Titanfall 2 & Titanfall 2 Tech Test (vertex_colour is all black)
        rbsp_titanfall_world_geo(&bsp_file, &bsp);
    } else {
        // Apex Legends (up to Season 10)
        rbsp_apex_world_geo(&bsp_file, &bsp);
    }
    printf("%d triangles; %d KB\n", bsp.index_count / 3, static_cast<int>(sizeof(RenderVertex) * bsp.vertex_count / 1024));
    // TODO: move this buffer initialisation to other functions / RenderObject methods
    // vertex buffer
    glGenBuffers(1, &bsp.vertex_buffer);
    glBindBuffer(GL_ARRAY_BUFFER, bsp.vertex_buffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(RenderVertex) * bsp.vertex_count, bsp.vertices, GL_STATIC_DRAW);
    SET_RENDERVERTEX_ATTRIBS  // MACRO; defined in renderables.hpp
    // index buffer
    glGenBuffers(1, &bsp.index_buffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bsp.index_buffer);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(unsigned int) * bsp.index_count, bsp.indices, GL_STATIC_DRAW);
    // shaders
    // TODO: select shaders w/ args (default: basic.vert & basic.frag)
    // NOTE: shaders can be edited without recompiling C++
    // -- however, shader uniform use is hardcoded
    std::filesystem::path exe_dir(argv[0]);
    exe_dir = exe_dir.parent_path();
    std::filesystem::path vertex_shader_file = "../src/viewer/shaders/debug.vert";
    vertex_shader_file = exe_dir / vertex_shader_file;
    std::filesystem::path fragment_shader_file = "../src/viewer/shaders/foggy.frag";
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
    glUniform1i(glGetUniformLocation(bsp.shader_program, "vertex_count"), bsp.vertex_count);
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

    // TODO: lots of frustrum related jitter, especially on large maps
    camera::Lens lens;
    lens.fov = 90;
    lens.aspect_ratio = static_cast<double>(width) / static_cast<double>(height);
    lens.clip.near = 16;
    lens.clip.far = 102400;
    lens.update_matrix();
    glUniformMatrix4fv(view_matrix_loc, 1, GL_FALSE, glm::value_ptr(lens.matrix));

    // INPUTS
    SDL_Keycode       key;
    bool              keys[122] = {false};
    // NOTE: ^ this system can't capture arrow keys or modifiers
    Vector2D<double>  mouse;

    // ENVIRONMENT
    unsigned int current_mesh = 0;  // index into bsp.children

    // TICKS
    uint64_t last_tick = time_ms();
    uint64_t tick_delta;
    uint64_t tick_length = 15; // ms per frame | ~66.67 fps
    uint64_t tick_accumulator = 0;

    // MAIN LOOP
    SDL_Event event;
    while (true) {
        // PROCESS INPUT
        // TODO: move to a function
        while(SDL_PollEvent(&event) != 0) {
            switch (event.type) {
                case SDL_QUIT:
                    goto JMP_QUIT;
                case SDL_KEYDOWN:
                    if (event.key.repeat)
                        break;
                    key = event.key.keysym.sym;
                    if (key == SDLK_ESCAPE)
                        goto JMP_QUIT;
                    if (key < 122) {
                        keys[key] = true;
                    } else {
                        fprintf(stderr, "Key %s (%d) is untracked!\n", SDL_GetKeyName(key), key);
                    }
                    break;
                case SDL_KEYUP:
                    if (event.key.repeat) { break; }
                    key = event.key.keysym.sym;
                    if (key < 122)
                        keys[key] = false;
                    break;
                case SDL_MOUSEMOTION:
                    mouse.x += event.motion.xrel;
                    mouse.y += event.motion.yrel;
                    // SDL_WarpMouseInWindow(window, width / 2, height / 2);
                    break;
            }
        }

        // SIMULATE
        tick_delta = (time_ms() - last_tick) + tick_accumulator;  // may be used in draw
        while (tick_delta >= tick_length) {  // 1 tick for each tick elapsed
            // UPDATE
            // imagine a hashmap matching keys to functions
            // TODO: camera speed increases
            using namespace camera::MOVE;
            memset(fp_camera.motion, false, 6);
            if (keys[SDLK_w])  fp_camera.motion[DOLLY_IN] = true;
            if (keys[SDLK_s])  fp_camera.motion[DOLLY_OUT] = true;
            if (keys[SDLK_a])  fp_camera.motion[PAN_LEFT] = true;
            if (keys[SDLK_d])  fp_camera.motion[PAN_RIGHT] = true;
            if (keys[SDLK_q])  fp_camera.motion[PAN_DOWN] = true;
            if (keys[SDLK_e])  fp_camera.motion[PAN_UP] = true;
            // if (keys[SDLK_LSHIFT])  fp_camera.speed *= 1.25;
            // if (keys[SDLK_LCTRL])   fp_camera.speed *= 0.8;
            // if (keys[SDLK_LEFT])   current_mesh = current_mesh == 0 ? bsp.child_count - 1 : current_mesh - 1;
            // if (keys[SDLK_RIGHT])  current_mesh = current_mesh == bsp.child_count - 1 ? 0 : current_mesh + 1;
            if (keys[SDLK_f]) {  // print some debug info
                printf("fp_camera @ (%.3f, %.3f, %.3f)\n",
                       fp_camera.position.x, fp_camera.position.y, fp_camera.position.z);
                printf("Isolating mesh %d\n", current_mesh);
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
        // lens.update_matrix();
        view_matrix = fp_camera.rotate(lens.matrix);
        // TODO: SKYBOX
        view_matrix = fp_camera.translate(view_matrix);
        // WORLD
        glUseProgram(bsp.shader_program);
        glUniformMatrix4fv(view_matrix_loc, 1, GL_FALSE, glm::value_ptr(view_matrix));
        glDrawElements(GL_TRIANGLES, bsp.index_count, GL_UNSIGNED_INT, NULL);
        /*
        glDrawRangeElements(GL_TRIANGLES,
                            bsp.children[current_mesh].start,
                            bsp.children[current_mesh].start + bsp.children[current_mesh].length,
                            bsp.children[current_mesh].length,
                            GL_UNSIGNED_INT,
                            NULL);
        */
        // NOTE: drawing in immediate mode will require gluPerspective etc. to match the fp_camera.matrix
        // PRESENT FRAME
        SDL_GL_SwapWindow(window);
    }

JMP_QUIT:
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
