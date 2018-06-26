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
#fix scrambled disp face bug
#TODO:
#  position to node / leaf
#  get a pvs range and translate to glDrawRangeElements inputs
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

class aabb:
    def __init__(self, mins, maxs):
        self.mins = vec3(mins)
        self.maxs = vec3(maxs)
        self.center = (self.mins + self.maxs) / 2

    def __repr__(self):
        return str(self.mins) + str(self.maxs)

    def draw(self):
        glVertex(self.mins.x, self.maxs.y, self.maxs.z)
        glVertex(*self.maxs)
        glVertex(self.maxs.x, self.mins.y, self.maxs.z)
        glVertex(self.mins.x, self.mins.y, self.maxs.z)

        glVertex(self.mins.x, self.maxs.y, self.maxs.z)
        glVertex(*self.maxs)
        glVertex(self.maxs.x, self.maxs.y, self.mins.z)
        glVertex(self.mins.x, self.maxs.y, self.mins.z)

        glVertex(self.mins.x, self.mins.y, self.maxs.z)
        glVertex(self.maxs.x, self.mins.y, self.maxs.z)
        glVertex(self.maxs.x, self.mins.y, self.mins.z)
        glVertex(*self.mins)

        glVertex(self.mins.x, self.maxs.y, self.mins.z)
        glVertex(self.maxs.x, self.maxs.y, self.mins.z)
        glVertex(self.maxs.x, self.mins.y, self.mins.z)
        glVertex(*self.mins)

def node_aabbs(node, bsp):
    aabbs = []
    for child in node['children']:
        if child > -1: #NODE
            child = bsp.NODES[child]
            aabbs += node_aabbs(child, bsp)
        else: #LEAF
            child = bsp.LEAVES[-1 - child]
        aabbs.append(aabb(child['mins'], child['maxs']))
    return aabbs

def node_faces(node, bsp, all_faces_map):
    child_faces = []
    for child in node['children']:
        if child < 0: #LEAVES ONLY
            child = bsp.LEAVES[-1 -child]
            child_faces = []
            child_flf = child['firstleafface']
            for face in bsp.LEAF_FACES[child_flf:child_flf + child['numleaffaces']]:
                child_faces.append(all_faces_map[face])
    draw_calls = compress_sequence.ref_compress(child_faces) #needs improving
    return draw_calls

