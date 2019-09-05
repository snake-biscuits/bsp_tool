#TODO:
# mouse select faces
# -- raycast drawn planes
# -- return index in bsp.FACES
# -- face edit window
# lightmap textures (mapping?)
#  -- clusters
#  -- traverse vis tree
#  -- use nodes to faces?
# physics simulation
#  -- planes booleaned with nodes
# console
# -- exec(input())
# skybox.vmt / .exr
# FIX SCRAMBLED FACES
# fix t-juncs
# https://www.gamedev.net/forums/topic/230012-eliminating-discontinuities-t-junctions-in-bsp/
# lightmap atlas
# -- bleeding / stitching
# -- bleed for edges that do not touch
# -- stitch for edges that do touch
# texture atlas
# -- uvs are already scaled
# -- lightmap pack
# -- lightmap lump size limit is 2048x2048 pixels (may not fit in that area)
# -- RGBExp32 conversion to RGB8 or similar (adjust with HDR?)
# displacements
# -- texture blending
# -- triangle_strip stitching (performance increase?)
# -- smooth normals (calculate normal per tri & blend)
# do t-juncts affect origfaces?
#TODO: change commented out code to modes / options
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

def calcTriFanIndices(vertices, startIndex):
    "polygon to triangle fan (indices only) by Exactol"
    indices = []
    for i in range(1, len(vertices) - 1):
        indices += [startIndex, startIndex + i, startIndex + i + 1]
    return indices

