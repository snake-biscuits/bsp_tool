import camera
import ctypes
import itertools
from OpenGL.GL import *
from OpenGL.GLU import *
from sdl2 import *
from time import time

import sys
sys.path.insert(0, '../')
import vector

sys.path.insert(0, '../../vmf_tool')
import vmf_tool

camera.sensitivity = .25

def main(width, height):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b'SDL2 OpenGL', SDL_WINDOWPOS_CENTERED,  SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS)
    glContext = SDL_GL_CreateContext(window)
    SDL_GL_SetSwapInterval(0)
    glClearColor(0.1, 0.1, 0.1, 0.0)
    gluPerspective(90, width / height, 0.1, 4096)

    mousepos = vector.vec2(0, 0)
    keys = set()
    
    VIEW_CAMERA = camera.freecam(None, None, 128)

    pixel_formats = {SDL_PIXELFORMAT_BGR24: GL_BGR} # 24bpp .bmp

    bsp_skyname = 'sky_upward' # worldspawn (first entity in LUMP_ENTITIES)
    exts = ['rt', 'lf', 'ft', 'bk', 'up', 'dn'] # Z-up
    cubemap_faces = ['POSITIVE_X', 'NEGATIVE_X', 'POSITIVE_Y', 'NEGATIVE_Y', 'POSITIVE_Z', 'NEGATIVE_Z']

    texture_SKYBOX = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_SKYBOX)
    for ext, face in zip(exts, cubemap_faces):
        # get names of textures from .vmt
        vmt = vmf_tool.namespace_from(open(f'materials/skybox/{bsp_skyname}{ext}.vmt'))
        texture = SDL_LoadBMP(f"materials/{vmt.sky['$basetexture']}.bmp".encode('utf-8'))
        return texture
        target = eval(f'GL_TEXTURE_CUBE_MAP_{face}')
        pixel_format = pixel_formats[texture.format]
        glTexImage2D(target, 0, pixel_format, texture.w, texture.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture.pixels)
    glTexParamateri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParamateri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    
    skybox_cube_vertices = []
    for i in range(8):
        x = 2048 if i // 4 % 2 == 0 else -2048
        y = 2048 if i // 2 % 2 == 0 else -2048
        z = 2048 if i % 2 == 0 else -2048
        corners.append((x, y, z))

    skybox_cube_indices = [0, 1, 2, 3,  0, 1, 2, 3,  0, 1, 2, 3,
                           0, 1, 2, 3,  0, 1, 2, 3,  0, 1, 2, 3]

    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_CaptureMouse(SDL_TRUE)

    oldtime = time()
    tick_ms = 0.015
    dt = tick_ms
    event = SDL_Event()
    while True:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT or event.key.keysym.sym == SDLK_ESCAPE and event.type == SDL_KEYDOWN:
                SDL_GL_DeleteContext(glContext)
                SDL_DestroyWindow(window)
                SDL_Quit()
                return False
            if event.type == SDL_KEYDOWN:
                keys.add(event.key.keysym.sym)
            if event.type == SDL_KEYUP:
                keys.remove(event.key.keysym.sym)
            if event.type == SDL_MOUSEMOTION:
                mousepos += vector.vec2(event.motion.xrel, event.motion.yrel)
                SDL_WarpMouseInWindow(window, width // 2, height // 2)
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button == SDL_BUTTON_RIGHT:
                    active = 0 if active == 1 else 1
            if SDLK_r in keys:
                VIEW_CAMERA = camera.freecam(None, None, 256)
            if SDLK_BACKQUOTE in keys:
                print(f'{VIEW_CAMERA.position:.3f}')
                
        dt = time() - oldtime
        if dt >= tick_ms:
            VIEW_CAMERA.update(mousepos, keys, tick_ms)
            # parse inputs
            # do logic
            dt -= tick_ms
            oldtime = time()

        #DISPLAY
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(90, width / height, 0.1, 128)
        VIEW_CAMERA.set()

        glColor(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex(-8, 8)
        glVertex(8, 8)
        glVertex(8, -8)
        glVertex(-8, -8)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex(-32, 32, -16)
        glVertex(32, 32, -16)
        glVertex(32, -32, -16)
        glVertex(-32, -32, -16)
        glEnd()

        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    try:
        out = main(1280, 720)
        raise RuntimeError()
    except Exception as exc:
        SDL_Quit()
        raise exc
