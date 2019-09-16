import colorsys
import ctypes
import itertools
import json
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from sdl2 import *
from time import time
import sys
sys.path.insert(0, "../")
import utils.camera
from utils.vector import *

utils.camera.sensitivity = 2

def main(width, height, json_file):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b'OpenGL Heatmap', SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL) #| SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    
    glClearColor(0, 0, 0, 0)
    gluPerspective(90, width / height, 0.1, 4096 * 4)
    glPointSize(2)
    glPolygonMode(GL_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glEnable(GL_CULL_FACE)
    glColor(1, 1, 1)

    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)

    heatmap = json.load(open(json_file))
    k_class = heatmap['fields'].index('killer_class')
    UNKNOWN = 0
    SCOUT = 1
    SNIPER = 2
    SOLDIER = 3
    DEMOMAN = 4
    MEDIC = 5
    HEAVY = 6
    PYRO = 7
    SPY = 8
    ENGINEER = 9
    k_x = heatmap['fields'].index('killer_x')
    v_class = heatmap['fields'].index('victim_class')
    v_x = heatmap['fields'].index('victim_x')
    filtered_kills = [*filter(lambda k: k[k_x:k_x + 3] != [0, 0, 0], heatmap['kills'])][:256]

    cam_spawn = vec3(0, 0, 32)
    init_speed = 128
    VIEW_CAMERA = utils.camera.freecam(cam_spawn, None, init_speed)
    mousepos = vec2()
    keys = []
    
    tickrate = 120
    event = SDL_Event()
    oldtime = time()
    while True:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT or event.key.keysym.sym == SDLK_ESCAPE and event.type == SDL_KEYDOWN:
                SDL_GL_DeleteContext(glContext)
                SDL_DestroyWindow(window)
                SDL_Quit()
                return False
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.sym not in keys:
                    keys.append(event.key.keysym.sym)
            if event.type == SDL_KEYUP:
                while event.key.keysym.sym in keys:
                    keys.remove(event.key.keysym.sym)
            if event.type == SDL_MOUSEMOTION:
                mousepos += vec2(event.motion.xrel, event.motion.yrel)
                SDL_WarpMouseInWindow(window, width // 2, height // 2)
            if event.type == SDL_MOUSEWHEEL:
                VIEW_CAMERA.speed += event.wheel.y * 32
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button not in keys:
                    keys.append(event.button.button)
            if event.type == SDL_MOUSEBUTTONUP:
                while event.button.button in keys:
                    keys.remove(event.button.button)

        dt = time() - oldtime
        while dt >= 1 / tickrate:
            VIEW_CAMERA.update(mousepos, keys, 1 / tickrate)
            if SDLK_BACKQUOTE in keys:
                ... # print some statistics
            if SDLK_r in keys:
                VIEW_CAMERA = utils.camera.freecam(cam_spawn, None, init_speed)
            if SDLK_LSHIFT in keys:
                VIEW_CAMERA.speed += VIEW_CAMERA.speed * .125
            if SDLK_LCTRL in keys:
                VIEW_CAMERA.speed -= VIEW_CAMERA.speed * .125
            dt -= 1 / tickrate
            oldtime = time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        VIEW_CAMERA.set()

        glBegin(GL_LINES)
        for x in range(3):
            axis = [0, 0, 0]
            axis[x] = 1
            glColor(*axis)
            glVertex(0, 0, 0)
            axis[x] = 128
            glVertex(*axis)
        glEnd()

        glTranslate(0, 0, 64)
        glBegin(GL_LINES)
        for kill in filtered_kills:
            glColor(*colorsys.hsv_to_rgb(kill[k_class] / 9, 1, .5))
            glVertex(*kill[k_x:k_x + 3])
            glColor(*colorsys.hsv_to_rgb(kill[v_class] / 9, 1, 1))
            glVertex(*kill[v_x:v_x + 3])
        glEnd()

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    main(1280, 720, 'pl_upward.json')