def main(width, height, bsp):
    bsp = bsp_tool.bsp("../maps/02a.bsp", mod=bsp_tool.vindictus)
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(bytes(bsp.filename, 'utf-8'), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL) #| SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    glClearColor(0, .5, 1, 0)
    
    try:
        light_environment = [e for e in bsp.ENTITIES if e.classname == 'light_environment'][0]
        light_environment.angles = tuple(map(float, light_environment.angles.split(' ')))
        light_environment.pitch = float(light_environment.pitch)
        light_environment._light = tuple(map(int, light_environment._light.split(' ')))
        light_environment._ambient = tuple(map(int, light_environment._ambient.split(' ')))
        sun_vector = vec3(1, 0, 0).rotate(light_environment.angles[2], -light_environment.pitch, light_environment.angles[1])
        sun_colour = (*[x / 255 for x in light_environment._light[:3]], light_environment._light[-1]) # vec4 (R, G, B) + Strength
        sun_ambient = (*[x / 255 for x in light_environment._ambient[:3]], light_environment._ambient[-1]) # vec4 (R, G, B) + Strength
        glClearColor(*sun_ambient[:3], 0)
    except: # no light_environment in .bsp
        sun_vector = vec3(1, 0, 0).rotate(0, 35, 108) # GOLDRUSH
        sun_colour = (1.00, 0.89, 0.73, 600)
        sun_ambient = (0.46, 0.45, 0.55, 350)
        glClearColor(*sun_ambient[:3], 0)
    
    gluPerspective(90, width / height, 0.1, 4096 * 4)
    glPointSize(4)
    glPolygonMode(GL_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glEnable(GL_CULL_FACE)
    glColor(1, 1, 1)

    filtered_faces = [f for f in bsp.FACES if f.light_offset != -1] # no sky or trigger
##    filtered_faces = [f for f in bsp.FACES if f.dispinfo != -1]) # disp only
##    filtered_faces = [f for f in bsp.FACES if f.lightofs != -1 and x.disp_info == -1] # no sky, trigger or disp
##    filtered_faces = [f for f in bsp.FACES if f.styles == (-1, -1, -1, -1)] # unlit? faces
##    filtered_faces = bsp.FACES # no filter

    face_count = len(filtered_faces)
    current_face_index = 0
    current_face = filtered_faces[current_face_index]
    current_face_verts = [v[0] for v in bsp.verts_of(current_face)]

    all_faces = []
    all_faces_map = []
    start = 0
    t1 = time()
    for face in filtered_faces:
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
        all_faces += f_verts
    slow_faces = all_faces.copy()
    all_faces = list(itertools.chain(*itertools.chain(*all_faces)))
    all_faces_size = len(all_faces)

    vertices = all_faces
    indices = range(all_faces_size)

##    print('compressing vertex buffer...')
##    vertices = []
##    indices = []
##    currentIndex = 0
##    for face in filtered_faces:
##        if face["dispinfo"] == -1:
##            faceVerts = bsp.verts_of(face)
##            faceIndices = calcTriFanIndices(faceVerts, currentIndex)
##        else:
##            power = bsp.DISP_INFO[face['dispinfo']]['power']
##            faceVerts = bsp_tool.disp_tris(bsp.dispverts_of(face), power)
##            faceIndices = bsp_tool.disp_tris(range((2 ** power + 1) ** 2), power)
##        vertices += faceVerts
##        indices += faceIndices
##        currentIndex = faceIndices[-1] + 1 # ?
##    vertices = list(itertools.chain(*itertools.chain(*vertices)))

##    RGB_LIGHTING = []
##    for RGBE_texel in struct.iter_unpack('3Bb', bsp.LIGHTING):
##        RGBA_texel = vec3(RGBE_texel[:-1]) * 2 ** RGBE_texel[-1]
##        RGBA_texel = [clamp(int(x) // 2, 0, 255) for x in RGBA_texel]
##        RGB_LIGHTING.append(struct.pack('3Bb', *RGBA_texel, RGBE_texel[3]))
##    RGB_LIGHTING = b''.join(RGB_LIGHTING)
##
##    lightmap = [] # store on GPU
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
    print()

    # SHADERS (check GLSL version)
    USING_ES = False
    try:
        vertShader = compileShader(open('shaders/bsp_faces.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_faces.f', 'rb'), GL_FRAGMENT_SHADER)
    except Exception as exc: # requires PyOpenGL changes described in older version of this repo
        USING_ES = True # if OpenGL 4.5 is not supported, switch to GLES 3.0
        vertShader = compileShader(open('shaders/bsp_faces_300_es.v', 'rb'), GL_VERTEX_SHADER)
        fragShader = compileShader(open('shaders/bsp_faces_300_es.f', 'rb'), GL_FRAGMENT_SHADER)
        raise exc # need to log error if issue is not GLSL version
    bsp_shader = compileProgram(vertShader, fragShader)
    glLinkProgram(bsp_shader)
    glUseProgram(bsp_shader) # must call UseProgram before setting uniforms

    # UNIFORMS
    if USING_ES:
        # GLES vertex attribs
        attrib_position = glGetAttribLocation(bsp_shader, 'vertexPosition')
        attrib_normal = glGetAttribLocation(bsp_shader, 'vertexNormal')
        attrib_texture_uv = glGetAttribLocation(bsp_shader, 'vertexTexCoord')
        attrib_lightmap_uv = glGetAttribLocation(bsp_shader, 'vertexLightCoord')
        attrib_colour_uv = glGetAttribLocation(bsp_shader, 'vertexColour')
##        ProjectionMatrixLoc = glGetUniformLocation(bsp_shader, 'ProjectionMatrix')
##        # https://www.khronos.org/opengl/wiki/GluPerspective_code
##        glUniformMatrix4f?(ProjectionMatrixLoc, ?, GL_FALSE, ...) # bad input?
    else: # glsl 450 core uniforms
        glUniform3f(glGetUniformLocation(bsp_shader, 'sun_vector'), *sun_vector)
        glUniform4f(glGetUniformLocation(bsp_shader, 'sun_colour'), *sun_colour)
        glUniform4f(glGetUniformLocation(bsp_shader, 'sun_ambient'), *sun_ambient)

    VERTEX_BUFFER, INDEX_BUFFER = glGenBuffers(2)
    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW) # INDICES
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW) # VERTICES
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


    glEnable(GL_TEXTURE_2D)
    glActiveTexture(GL_TEXTURE0)
    # texture = open('materials/obsolete.bmp', 'rb')
    texture = open('materials/dev/reflectivity_100.bmp', 'rb')
    texture.seek(54)
    # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB4, 256, 256, 0, GL_BGR, GL_UNSIGNED_BYTE, texture.read())
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB4, 512, 512, 0, GL_BGR, GL_UNSIGNED_BYTE, texture.read())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    texture.close()
    del texture

    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)

    cam_spawn = vec3(0, 0, 32)
    init_speed = 128
    VIEW_CAMERA = camera.freecam(cam_spawn, None, init_speed)

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
                return bsp
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
            sun_vector = sun_vector.rotate(.05, 0, 0)
            glUseProgram(bsp_shader)
            glUniform3f(glGetUniformLocation(bsp_shader, 'sun_vector'), *sun_vector)
            # update projection matrix (GLES only)
            if SDLK_BACKQUOTE in keys:
                face_values = [f"{s}: {getattr(face, s)}" for s in face.__slots__]
                print(f'{bsp.filename}.FACES[{bsp.FACES.index(current_face)}]', *face_values, sep='\n')
                fe, ne = current_face.first_edge, current_face.num_edges
                se_loop = bsp.SURFEDGES[fe:fe + ne]
                e_loop = [bsp.EDGES[e] for e in se_loop]
                face_verts = [bsp.VERTICES[v] for v in itertools.chain(*e_loop)][::2]
                print(*[f"{v.x:.3f}, {v.y:.3f}, {v.z:.3f}" for v in face_verts], sep="\n")
                face_center = sum(map(vec3, current_face_verts), vec3()) / len(current_face_verts)
                face_normal = bsp.PLANES[current_face.plane_num].normal
                VIEW_CAMERA.position = face_center + vec3(face_normal) * 32
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
                # filter to only displacements so I can debug this mess
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
        glUseProgram(bsp_shader)
