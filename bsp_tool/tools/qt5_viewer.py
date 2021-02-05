from collections import namedtuple
import itertools
import os
from typing import Dict, List, Set

import numpy as np
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import gluPerspective
from PyQt5 import QtCore, QtWidgets


shader_folder = os.path.join(os.path.basepath(__file__), "shaders")

Renderable = namedtuple("Renderable", ["name", "shader", "vertex_span", "index_span"])
Update = namedtuple("Update", ["vertices", "vertex_start", "indices", "index_start"])

attrib_types = {"vec3": (3 * 4, gl.GL_FLOAT),
                "vec4": (4 * 4, gl.GL_FLOAT)}

uniform_types = {"vec3": gl.glUniform3f,
                 "vec4": gl.glUniform4f,
                 # NOTE: matrices are treated differently
                 "mat4": gl.glUniformMatrix4fv}  # glUniformMatrix4fv(uniform_location, 1, GL_FALSE, values)


class RenderManager:
    hidden: Set[Renderable]
    renderables: Dict[str, Set[Renderable]]
    # ^ {"shader": Renderable}
    shaders: Dict[str, int]
    # ^ {"shader": id}
    uniforms: Dict[str, Dict[str, int]]
    # ^ {"shader": {"uniform": id}}
    update_queue: List[Update]
    vertex_formats: Dict[str, List[(str, ...)]]
    # ^ {"shader", ""}

    def __init__(self):
        self.renderables = dict()
        self.shaders = dict()
        self.uniforms = dict()
        self.update_queue = list()
        # sampler functions to update shader uniforms
        # constant shader uniform values to be calculated & set before rendering

    def init_GL(self):
        gl.glClearColor(0.25, 0.25, 0.5, 0.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gluPerspective(90, 1, 0.1, 1024)
        gl.glTranslate(0, 0, -8)
        gl.glPointSize(4)
        self.import_shader("mesh_flat")

    def import_shader(self, shader: str):
        global shader_folder
        with open(os.path.join(shader_folder,  f"{shader.split('_')[0]}.vert")) as file:  # mesh_flat -> mesh.vert
            vertex_shader_text = file.read()
        with open(os.path.join(shader_folder, f"{shader}.frag")) as file:  # mesh_flat -> mesh_flat.frag
            fragment_shader_text = file.read()
        vert_shader = compileShader(vertex_shader_text, gl.GL_VERTEX_SHADER)
        frag_shader = compileShader(fragment_shader_text, gl.GL_FRAGMENT_SHADER)
        self.shaders[shader] = compileProgram(vert_shader, frag_shader)
        gl.glLinkProgram(self.shaders[shader])  # compile step 2

        uniforms = dict()
        # ^ {"uniform": }
        layouts = dict()  # for updating vertex attribs & setting render offset
        # ^ {location: ("attrib", glsl_type)}
        for line in vertex_shader_text.split(";"):
            line = line.split()
            if line[0] == "uniform":
                # "uniform", ~precision, glsl_type, uniform
                glsl_type, uniform = line[-2], line[-1]
                uniforms[uniform] = glsl_type
            elif line[0] == "layout(location":
                # "layout(location", "=", location + ")", "in", ~precision, glsl_type, attribute
                location = int(line[2][:-1])
                glsl_type, attribute = line[-2], line[-1]
                layouts[location] = (attribute, glsl_type)

        gl.glUseProgram(self.shaders[shader])
        self.uniforms[shader] = dict()
        for uniform in uniforms:
            self.uniforms[shader][uniform] = gl.glGetUniformLocation(self.shaders[shader], uniform)

    def init_buffers(self, size=256*10**6):  # size is in bytes (default 256MB)
        self.VERTEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VERTEX_BUFFER)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size, None, gl.GL_DYNAMIC_DRAW)
        self.INDEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.INDEX_BUFFER)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, size, None, gl.GL_DYNAMIC_DRAW)
        # shader attrib pointers, must be post buffer setup
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 12, gl.GLvoidp(0))

    def draw(self):
        gl.glUseProgram(self.shaders["basic"])
        gl.glDrawElements(gl.GL_TRIANGLES, self.draw_length, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))

    def update(self):
        if len(self.update_queue) > 0:
            vertices, indices = self.update_queue.pop(0)
            self.update_buffers(vertices, indices)
        view_matrix = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        gl.glUseProgram(self.basic_shader)
        gl.glUniformMatrix4fv(self.matrix_location, 1, gl.GL_FALSE, view_matrix)

    def render_bsp(self, vertices, indices):
        vertices, indices = [(0, 1, 0)], 0
        # data ==>> buffers
        vertex_data = list(itertools.chain(*vertices))  # [(x, y, z), (x, y, z)] -> [x, y, z, x, y, z]
        vertex_data = np.array(vertex_data, dtype=np.float32)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, len(vertex_data) * 4, vertex_data)
        index_data = np.array(indices, dtype=np.uint32)
        gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, len(index_data) * 4, index_data)


class Viewport(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Viewport, self).__init__(parent=None)
        self.render_manager = RenderManager()
        self.clock = QtCore.QTimer()
        self.clock.timeout.connect(self.update)

    def initializeGL(self):
        self.render_manager.init_GL()
        self.render_manager.init_buffers()
        self.clock.start(15)  # tick_length in milliseconds

    def update(self, tick_length=0.015):
        self.makeCurrent()
        gl.glRotate(30 * tick_length, 1, 0, 1.25)
        self.render_manager.update()
        self.doneCurrent()
        super(Viewport, self).update()  # calls paintGL

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.render_manager.draw()


if __name__ == "__main__":
    import sys

    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook  # Python Qt Debug

    app = QtWidgets.QApplication(sys.argv)
    window = Viewport()
    window.setGeometry(128, 64, 576, 576)
    window.render_manager.load_bsp("E:/Mod/Titanfall/maps/mp_angel_city.bsp")
    window.show()
    app.exec_()

