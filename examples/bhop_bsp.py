#TODO:
#fix plane collision fp error jerkiness
#.chf Convex Heirarcy File
#ABCD Plane and AABB defines a surface

#need to limit auto step to 18 hu
#also walls are sticky
#fix hitting same plane multiple times
#fix a position previously touched pushing

#bounding box switching
#--crouch & crouch jump
#--slide
#--slide jump

#proper acceleration and friction
#use octrees for collision

#raycast collisions to sort closest

#jump counting (double jump)
#water

#walls != floors
#dot plane normal against gravity to get wallness factor
#defines slide amount (SURF!)

#spec cam keyboard and client xbox controller would be neat
from collections import namedtuple
import ctypes
import itertools
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from sdl2 import *
from time import time
import camera
import vector
from physics import aabb
import sys
sys.path.insert(0, '../')
import bsp_tool

gravity = vector.vec3(0, 0, -600)
camera.sensitivity = .25

plane_object = namedtuple('plane', ['normal', 'distance'])

def verts_to_box(verts):
    min_x = max_x = verts[0][0]
    min_y = max_y = verts[0][1]
    min_z = max_z = verts[0][2]
    for vert in verts[1:]:
        if vert[0] < min_x:
            min_x = vert[0]
        elif vert[0] > max_x:
            max_x = vert[0]
        if vert[1] < min_y:
            min_y = vert[1]
        elif vert[1] > max_y:
            max_y = vert[1]
        if vert[2] < min_z:
            min_z = vert[2]
        elif vert[2] > max_z:
            max_z = vert[2]
    return (min_x, min_y, min_z), (max_x, max_y, max_z)

