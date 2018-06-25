#TODO:
#First-person and Third-person camera need update
#to receive information based on character motion
#An AI that interprets inputs into realistic camera motion would be cool
#Inputs should be typed (Cython)
#
#FIXED CAMERA with either:
#no rotation
#scripted rotation (i.e. security camera)
#player controlled rotation (i.e. PSX Era Square Enix Games)
#
#Sensitivity is changed by setting camera.sensitivity in main()
#
#Scripted Camera Motion?
#
#Per Camera FoV?

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from sdl2 import *
from vector import vec2, vec3

sensitivity = 0.25

class freecam:
    """Quake / Source Free Camera"""
    
    def __init__(self, position, rotation, speed=0.75):
        self.position = vec3(position) if position != None else vec3()
        self.rotation = vec3(rotation) if rotation != None else vec3()
        self.speed = speed

    def update(self, mousepos, keys, dt): #diagonal?
        global sensitivity
        self.rotation.z = mousepos.x * sensitivity
        self.rotation.x = mousepos.y * sensitivity
        local_move = vec3()
        local_move.x = ((SDLK_d in keys) - (SDLK_a in keys))
        local_move.y = ((SDLK_w in keys) - (SDLK_s in keys))
        local_move.z = ((SDLK_q in keys) - (SDLK_e in keys))
        global_move = local_move.rotate(*-self.rotation)
        self.position += global_move * self.speed * dt

    def set(self):
        glRotate(-90, 1, 0, 0)
        try:
            glRotate(self.rotation.x, 1, 0, 0)
        except Exception as exc:
            print(exc)
            print(self.rotation)
        glRotate(self.rotation.z, 0, 0, 1)
        glTranslate(-self.position.x, -self.position.y, -self.position.z)

    def __repr__(self):
        pos = [round(x, 2) for x in self.position]
        pos_string = str(pos)
        rot = [round(x, 2) for x in self.rotation]
        rot_string = str(rot)
        v = round(self.speed, 2)
        v_string = str(v)
        return '  '.join([pos_string, rot_string, v_string])


class firstperson:
    """First Person Camera (ALL CLIENTS SHOULD HAVE ONE)"""
    
    def __init__(self, rotation=None):
        self.rotation = vec3(rotation) if rotation != None else vec3()

    def update(self, mouse):
        global sensitivity
        self.rotation.z += mouse.x * sensitivity
        self.rotation.x += mouse.y * sensitivity

    def set(self, position):
##        glRotate(-90, 1, 0, 0)
        glRotate(self.rotation.x - 90, 1, 0, 0)
        glRotate(self.rotation.z, 0, 0, 1)
        glTranslate(-position.x, -position.y, -position.z)


class thirdperson:
    """Third Person Camera"""
    #GDC 2014: 50 Game Camera Mistakes
    #http://gdcvault.com/play/1020460/50-Camera
    #https://www.youtube.com/watch?v=C7307qRmlMI
    
    def __init__(self, position, rotation, radius, offset=(0, 0)):
        self.position = vec3(position) if position != None else vec3()
        self.rotation = vec3(rotation) if rotation != None else vec3()
        self.radius = radius if radius != None else 0
        self.offset = vec2(offset)

    def update(self):
        #take player, self and environment,
        #adjust to more ideal camera position
        #raycasts into world and path hints
        #adjust all 7 axis
        pass

    def set(self):
        glRotate(self.rotation.x, 1, 0, 0)
        glRotate(self.rotation.y, 0, 1, 0)
        glRotate(self.rotation.z, 0, 0, 1)
        glTranslate(-self.position.x, -self.position.y, -self.position.z)
        glTranslate(0, 0, -self.radius)
        glTranslate(self.offset.x, self.offset.y, 0)

class fixed:
    def __init__(self, position, rotation):
        self.position = vec3(position)
        self.rotation = vec3(rotation)

    def set(self):
        glRotate(self.rotation.x - 90, 1, 0, 0)
        glRotate(self.rotation.z, 0, 0, 1)
        glTranslate(-self.position.x, -self.position.y, -self.position.z)
        
