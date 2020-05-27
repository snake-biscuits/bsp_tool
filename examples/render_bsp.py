import colorsys
import ctypes
import itertools
import math
import time
import struct
import sys
# third-party imports
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
from sdl2 import *
# local imports
import utils.camera
sys.path.insert(0, '../')
import bsp_tool
from vector import *

utils.camera.sensitivity = 2

def clamp(x, minimum=0, maximum=1):
    return maximum if x > maximum else minimum if x < minimum else x

def calcTriFanIndices(vertices, startIndex):
    "polygon to triangle fan (indices only) - by Exactol"
    indices = []
    for i in range(1, len(vertices) - 1):
        indices += [startIndex, startIndex + i, startIndex + i + 1]
    return indices

def main(width, height, bsp):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(bytes(bsp.filename, 'utf-8'), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL) #| SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    # GL SETUP
    glClearColor(0, .5, 1, 0)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glPointSize(4)
    glPolygonMode(GL_BACK, GL_LINE)
    gluPerspective(90, width / height, 0.1, 4096 * 4)

    # BSP => VERTEX BUFFER OBJECTS
    conversion_start = time.time()
    all_faces = []
    all_faces_map = [] # [(start, length), ...]
    start = 0
    for face in bsp.FACES:
        if face.disp_info == -1:
            f_verts = bsp.verts_of(face) # add to vertex buffer here and fan the indices
            out = f_verts[:3]
            f_verts = f_verts[3:]
            for vert in f_verts:
                out += [out[0], out[-1], vert]
            f_verts = out
            f_verts_len = len(f_verts)
            all_faces_map.append((start, f_verts_len))
            start += f_verts_len
        else: # face is a displacement
            power = bsp.DISP_INFO[face.disp_info].power
            f_verts = bsp.dispverts_of(face)
            f_verts = bsp_tool.disp_tris(f_verts, power)
            f_verts_len = len(f_verts)
            all_faces_map.append((start, f_verts_len))
            start += f_verts_len
        all_faces += f_verts
    slow_faces = all_faces.copy()
    all_faces = list(itertools.chain(*itertools.chain(*all_faces)))
    all_faces_size = len(all_faces)

    vertices = all_faces
    indices = range(all_faces_size)

    conversion_end = time.time()
    print(bsp.filename.upper(), end=' ')
    print(f"{bsp.bytesize // 1024:,}KB BSP", end=" >>> ")
    print(f"{len(vertices) // 9:,} TRIS", end=" & ")
    print(f"{(len(vertices) * 4) // 1024:,}KB VRAM")
    print(f"ASSEMBLED IN {(conversion_end - conversion_start) * 1000:,.3f}ms")
    print()

    VERTEX_BUFFER, INDEX_BUFFER = glGenBuffers(2)
    # VERTICES
    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)
    # INDICES
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, np.array(indices, dtype=np.uint64), GL_STATIC_DRAW)

    # SHADERS
    USING_ES = False
    try:
        vertShader = compileShader(open('shaders/bsp_lightmap.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_lightmap.f', 'rb'), GL_FRAGMENT_SHADER)
    except Exception as exc: # if GLSL 450 not supported, use GLES 300
        raise exc # error may not mean incorrect GLSL version
        USING_ES = True
        vertShader = compileShader(open('shaders/bsp_faces_300_es.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_faces_300_es.f', 'rb'), GL_FRAGMENT_SHADER)
    bsp_shader = compileProgram(vertShader, fragShader)
    glLinkProgram(bsp_shader)
    glUseProgram(bsp_shader) # must call UseProgram before setting uniforms

    # VERTEX FORMAT (FOR SHADERS)
    glEnableVertexAttribArray(0)  #vertexPosition
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 52, GLvoidp(0))
    glEnableVertexAttribArray(1)  #vertexNormal
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_TRUE, 52, GLvoidp(12))
    glEnableVertexAttribArray(2) #vertexTexcoord
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 52, GLvoidp(24))
    glEnableVertexAttribArray(3) #vertexLightmapCoord
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 52, GLvoidp(32))
    glEnableVertexAttribArray(4) #reflectivityColour
    glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 52, GLvoidp(40))

    # UNIFORMS
    if USING_ES:
        attrib_position = glGetAttribLocation(bsp_shader, 'vertexPosition')
        attrib_normal = glGetAttribLocation(bsp_shader, 'vertexNormal')
        attrib_texture_uv = glGetAttribLocation(bsp_shader, 'vertexTexCoord')
        attrib_lightmap_uv = glGetAttribLocation(bsp_shader, 'vertexLightCoord')
        attrib_colour_uv = glGetAttribLocation(bsp_shader, 'vertexColour')
        # get MVP matrix location