def main(width, height, bsp):
    bsp = bsp_tool.bsp(bsp)
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(bytes(bsp.filename, 'utf-8'), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    glColor(0, 0, 0, 0)
    gluPerspective(90, width / height, 0.1, 4096 * 4)
    glPointSize(2)
    glPolygonMode(GL_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    glColor(1, 1, 1)
    glFrontFace(GL_CW)

    filtered_faces = list(bsp.FACES) #unfiltered for draw by node

    FACE = iter(filtered_faces)
    current_face = next(FACE)
    current_face_verts = bsp.verts_of(current_face)

    all_faces = []
    all_faces_map = []
    start = 0
    for face in filtered_faces:
        f_normal = bsp.PLANES[face['planenum']]['normal']
        f_texinfo = bsp.TEXINFO[min(face['texinfo'], len(bsp.TEXINFO)-1)]
        f_texdata = bsp.TEXDATA[min(f_texinfo['texdata'], len(bsp.TEXDATA)-1)]
        f_colour = f_texdata['reflectivity']
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
            f_verts = bsp.dispverts_of(face)
        for vert in f_verts:
            all_faces.append(vert)
            all_faces.append(f_colour)
            all_faces.append(f_normal)
    all_faces = list(itertools.chain(*all_faces))

    NODE = iter(filter(lambda x: x['children'][1] < 0, bsp.NODES))
    NODE = sorted(bsp.NODES, key=lambda node: sum([x[1] for x in node_faces(node, bsp, all_faces_map)]))
    current_node = NODE[0]
    current_node_index = 0
    draw_calls = node_faces(current_node, bsp, all_faces_map)
    current_node_aabb = aabb(current_node['mins'], current_node['maxs'])
    cnff = current_node['firstface']
    current_node_faces = all_faces_map[cnff: cnff + current_node['numfaces']]
    try:
        cn_start = current_node_faces[0][0]
        cn_count = sum([x[1] for x in current_node_faces])
    except:
        cn_start = 0
        cn_count = 0
                    
    all_nodes = list(map(lambda x: aabb(x['mins'], x['maxs']), bsp.NODES))
    all_leaves = list(map(lambda x: aabb(x['mins'], x['maxs']), bsp.LEAVES))

    print(bsp.filename.upper(), end=' ')
    print('{:,}KB BSP'.format(bsp.bytesize // 1024), '>>>', end=' ')
    print('{:,} TRIS'.format(len(all_faces) // 9), end=' & ')
    print('{:,}KB VRAM'.format((len(all_faces) * 4) // 1024))
    print('{:,} NODES'.format(len(bsp.NODES)))
    
    STATIC_BUFFER = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, STATIC_BUFFER)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 36, GLvoidp(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_TRUE, 36, GLvoidp(12))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 36, GLvoidp(24))
    glBufferData(GL_ARRAY_BUFFER, len(all_faces) * 4, np.array(all_faces, dtype=np.float32), GL_STATIC_DRAW)

    vertShader = compileShader(open('bsp_faces.v', 'rb'), GL_VERTEX_SHADER)
    fragShader = compileShader(open('bsp_faces.f', 'rb'), GL_FRAGMENT_SHADER)
    bsp_shader = compileProgram(vertShader, fragShader)
    glLinkProgram(bsp_shader)

    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)

    cam_spawn = vec3(0, 0, 0)
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
            if SDLK_TAB in keys: #skip from game to game
                raise TabError('Fake Error')
            if SDLK_BACKQUOTE in keys:
                #NODES
                print(current_node, draw_calls, sep='\n\n')
                VIEW_CAMERA.position = current_node_aabb.center
                while SDLK_BACKQUOTE in keys:
                    keys.remove(SDLK_BACKQUOTE)
            if SDLK_r in keys:
                VIEW_CAMERA = camera.freecam(cam_spawn, None, init_speed)
            if SDLK_LSHIFT in keys:
                VIEW_CAMERA.speed += VIEW_CAMERA.speed * .125
            if SDLK_LCTRL in keys:
                VIEW_CAMERA.speed -= VIEW_CAMERA.speed * .125
            if SDLK_LEFT in keys or SDL_BUTTON_LEFT in keys:
                current_node_index -= 1
                current_node = NODE[current_node_index]
                draw_calls = node_faces(current_node, bsp, all_faces_map)
                current_node_aabb = aabb(current_node['mins'], current_node['maxs'])
                VIEW_CAMERA.position = current_node_aabb.center
                cnff = current_node['firstface']
                current_node_faces = all_faces_map[cnff:cnff + current_node['numfaces']]
                try:
                    cn_start = current_node_faces[0][0]
                    cn_count = sum([x[1] for x in current_node_faces])
                except:
                    cn_start = 0
                    cn_count = 0
                while SDLK_LEFT in keys:
                    keys.remove(SDLK_LEFT)
                while SDL_BUTTON_LEFT in keys:
                    keys.remove(SDL_BUTTON_LEFT)
            if SDLK_RIGHT in keys or SDL_BUTTON_RIGHT in keys:
                current_node_index += 1
                current_node = NODE[current_node_index]
                draw_calls = node_faces(current_node, bsp, all_faces_map)
                current_node_aabb = aabb(current_node['mins'], current_node['maxs'])
                VIEW_CAMERA.position = current_node_aabb.center
                cnff = current_node['firstface']
                current_node_faces = all_faces_map[cnff:cnff + current_node['numfaces']]
                try:
                    cn_start = current_node_faces[0][0]
                    cn_count = sum([x[1] for x in current_node_faces])
                except:
                    cn_start = 0
                    cn_count = 0
                while SDLK_RIGHT in keys:
                    keys.remove(SDLK_RIGHT)
                while SDL_BUTTON_RIGHT in keys:
                    keys.remove(SDL_BUTTON_RIGHT)
            dt -= 1 / tickrate
            oldtime = time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        VIEW_CAMERA.set()

        glPolygonMode(GL_FRONT, GL_LINE)
##        glUseProgram(0)
        glColor(1, 0, 1)
        glBegin(GL_QUADS)
        current_node_aabb.draw()
        glEnd()
        
        glColor(1, 1, 1)
        glDrawArrays(GL_TRIANGLES, cn_start, cn_count)

##        glUseProgram(bsp_shader)
        glColor(1, .5, 0)
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK, GL_LINE)
        try:
            for draw_call in draw_calls:
                glDrawArrays(GL_TRIANGLES, draw_call[0], draw_call[1])
        except:
            pass

        #CENTER POINT
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

        glPopMatrix()
        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    import getopt
    import sys, os
    options = getopt.getopt(sys.argv[1:], 'w:h:bsp:')
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
##    bsp = TF2 + 'pl_upward'
##    bsp = TF2 + 'ctf_2fort_unpacked'
##    bsp = TF2 + 'tc_hydro_unpacked'
##    bsp = TF2 + DOWNLOAD + 'jump_4starters' #triangles
    bsp = 'bsp_import_props'
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
