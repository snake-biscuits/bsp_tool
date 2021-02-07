from typing import List

import OpenGL.GL as gl


class Camera:
    position: List[float]
    rotation: List[float]
    speed: float = 384

    def __init__(self, position: (float, float, float), rotation: (float, float, float) = (0, 0, 0)):
        self.position = position
        self.rotation = rotation

    def update(self, mousepos)