##    else: # GLSL 450
##        # SUN (with simulated time of day)
##        try:
##            light_environment = [e for e in bsp.ENTITIES if e.classname == 'light_environment'][0]
##            light_environment.angles = tuple(map(float, light_environment.angles.split(' ')))
##            light_environment.pitch = float(light_environment.pitch)
##            light_environment._light = tuple(map(int, light_environment._light.split(' ')))
##            light_environment._ambient = tuple(map(int, light_environment._ambient.split(' ')))
##            sun_vector = vec3(1, 0, 0).rotate(light_environment.angles[2], -light_environment.pitch, light_environment.angles[1])
##            sun_colour = (*[x / 255 for x in light_environment._light[:3]], light_environment._light[-1]) # vec4 (R, G, B) + Strength
##            sun_ambient = (*[x / 255 for x in light_environment._ambient[:3]], light_environment._ambient[-1]) # vec4 (R, G, B) + Strength
##            glClearColor(*sun_ambient[:3], 0)
##        except: # no light_environment in .bsp
##            sun_vector = vec3(1, 0, 0).rotate(0, 35, 108) # GOLDRUSH
##            sun_colour = (1.00, 0.89, 0.73, 600)
##            sun_ambient = (0.46, 0.45, 0.55, 350)
##            glClearColor(*sun_ambient[:3], 0)
##        glUniform3f(glGetUniformLocation(bsp_shader, 'sun_vector'), *sun_vector)
##        glUniform4f(glGetUniformLocation(bsp_shader, 'sun_colour'), *sun_colour)
##        glUniform4f(glGetUniformLocation(bsp_shader, 'sun_ambient'), *sun_ambient)

    keys = []
    mousepos = vec2()
    view_init = vec3(0, 0, 32), None, 128
    VIEW_CAMERA = utils.camera.freecam(*view_init)

    event = SDL_Event()
    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)

    end_of_previous_tick = time.time()
    tickrate = 120
    while True:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT or event.key.keysym.sym == SDLK_ESCAPE and event.type == SDL_KEYDOWN:
                SDL_GL_DeleteContext(glContext)
                SDL_DestroyWindow(window)
                SDL_Quit()
                return bsp # let the user play with the bsp after we're done
            # KEYBOARD INPUT
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.sym not in keys:
                    keys.append(event.key.keysym.sym)
            if event.type == SDL_KEYUP:
                while event.key.keysym.sym in keys:
                    keys.remove(event.key.keysym.sym)
            # MOUSE INPUT
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

        # PROCESS TICK
        dt = time.time() - end_of_previous_tick
        while dt >= 1 / tickrate:
            VIEW_CAMERA.update(mousepos, keys, 1 / tickrate)
##            sun_vector = sun_vector.rotate(.05, 0, 0)
##            glUseProgram(bsp_shader)
##            glUniform3f(glGetUniformLocation(bsp_shader, 'sun_vector'), *sun_vector)
            # HANDLE KEYPRESSES
            if SDLK_BACKQUOTE in keys: # ~ = print data for debugging
                print(">>> PRINT RELEVANT DATA HERE <<<")
                while SDLK_BACKQUOTE in keys:
                    keys.remove(SDLK_BACKQUOTE)
            if SDLK_r in keys: # R = reset camera
                VIEW_CAMERA = utils.camera.freecam(*view_init)
            if SDLK_LSHIFT in keys: # LShift = Camera speed +
                VIEW_CAMERA.speed += 5
            if SDLK_LCTRL in keys: # LCtrl = Camera speed -
                VIEW_CAMERA.speed -= 5
            dt -= 1 / tickrate # if dt >= 2/tickrate: simulate another tick
            end_of_previous_tick = time.time()

        # RENDER PASS
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        VIEW_CAMERA.set()

##        glPolygonMode(GL_FRONT, GL_FILL)
##        glUseProgram(bsp_shader)
##        for i, face in enumerate(all_faces_map):
##            texture = lightmap[i]
##            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8UI, texture[1][0], texture[1][1], 0, GL_RGBA_INTEGER, GL_UNSIGNED_BYTE, texture[0])
##            glDrawArrays(GL_TRIANGLES, face[0], face[1])
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
##        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, GLvoidp(0))

        # RAW LIGHTMAPS (NO SHADERS)
##        glUseProgram(0)
##        for i, f_map in enumerate(all_faces_map):
####            texture = lightmap[i]
####            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture[1][0], texture[1][1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture[0])
##            face = slow_faces[f_map[0]: f_map[0] + f_map[1]]
##            glBegin(GL_TRIANGLES)
##            for vertex in face:
##                pos, normal, uv, uv2, colour = vertex
##                glColor(*colour)
##                glTexCoord(*uv)
##                glVertex(*pos)
##            glEnd()

        # CENTER MARKER
        glUseProgram(0)
        glBegin(GL_LINES)
        glColor(1, 0, 0)
        glVertex(0, 0, 0)
        glVertex(128, 0, 0)
        glColor(0, 1, 0)
        glVertex(0, 0, 0)
        glVertex(0, 128, 0)
        glColor(0, 0, 1)
        glVertex(0, 0, 0)
        glVertex(0, 0, 128)
        glEnd()

##        glUseProgram(0)
##        # SELECTED FACE
##        glDisable(GL_TEXTURE_2D)
##        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
##        glColor(1, 1, 1)
##        glDisable(GL_DEPTH_TEST)
##        glBegin(GL_LINE_LOOP)
##        for vertex in current_face_verts:
##            glVertex(*vertex)
##        glEnd()
##        glBegin(GL_POINTS)
##        for vertex in current_face_verts:
##            glVertex(*vertex)
##        glEnd()

        # SUN
##        glPointSize(24)
##        glBegin(GL_POINTS)
##        glVertex(*(sun_vector * 4096))
##        glEnd()

        # ENTITIES (prop origins)
##        glPointSize(18)
##        glColor(1, 0, 1)
##        glBegin(GL_POINTS)
##        for p in props:
##            position = [float(s) for s in p.origin.split()]
##            glVertex(*position)
##        glEnd()
##        glPointSize(4)
##        glEnable(GL_DEPTH_TEST)
##        glEnable(GL_TEXTURE_2D)

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    width, height = 1280, 720

    mod = bsp_tool.team_fortress2
    folder = "D:/SteamLibrary/steamapps/common/Team Fortress 2/tf/maps/"
    filename = "cp_cloak.bsp"

##    mod = bsp_tool.titanfall2
##    folder = "E:/Mod/Titanfall2/"
##    filename = "mp_glitch/maps/mp_glitch.bsp"
    
    bsp = bsp_tool.bsp(folder + filename, mod)
    
    try:
        bsp_file = main(1280, 720, bsp)
    except Exception as exc:
        SDL_Quit()
        raise exc
