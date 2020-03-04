# TODO:
# fix plane collision fp error jerkiness
# .chf Convex Heirarcy File (limit checks to PVS)
# ABCD Plane and AABB defines a surface
# SWEPT LAST-POS COLLISION DETECTION

# PROPER GRAVITY AND PLANE COLISIONS:
# if aabb is intersecting plane, move out of plane along velociy vector
# gravity for given time falling:
# distance = 0.5 * 9.81 * time**2
# Quake 3 Gravity is 800 inches/second
# approx. 20.32 m/s

# ENSURE JUMP IS DETERMINISTIC
# RECORD PEAK HEIGHTS AND TEST AT DIFFERENT TICKRATES

# FLOOR COLLISION IS ROUGH
# VELOCITY ESPECIALLY
import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from sdl2 import *
from time import time

import utils.camera
from utils.physics import aabb

import sys
sys.path.insert(0, '../')
import vector

utils.camera.sensitivity = 2

class plane_struct:
    def __init__(self, normal, distance, BBmin, BBmax):
        self.normal = vector.vec3(normal).normalise()
        self.distance = distance
        self.aabb = aabb(BBmin, BBmax)

    def __repr__(self):
        P = str((self.normal, self.distance))
        return str(P + " " + str(self.aabb))


class client:
    def __init__(self, name):
        self.aabb = aabb((-.5, -.5, 0), (.5, .5, 2))
        self.swept_aabb = aabb((0, 0, 0), (0, 0, 0)) #can be local to update?
        self.camera = utils.camera.firstperson()
        self.position = vector.vec3(0, 0, 0)
        self.old_position = vector.vec3(0, 0, 0)
        self.rotation = vector.vec3(0, 0, 0)
        self.front = vector.vec3(0, 1, 0)
        self.speed = 10
        self.name = name
        self.onGround = False
        self.velocity = vector.vec3()
##        self.last
        #VARIABLE GRAVITY

    def update(self, mouse, keys, dt):#GRAVITY VELOCITY / ACCELERATION
        self.camera.update(mouse)
        self.rotation = self.camera.rotation
        wish_vector = vector.vec3()
        wish_vector.x = ((SDLK_d in keys) - (SDLK_a in keys))
        wish_vector.y = ((SDLK_w in keys) - (SDLK_s in keys))
        true_wish = wish_vector.rotate(0, 0, -self.rotation.z)
        self.front = vector.vec3(0, 1, 0).rotate(0, 0, -self.rotation.z)
        #GET CURRENT FRICTION (FROM SURFACE CONTACT)
        true_speed = self.speed * (1 if self.onGround else 1.75)
        self.position += true_wish * true_speed * dt #NEED FRICTION
        if not self.onGround:
            self.velocity += 0.5 * vector.vec3(0, 0, -9.81) * dt #GRAVITY
        self.onGround = False
        self.old_position = self.position
        self.position += self.velocity
        #min maxing old & new positions
        min_x = min(self.old_position.x, self.position.x)
        max_x = max(self.old_position.x, self.position.x)
        min_y = min(self.old_position.y, self.position.y)
        max_y = max(self.old_position.y, self.position.y)
        min_z = min(self.old_position.z, self.position.z)
        max_z = max(self.old_position.z, self.position.z)
        self.swept_aabb = aabb(vector.vec3(min_x, min_y, min_z) + self.aabb.min,
                               vector.vec3(max_x, max_y, max_z) + self.aabb.max)
        global planes
        for plane in planes: #filtered with position & bsp nodes
            #also should combine results rather than applying in order
            if self.swept_aabb.intersects(plane.aabb):
                p = vector.dot(self.position, plane.normal)
                max_p = self.swept_aabb.depth_along_axis(plane.normal)
                if p <= max_p and p <= abs(plane.distance): # simplify
                    # push out of the plane, without changing velocity
                    self.position += math.fsum([plane.distance, -p]) * plane.normal
                    # reset jump? (45 degree check)
                    if vector.dot(plane.normal, vector.vec3(z=1)) <= math.sqrt(2):
                        self.onGround = True
                    self.velocity = vector.vec3()
                    #friction, surf & bounce
    ##                    self.velocity -= self.velocity * plane.normal
                    if SDLK_SPACE in keys: #JUMP
                        self.velocity.z += .6
    
    def draw_aabb(self, aabb): #should be a function in physics
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
        # FRONT
        glVertex(0, 0, (self.aabb.min.z + self.aabb.max.z) / 2)
        glVertex(self.front.x, self.front.y, (self.aabb.min.z + self.aabb.max.z) / 2)
        # VELOCITY
        glColor(0, 1, 0.1)
        glVertex(0, 0, (self.aabb.min.z + self.aabb.max.z) / 2)
        glVertex(self.velocity.x, self.velocity.y, (self.velocity.z + (self.aabb.min.z + self.aabb.max.z)) / 2)
        # WISH
        glColor(0, 0.1, 1)
        glVertex(0, 0, (self.aabb.min.z + self.aabb.max.z) / 2)
        glVertex(self.velocity.x, self.velocity.y, (self.aabb.min.z + self.aabb.max.z) / 2)
        glEnd()
        glColor(1, 0, 1)
        glBegin(GL_POINTS)
        glVertex(0, 0, 0)
        glEnd()
        self.draw_aabb(self.aabb)
        glPopMatrix()
