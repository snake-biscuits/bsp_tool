#TODO:
#mouse select faces
# --raycast each tri in all_faces
# --get all_faces_map index
# --return bsp.FACES[index]
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
import bsp_tool
import compress_sequence
import ctypes
import itertools
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
from sdl2 import *
from time import time
from vector import *
import camera
import sys
import struct

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
    current_face_verts = bsp.verts_of(current_face)

    all_faces = []
    all_faces_map = []
    start = 0
    t1 = time()
    for face in filtered_faces:
        f_normal = bsp.PLANES[face['planenum']]['normal']
        f_texinfo = bsp.TEXINFO[min(face['texinfo'], len(bsp.TEXINFO)-1)]
        f_texdata = bsp.TEXDATA[min(f_texinfo['texdata'], len(bsp.TEXDATA)-1)]
        f_texvecs = f_texinfo['textureVecs']
        f_lightvecs = f_texinfo['lightmapVecs']
        if face['dispinfo'] == -1:
            f_verts = bsp.verts_of(face)
            f_verts = bsp.verts_check(face, f_verts)
            out = f_verts[:3]
            f_verts = f_verts[3:]
            for vert in f_verts:
                out += [out[0], out[-1], vert]
            f_verts = out
            f_verts_len = len(f_verts)
            all_faces_map.append((start, f_verts_len))
            start += f_verts_len
        else:
            f_verts = bsp.dispverts_of(face)
            f_verts_len = len(f_verts)
            all_faces_map.append((start, f_verts_len))
            start += f_verts_len
        for vert in f_verts:
            #github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
            #SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
            uv = [dot(vec3(*vert), vec3(*f_texvecs[0][:-1])) + f_texvecs[0][3],
                  dot(vec3(*vert), vec3(*f_texvecs[1][:-1])) + f_texvecs[1][3]]
            uv[0] /= f_texdata['view_width']
            uv[1] /= f_texdata['view_height']
            uv2 = [dot(vec3(*vert), vec3(*f_lightvecs[0][:-1])) + f_lightvecs[0][3],
                   dot(vec3(*vert), vec3(*f_lightvecs[1][:-1])) + f_lightvecs[1][3]]
            uv2[0] -= face['LightmapTextureMinsinLuxels'][0]
            uv2[1] -= face['LightmapTextureMinsinLuxels'][1]
            uv2[0] /= face['LightmapTextureSizeinLuxels'][0]
            uv2[1] /= face['LightmapTextureSizeinLuxels'][1]
            #displacement lightmaps must be rotated 90 * .index(firstvert) degrees
            all_faces.append(vert)
            all_faces.append(f_normal)
            all_faces.append(uv)
            all_faces.append(uv2)
    all_faces = list(itertools.chain(*all_faces))
    all_faces_size = len(all_faces)
    
    RGB_LIGHTING = []
    for RGBE_texel in struct.iter_unpack('3Bb', bsp.LIGHTING):
        RGBA_texel = vec3(RGBE_texel[:-1]) * 2 ** RGBE_texel[-1]
        RGBA_texel = [clamp(int(x) // 2, 0, 255) for x in RGBA_texel]
        RGB_LIGHTING.append(struct.pack('3Bb', *RGBA_texel, RGBE_texel[3]))
    RGB_LIGHTING = b''.join(RGB_LIGHTING)

    lightmap = []
    for face in filtered_faces:
        lmap_start = face['lightofs']
        if lmap_start != -1:
            bounds = face['LightmapTextureSizeinLuxels']
            bounds = [x + 1 for x in bounds]
            num_styles = sum([1 if x is not -1 else 0 for x in face['styles']])
            lmap_end = lmap_start + bounds[0] * bounds[1] * 4 * num_styles
            lmap_bytes = RGB_LIGHTING[lmap_start:lmap_end]
            lightmap.append([lmap_bytes, bounds])
    
    t2 = time()
    print(bsp.filename.upper(), end=' ')
    print('{:,}KB BSP'.format(bsp.bytesize // 1024), '>>>', end=' ')
    print('{:,} TRIS'.format(len(all_faces) // 9), end=' & ')
    print('{:,}KB VRAM'.format((len(all_faces) * 4) // 1024))
    print('ASSEMBLED IN {:,.3f}ms'.format((t2 - t1) * 1000))

    STATIC_BUFFER = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, STATIC_BUFFER)
    glEnableVertexAttribArray(0)  #vertexPosition
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 40, GLvoidp(0))
    glEnableVertexAttribArray(1)  #vertexNormal
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_TRUE, 40, GLvoidp(12))
    glEnableVertexAttribArray(2) #vertexTexcoord
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 40, GLvoidp(24))
    glEnableVertexAttribArray(3) #vertexLightmapCoord
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 40, GLvoidp(32))
    glBufferData(GL_ARRAY_BUFFER, len(all_faces) * 4, np.array(all_faces, dtype=np.float32), GL_STATIC_DRAW)

    vertShader = compileShader(open('bsp_faces.v', 'rb'), GL_VERTEX_SHADER)
    fragShader = compileShader(open('bsp_faces.f', 'rb'), GL_FRAGMENT_SHADER)
    bsp_shader = compileProgram(vertShader, fragShader)
    glLinkProgram(bsp_shader)

    glEnable(GL_TEXTURE_2D)

##    activeTexture = 0
##    glGenTextures(1, activeTexture)
##    glBindTexture(GL_TEXTURE_2D, activeTexture)
    
    glActiveTexture(GL_TEXTURE0)
##    texture = open('obsolete.bmp', 'rb')
    texture = open('tf2_demo_tool/materials/dev/reflectivity_40.bmp', 'rb')
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
    tickrate = 120

    mousepos = vec2()
    keys = []

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
            if SDLK_TAB in keys: #skips folders
                raise TabError('Fake Error')
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
                VIEW_CAMERA.speed += VIEW_CAMERA.speed * .125
            if SDLK_LCTRL in keys:
                VIEW_CAMERA.speed -= VIEW_CAMERA.speed * .125
            if SDLK_LEFT in keys or SDL_BUTTON_LEFT in keys:
                current_face_index -= 1
                current_face = filtered_faces[current_face_index]
                current_face_verts = bsp.verts_of(current_face)
                while SDLK_LEFT in keys:
                    keys.remove(SDLK_LEFT)
                while SDL_BUTTON_LEFT in keys:
                    keys.remove(SDL_BUTTON_LEFT)
            if SDLK_RIGHT in keys or SDL_BUTTON_RIGHT in keys:
                current_face_index += 1
                current_face = filtered_faces[current_face_index]
                current_face_verts = bsp.verts_of(current_face)
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
        glDrawArrays(GL_TRIANGLES, 0, all_faces_size)

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
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    import getopt
    import sys, os
    options = getopt.getopt(sys.argv[1:], 'w:h:bsp:')
##    width, height = 640, 480
    width, height = 1280, 720
##    width, height = 1920, 1080
##    width, height = 3840, 2160
    steam = 'E:/Steam/SteamApps/common/'
    sourcemod = 'E:/Steam/SteamApps/sourcemods/'
    AS = steam + 'Alien Swarm/swarm/maps/'
    ASRD = steam + 'Alien Swarm Reactive Drop/reactivedrop/maps/'
    BMDS = steam + 'Black Mesa Dedicated Server/bms/maps/'
    CSS = steam + 'Counter-Strike Source/cstrike/maps/'
    CSGO = steam + 'Counter-Strike Global Offensive/csgo/maps/'
    DOD = steam + 'day of defeat source/dod/maps/'
    FF = steam + 'Fortress Forever/FortressForever/maps/'
    FOF = steam + 'Fistful of Frags/fof/maps/'
    GM = steam + 'GarrysMod/garrysmod/maps/'
    HL2 = steam + 'Half-Life 2/hl2/maps/'
    HL2_EP1 = steam + 'Half-Life 2/episodic/maps/'
    HL2_EP2 = steam + 'Half-Life 2/ep2/maps/'
    HL2_DM = steam + 'half-life 2 deathmatch/hl2mp/maps/'
    LW = steam + 'Lambda Wars/lambdawars/maps/'
    L4D = steam + 'left 4 dead/left4dead/maps/'
    L4D_DLC3 = steam + 'left 4 dead/left4dead_dlc3/maps/'
    L4D2 = steam + 'Left 4 Dead 2/left4dead2/maps/' #+dlc1, 2 & 3
    NEOTOKYO = steam + 'NEOTOKYO/NeotokyoSource/maps/'
    PORTAL = steam + 'Portal/portal/maps'
    PORTAL2 = steam + 'Portal 2/portal2/maps/' #dlc1 & 2
    PSM = steam + 'Portal Stories Mel/portal_stories/maps/'
    TF2 = steam + 'Team Fortress 2/tf/maps/'
    TF2C = sourcemod + 'tf2classic/maps/'
    DOWNLOAD = '../download/maps/'
    ...
##    bsp = TF2 + 'cp_coldfront' #horribly messy
##    bsp = 'import_bsp/bsp_import_props'
    bsp = TF2 + 'pl_upward'
##    bsp = 'f:/modding/tf2 maps/cp_sapphire_dev/cp_sapphire_a7'
##    bsp = TF2 + 'pl_badwater_b1'
##    bsp = TF2 + 'ctf_2fort_unpacked'
##    bsp = TF2 + 'tc_hydro_unpacked'
##    bsp = TF2 + DOWNLOAD + 'jump_4starters' #t-juncs
##    bsp = 'import_bsp/bsp_import_props' #small and simple
##    bsp = TF2 + 'ctf_turbine.bsp'
##    bsp = TF2 + 'pl_goldrush_unpacked'
##    bsp = TF2 + 'koth_lazarus_unpacked'
##    bsp = TF2 + 'cp_powerhouse_unpacked'
##    bsp = 'F:/Modding/tf2 maps/_TF2MAPS.NET_DOWNLOADS/maps/pl_shoreleave_rc1_unpacked'
    for option in options:
        for key, value in option:
            if key == '-w':
                width = int(value)
            elif key == '-h':
                height = int(value)
            elif key == '-bsp':
                bsp = value
    main(width, height, bsp)
    raise RuntimeError

    import traceback
    def load_folder(folder, filterfunc=None):
        maplist = list(filter(lambda x: x.endswith('.bsp'), os.listdir(folder)))
        if filterfunc is not None:
            maplist = list(filter(filterfunc, maplist))
        print(folder.split('/')[4], '{} maps'.format(len(maplist)))
        for bsp in maplist:
            try:
                main(width, height, folder + bsp)
            except TabError:
                break
            except Exception as exc:
                print(bsp, 'crashed:', exc)
                traceback.print_tb(exc.__traceback__)

    load_folder(TF2)
    load_folder(TF2 + DOWNLOAD)
    raise RuntimeError()

    load_folder(AS) #Alien Swarn
    load_folder(ASRD) #Alien Swarm: Rewactive Drop
    load_folder(BMDS) #Black Mesa Dedicated Server (SP is vpk)
    load_folder(CSGO) #Counter-Strike: Global Offensive (mostly vpk)
    load_folder(CSS) #Counter-Strike: Source
    load_folder(DOD) #Day of Defeat: Source
    load_folder(FF) #Fortress Forever
    load_folder(FOF) #Fistful of Frags
    load_folder(GM) #Garry's Mod
    load_folder(HL2) #Half-Life 2
    load_folder(HL2_EP1) #Half-Life 2: Episode 1
    load_folder(HL2_EP2) #Half-Life 2: Episode 2
    load_folder(HL2_DM) #Half-Life 2: Deathmatch
    load_folder(LW) #Lambda Wars
    load_folder(L4D) #Left 4 Dead
    load_folder(L4D_DLC3) #Left 4 Dead: The Passing
    load_folder(L4D2) #Left 4 Dead 2
    load_folder(NEOTOKYO) #Neotokyo
    load_folder(PORTAL) #Portal
    load_folder(PORTAL2) #Portal 2
    load_folder(PSM) #Portal Stories Mel
    load_folder(TF2) #Team Fortress 2
    load_folder(TF2C) #Team Fortress 2 Classic