class client:
    def __init__(self, name):
        self.aabb = aabb((-16, -16, 0), (16, 16, 72))
        self.swept_aabb = aabb((0, 0, 0), (0, 0, 0))
        self.camera = camera.firstperson()
        self.position = vector.vec3(0, 0, 0)
        self.old_position = vector.vec3(0, 0, 0)
        self.rotation = vector.vec3(0, 0, 0)
        self.front = vector.vec3(0, 1, 0)
        self.speed = 256
        self.name = name
        self.onGround = False
        self.velocity = vector.vec3()

    def update(self, mouse, keys, dt):
        global gravity
        self.camera.update(mouse)
        self.rotation = self.camera.rotation
        wish_vector = vector.vec3()
        wish_vector.x = ((SDLK_d in keys) - (SDLK_a in keys))
        wish_vector.y = ((SDLK_w in keys) - (SDLK_s in keys))
        true_wish = wish_vector.rotate(0, 0, -self.rotation.z)
        self.front = vector.vec3(0, 1, 0).rotate(0, 0, -self.rotation.z)
        self.velocity += true_wish * self.speed * dt
        self.velocity += 0.5 * gravity * dt
        self.onGround = False
        self.old_position = self.position
        self.position += self.velocity
        min_x = min(self.old_position.x, self.position.x)
        max_x = max(self.old_position.x, self.position.x)
        min_y = min(self.old_position.y, self.position.y)
        max_y = max(self.old_position.y, self.position.y)
        min_z = min(self.old_position.z, self.position.z)
        max_z = max(self.old_position.z, self.position.z)
        self.swept_aabb = aabb(vector.vec3(min_x, min_y, min_z) + self.aabb.min,
                               vector.vec3(max_x, max_y, max_z) + self.aabb.max)
        corners = []
        for i in range(8):
            x = min_x if i // 4 % 2 == 0 else max_x
            y = min_y if i // 2 % 2 == 0 else max_y
            z = min_z if i % 2 == 0 else max_z
            corners.append(vector.vec3(x, y, z))

        global planes
        for plane, faces in planes.items():
            if any(self.swept_aabb.intersects(x) for x in faces):
                intersect_depth = 0
                plane_dot = vector.dot(self.position, plane[0])
                ### Some planes have negative D (distance)
                ### since some planes can face towards O (origin point)
                ### so it will be > for positive D and < for negative
                if plane[1] > 0:
                    if plane_dot > plane[1]:
                        intersect_depth = plane_dot + plane[1]
                else:
                    if plane_dot < plane[1]:
                        intersect_depth = plane_dot - plane[1]
                
                self.position += vector.vec3(*plane[0]) * intersect_depth
                if intersect_depth != 0:
                    global physFrozen
                    physFrozen = True
                    plane_v = vector.vec3(*plane[0])
                    print(f'({plane_v:.2f}) {plane[1]:.2f}D = {plane_dot:.2f} ({intersect_depth:.2f})')
                    self.onGround = True
                    if SDLK_SPACE in keys: #JUMP
                            self.velocity.z += 20
        
    
    def draw_aabb(self, aabb):
        glBegin(GL_QUADS)
        glVertex(aabb.min.x, aabb.max.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.max.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.min.y, aabb.max.z)
        glVertex(aabb.min.x, aabb.min.y, aabb.max.z)

        glVertex(aabb.min.x, aabb.max.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.max.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.max.y, aabb.min.z)
        glVertex(aabb.min.x, aabb.max.y, aabb.min.z)

        glVertex(aabb.min.x, aabb.min.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.min.y, aabb.max.z)
        glVertex(aabb.max.x, aabb.min.y, aabb.min.z)
        glVertex(aabb.min.x, aabb.min.y, aabb.min.z)

        glVertex(aabb.min.x, aabb.max.y, aabb.min.z)
        glVertex(aabb.max.x, aabb.max.y, aabb.min.z)
        glVertex(aabb.max.x, aabb.min.y, aabb.min.z)
        glVertex(aabb.min.x, aabb.min.y, aabb.min.z)
        glEnd()

    def draw(self):
        glPushMatrix()
        glTranslate(self.position.x, self.position.y, self.position.z)
        glColor(1, 0, 1)
        glBegin(GL_LINES)
        glVertex(0, 0, (self.aabb.min.z + self.aabb.max.z) / 2)
        glVertex(self.front.x * 48, self.front.y * 48, (self.aabb.min.z + self.aabb.max.z) / 2)
        glEnd()
        glBegin(GL_POINTS)
        glVertex(0, 0, 0)
        glEnd()
        self.draw_aabb(self.aabb)
        glPopMatrix()
        glPushMatrix()
        glTranslate(self.old_position.x, self.old_position.y, self.old_position.z)
        glColor(0, 1, 1)
        glBegin(GL_POINTS)
        glVertex(0, 0, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        sweep_line = self.position - self.old_position
        glVertex(sweep_line.x, sweep_line.y, sweep_line.z)
        glEnd()
        self.draw_aabb(self.aabb)
        glPopMatrix()
        glColor(1, 0, 0)
        self.draw_aabb(self.swept_aabb)

    def draw_lerp(self, dt):
        global tickrate
        dt *= tickrate
        position = vector.lerp(self.old_position, self.position, dt)
        glPushMatrix()
        glTranslate(*position)
        glColor(1, 0, 1)
        glBegin(GL_LINES)
        glVertex(0, 0, (self.aabb.min.z + self.aabb.max.z) / 2)
        glVertex(self.front.x * 48, self.front.y * 48, (self.aabb.min.z + self.aabb.max.z) / 2)
        glEnd()
        glBegin(GL_POINTS)
        glVertex(0, 0, 0)
        glEnd()
        self.draw_aabb(self.aabb)
        glPopMatrix()

    def set_view(self):
        self.camera.set(self.position + (0, 0, 64))

    def set_view_lerp(self, dt):
        global tickrate
        dt *= tickrate
        position = vector.lerp(self.old_position, self.position, dt)
        self.camera.set(vector.vec3(position) + vector.vec3(0, 0, 64))

    def spawn(self, position=(0, 0, 0)):
        self.position = vector.vec3(position)
        self.velocity = vector.vec3()
        self.onGround = False

    def report(self):
        print('@ {:.2f} {:.2f} {:.2f} with velocity of: {:.2f} {:.2f} {:.2f}'.format(*self.position, *self.velocity))
        print('OnGround' if self.onGround else 'not OnGround')


def main(width, height):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b'SDL2 OpenGL', SDL_WINDOWPOS_CENTERED,  SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS)
    glContext = SDL_GL_CreateContext(window)
    SDL_GL_SetSwapInterval(0)
    glClearColor(0.1, 0.1, 0.1, 0.0)
    gluPerspective(90, width / height, 0.1, 4096)
    glRotate(90, -1, 0, 0)
    glTranslate(0, 8, 0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glEnable(GL_DEPTH_TEST)
    glPointSize(8)

    mouse = vector.vec2(0, 0)
    spec_mouse = mouse
    keys = []

    bsp = bsp_tool.bsp("../mapsrc/bsp_import_props.bsp")

    filtered_faces = list(filter(lambda x: x['lightofs'] != -1, bsp.FACES))

    global planes
    planes = {} # planes = {plane: [*faces], ...}
    for face in filtered_faces:
        plane = bsp.PLANES[face['planenum']]
        verts = bsp.verts_of(face)
        face_bounds = aabb(*verts_to_box(verts))
        plane_key = (plane['normal'], plane['dist'])
        if plane_key in planes.keys():
            planes[plane_key].append(face_bounds)
        else:
            planes[plane_key] = [face_bounds]

    bsptris = list(itertools.chain(*[bsp.verts_of(face) for face in filtered_faces]))

    client0 = client('b!scuit') #TODO: draw client name at client position
    spectator_camera = camera.freecam((0, 0, 128), (0, 0, 0), speed=368)

    active_camera = 0

    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_CaptureMouse(SDL_TRUE)

    global physFrozen
    physFrozen = False

    global tickrate
    tickrate = 1 / 0.015 #66.67 for tf2 (~15ms per frame)
    tick_number = 0
    dt = 1 / tickrate
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
                keys.append(event.key.keysym.sym)
            if event.type == SDL_KEYUP:
                while event.key.keysym.sym in keys:
                    keys.remove(event.key.keysym.sym)
            if event.type == SDL_MOUSEMOTION:
                mouse = vector.vec2(event.motion.xrel, event.motion.yrel)
                SDL_WarpMouseInWindow(window, width // 2, height // 2)
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button == SDL_BUTTON_RIGHT:
                    active_camera = 0 if active_camera == 1 else 1
            if SDLK_r in keys:
                client0.spawn((0, 0, 2048))
            if SDLK_BACKQUOTE in keys:
                physFrozen = False
            if SDLK_SPACE in keys:
                physFrozen = True
                
        dt = time() - oldtime
        if dt >= 1 / tickrate:
            if not physFrozen:
                print('TICK #{}'.format(tick_number))
                tick_number += 1
                client0.report()
            if active_camera == 0:
                if not physFrozen:
                    client0.update(mouse, keys, 1 / tickrate)
            else:
                spec_mouse += mouse
                spectator_camera.update(spec_mouse, keys, 1 / tickrate)
                if not physFrozen:
                    client0.update(vector.vec2(0, 0), [], 1 / tickrate) #inputless update to maintain physics
            mouse = vector.vec2(0, 0)
            dt -= 1 / tickrate
            oldtime = time()

        #DISPLAY
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(90, width / height, 0.1, 4096)
        if active_camera == 0:
            if not physFrozen:
                client0.set_view_lerp(dt)
            else:
                client0.set_view()
        else:
            spectator_camera.set()

        glPolygonMode(GL_BACK, GL_FILL)
        for face in filtered_faces:
            normal = bsp.PLANES[face['planenum']]['normal']
            normal = [(x + 1) / 2 for x in normal]
            colour = normal[0] / 3 + 1/3 * normal[1] / 3 + 2/3 * normal[2] / 3
            glColor(*[[colour] * 3])
            glBegin(GL_POLYGON)
            for vertex in bsp.verts_of(face):
                glVertex(*vertex)
            glEnd()
        glPolygonMode(GL_BACK, GL_LINE)

        # normal indicator
##        glBegin(GL_LINES)
##        for plane in planes:
##            center = sum(plane.aabb, vector.vec3()) / 2
##            glColor(0, 1, 0)
##            glVertex(*center)
##            glColor(.1, .1, .1)
##            glVertex(*(center + plane.normal * 64))
##        glEnd()

        if not physFrozen:
            client0.draw_lerp(dt)
        else:
            client0.draw()

        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    import getopt
    import sys
    options = getopt.getopt(sys.argv[1:], 'w:h:')
    width = 1280
    height = 720
    for option in options:
        for key, value in option:
            if key == '-w':
                width = int(value)
            elif key == '-h':
                height = int(value)
    main(width, height)
