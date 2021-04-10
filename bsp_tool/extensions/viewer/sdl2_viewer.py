import ctypes
import time
from typing import Set

import OpenGL.GL as gl
import sdl2

from . import camera
from . import render
from . import vector


camera.keybinds = {camera.UP: [sdl2.SDLK_q], camera.FORWARD: [sdl2.SDLK_w], camera.DOWN: [sdl2.SDLK_e],
                   camera.LEFT: [sdl2.SDLK_a], camera.BACK: [sdl2.SDLK_s], camera.RIGHT: [sdl2.SDLK_d]}

camera.sensitivity = 1


class Viewport:
    camera: camera.Camera
    keys: Set[int]
    mouse_velocity: vector.vec2
    old_time: float
    render_manager: render.Manager
    tickrate: float = 1 / 0.015  # 15ms per frame ~66 fps
    # window: SDL2 Window

    def __init__(self):
        self.camera = camera.Camera((0, 0, 0))
        self.render_manager = render.Manager()
        # input
        self.keys = set()
        self.mouse_velocity = vector.vec2(0, 0)

    def open_window(self, width=576, height=576):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.SDL_CreateWindow(b"SDL2 OpenGL", sdl2.SDL_WINDOWPOS_CENTERED,  sdl2.SDL_WINDOWPOS_CENTERED,
                                            width, height, sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_BORDERLESS)
        gl_context = sdl2.SDL_GL_CreateContext(self.window)
        self.render_manager.init_GL()
        # self.render_manager.init_buffers()
        sdl2.SDL_GL_SetSwapInterval(0)  # high framerates

        self.old_time = time.time()
        sdl_event = sdl2.SDL_Event()
        while self.handle_events(sdl_event):
            self.update()
            self.draw()
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()
        self.render_manager = render.Manager()
        # TODO: save renderables to reload when a new window is opened

    def handle_events(self, event):
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            escape_pressed = (event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE)
            if event.type == sdl2.SDL_QUIT or escape_pressed:
                return False  # close the window
            elif event.type == sdl2.SDL_KEYDOWN:
                self.keys.add(event.key.keysym.sym)
            elif event.type == sdl2.SDL_KEYUP:
                self.keys.discard(event.key.keysym.sym)
            elif event.type == sdl2.SDL_MOUSEMOTION:
                # TODO: accumulate mouse_motion between ticks
                self.mouse_velocity += vector.vec2(event.motion.xrel, event.motion.yrel)
        return True

    def handle_hotkeys(self):
        if sdl2.SDLK_r in self.keys:  # [R]eset Camera
            self.camera = camera.Camera((0, 0, 0))

    def update(self):
        dt = time.time() - self.old_time
        while dt >= 1 / self.tickrate:
            # -- UPDATE ONE TICK -- #
            self.handle_hotkeys()
            self.camera.update(self.mouse_velocity, self.keys, dt)
            self.mouse_velocity = vector.vec2(0, 0)
            # self.render_manager.update()
            # TODO: render.Manager.update(dt) to update uniforms
            # -- CALCULATE ELAPSED TIME -- #
            self.old_time = time.time()
            dt -= 1 / self.tickrate
            self.old_time = time.time()

    def draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        self.camera.set()
        # TODO: replace with: rotate camera. draw 2d skybox. move camera

        # self.render_manager.draw()

        # origin marker
        gl.glUseProgram(0)
        gl.glBegin(gl.GL_LINES)
        gl.glColor(1, 0, 0)  # X+
        gl.glVertex(0, 0, 0)
        gl.glVertex(1, 0, 0)
        gl.glColor(0, 1, 0)  # Y+
        gl.glVertex(0, 0, 0)
        gl.glVertex(0, 1, 0)
        gl.glColor(0, 0, 1)  # Z+
        gl.glVertex(0, 0, 0)
        gl.glVertex(0, 0, 1)
        gl.glEnd()

        sdl2.SDL_GL_SwapWindow(self.window)


def view_bsp(rbsp):  # rBSP only!
    # just grab the first mesh of a rBSP
    special_vertices = rbsp.vertices_of_mesh(0)
    vertices = list()
    for vertex in special_vertices:
        position = rbsp.VERTICES[vertex.position_index]
        normal = rbsp.VERTEX_NORMALS[vertex.normal_index]
        vertices.append((position, normal, vertex.uv))  # universal format
    indices = [i for i, v in enumerate(vertices)]

    viewport = Viewport()
    viewport.render_manager.add_renderable(render.Renderable("Mesh 0", "mesh_flat", vertices, indices))
    viewport.open_window(576, 576)
