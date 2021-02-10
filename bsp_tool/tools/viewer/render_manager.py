from collections import namedtuple
import itertools
import os
from typing import Any, Dict, List, Set

import numpy as np
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import gluPerspective


shader_folder = os.path.join(os.path.dirname(__file__), "shaders")

Renderable = namedtuple("Renderable", ["name", "shader", "vertices", "indices"])
# ^ name: str, shader: str, vertices: List[List[float]], indices: List[int]
StoredRenderable = namedtuple("StoredRenderable", ["name", "vertex_span", "index_span"])
# ^ name: str, vertex_span: (int, int), index_span: (int, int)
Update = namedtuple("Update", ["vertices_start", "vertices", "indices_start", "indices"])
# ^ vertices_start: int, vertices: List[List[float]], indices_start: int, indices: List[int]

attrib_types = {"vec2": (2 * 4, gl.GL_FLOAT),
                "vec3": (3 * 4, gl.GL_FLOAT),
                "vec4": (4 * 4, gl.GL_FLOAT),
                "mat4": (4 * 4 * 4, gl.GL_FLOAT)}
# ^ {"glsl_type": (size, GL_TYPE)}

uniform_setter = {"vec2": lambda uniform_loc, value: gl.glUniform2f(uniform_loc, *value),
                  "vec3": lambda uniform_loc, value: gl.glUniform3f(uniform_loc, *value),
                  "vec4": lambda uniform_loc, value: gl.glUniform4f(uniform_loc, *value),
                  "mat4": lambda uniform_loc, value: gl.glUniformMatrix4fv(uniform_loc, 1, gl.GL_FALSE, value)}
# ^ {"glsl_type": setter_lambda(uniform_location, value)}


class RenderManager:
    hidden: Set[Renderable]
    renderables: Dict[str, Set[StoredRenderable]]
    # ^ {"shader": {StoredRenderable}}
    shaders: Dict[str, int]
    # ^ {"shader": id}
    uniforms: Dict[str, Dict[str, int]]
    # ^ {"shader": {"uniform": id}}
    update_queue: List[Update]
    vertex_formats: Dict[str, List[Any]]  # "Any" is actually (str, str)
    # ^ {"shader": [("attribute", "glsl_type")]}

    def __init__(self, size=256*10**6):  # size is in bytes (default 256MB)
        self.buffer_size = size
        self.renderables = dict()
        self.shaders = dict()
        self.uniforms = dict()
        self.update_queue = list()
        self.vertex_formats = dict()
        # sampler functions to update shader uniforms
        # constant shader uniform values to be calculated & set before rendering

    def init_GL(self):
        gl.glClearColor(0.25, 0.25, 0.5, 0.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gluPerspective(90, 1, 0.1, 1024)
        gl.glTranslate(0, 0, -8)
        gl.glPointSize(4)
        # TODO: load all shaders from shader_folder
        # load vertex shaders only once and match to all matching fragment shaders
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
        # ^ {("attrib", glsl_type): location}
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
                layouts[(attribute, glsl_type)] = location

        self.vertex_formats[shader] = sorted(layouts, key=lambda k: layouts[k])
        # TODO: configure vertex attribs for each shader (set_shader method?)

        gl.glUseProgram(self.shaders[shader])
        self.uniforms[shader] = dict()
        for uniform in uniforms:
            self.uniforms[shader][uniform] = gl.glGetUniformLocation(self.shaders[shader], uniform)

    def init_buffers(self):
        self.VERTEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VERTEX_BUFFER)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.buffer_size, None, gl.GL_DYNAMIC_DRAW)
        self.INDEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.INDEX_BUFFER)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffer_size, None, gl.GL_DYNAMIC_DRAW)
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
        # update frequently updated shader uniforms; have a queue / cooldowns?
        gl.glUseProgram(self.basic_shader)
        gl.glUniformMatrix4fv(self.matrix_location, 1, gl.GL_FALSE, view_matrix)

    def update_buffers(self):
        if len(self.update_queue) == 0:
            return
        update = self.update_queue.pop(0)
        vertex_data = itertools.chain(*update.vertices)
        vertex_data = np.array(vertex_data, dtype=np.float32)
        # TODO: add an offset
        index_data = np.array(update.indices, dtype=np.uint32)
        gl.glBufferSubData(self.VERTEX_BUFFER, 0, len(vertex_data) * 4, vertex_data)
        gl.glBufferSubData(self.INDEX_BUFFER, 0, len(index_data) * 4, index_data)

    def add_renderable(self, renderable: Renderable):
        if renderable.shader not in self.shaders:
            raise RuntimeError(f"{renderable.shader} not loaded! cannot add renderable '{renderable.name}'")
        # TODO: pick a stretch of memory to fit vertex /index data into
        # use self.buffer_size & self.renderables[shader].allocated
        # need methods for finding & merging spans
        vertex_start = 0
        vertex_size = sum([attrib_types[g][0] for a, g in self.vertex_formats[renderable.shader]])
        flat_vertices = itertools.chain(*renderable.vertices)  # List[List[float]] --> List[float]

        index_start = 0
        offset_indices = [i + (vertex_start // vertex_size) for i in renderable.indices]

        update = Update(vertex_start, flat_vertices, 0, offset_indices)
        self.update_queue.append(update)

        vertex_span = (vertex_start, len(renderable.vertices) * vertex_size)
        index_span = (index_start, len(renderable.indices) * 4)
        stored_renderable = StoredRenderable(renderable.name, vertex_span, index_span)
        self.renderables[renderable.shader].add(stored_renderable)
        # TODO: add to buffer update queue, possibly mutating an existing entry?
