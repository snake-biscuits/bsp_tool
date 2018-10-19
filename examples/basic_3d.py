import camera
import ctypes
import itertools
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
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
    glPolygonMode(GL_BACK, GL_LINE)

    mousepos = vector.vec2(0, 0)
    keys = set()
    
    VIEW_CAMERA = camera.freecam(None, None, 32)

    pixel_formats = {SDL_PIXELFORMAT_BGR24: GL_BGR} # 24bpp .bmp

    # {name: {width, height, pixel_format, ...}}
    loaded_textures = dict()
    # store the bytes to avoid loading a texture twice
    
    bsp_skyname = 'sky_upward' # worldspawn (first entity in LUMP_ENTITIES)
    tails = ['rt', 'lf', 'ft', 'bk', 'up', 'dn'] # Z-up
    cubemap_faces = ['POSITIVE_X', 'NEGATIVE_X', 'POSITIVE_Y', 'NEGATIVE_Y', 'POSITIVE_Z', 'NEGATIVE_Z']

    #.vmt "$basetexturetrasnsform" "center 0 0 scale 1 2 rotate 0 translate 0 0"
    # load all textures for skybox & scale to 1024 x 1024

    texture_SKYBOX = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_SKYBOX)
    # each texture must be a square, and the same size as the others
    # load textures & scale
    # then load each into the appropriate face
    for tail, face in zip(tails, cubemap_faces):
        # need to create a loadTexture module
        # .bmp (various bpps)
        # .vtf (many compression types)
        # load & read headers purely in python
        # texture file to texture buffer
        target = eval(f'GL_TEXTURE_CUBE_MAP_{face}')
        vmt = vmf_tool.namespace_from(open(f'materials/skybox/{bsp_skyname}{tail}.vmt'))
        texture_filename = f"materials/{vmt.sky['$basetexture']}.bmp"
        texture_filename = "materials/skybox/sky_upwardside.bmp"
        texture_file = open(texture_filename, 'rb')
        texture_file.seek(54)
        texture_bytes = texture_file.read()
        texture_file.close()
        texture_header = SDL_LoadBMP(texture_filename.encode('utf-8')).contents
        pixel_format = pixel_formats[texture_header.format.contents.format]
        texture_width = texture_header.w
        texture_height = texture_header.h
        SDL_FreeSurface(texture_header)
        if texture_width // 2 == texture_height: # square hack
            texture_bytes = bytes(itertools.chain(*[texture_bytes[i*6:(i*6) + 3] for i in range(len(texture_bytes) // 6)]))
            texture_width = texture_height
        elif texture_width != texture_height:
            raise RuntimeError(f'{texture_filename} is not square!')
        glTexImage2D(target, 0, GL_RGBA, texture_width, texture_height, 0, pixel_format, GL_UNSIGNED_BYTE, texture_bytes) 
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS) # OpenGL 3.5+
    
    vertices = []
    for i in range(8):
        x = 1 if i // 4 % 2 == 0 else -1
        y = 1 if i // 2 % 2 == 0 else -1
        z = 1 if i % 2 == 0 else -1
        vertices.append((x, y, z))

    indices = [6, 4, 0, 2,  3, 1, 5, 7,  7, 5, 4, 6,
               2, 0, 1, 3,  0, 4, 5, 1,  6, 2, 3, 7]

    sky_vert = compileShader(open('shaders/skybox.v', 'rb'), GL_VERTEX_SHADER)
    sky_frag = compileShader(open('shaders/skybox.f', 'rb'), GL_FRAGMENT_SHADER)
    sky_shader = compileProgram(sky_vert, sky_frag)
    glLinkProgram(sky_shader)
    glUseProgram(sky_shader)

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
        # rotate camera
        glDepthMask(GL_FALSE)
        glRotate(-90, 1, 0, 0)
        glRotate(VIEW_CAMERA.rotation.x, 1, 0, 0)
        glRotate(VIEW_CAMERA.rotation.z, 0, 0, 1)
        glDisable(GL_DEPTH_TEST)
        # draw skybox
        glUseProgram(sky_shader)
        glBegin(GL_QUADS)
        for i in indices:
            glVertex(*vertices[i])
        glEnd()
        glUseProgram(0)
        glEnable(GL_DEPTH_TEST)
        # move camera
        glTranslate(-VIEW_CAMERA.position.x, -VIEW_CAMERA.position.y, -VIEW_CAMERA.position.z)
        glDepthMask(GL_TRUE)

        # not the skybox (so, the world i guess)
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

        # which way is up?
        glColor(0, 0, 1)
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(0, 0, 1)
        glEnd()

        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    try:
        main(1280, 720)
    except Exception as exc:
        SDL_Quit()
        raise exc