##        glPushMatrix()
##        glTranslate(self.old_position.x, self.old_position.y, self.old_position.z)
##        glColor(0, 1, 1)
##        glBegin(GL_POINTS)
##        glVertex(0, 0, 0)
##        glEnd()
##        glBegin(GL_LINES)
##        glVertex(0, 0, 0)
##        sweep_line = self.position - self.old_position
##        glVertex(sweep_line.x, sweep_line.y, sweep_line.z)
##        glEnd()
##        self.draw_aabb(self.aabb)
##        glPopMatrix()
##        glColor(1, 0, 0)
##        self.draw_aabb(self.swept_aabb)

    def set_view(self):
        self.camera.set(self.position + (0, 0, 1.75))

    def spawn(self, position=vector.vec3()):
        #take a TFclass and set AABB accordingly
        self.position = position
        self.velocity = vector.vec3()

    def report(self):
        print('@', self.position.z, 'with velocity of:', self.velocity)


def main(width, height):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b'SDL2 OpenGL', SDL_WINDOWPOS_CENTERED,  SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_BORDERLESS)
    glContext = SDL_GL_CreateContext(window)
    SDL_GL_SetSwapInterval(0)
    glClearColor(0.1, 0.1, 0.1, 0.0)
    gluPerspective(90, width / height, 0.1, 4096)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glPointSize(8)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    mouse = vector.vec2(0, 0)
    keys = []
    
    global planes
    planes = [plane_struct((0, 0, 1), 0, (-8, -16, -0.1), (8, 16, 0.1)),
              plane_struct((0, 0, 1), -16, (-32, -32, -15.9), (32, 32, -16.1)),
              plane_struct((1, 0, 1), 0, (-16, -16, 0), (16, 16, 4))]

    # convert planes within aabbs to drawable geo
    # slice planes with other planes to create ngons

    client0 = client('b!scuit') # TODO: draw client name at client position
    spectator_camera = utils.camera.fixed((0, 0, 16), (90, 0, 0))

    # CAMERA SWITCHING SYSTEM IS UGLY
    cameras = [client0.set_view, spectator_camera.set]
    active = 1

    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_CaptureMouse(SDL_TRUE)

    oldtime = time()
    tickrate = 125
    dt = 1 / tickrate
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
                    active = 0 if active == 1 else 1
            if SDLK_r in keys:
                client0.spawn()
            if SDLK_BACKQUOTE in keys:
                client0.report()
        dt = time() - oldtime
        if dt >= 1 / tickrate:
            client0.update(mouse, keys, 1 / tickrate)
            mouse = vector.vec2(0, 0)
            dt -= 1 / tickrate
            oldtime = time()

        # DISPLAY
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(90, width / height, 0.1, 128)
        cameras[active]() # ew

        # floor
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor(1, 0.5, 0, 0.25)
        glBegin(GL_QUADS)
        glVertex(-8, 16)
        glVertex(8, 16)
        glVertex(8, -16)
        glVertex(-8, -16)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex(-32, 32, -16)
        glVertex(32, 32, -16)
        glVertex(32, -32, -16)
        glVertex(-32, -32, -16)
        glEnd()

        glBegin(GL_QUADS)
        glVertex(-8, 16, 4)
        glVertex(8, 16, -4)
        glVertex(8, -16, -4)
        glVertex(-8, -16, 4)
        glEnd()

        glColor(0, 0.5, 1)
        glBegin(GL_LINES)
        for plane in planes:
            glVertex(*(plane.normal * plane.distance))
            glVertex(*(plane.normal * (plane.distance + 1)))
        glEnd()

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        # client
        client0.draw()

        SDL_GL_SwapWindow(window)

if __name__ == '__main__':
    try:
        main(1280, 720)
    except Exception as exc:
        SDL_Quit()
        raise exc
