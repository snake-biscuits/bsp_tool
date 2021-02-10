from typing import Any, List

import OpenGL.GL as gl

from . import vector


FORWARD = 0x00
BACK = 0x01
LEFT = 0x02
RIGHT = 0x03
UP = 0x04
DOWN = 0x05

keybinds = {FORWARD: [], BACK: [],
            LEFT: [], RIGHT: [],
            UP: [], DOWN: []}

sensitivity = 2


class Camera:
    position: vector.vec3
    rotation: vector.vec3
    speed: float = 384

    def __init__(self, position: (float, float, float), rotation: (float, float, float) = (0, 0, 0)):
        self.position = vector.vec3(*position)
        self.rotation = vector.vec3(*rotation)

    def __repr__(self):
        pos = [round(x, 2) for x in self.last_position]
        pos_string = str(pos)
        rot = [round(x, 2) for x in self.rotation]
        rot_string = str(rot)
        v = round(self.speed, 2)
        v_string = str(v)
        return "  ".join([pos_string, rot_string, v_string])

    def update(self, mouse_motion: vector.vec2, keys: List[Any], dt: float):
        # mouse
        global sensitivity
        self.rotation.z += mouse_motion.x * sensitivity
        self.rotation.x += mouse_motion.y * sensitivity
        # keyboard
        local_move = vector.vec3()

        def pressed(direction):
            return any((k in keys) for k in keybinds[direction])

        local_move.x = -(pressed(LEFT) - pressed(RIGHT))
        local_move.y = -(pressed(BACK) - pressed(FORWARD))
        local_move.z = -(pressed(DOWN) - pressed(UP))
        global_move = local_move.rotate(*-self.rotation)
        self.position += global_move * self.speed * dt

    def set(self):
        gl.glRotate(-90, 1, 0, 0)  # default Y+ forward
        gl.glRotate(self.rotation.x, 1, 0, 0)
        gl.glRotate(self.rotation.z, 0, 0, 1)
        gl.glTranslate(*-self.position)
