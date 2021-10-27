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
    int       position;
    int       normal;
    float     colour[3];
    Vector2D  uv;
};


// TODO: shader init, buffer init, libsm64 init

using namespace bsp_tool::respawn_entertainment;
void load_bsp(RespawnBsp bsp, GLuint vertex_buffer, GLuint index_buffer) {
    // TODO
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
    if (argc <= 1) { // a.out
        print_help(argv[0]);  // NOTE: print usage and render the window
    }
    else if (argc == 4) {  // a.out MAPNAME.bsp WIDTH HEIGHT
        width  = atoi(argv[2]);
        height = atoi(argv[3]);
    }
    else if (argc != 2) { // a.out MAPNAME.bsp
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
    glClearColor(0.25, 0.25, 0.25, 0.0);
    glEnable(GL_DEPTH_TEST);
    // TODO: load shaders
    // TODO: vertex & index buffers

    // TODO: libsm64

    // SIMULATION VARIABLES
    // bsp_tool::respawn_entertainment::RespawnBsp  bsp = (argv[1]);
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