##        for i, face in enumerate(all_faces_map):
##            texture = lightmap[i]
##            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture[1][0], texture[1][1], 0, GL_RGBA, GL_UNSIGNED_BYTE, texture[0])
##            glDrawArrays(GL_TRIANGLES, face[0], face[1])
##        glDrawArrays(GL_TRIANGLES, 0, all_faces_size) # supported in gl3.0 Mesa?
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, GLvoidp(0))

        # for when shaders are too much work
##        glBegin(GL_TRIANGLES)
##        for pos, normal, uv, uv2, colour in slow_faces[:2048]:
##            glColor(*colour)
##            glTexCoord(*uv)
##            glVertex(*pos)
##        glEnd()

        # CENTER MARKER
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

        glUseProgram(0)
        glDisable(GL_TEXTURE_2D)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor(1, 1, 1)
        glDisable(GL_DEPTH_TEST)
        
        glBegin(GL_LINE_LOOP)
        for vertex in current_face_verts:
            glVertex(*vertex)
        glEnd()
        glBegin(GL_POINTS)
        for vertex in current_face_verts:
            glVertex(*vertex)
        glEnd()
        
        glPointSize(24)
        glBegin(GL_POINTS)
        glVertex(*(sun_vector * 4096))
        glEnd()
        glPointSize(4)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    import getopt
    import sys, os
    options = getopt.getopt(sys.argv[1:], 'w:h:bsp:')
    # try argpase
    width, height = 1280, 720
    TF = 'E:/Steam/SteamApps/common/Team Fortress 2/tf/'
##    bsp = '../maps/pl_upward.bsp'
##    bsp = TF + 'maps/cp_cloak.bsp'
##    bsp = TF + 'maps/cp_manor_event.bsp'
    bsp = TF + 'maps/cp_coldfront.bsp'
##    bsp = TF + 'maps/koth_harvest_final.bsp'
    for option in options:
        for key, value in option:
            if key == '-w':
                width = int(value)
            elif key == '-h':
                height = int(value)
            elif key == '-bsp':
                bsp = value
    try:
        bsp_file = main(width, height, bsp)
    except Exception as exc:
        SDL_Quit()
        raise exc
