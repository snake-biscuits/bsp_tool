import ctypes
import itertools
from time import time

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
from sdl2 import *

import texture
from utils import camera
from utils import vector


camera.sensitivity = .5


def main(width, height):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"SDL2 OpenGL", SDL_WINDOWPOS_CENTERED,  SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS)
    glContext = SDL_GL_CreateContext(window)
    SDL_GL_SetSwapInterval(0)
    glClearColor(0.1, 0.1, 0.1, 0.0)
    gluPerspective(90, width / height, 0.1, 4096)
    glPolygonMode(GL_BACK, GL_LINE)

    mousepos = vector.vec2(0, 0)
    keys = set()
    
    VIEW_CAMERA = camera.freecam(None, None, 32)

    pixel_formats = {SDL_PIXELFORMAT_BGR24: GL_BGR} # 24bpp .bmp

    # {name: {width, height, pixel_format, ...}}
    loaded_textures = dict() # load each texture once
    vmt_map = dict() # {vmt_filename: vtf_filename}
    
    bsp_skyname = "sky_hydro_01" # worldspawn (first entity in LUMP_ENTITIES)
    sky_scale = 512
    sky_textures = dict()
    tails = ["dn", "up", "rt", "lf", "ft", "bk"] # Z-up
    for t in tails:
        vmt_filename = f"materials/skybox/{bsp_skyname}{t}.vmt"
        # PARSE VMT HERE TO FIND ACTUAL VTF & MODIFIERS
        filename = f"materials/skybox/{bsp_skyname}{t}.bmp"
        vmt_map[vmt_filename] = filename
        if filename not in loaded_textures:
            bmp = texture.load_BMP(filename)
            x_scale = sky_scale / bmp.width
            y_scale = sky_scale / bmp.height
            scaled_texture = bmp.scale(x_scale, y_scale)
            loaded_textures[filename] = scaled_texture
        else:
            print(f"{t} already loaded: {filename}")
        sky_textures[vmt_filename] = filename
    
    # use already loaded textures
    cubemap_faces = ["POSITIVE_Y", "NEGATIVE_Y", "POSITIVE_Z", "NEGATIVE_Z", "POSITIVE_X", "NEGATIVE_X"]
    # {"dn": "POSITIVE_Y", "up": "NEGATIVE_Y"} etc.
    # TODO: rotate textures for some faces
    # GL_TEXTURE_CUBE_MAP_POSITIVE_X 	Right	rt / _hdrrt
    # GL_TEXTURE_CUBE_MAP_NEGATIVE_X 	Left	lf / _hdrlf
    # GL_TEXTURE_CUBE_MAP_POSITIVE_Y 	Top	up / _hdrup
    # GL_TEXTURE_CUBE_MAP_NEGATIVE_Y 	Bottom	dn / _hdrdn
    # GL_TEXTURE_CUBE_MAP_POSITIVE_Z 	Back	bk / _hdrft
    # GL_TEXTURE_CUBE_MAP_NEGATIVE_Z 	Front	ft / _hdrft
    for tex, face in zip(sky_textures, cubemap_faces):
        tex = loaded_textures[vmt_map[tex]]
        target = eval(f"GL_TEXTURE_CUBE_MAP_{face}")
        glTexImage2D(target, 0, GL_RGBA, tex.width, tex.height, 0, tex.pixel_format, GL_UNSIGNED_BYTE, tex.pixels)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS) # OpenGL 3.5+

    # GENERATE SKYBOX CUBE
    vertices = []
    for i in range(8):
        x = 1 if i // 4 % 2 == 0 else -1
        y = 1 if i // 2 % 2 == 0 else -1
        z = 1 if i % 2 == 0 else -1
        vertices.append((x, y, z))

    indices = [6, 4, 0, 2,  3, 1, 5, 7,  7, 5, 4, 6,
               2, 0, 1, 3,  0, 4, 5, 1,  6, 2, 3, 7]

    sky_vert = compileShader(open("shaders/300_ES/skybox.v", "rb"), GL_VERTEX_SHADER)
    sky_frag = compileShader(open("shaders/300_ES/skybox.f", "rb"), GL_FRAGMENT_SHADER)
    sky_shader = compileProgram(sky_vert, sky_frag)
    glLinkProgram(sky_shader)
    glUseProgram(sky_shader)

    MVP_MATRIX = glGetFloatv(GL_MODELVIEW_MATRIX)
    MVP_LOCATION = glGetUniformLocation(sky_shader, "mvpMatrix")
    glUniformMatrix4fv(MVP_LOCATION, 1, GL_FALSE, *MVP_MATRIX)

    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_CaptureMouse(SDL_TRUE)

    oldtime = time()
    tick_ms = 0.015
    dt = tick_ms
    event = SDL_Event()
    while True:
        # PARSE INPUT
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
            if SDLK_r in keys: # RESET
                VIEW_CAMERA = camera.freecam(None, None, 256)
            if SDLK_BACKQUOTE in keys:
                print(f"{VIEW_CAMERA.position:.3f}")
                
        dt = time() - oldtime
        if dt >= tick_ms:
            # BEGIN TICK
            VIEW_CAMERA.update(mousepos, keys, tick_ms)
            # END TICK
            dt -= tick_ms
            oldtime = time()

        # BEGIN DRAW
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # CAMERA ROTATION
        glLoadIdentity()
        gluPerspective(90, width / height, 0.1, 128)
        glRotate(-90, 1, 0, 0)
        glRotate(VIEW_CAMERA.rotation.x, 1, 0, 0)
        glRotate(VIEW_CAMERA.rotation.z, 0, 0, 1)
        # SKYBOX
        glDepthMask(GL_FALSE)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(sky_shader)
        MVP_MATRIX = glGetFloatv(GL_MODELVIEW_MATRIX)
        glUniformMatrix4fv(MVP_LOCATION, 1, GL_FALSE, *MVP_MATRIX)
        glBegin(GL_QUADS)
        for i in indices:
            glVertex(*vertices[i])
        glEnd()
        # CAMERA POSITION
        glTranslate(-VIEW_CAMERA.position.x, -VIEW_CAMERA.position.y, -VIEW_CAMERA.position.z)
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glUseProgram(0)
        # ORIGIN
        glBegin(GL_LINES)
        glColor(1, 0, 0) # X+ Red
        glVertex(0, 0, 0)
        glVertex(1, 0, 0)
        glColor(0, 1, 0) # Y+ Green
        glVertex(0, 0, 0)
        glVertex(0, 1, 0)
        glColor(0, 0, 1) # Z+ Blue
        glVertex(0, 0, 0)
        glVertex(0, 0, 1)
        glEnd()
        # WORLD GEO DRAWN OVER SKYBOX
        glColor(1, .5, 0)
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex(1, 1)
        glTexCoord(1, 0)
        glVertex(-1, 1)
        glTexCoord(1, 1)
        glVertex(-1, -1)
        glTexCoord(0, 1)
        glVertex(1, -1)
        glEnd()
        # END DRAW
        SDL_GL_SwapWindow(window)


if __name__ == "__main__":
    try:
        main(640, 360)
    except Exception as exc:
        SDL_Quit()
        raise exc
