#TODO:
#mouse select faces
# --raycast drawn planes
# --return index in bsp.FACES
# --Tkinter face edit window (realtime?)
#lightmap textures (mapping?)
#vis simulation
#  --traverse vis tree
#  --use nodes to faces?
#physics simulation
#  --planes booleaned with nodes
#better camera speed control
# --camera speed inconsistent
# --fullscreen overclocks
#console
# --exec(input())
#skybox.vmt / .exr
#fix t-juncs
#https://www.gamedev.net/forums/topic/230012-eliminating-discontinuities-t-junctions-in-bsp/
#lightmap atlas
# --bleeding / stitching
# --bleed for edges that do not touch
# --stitch for edges that do touch
#texture atlas
# --uvs are already scaled
# --lightmaps are 2048x2048 pixels (may not fit due to shapes)
# --lightmap RGBExp32 to RGB8 on GPU (render whole atlas and discard shader)
#displacements
# --blending
# --triangle_strip
# --faster vertex assembly
# --assemble vertex bytes (uvs need this) THEN sort into index buffer
#do t-juncts affect origfaces?
#TODO: change commented out code to launch options
import colorsys
import compress_sequence
import ctypes
import itertools
import json
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
from sdl2 import *
from time import time
import urllib.request
import camera
import struct
import sys
sys.path.insert(0, '../')
import bsp_tool
from vector import *

def clamp(x, minimum=0, maximum=1):
    return maximum if x > maximum else minimum if x < minimum else x

def main(width, height, bsp):
    bsp = bsp_tool.bsp(bsp)
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(bytes(bsp.filename, 'utf-8'), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL) #| SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    glClearColor(0, 0, 0, 0)
    gluPerspective(90, width / height, 0.1, 4096 * 4)
    glPointSize(2)
    glPolygonMode(GL_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glEnable(GL_CULL_FACE)
    glColor(1, 1, 1)

    filtered_faces = list(filter(lambda x: x['lightofs'] != -1, bsp.FACES)) #no sky or trigger
##    filtered_faces = list(filter(lambda x: x['lightofs'] != -1 and x['dispinfo'] == -1, bsp.FACES)) #no sky, trigger or disp
##    filtered_faces = list(filter(lambda x: x['styles'] == (-1, -1, -1, -1), bsp.FACES))
##    filtered_faces = bsp.FACES

    face_count = len(filtered_faces)
    current_face_index = 0
    current_face = filtered_faces[current_face_index]
    current_face_verts = [v[0] for v in bsp.verts_of(current_face)]

    all_faces = []
    all_faces_map = []
    start = 0
    t1 = time()
    for face in filtered_faces:
        if face['dispinfo'] == -1:
            f_verts = bsp.verts_of(face)
            out = f_verts[:3]
            f_verts = f_verts[3:]
            for vert in f_verts:
                out += [out[0], out[-1], vert]
            f_verts = out
            f_verts_len = len(f_verts)
            all_faces_map.append((start, f_verts_len))
            start += f_verts_len
        else:
            power = bsp.DISP_INFO[face['dispinfo']]['power']
            f_verts = bsp.dispverts_of(face)
            f_verts = bsp_tool.disp_tris(f_verts, power)
        all_faces += f_verts
##    slow_faces = all_faces.copy()
    all_faces = list(itertools.chain(*itertools.chain(*all_faces)))
    all_faces_size = len(all_faces)
    
##    RGB_LIGHTING = []
##    for RGBE_texel in struct.iter_unpack('3Bb', bsp.LIGHTING):
##        RGBA_texel = vec3(RGBE_texel[:-1]) * 2 ** RGBE_texel[-1]
##        RGBA_texel = [clamp(int(x) // 2, 0, 255) for x in RGBA_texel]
##        RGB_LIGHTING.append(struct.pack('3Bb', *RGBA_texel, RGBE_texel[3]))
##    RGB_LIGHTING = b''.join(RGB_LIGHTING)
##
##    lightmap = [] # try pixel buffers
##    for face in filtered_faces:
##        lmap_start = face['lightofs']
##        if lmap_start != -1:
##            bounds = face['LightmapTextureSizeinLuxels']
##            bounds = [x + 1 for x in bounds]
##            num_styles = sum([1 if x is not -1 else 0 for x in face['styles']])
##            lmap_end = lmap_start + bounds[0] * bounds[1] * 4 * num_styles
##            lmap_bytes = RGB_LIGHTING[lmap_start:lmap_end]
##            lightmap.append([lmap_bytes, bounds])
    
    t2 = time()
    print(bsp.filename.upper(), end=' ')
    print(f'{bsp.bytesize // 1024:,}KB BSP', end=' >>> ')
    print(f'{len(all_faces) // 9:,} TRIS', end=' & ')
    print(f'{(len(all_faces) * 4) // 1024:,}KB VRAM')
    print(f'ASSEMBLED IN {(t2 - t1) * 1000:,.3f}ms')

    USING_ES = False
    try:
        vertShader = compileShader(open('shaders/bsp_faces.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_faces.f', 'rb'), GL_FRAGMENT_SHADER)
    except RuntimeError: # requires PyOpenGL changes described elsewhere
        vertShader = compileShader(open('shaders/bsp_faces_300_es.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_faces_300_es.f', 'rb'), GL_FRAGMENT_SHADER)
        USING_ES = True # if OpenGL 4.5 is not supported, switch to GLES 3.0
    bsp_shader = compileProgram(vertShader, fragShader)
    glLinkProgram(bsp_shader)
    if USING_ES:
        # GLES vertex attribs
        attrib_position = glGetAttribLocation(bsp_shader, 'vertexPosition')
        attrib_normal = glGetAttribLocation(bsp_shader, 'vertexNormal')
        attrib_texture_uv = glGetAttribLocation(bsp_shader, 'vertexTexCoord')
        attrib_lightmap_uv = glGetAttribLocation(bsp_shader, 'vertexLightCoord')
        attrib_colour_uv = glGetAttribLocation(bsp_shader, 'vertexColour')
##        ProjectionMatrixLoc = glGetUniformLocation(bsp_shader, 'ProjectionMatrix')
##        # https://www.khronos.org/opengl/wiki/GluPerspective_code
##        glUniformMatrix4fv(ProjectionMatrixLoc, 1, GL_FALSE, ProjectionMatrix) # bad input?

    STATIC_BUFFER = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, STATIC_BUFFER)
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
    # displacement alpha (seperate format or shared?)
    glBufferData(GL_ARRAY_BUFFER, len(all_faces) * 4, np.array(all_faces, dtype=np.float32), GL_STATIC_DRAW)

    glEnable(GL_TEXTURE_2D)

