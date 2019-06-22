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
import camera
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
import sys
sys.path.insert(0, '../')
import bsp_tool
import vector


class aabb:
    def __init__(self, mins, maxs):
        self.mins = vector.vec3(mins)
        self.maxs = vector.vec3(maxs)

    def __repr__(self):
        return f'({self.mins:.3f}), ({self.maxs:.3f})'
    
    def draw(self):
        """use glBegin(GL_LINES)"""
        for axis in range(3):
            min_axis = [*self.mins]
            max_axis = min_axis
            max_axis[axis] = self.maxs[axis]
            glVertex(*min_axis)
            glVertex(*max_axis)

    def contains(self, point):
        for i, a in enumerate(point):
            if not self.min[i] < a < self.max[i]:
                return False
        return True

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

    FACE = iter(bsp.FACES)
    current_face = next(FACE)
    current_face_verts = bsp.verts_of(current_face)

    all_faces = []
    all_faces_map = []
    start = 0
    for face in bsp.FACES:
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
            f_verts = bsp_tool.disp_tris(bsp.dispverts_of(face), power)
        all_faces += f_verts
##    all_faces = list(itertools.chain(*all_faces))

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
    
    # shader & vertex buffer would go here

    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)

    cam_spawn = vector.vec3(0, 0, 0)
    init_speed = 128
    VIEW_CAMERA = camera.freecam(cam_spawn, None, init_speed)

    mousepos = vector.vec2()
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
                mousepos += vector.vec2(event.motion.xrel, event.motion.yrel)
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
                #NODES
                print(current_node, draw_calls, sep='\n\n')
                cn_center = (current_node_aabb.mins + current_node_aabb.maxs) / 2
                VIEW_CAMERA.position = cn_center
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
        glBegin(GL_LINES)
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
    bsp = '../maps/test1.bsp'
    for option in options:
        for key, value in option:
            if key == '-w':
                width = int(value)
            elif key == '-h':
                height = int(value)
            elif key == '-bsp':
                bsp = value
    try:
        bsp = bsp_tool.bsp(bsp) # load bsp file for debug
        main(width, height, bsp)
    except Exception as exc:
        SDL_Quit()
        raise exc
    
