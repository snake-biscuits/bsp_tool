#include <chrono>
#include <cstdio>

#include <GL/gl.h>  // -lGL
#include <SDL.h>  // `sdl2-config --cflags --libs`
#include <SDL_opengl.h>

// #include "bsp_tool.hpp"
// #include "camera.hpp"


#define WIDTH   960
#define HEIGHT  544


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

    // SETUP OpenGL
    glClearColor(0.25, 0.25, 0.25, 0.0);
    glEnable(GL_DEPTH_TEST);
    // NOTE: gluPerspective 3; GLEW?
    // TODO: load shaders
    // TODO: vertex & index buffers

    // SIMULATION VARIABLES
    // bsp_tool::respawn_entertainment::RespawnBsp  bsp = (argv[1]);
    // Camera  free_cam;
    float  speed = 0.01;
    float  position[3] = {0, 0, 0.5};

    // INPUTS
    SDL_Keycode  key;
    bool         keys[36] = {false};  // [0-9] SDLK_0-9, [10-35] SDLK_a-z
    int          mouse_x, mouse_y;

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
                case SDL_MOUSEMOTION:
                    mouse_x = event.motion.x;
                    mouse_y = event.motion.y;
            }
        }

        // SIMULATE
        tick_delta = (time_ms() - last_tick) + tick_accumulator;  // may be used in draw
        while (tick_delta >= tick_length) {  // 1 tick for each tick elapsed
            // UPDATE
            if (keys[SDLK_w - 87]) {
                position[1] -= speed; }
            else if (keys[SDLK_s - 87]) {
                position[1] += speed; }
            else if (keys[SDLK_a - 87]) {
                position[0] += speed; }
            else if (keys[SDLK_d - 87]) {
                position[0] -= speed; }
            else if (keys[SDLK_r - 87]) {
                glLoadIdentity();
            }
            tick_delta -= tick_length; }
        tick_accumulator = tick_delta;
        last_tick = time_ms();

        // DRAW
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity();  // NOTE: misbehaving
        // CAMERA
        glRotatef(-90, 1, 0, 0);
        glRotatef(mouse_y, 1, 0, 0);
        glRotatef(mouse_x, 0, -1, 0);
        // TODO: SKYBOX
        glTranslated(-position[0], -position[1], -position[2]);
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
        // PRESENT FRAME
        SDL_GL_SwapWindow(window);
    }

    // QUIT
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