##    activeTexture = 0
##    glGenTextures(1, activeTexture)
##    glBindTexture(GL_TEXTURE_2D, activeTexture)
    
    glActiveTexture(GL_TEXTURE0)
##    texture = open('obsolete.bmp', 'rb')
    texture = open('materials/dev/reflectivity_40.bmp', 'rb')
    texture.seek(54)
##    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB4, 256, 256, 0, GL_BGR, GL_UNSIGNED_BYTE, texture.read())
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB4, 512, 512, 0, GL_BGR, GL_UNSIGNED_BYTE, texture.read())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    texture.close()
    del texture

##    Texture0Loc = glGetUniformLocation(bsp_shder, "activeTexture")
##    glUniform1i(Texture0Loc, activeTexture)

##    texture = lightmap[0]
##    glActiveTexture(GL_TEXTURE1)
##    glEnable(GL_TEXTURE_2D)
##    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texture[1][0], texture[1][1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture[0])
##    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
##    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
##
##    glActiveTexture(GL_TEXTURE0)

    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)

    cam_spawn = vec3(0, 0, 32)
    init_speed = 128
    VIEW_CAMERA = camera.freecam(cam_spawn, None, init_speed)

    # http://heatmaps.tf/api.html
    url_tail = '.json?fields=id,timestamp,killer_class,killer_weapon,killer_x,killer_y,killer_z,victim_class,victim_x,victim_y,victim_z,customkill,damagebits,death_flags,team&limit=1024'
##    heatmap = json.load(urllib.request.urlopen('http://heatmaps.tf/data/kills/' + bsp.filename[:-4] + url_tail)) # including the limit in the url is great for load times
    heatmap = json.load(open('heatmaps.tf/pl_upward_complete.json'))
    k_class = heatmap['fields'].index('killer_class')
    k_wep = heatmap['fields'].index('killer_weapon')
    MINI_SENTRY = -2
    SENTRY = -1
    WORLD = 0
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
    kill_range = lambda kill: (vec3(*kill[v_x:v_x + 3]) - vec3(*kill[k_x:k_x + 3])).magnitude()
    
    filtered_kills = [*filter(lambda k: k[k_wep] == MINI_SENTRY, heatmap['kills'])][:1024]

    mousepos = vec2()
    keys = []

    tickrate = 120
    oldtime = time()
    event = SDL_Event()
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
            #update projection matrix
            if SDLK_BACKQUOTE in keys:
##                print(VIEW_CAMERA)
                #FACES
                print()
                print(current_face)
                if current_face['texinfo'] != -1:
                    print(bsp.TEXINFO[current_face['texinfo']])
##                face_center = sum(map(vec3, current_face_verts), vec3()) / len(current_face_verts)
##                face_normal = bsp.PLANES[current_face['planenum']]['normal']
##                VIEW_CAMERA.position = face_center + vec3(face_normal) * 32
                while SDLK_BACKQUOTE in keys:
                    keys.remove(SDLK_BACKQUOTE)
            if SDLK_r in keys:
                VIEW_CAMERA = camera.freecam(cam_spawn, None, init_speed)
            if SDLK_LSHIFT in keys:
                VIEW_CAMERA.speed += 5
            if SDLK_LCTRL in keys:
                VIEW_CAMERA.speed -= 5
            if SDLK_LEFT in keys or SDL_BUTTON_LEFT in keys:
                current_face_index -= 1
                current_face = filtered_faces[current_face_index]
                current_face_verts = [v[0] for v in bsp.verts_of(current_face)]
                while SDLK_LEFT in keys:
                    keys.remove(SDLK_LEFT)
                while SDL_BUTTON_LEFT in keys:
                    keys.remove(SDL_BUTTON_LEFT)
            if SDLK_RIGHT in keys or SDL_BUTTON_RIGHT in keys:
                current_face_index += 1
                current_face = filtered_faces[current_face_index]
                current_face_verts = [v[0] for v in bsp.verts_of(current_face)]
                while SDLK_RIGHT in keys:
                    keys.remove(SDLK_RIGHT)
                while SDL_BUTTON_RIGHT in keys:
                    keys.remove(SDL_BUTTON_RIGHT)
            dt -= 1 / tickrate
            oldtime = time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        VIEW_CAMERA.set()

        glPolygonMode(GL_FRONT, GL_FILL)
##        glUseProgram(bsp_shader)
##        for i, face in enumerate(all_faces_map):
##            texture = lightmap[i]
##            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture[1][0], texture[1][1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture[0])
##            glDrawArrays(GL_TRIANGLES, face[0], face[1])
        glDrawArrays(GL_TRIANGLES, 0, all_faces_size) # supported in gl3.0 Mesa?

        # for when shaders are too much work
##        glBegin(GL_TRIANGLES)
##        for pos, normal, uv, uv2, colour in slow_faces[:2048]:
##            glColor(*colour)
##            glTexCoord(*uv)
##            glVertex(*pos)
##        glEnd()

##        glUseProgram(0)
##        glBegin(GL_LINES)
##        glColor(1, 0, 0)
##        glVertex(0, 0, 0)
##        glVertex(128, 0, 0)
##        glColor(0, 1, 0)
##        glVertex(0, 0, 0)
##        glVertex(0, 128, 0)
##        glColor(0, 0, 1)
##        glVertex(0, 0, 0)
##        glVertex(0, 0, 128)
##        glEnd()

##        glUseProgram(0)
        glDisable(GL_TEXTURE_2D)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor(1, 1, 1)
        glDisable(GL_DEPTH_TEST)
        glBegin(GL_LINE_LOOP)
        for vertex in current_face_verts:
            glVertex(*vertex)
        glEnd()
        glEnable(GL_DEPTH_TEST)

        glTranslate(0, 0, 64)
        glBegin(GL_LINES)
        for kill in filtered_kills:
            glColor(*colorsys.hsv_to_rgb(kill[k_class] / 9, 1, .75))
            glVertex(*kill[k_x:k_x + 3])
            glColor(*colorsys.hsv_to_rgb(kill[v_class] / 9, 1, 1))
            glVertex(*kill[v_x:v_x + 3])
        glEnd()

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    import getopt
    import sys, os
    options = getopt.getopt(sys.argv[1:], 'w:h:bsp:')
    # try argpase
    width, height = 1280, 720
    bsp = '../maps/pl_upward.bsp'
    for option in options:
        for key, value in option:
            if key == '-w':
                width = int(value)
            elif key == '-h':
                height = int(value)
            elif key == '-bsp':
                bsp = value
    try:
        main(width, height, bsp)
    except Exception as exc:
        SDL_Quit()
        raise exc
